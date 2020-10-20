from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order, OrderLineItem
from merch.models import Merch
from profiles.models import UserProfile

import json
import time


class StripeWebhookHandler:
    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200,
        )

    def _send_confirmation_email(self, order):
        merch_customer_email = order.email
        subject = render_to_string(
            'checkout/emails/email_subject.txt',
            {
                'order': order,
            },
        )
        body = render_to_string(
            'checkout/emails/email_body.txt',
            {
                'order': order,
                'contact_email': settings.DEFAULT_EMAIL,
            },
        )
        send_mail(
            subject,
            body,
            settings.DEFAULT_EMAIL,
            [merch_customer_email],
        )

    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        payment_id = intent.id
        cart = intent.metadata.cart
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details
        delivery_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        for field, value in delivery_details.address.items():
            if value == '':
                delivery_details.address[field] = None

        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = delivery_details.phone
                profile.default_country = delivery_details.address.country
                profile.default_postcode = delivery_details.address.postal_code
                profile.default_town_or_city = delivery_details.address.city
                profile.default_street_address1 = delivery_details.address.line1
                profile.default_street_address2 = delivery_details.address.line2
                profile.default_county = delivery_details.address.state
                profile.save()

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=delivery_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=delivery_details.phone,
                    country__iexact=delivery_details.address.country,
                    postcode__iexact=delivery_details.address.postal_code,
                    town_or_city__iexact=delivery_details.address.city,
                    street_address1__iexact=delivery_details.address.line1,
                    street_address2__iexact=delivery_details.address.line2,
                    county__iexact=delivery_details.address.state,
                    grand_total=grand_total,
                    original_cart=cart,
                    stripe_payment_id=payment_id,
                )
                order_exists = True
                break

            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Order \
                    already exists in the database.',
                status=200,
            )
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=delivery_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=delivery_details.phone,
                    country=delivery_details.address.country,
                    postcode=delivery_details.address.postal_code,
                    town_or_city=delivery_details.address.city,
                    street_address1=delivery_details.address.line1,
                    street_address2=delivery_details.address.line2,
                    county=delivery_details.address.state,
                    original_cart=cart,
                    stripe_payment_id=payment_id,
                )
                for item_id, item_data in json.loads(cart).items():
                    item = Merch.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            item=item,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                item=item,
                                quantity=quantity,
                                item_size=size
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500,
                )

        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200,
        )

    def handle_payment_intent_payment_failed(self, event):
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Order created in webhook.',
            status=200,
        )

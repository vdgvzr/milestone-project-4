from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.conf import settings
from merch.models import Merch


def cart_contents(request):
    """ Create a global context of store totals to be used site-wide """

    """ Define cart variables """
    cart_items = []
    total = 0
    item_count = 0
    cart = request.session.get('cart', {})

    """ For every item in the cart view,
        append to the cart for checkout """
    for item_id, item_data in cart.items():
        if isinstance(item_data, int):
            item = get_object_or_404(Merch, pk=item_id)
            total += item_data * item.price
            item_count += item_data
            cart_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'item': item,
            })
        else:
            item = get_object_or_404(Merch, pk=item_id)
            for size, quantity in item_data['items_by_size'].items():
                total += quantity * item.price
                item_count += quantity
                cart_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'item': item,
                    'size': size,
                })

    delivery = total * Decimal(settings.DELIVERY_PERCENTAGE / 100)

    """ If the user has paid their subscription,
        add the member discount, otherwise create
        the context without """
    if request.user.is_authenticated:
        if request.user.subscription.status == 'paid':
            discount = total * Decimal(settings.MEMBER_DISCOUNT / 100)
            grand_total = delivery + total - discount
            context = {
                'cart_items': cart_items,
                'total': total,
                'item_count': item_count,
                'delivery': delivery,
                'discount': discount,
                'grand_total': grand_total,
            }
        else:
            grand_total = delivery + total
            context = {
                'cart_items': cart_items,
                'total': total,
                'item_count': item_count,
                'delivery': delivery,
                'grand_total': grand_total,
            }
    else:
        grand_total = delivery + total
        context = {
            'cart_items': cart_items,
            'total': total,
            'item_count': item_count,
            'delivery': delivery,
            'grand_total': grand_total,
        }

    return context

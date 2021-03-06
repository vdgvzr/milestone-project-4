/* 
    Stripe payemnts
*/

// Define the constants to be used in the script
const stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
const clientSecret = $('#id_client_secret').text().slice(1, -1);
const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();

// Define the styling of the stripe element
let style = {
    base: {
        color: '#000000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
        color: '#aab7c4'
        }
    },

    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545',
    }
};

// Define and mount the element to the div
let card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function(event) {
    let errorDiv = document.getElementById('card-errors');

    if (event.error) {
        let html = `
            <span class="icon card-error-icon" role="alert">
                <i class="fa fa-times"></i>
            </span>

            <span>${event.error.message}</span>
        `;

        $(errorDiv).html(html);
    } else {
        errorDiv.textContext = '';
    }
});

// Handle form submit
let form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    // Prevent the form from being submitted
    ev.preventDefault();
    card.update({'disabled': true});
    $('#submit-button').attr('disabled', true);

    // Define post variables
    let saveInfo = Boolean($('#id-save-info').attr('checked'));
    let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    let postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    }
    let url = '/checkout/cache_checkout_data/';

    // Post payment method
    $.post(url, postData).done(function() {
        stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
            billing_details: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                email: $.trim(form.email.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    state: $.trim(form.county.value),
                }
            }
        },
        shipping: {
            name: $.trim(form.full_name.value),
            phone: $.trim(form.phone_number.value),
            address: {
                line1: $.trim(form.street_address1.value),
                line2: $.trim(form.street_address2.value),
                city: $.trim(form.town_or_city.value),
                country: $.trim(form.country.value),
                postal_code: $.trim(form.postcode.value),
                state: $.trim(form.county.value),
            }
        },
        }).then(function(result) {
            // Then check result for errors and handle
            if (result.error) {
                let errorDiv = document.getElementById('card-errors');
                let html = `
                    <span class="icon card-error-icon" role="alert">
                        <i class="fa fa-times"></i>
                    </span>

                    <span>${result.error.message}</span>
                `;
                
                $(errorDiv).html(html);
                card.update({'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                // If the intent is successful, submit the form
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function() {
        // If the form submit fails for whatever reason, reload the checkout page
        location.reload();
    })
});





from decouple import config
from django.utils.html import strip_tags

from twilio.rest import Client

from .helpers import generate_bitly_link

account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

# def send_media_on_whatsapp(phone_no):
#     message = client.messages.create(
#         media_url=['https://images.unsplash.com/photo-1545093149-618ce3bcf49d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=668&q=80'],
#         from_='whatsapp:+14155238886',
#         to='whatsapp:{}'.format(phone_no)
#     )
#     print(message.sid)


def send_message_on_whatsapp(invoice,params):
    attachment= []
    for data in invoice.invoice_attachment.all():
        attachment.append(generate_bitly_link(data.attachment.url))
    msg = ',\n'.join(attachment)
    body = params['body'].replace('&nbsp;','')

    message = client.messages.create(
        from_='whatsapp:{}'.format(config('TWILIO_NUMBER')),
        body='{}\nHere is the invoice attachment: {}'.format(
            strip_tags(body),
            msg
        ),
        to='whatsapp:{}'.format(params['to'])
    )
    print(message.sid)
    if 'additional' in params and params['additional'] != '':
        message = client.messages.create(
            from_='whatsapp:{}'.format(config('TWILIO_NUMBER')),
            body='{}\nHere is the invoice attachment: {}'.format(
                params['body'],
                msg
            ),
            to='whatsapp:{}'.format(params['additional'])
        )
        print(message.sid)

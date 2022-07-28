




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
    # message = client.messages.create(
    #     from_='whatsapp:{}'.format(config('TWILIO_NUMBER')),
    #     body='Hi {},\nPlease find the invoice details:\nInvoice No: {},\nInvoice Amount: {},\nInvoice Due Date: {},\nHere is the invoice attachment: {}'.format(
    #         invoice.customer.full_name,
    #         invoice.invoice_number,
    #         invoice.due_amount,
    #         invoice.due_date,
    #         msg
    #     ),
    #     # status_callback='http://postb.in/1234abcd',
    #     to='whatsapp:{}'.format(invoice.customer.primary_phone)
    # )


    message = client.messages.create(
        from_='whatsapp:{}'.format(config('TWILIO_NUMBER')),
        body='Hi {},{}\n,{},\nHere is the invoice attachment: {}'.format(
            invoice.customer.full_name,
            params['subject'],
            strip_tags(params['body']),
            msg
        ),
        to='whatsapp:{}'.format(params['to'])
    )
    print(message.sid)

    if 'additional' in params and params['additional'] != '':
        message = client.messages.create(
            from_='whatsapp:{}'.format(config('TWILIO_NUMBER')),
            body='Hi {},{}\n,{},\nHere is the invoice attachment: {}'.format(
                invoice.customer.full_name,
                params['subject'],
                params['body'],
                msg
            ),
            to='whatsapp:{}'.format(params['additional'])
        )
        print(message.sid)


# string = "<p>Dear Abc Ltd.</p>\n\n<p>Please find your invoice detail below. Feel free to contact us if you have any questions.</p>\n\n<p>&nbsp;</p>\n\n<p>Best,<br />\nJustin Enterprises</p>\n\n<p>&nbsp;</p>\n"

# string = strip_tags(string)
# print(string)
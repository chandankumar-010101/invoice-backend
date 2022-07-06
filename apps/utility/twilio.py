




import os
from twilio.rest import Client


account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

def send_media_on_whatsapp(phone_no):
    message = client.messages.create(
        media_url=['https://images.unsplash.com/photo-1545093149-618ce3bcf49d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=668&q=80'],
        from_='whatsapp:+14155238886',
        to='whatsapp:{}'.format(phone_no)
    )

    print(message.sid)


def send_message_on_whatsapp(phone_no):
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body='Hey, I just met you, and this is crazy...',
        status_callback='http://postb.in/1234abcd',
        to='whatsapp:{}'.format(phone_no)
    )
    print(message.sid)
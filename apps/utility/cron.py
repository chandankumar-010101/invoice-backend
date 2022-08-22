import os
import datetime
import logging



from decouple import config
from django.utils.html import strip_tags

from twilio.rest import Client

from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string

from apps.invoice.models import Invoice
from apps.utility.helpers import SiteUrl,SendMail,GenerateLink
from apps.utility.peach import PeachPay
from .helpers import generate_bitly_link


account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)


def send_reminder_on_whats_app(invoice,body,url):
    attachment= []
    for data in invoice.invoice_attachment.all():
        attachment.append(generate_bitly_link(data.attachment.url))
    body = body.replace('&nbsp;','')
    msg = ',\n'.join(attachment)
    message = client.messages.create(
        from_='whatsapp:{}'.format(config('TWILIO_NUMBER')),
        body='{}\n\nHere is the invoice attachment: {}\nPayment Link: {}'.format(
            strip_tags(body),
            msg,
            url
        ),
        to='whatsapp:{}'.format(invoice.customer.primary_phone)
    )
    print(message.sid)

def send_email(invoice,reminder,manually=False):
    is_sucess, url = PeachPay().generate_payment_link(invoice)
    user = reminder.user
    from datetime import date  
    td = date.today()
    due_date_status = "Due in {} days".format(abs((td-invoice.due_date).days))
            
    if is_sucess:
        subject = reminder.subject.replace('{{invoice_no}}',invoice.invoice_number)
        subject = subject.replace('{{company_name}}',invoice.customer.organization.company_name)
        body = reminder.body.replace('{{customer}}',invoice.customer.full_name)
        body = body.replace('{{invoice_no}}',invoice.invoice_number)
        body = body.replace('{{amount_due}}',str(invoice.due_amount))
        body = body.replace('{{company_name}}',invoice.customer.organization.company_name)
        due_date_status = "{} {}".format(reminder.reminder_type,reminder.days)
        body = body.replace('{{due_date_status}}',due_date_status)

        context = {
            'amount':invoice.due_amount,
            'invoice':invoice,
            'subject':subject,
            'body':body,
            'site_url': 'https://stage.api.jasiricap.com',
            'payment':url
        }
        try:
            get_template = render_to_string(
            'email_template/reminder.html', context)
            SendMail.invoice(
                "You have an invoice reminder from {} due on {}".format(invoice.customer.organization.company_name,invoice.due_date), invoice.customer.primary_email, get_template,[],invoice)
            invoice.invoice_status = 'SENT'
            invoice.reminders +=1
            invoice.save()
            send_reminder_on_whats_app(invoice,body,url)
            print("SENT AND DONE")
        except Exception as e:
            print("ERRROR",e)
        
def send_reminder():
    now = datetime.datetime.now()
    print("====================================")
    print("Running Timing:", now.strftime("%Y-%m-%d %H:%M:%S"))
    today = datetime.datetime.now().date()
    invoices = Invoice.objects.filter(is_online_payment=True).exclude(invoice_status='PAYMENT_DONE')
    for invoice in invoices:
        difference = (today-invoice.due_date).days
        user = invoice.customer.user
        reminder = user.reminder_user.all().last()
        user = reminder.user
        if hasattr(user, 'payment_method') and user.payment_method.auto_payment_reminder:
            if difference < 0:
                for rem in reminder.filter(reminder_type='Overdue By'):
                    if rem.days == abs(difference):
                        send_email(invoice,rem)
            elif difference >= 1:
                for rem in reminder.filter(reminder_type='Due In'):
                    if rem.days == abs(difference):
                        send_email(invoice,rem)
    print("Ending Timing:", now.strftime("%Y-%m-%d %H:%M:%S"))
    print("====================================\n")
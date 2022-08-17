import os
import datetime
import logging

from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string

from apps.invoice.models import Invoice
from apps.utility.helpers import SiteUrl,SendMail,GenerateLink
from apps.utility.peach import PeachPay

def send_email(invoice,reminder,manually=False):
    is_sucess, url = PeachPay().generate_payment_link(invoice)
    msg_type = "Due in "
    msg = abs((td-invoice.due_date).days)
    if manually:
        from datetime import date  
        td = date.today()
        if (td-invoice.due_date).days == 0:
            msg_type = 'Due '
            msg = "Today"
        elif (td-invoice.due_date).days > 1:
            msg_type = "Overdue by "
            msg = abs((td-invoice.due_date).days)
        
    if is_sucess:
        subject = reminder.subject.replace('{{invoice_no}}',invoice.invoice_number)
        subject = subject.replace('{{organization}}',invoice.customer.organization.company_name)
        if manually:
            subject = subject.replace('{{day}}',str(msg))
            subject = subject.replace('{{reminder_type}}',msg_type)
        else:
            subject = subject.replace('{{day}}',str(reminder.days))
            subject = subject.replace('{{reminder_type}}',reminder.reminder_type)
        body = reminder.body.replace('{{customer}}',invoice.customer.full_name)
        body = body.replace('{{invoice_no}}',invoice.invoice_number)
        body = body.replace('{{amount}}',str(invoice.due_amount))
        body = body.replace('{{organization}}',invoice.customer.organization.company_name)
        body = body.replace('{{company_name}}',invoice.customer.organization.company_name)

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
            print("SENT AND DONE")
        except Exception as e:
            print("ERRROR",e)
        
def send_reminder():
    now = datetime.datetime.now()
    print("==================================")
    print("Running Timing:", now.strftime("%Y-%m-%d %H:%M:%S"))
    today = datetime.datetime.now().date()
    invoices = Invoice.objects.filter(is_online_payment=True).exclude(invoice_status='PAYMENT_DONE')
    for invoice in invoices:
        difference = (today-invoice.due_date).days
        user = invoice.customer.user
        reminder = user.reminder_user.all()
        if difference < 0:
            for rem in reminder.filter(reminder_type='Overdue By'):
                if rem.days == abs(difference):
                    send_email(invoice,rem)
        elif difference >= 1:
            for rem in reminder.filter(reminder_type='Due In'):
                if rem.days == abs(difference):
                    send_email(invoice,rem)
    print("Ending Timing:", now.strftime("%Y-%m-%d %H:%M:%S"))
    print("==================================\n")
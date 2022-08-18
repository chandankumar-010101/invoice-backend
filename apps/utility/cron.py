import os
import datetime
import logging

from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string

from apps.invoice.models import Invoice
from apps.utility.helpers import SiteUrl,SendMail,GenerateLink
from apps.utility.peach import PeachPay


def send_reminder_on_whats_app(invoice,reminder):
    pass

def send_email(invoice,reminder,manually=False):
    is_sucess, url = PeachPay().generate_payment_link(invoice)
    user = reminder.user
    from datetime import date  
    td = date.today()
    due_date_status = "Due in {} days".format(abs((td-invoice.due_date).days))
    if manually:
        if (td-invoice.due_date).days == 0:
            due_date_status = 'Due Today'
        elif (td-invoice.due_date).days > 1:
            due_date_status = "Overdue by {} days".format(abs((td-invoice.due_date).days))
        
    if is_sucess:
        subject = reminder.subject.replace('{{invoice_no}}',invoice.invoice_number)
        subject = subject.replace('{{company_name}}',invoice.customer.organization.company_name)
        body = reminder.body.replace('{{customer}}',invoice.customer.full_name)
        body = body.replace('{{invoice_no}}',invoice.invoice_number)
        body = body.replace('{{amount_due}}',str(invoice.due_amount))
        body = body.replace('{{company_name}}',invoice.customer.organization.company_name)
        if manually:
            subject = subject.replace('{{due_date_status}}',due_date_status)
            body = body.replace('{{due_date_status}}',due_date_status)
        else:
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
        reminder = user.reminder_user.all()
        try:
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
        except Exception as e:
            print("Error",e)
    print("Ending Timing:", now.strftime("%Y-%m-%d %H:%M:%S"))
    print("====================================\n")
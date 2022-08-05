import json
import requests

from decouple import config

try:
	from urllib.parse import urlencode
	from urllib.request import build_opener, Request, HTTPHandler
	from urllib.error import HTTPError, URLError
except ImportError:
	from urllib import urlencode
	from urllib2 import build_opener, Request, HTTPHandler, HTTPError, URLError


from apps.invoice.models import Invoice

class PeachPay:
    def __init__(self):
        pass

    def generate_payment_link(self,invoice):
        url = "https://test.ppay.io/merchant/api/payments/generatePaymentLinkApi.json"
        payload = json.dumps({
            "Authentication": {
                "userid": config('PEACH_USER_ID'),
                "password": config('PEACH_PASSWORD'),
                "entityid": config('PEACH_ENTITY_ID')
            },
            "Payment": {
                "merchantInvoiceId": invoice.invoice_number,
                "amount": invoice.due_amount,
                "currency": "KES",
                "files": [],
                "sendEmail": False,
                "sendSms": False,
                "emailCc": invoice.customer.customer.alternate_email if hasattr(invoice.customer, 'customer') else "",
                "emailBcc": "",
                "expiryTime": 3600,
                "notes": "Payment"
            },
            "Customer": {
                "givenName": invoice.customer.full_name,
                "surname": "",
                "email": invoice.customer.primary_email,
                "mobile": "917278737088"
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            print(response.json())
            return True,response.json()['response']['url']
        return  False,response.json()


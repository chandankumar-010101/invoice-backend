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
                "expiryTime": 86400,
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

    
    def get_checkout_id(self,params):
        url = "https://eu-test.oppwa.com/v1/checkouts"
        data = {
            'entityId' :config('PEACH_ENTITY_ID'),
            'amount' : params['amount'],
            'currency' : 'ZAR',
            'paymentType' : 'DB'
        }
        try:
            opener = build_opener(HTTPHandler)
            request = Request(url, data=urlencode(data).encode('utf-8'))
            request.add_header('Authorization', 'Bearer {}'.format(config('PEACH_ACCESS_TOKEN')))
            request.get_method = lambda: 'POST'
            response = opener.open(request)
            return json.loads(response.read())
        except HTTPError as e:
            return json.loads(e.read())
        except URLError as e:
            return e.reason

    def get_payment_status(self,id):
        url = "https://eu-test.oppwa.com/v1/checkouts/{}/payment?entityId={}".format(
            id,
            config('PEACH_ENTITY_ID')
        )
        try:
            opener = build_opener(HTTPHandler)
            request = Request(url, data=b'')
            request.add_header('Authorization', 'Bearer {}'.format(config('PEACH_ACCESS_TOKEN')))
            request.get_method = lambda: 'GET'
            response = opener.open(request)
            return json.loads(response.read())
        except HTTPError as e:
            return json.loads(e.read())
        except URLError as e:
            return e.reason

            
# invoice = Invoice.objects.all().last()
# PeachPay().generate_payment_link(invoice)




# responseData = get_checkout_id()
# print(responseData['id'])
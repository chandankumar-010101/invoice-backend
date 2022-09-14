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
                "mobile": str(invoice.customer.primary_phone).replace("+", "")
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
    
    def recurring(self):
        url = "https://eu-test.oppwa.com/v1/payments"
        data = {
            'entityId' :  config('PEACH_ENTITY_ID'),
            'amount' : '92.00',
            'currency' : 'KES',
            'paymentBrand' : 'VISA',
            'paymentType' : 'DB',
            'card.number' : '4111111111111111',
            'card.holder' : 'Jane Jones',
            'card.expiryMonth' : '05',
            'card.expiryYear' : '2034',
            'card.cvv' : '123',
            'standingInstruction.mode' : 'REPEATED',
            'standingInstruction.source' : 'CIT',
            'standingInstruction.type' : 'RECURRING',
            'createRegistration' : 'true',
            'shopperResultUrl':"https://google.com",
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

    

    def get_webhook_details(self,params):
        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
        }

        json_data = {
            'Authentication': {
                "userid": config('PEACH_USER_ID'),
                "password": config('PEACH_PASSWORD'),
                "entityid": config('PEACH_ENTITY_ID')
            },
            'Event': {
                'eventId': params['Event[eventId]'],
                'type': params['Event[type]'],
            },
        }

        response = requests.post('https://test.ppay.io/merchant/api/payments/getActivityDetail.json', headers=headers, json=json_data)
        # print(response)
        # print(response.json())
        return response.json()


    def get_checkout_id(self,params):
        url = "https://eu-test.oppwa.com/v1/checkouts"
        data = {
            'entityId' :config('PEACH_ENTITY_ID'),
            'amount' : params['amount'],
            'currency' : 'KES',
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

    
    def mpesa(self,params):
        url = "https://testapi.peachpayments.com/v1/payments/"
        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"authentication.userId\"\r\n\r\n"+config('MPESA_PEACH_USER_ID')+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"authentication.password\"\r\n\r\n"+config('MPESA_PEACH_PASSWORD')+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"authentication.entityId\"\r\n\r\n"+config('MPESA_PEACH_ENTITY_ID')+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"merchantTransactionId\"\r\n\r\n"+params['transaction_id']+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"amount\"\r\n\r\n"+params['amount']+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"currency\"\r\n\r\nKES\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"paymentBrand\"\r\n\r\nMPESA\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"paymentType \"\r\n\r\nDB\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"virtualAccount.accountId\"\r\n\r\n"+params['phone_no']+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"shopperResultUrl\"\r\n\r\nhttps://stage.jasiricap.com/\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'cache-control': "no-cache",
            'postman-token': "beb639f1-c0d3-f46b-14ae-5b1b27a86cb1"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        return response.json()
    
# invoice = Invoice.objects.all().last()
# PeachPay().generate_payment_link(invoice)

# print(PeachPay().recurring())

# responseData = get_checkout_id()
# print(responseData['id'])


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
       

    def checkout(self,invoice):
        url = "https://eu-test.oppwa.com/v1/checkouts"
        data = {
            'entityId' : config('PEACH_ENTITY_ID'),
            'amount' : int(invoice.due_amount),
            'currency' : 'KSH',
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

    def status(self,id):
        url = "https://eu-test.oppwa.com/v1/checkouts/{}/payment?entityId={}".format(id,config('PEACH_ENTITY_ID'))
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
# obj = PeachPay()
# responseData = obj.checkout(invoice)
# print(responseData)

# responseData = obj.status("24CC71D3DAC8C583A29CB9B06312888E.uat01-vm-tx01")
# print(responseData)
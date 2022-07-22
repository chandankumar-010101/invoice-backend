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


class PeachPay:
    def __init__(self):
        pass

        

    def checkout(self,params):
        url = "https://eu-test.oppwa.com/v1/checkouts"
        data = {
            'entityId' : config('PEACH_ENTITY_ID'),
            'amount' : '92.00',
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

responseData = request()
print(responseData)
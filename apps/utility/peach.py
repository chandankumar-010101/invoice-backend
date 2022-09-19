import json
import requests

from decouple import config

import os
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
 

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
    
    def recurring(self,instance,amount):
        url = "https://eu-test.oppwa.com/v1/payments"
        data = {
            'entityId' :  config('PEACH_ENTITY_ID'),
            'amount' : amount,
            'currency' : 'KES',
            'paymentBrand' : instance.card_type,
            'paymentType' : 'DB',
            'card.number' : instance.card_number,
            'card.holder' : instance.holder_name,
            'card.expiryMonth' : instance.expiry_month,
            'card.expiryYear' : instance.expiry_year,
            'card.cvv' : instance.cvv_code,
            'standingInstruction.mode' : 'REPEATED',
            'standingInstruction.source' : 'CIT',
            'standingInstruction.type' : 'RECURRING',
            'createRegistration' : 'true',
            'shopperResultUrl':"https://stage.jasiricap.com/",
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
        return response.json()

    def get_decrypting_webhook_data(self,http_body):
        # Data from configuration
        key_from_configuration = "000102030405060708090a0b0c0d0e0f000102030405060708090a0b0c0d0e0f"
        
        # Data from server
        iv_from_http_header = "000000000000000000000000"
        auth_tag_from_http_header = "CE573FB7A41AB78E743180DC83FF09BD"
        http_body = "0A3471C72D9BE49A8520F79C66BBD9A12FF9"
        
        # Convert data to process
        key = binascii.unhexlify(key_from_configuration)
        iv = binascii.unhexlify(iv_from_http_header)
        auth_tag = binascii.unhexlify(auth_tag_from_http_header)
        cipher_text = binascii.unhexlify(http_body)
        
        # Prepare decryption
        decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, auth_tag), backend = default_backend()).decryptor()
        
        # Decrypt
        result = decryptor.update(cipher_text) + decryptor.finalize()
        print("HIII",result.decode('utf-8'))

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


# encryptedBody ='A841198285388A1C44BCE2D50D05BC5B3671F523BBB5A1B0C76199E56940F69B0984E7BFC80774BB6975C1720E81A79B9D3E5DCD9C1CFBC45C3A6ADDE74F3A8ACA5D1E4698079DFAA3E1771EC8EEE02C85303CFCB12B39222C2D0DCA0AAF02D03CB05FCD4A206D689A766472ABBAC8BA518FC7A8913FA90209FBE27262A6E6B35650251F0177280AB014219853E94514407AB0C7D7BD463D136014A421C050FD78D657FE9E0A218C85D2E3060FC101712D2B0B0755CD0104798E9B64C24809CB1D722FF9B68E47686FD45B2694BD01A2E64BFC448B84C91291F53AE5B3E170A4B5CD2EE7DE7AA6F93F3AEDA5F42179702BF21C6837270852B7C0706A192A531EEE2DA27FA7400E89CF6013E800C2153031091D418141919E95F58D5C97A8BDD63C6D1A612FF915DBB8F4841696DC727C82853C934848910A4EC7F1B2582AB84532B6B6889C015AE0227AB4A99C8F4669AE132D58A1F4DFAB75911E684B1E4682787835A0C8384FDA432E6DBC5E535D5D0BE9AD23F4808699BB8DE4AF71DAF778FE6FAFF5D7362A4BD90931CBC64C828CB888FE24212668CA5320AAF10269B500FE0C4D68D570CB76BBA78C5C940B81F8845E33DE03ABAF8DF2CD7D0C092E4F5E1F18D9DCC84D38AB665FF626BF33593D715F95C6EB46344F8E04BDFA5480674B24457E17A9B9667C9AAF9C7009C9783DF4BBF0583B8101A6C4EF81B1A6AE56B38CFD6D486B4C7DBD9361B1BAB1EBDF29E5958144216380FA2AE9394E903746AA43236ADB3582423CF8D589BB1815D43405414697D93374D541A3AD504B72282C450B044BC2FD8B2281A075F6C9785C8421D560750C78EAA71A98FD8310EB727D63D96C9479B83F0CD2FA2A7304AEF16D45E39D2D583A59F99D0967720906B4D01BC14D45681D21E9F7524F00BC8A32762F21E71D320E52AA60E4875539C6FA9E9FA5C5D0FC7ACA62190034D65EE1552128A10AEE9CBC2F44C89FBE33F32296B3E8618BC542C18992C5DC41E03C4293BBD8AFF5C8EE4D97FFD4CDB06690B15050B1D4CF429AF0B85925121ABFC6C46BE615D9AAB8177A0A34C39A07AF06064A719FC0284F0F19C3191365249F50CB9129D0228CAA5D23C90583266BAE55DA57E4CDD016B84795A013934E8411E0DEAA1C988EBB7F998E0168AA6EC6B79D8295640F7446F805A59FC6490C94ABD413C70D255B5FA8790D93F7E4D409C7ECF91172763CC77BB990C191ADECB764ADDE5F7D81DD7A8479D65FFA5515CAF2880CC6E6986BB86C96C5786B23B1D65F3E8E20ACC5C3CA762050CD13D7A4F42B65262B97C6A72E05C093F732BDD87947ADC8483F5B5E80E4B66DA5446F70AA4EE1950F511D044029FF94DBA6E96DEE8F7D78B4E359657DE46BCD32508C1557F689231C2E8CE2EDA0949121BB1E94F58F23B75E215876DD91EB73E275EBD801D7469F20E3E3DA1B079656D28D3B6C240301715DBF51790AD5EAA3647DAAE362F34F77E88F185C1E0680372849A77A64CC86EE552EBBA228092A48E9247F04B631A8DA826875C49A3714988FE0A72EEF5A6A49E185F3E6D2EB453F96BFBDF7EC234241F3C4AC20B63616EBAFC62B3A80B96EA0D9879ABB1735AE085481A55E31F6AF7CFCB2658C561156D4311284233BFAB49D996D0FB4016A78EDD63A22DEEB782491E96D30EBBB7B3B04A947E8C02D64BF330EE23330CE30681F567DD064761F85374E9F872843489E79129FE1D9D8FF38CC6D611C557F8CD8C10BEEBC2C1C70A31929C4CEF2AA2C77F5A8E417F63A9FB51853C2BFE2E4300B7D6BC68375813C85897CE676806C3DA027EAAAB682513635CC85D26A3C4BF2E630EA4235EF269BD8A18936E29872E2FD807FA14EDADDF5F0312E82586EF34EC498DEA61B99F4C1656C5CEA757E0A1184B0D722E24F6EE3480185C7C79CB4DB747CBD98F3C38DB97D125255DF6527F4166C64AF5A7598368445E675DB1065C422F14D3BC5CCC03E5DCADA4D2C72A497345D08D2D1CA2737EA3BFEAA9A09085D81BC914AFC0E0DC270F3B625D64513718027F612D7327AC9BC62F43B60D52F23A422B4AEEC5AB57ADE12B89A3FE8C9F2FDFCDAF259EA0066663279AC6E801B'
# PeachPay().get_decrypting_webhook_data(encryptedBody)
  
# invoice = Invoice.objects.all().last()
# PeachPay().generate_payment_link(invoice)

# print(PeachPay().recurring())

# responseData = get_checkout_id()
# print(responseData['id'])


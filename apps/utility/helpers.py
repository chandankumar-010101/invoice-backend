import random
import datetime
import requests
import mimetypes

from decouple import config

from django.utils import timezone

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes,force_str
from django.utils.dateparse import parse_datetime
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from apps.account.models import User



def filename_path(folder, instance, filename) -> str:
    """
    :param folder: the folder path
    :param instance: the instance of the the file will be upload to
    :param filename: the original file name
    :return: Path string to the file location
    """
    return '{folder_name}/{file_name}.{ext}'.format(
        folder_name=folder,
        file_name=timezone.now().strftime('%Y%m%d%w%H%M%S%f%j'),
        ext=filename.split('.')[-1].lower(),
    )



class GenerateForgotLink(object):
    @staticmethod
    def generate(request,user):
        uid = urlsafe_base64_encode(force_bytes(user.uuid))
        time = urlsafe_base64_encode(force_bytes(datetime.datetime.now()))
        url = "https://stage.jasiricap.com/reset-password/?uuid={0}&time={1}".format(uid, time) 
        return url
        
    @staticmethod
    def decode(uuid,time):
        decoded_time = parse_datetime(force_str(urlsafe_base64_decode(time)))
        minute = (datetime.datetime.now() - decoded_time).total_seconds()/60.0
        user = User.objects.get(uuid=force_str(urlsafe_base64_decode(uuid)))
        return user,minute

class SendMail(object):

    ''' Common Email Setting '''

    @staticmethod
    def mail(subject, email, email_html):
        try:
            to = [email]
            from_email = settings.EMAIL_EMAIL_ID
            msg = EmailMessage(
                subject, email_html, to=to,
                from_email=from_email
            )
            msg.content_subtype = "html"
            msg.send()
            return True
        except Exception as e:
            print("####",e)
            return False

    @staticmethod
    def invoice(subject,email,email_html,cc,invoice):
        try:
            to = [email]
            from_email = settings.EMAIL_EMAIL_ID
            msg = EmailMessage(
                subject, email_html, to=to,
                from_email="{}<{}>".format(invoice.customer.organization.company_name,from_email),
                cc=cc
            )
            for data in invoice.invoice_attachment.all():
                msg.attach(
                    str(data.attachment).split('/')[1], 
                    data.attachment.read(),
                    mimetypes.guess_type(data.attachment.name)[0]
                )
            msg.content_subtype = "html"
            msg.send()
            return True
        except Exception as e:
            print("####",e)
            return False



class SiteUrl(object):

    ''' Get secure and unsecure host name '''

    @staticmethod
    def site_url(request):
        if request.is_secure():
            site_url = 'https://' + request.get_host()
        else:
            site_url = 'http://' + request.get_host()
        return site_url


def generate_bitly_link(url):
    # headers = {
    #     'Authorization': 'Bearer 7c874b571dfac5419a41b1c72b98b3cdb1ffc59b',
    #     'Content-Type': 'application/json',
    # }

    # json_data = {
    #     'long_url': url,
    #     'domain': 'bit.ly',
    # }

    # response = requests.post('https://api-ssl.bitly.com/v4/bitlinks', headers=headers, json=json_data)
    # # print(response.json())
    # if response.status_code == 200:
    #     return response.json()['link']
    return url


def download_file_from_s3(url):
    response = requests.get(url)
    file_name = random.randint(11,99999999)
    extension = 'pdf'
    if 'png' in url:
        extension = "png"
    elif 'jpg' in url:
        extension = "jpg"
    elif 'jpeg' in url:
        extension = "jpeg"
    open("media/temp/{}.{}".format(file_name,extension), "wb").write(response.content)
    return "media/temp/{}.{}".format(file_name,extension)


def ordinal(n): return "%d%s" % (
    n, "tsnrhtdd"[(n//10 % 10 != 1)*(n % 10 < 4)*n % 10::4])


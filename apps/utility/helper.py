import datetime

from decouple import config

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
    
    def generate(request,user):
        uid = urlsafe_base64_encode(force_bytes(user.uuid))
        time = urlsafe_base64_encode(force_bytes(datetime.datetime.now()))
        url = "http://52.7.133.188/forget-password/?uuid={0}&time={1}".format(uid, time) 
        return url
    
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

class SiteUrl(object):

    ''' Get secure and unsecure host name '''

    @staticmethod
    def site_url(request):
        if request.is_secure():
            site_url = 'https://' + request.get_host()
        else:
            site_url = 'http://' + request.get_host()
        return site_url

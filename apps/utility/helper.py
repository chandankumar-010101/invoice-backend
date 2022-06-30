import datetime

from decouple import config

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode



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
        uid = urlsafe_base64_encode(force_bytes(user.id))
        print(uid)
        time = urlsafe_base64_encode(force_bytes(datetime.datetime.now()))
        url = "{}?uuid={0}&time={1}".format(str(SiteUrl.site_url(request)),uid, time) 
        print(url)
        return url

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

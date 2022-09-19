from email import message
import logging

from datetime import datetime, date,timedelta


from django.template.loader import render_to_string
from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q,Sum

from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from .utils import get_jwt_tokens_for_user
import apps.account.user_service as user_service
import apps.account.response_messages as resp_msg
from .models import UserProfile,Organization,StaticContent,User
from .serializer import (
    OrganizationSerializer,
    SignupSerializer, LoginSerializers,
    UserProfileSerializer, UserCreateSerializer,
    UserProfileListSerializer, 
    PasswordchangeSerializer
)
from apps.customer.pagination import CustomPagination
from apps.customer.models import Customer
from apps.invoice.models import Invoice,Subscription

from apps.utility.helpers import SiteUrl,SendMail,GenerateLink
from .permissions import IsAdminOnly
from .schema import (
    login_schema,
    change_password_schema,
    forgot_password_schema,reset_password_schema,
    profile_update_schema,create_user_schema
)
from apps.invoice.serializer import (
    PaymentReminderSerializer,
    CardSerializer,NotificationSerializer,
    SubscriptionSerializer
)
from apps.invoice.models import RolesAndPermissions,PaymentReminder,Notification
logger = logging.getLogger(__name__)


class PaymentView(View):
    def get(self,request):
        # params = request.GET
        return render(request,'payment.html',)


class OrganizationListView(generics.ListAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class SignupView(APIView):
    """ Create new User and organization.

    Register a user and organization and create
    a user profile.
    """

    def save_roles(self,user):
        import json
        data = json.load(open('json/roles.json'))
        RolesAndPermissions.objects.create(
            user=user,
            roles = data
        )
    
    def save_reminder(self,user):
        subject = "Invoice No {{invoice_no}} from {{my_company_name}} is {{due_date_status}}"
        body = """<p>Dear {{customer}},</p>

<p>We want to remind you that invoice {{invoice_no}} is {{due_date_status}} , with an outstanding balance of KES {{amount_due}}</p><br>

<p>Please review your invoice and promptly remit payment at your earliest convenience. Let us know if you have any questions.</p>

<p>Best,<br />
{{my_company_name}}</p>"""

        for days in [3,7,14,21,30]:
            PaymentReminder.objects.create(
                user = user,
                days = days,
                reminder_type = 'Due In' if days ==3 else 'Overdue By',
                subject = subject,
                body = body
            )

    def post(self, request, *args, **kwargs):
        response = {}
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            # create Organization
            is_success,org = user_service.create_organization(request)
            user_type = 2
            if not is_success:
                return Response(org, status=status.HTTP_400_BAD_REQUEST)

            # create user
            try:
                user = user_service.create_admin_user(request, user_type)
            except Exception as e:
                print(str(e))
                logger.error(e)
                return Response({
                    'error': resp_msg.USER_CREATION_UNSUCCESSFULL
                },status=status.HTTP_400_BAD_REQUEST)
            # create profile
            profile = user_service.create_user_profile(request, user, org)
            if (org is not None and
                user is not None and
                    profile is not None):
                queryset = UserProfile.objects.get(email=profile.email)
                serializer = UserProfileSerializer(queryset)
                self.save_roles(user)
                self.save_reminder(user)
                response['profile'] = serializer.data
                response['organization'] = queryset.organization.company_name
                response['user_type'] = user.user_type
                #TODO send email
                return Response(response, status=status.HTTP_201_CREATED)
        logger.error(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """ Login a user in the platform.

    Login the user in the platform and generate access and 
    refresh jwt token for users.
    """
    @swagger_auto_schema(request_body=login_schema, operation_description='Login')
    def post(self, request, *args, **kwargs):
        response = {}
        email = request.data.get('email')
        password = request.data.get('password')
        serializer = LoginSerializers(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                queryset = UserProfile.objects.get(email=email)
                serializer = UserProfileSerializer(queryset)
                token = get_jwt_tokens_for_user(user)
                admin_user = user.parent if user.parent else user
                roles = admin_user.roles_permission_user.roles
                response['profile'] = serializer.data
                response['organization'] = queryset.organization.company_name
                response['phone_number'] = queryset.organization.phone_number
                response['user_type'] = user.get_user_type_display()
                response['access'] = token.get('access')
                response['refresh'] = token.get('refresh')
                response['roles'] = roles
                response['last_login'] = user.last_login
                return Response(response, status=status.HTTP_200_OK)
            return Response({
                'detail': [resp_msg.INVALID_EMAIL_PASSWORD]
            },status=status.HTTP_400_BAD_REQUEST)
        logger.error(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateView(APIView):
    """ Create new User for an organization.
    Register a user and create a user profile.
    validation for only admin user can create new user.
    """

    permission_classes = (IsAuthenticated & IsAdminOnly,)

    @swagger_auto_schema(request_body=create_user_schema, operation_description='Create User')
    def post(self, request, *args, **kwargs):
        admin_user = request.user.parent if request.user.parent else request.user
        serializer = UserCreateSerializer(data=request.data)
        password = ''
        if serializer.is_valid():
            try:
                user_org = UserProfile.objects.get(user=admin_user).organization
                user,password = user_service.create_user_with_role(request)
            except Exception as e:
                print(str(e))
                logger.error(e)
                return Response({
                    'error': resp_msg.USER_CREATION_UNSUCCESSFULL
                },status=status.HTTP_400_BAD_REQUEST)
            if user:
                profile = user_service.create_user_profile(
                    request, user, user_org)
                queryset = UserProfile.objects.get(pk=profile.pk)
                serializer = UserProfileSerializer(queryset)
            context = {
                'email':user.email,
                'password': password,
                'site_url': str(SiteUrl.site_url(request)),
            }
            get_template = render_to_string(
                'email_template/welcome.html', context)
            SendMail.mail(
                "New User Onboarding", user.email, get_template)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateView(APIView):
    """ Create new User for an organization.
    Register a user and create a user profile.
    validation for only admin user can create new user.
    """

    permission_classes = (IsAuthenticated & IsAdminOnly,)
    @swagger_auto_schema(request_body=create_user_schema, operation_description='Update User')
    def put(self, request,pk, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                params = request.data
                instance = UserProfile.objects.get(pk=pk)
                if instance.email != params['email']:
                    if UserProfile.objects.filter(email=params['email']).exists():
                        return Response({
                            'detail': [resp_msg.EMAIL_ALREADY_EXISTS]
                        },status=status.HTTP_400_BAD_REQUEST)
                    else:
                        instance.email = params['email']
                        instance.user.email = params['email']
                if instance.phone != params['phone_number']:
                    if UserProfile.objects.filter(phone=params['phone_number']).exists():
                        return Response({
                            'detail': [resp_msg.PHONE_ALREADY_EXISTS]
                        },status=status.HTTP_400_BAD_REQUEST)
                    else:
                        instance.phone = params['phone_number']
                instance.full_name = params['full_name']
                instance.user.user_type = params['role']
                instance.save()
                instance.user.save()
                return Response({"message": "User updated successfully"})
            except Exception as error:
                logger.error(error)
                return Response({
                    'detail': [error.args[0]]
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request,pk):
        try:
            queryset = UserProfile.objects.get(pk=pk)
            serializer = UserProfileListSerializer(queryset)
            return Response({
                'message':"Data fatched sucessfully",
                'data':serializer.data
            })
        except Exception as error:
            logger.error(error.args[0])
            return Response({
                "data": [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        instance = UserProfile.objects.get(pk=pk)
        instance.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserListView(generics.ListAPIView):
    """ List of user from an organization.

    List of user from an organization, only admin user
    are allowed.
    """

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileListSerializer
    permission_classes = (IsAuthenticated,)
    # permission_classes = (IsAuthenticated & IsAdminOnly,)
    pagination_class = CustomPagination
    pagination_class.page_size = 10

    def list(self, request, *args, **kwargs):
        params = request.GET
        user = request.user.parent if request.user.parent else request.user
        organization = UserProfile.objects.get(user=user).organization
        queryset = UserProfile.objects.filter(organization=organization).exclude(user=self.request.user.profile)

        if 'search' in params and params['search'] !='':
            queryset = queryset.filter(full_name__icontains=params['search'])

        if 'filter' in params and params['filter'] !='':
            queryset = queryset.filter(user__user_type=params['filter'])

        if 'order_by' in params and params['order_by'] !='':
            queryset = queryset.order_by(params['order_by'])
        serializer = self.serializer_class(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class LogoutView(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request):
        logout(request)
        return Response({
            'success': True
        }, status=status.HTTP_200_OK)


class ProfileupdateView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(request_body=profile_update_schema, operation_description='Profile Update')
    def post(self, request, *args, **kwargs):
        params = request.data
        User = get_user_model()
        is_admin = False if request.user.parent else True
        admin_user = request.user.parent if request.user.parent else request.user

        try:
            if params['email'] != request.user.email:
                if User.objects.filter(email = params['email']).exists():
                    return Response({
                        "message": resp_msg.USER_ALREADY_EXISTS
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if is_admin and  params['company_name'] != request.user.profile.organization.company_name:
                if Organization.objects.filter(company_name = params['company_name']).exists():
                    return Response({
                        "message": resp_msg.COMPANY_ALREADY_EXISTS
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if params['phone_number'] != request.user.profile.phone:
                if UserProfile.objects.filter(phone = params['phone_number']).exists():
                    return Response({
                        "message": resp_msg.PHONE_ALREADY_EXISTS
                    }, status=status.HTTP_400_BAD_REQUEST)
            request.user.email = params['email']
            request.user.profile.email = params['email']
            request.user.profile.phone = params['phone_number']
            request.user.profile.full_name = params['full_name']
            if is_admin:
                request.user.profile.organization.email = params['email']
                request.user.profile.organization.phone_number = params['phone_number']
                request.user.profile.organization.company_name = params['company_name']
                request.user.profile.organization.save()
            request.user.save()
            request.user.profile.save()
            serializer = UserProfileSerializer(request.user.profile)
            response={}
            response['profile'] = serializer.data
            response['organization'] = admin_user.profile.organization.company_name
            response['user_type'] = admin_user.user_type
            response['last_login'] = admin_user.last_login
            return Response(response, status=status.HTTP_200_OK)
        except Exception as error:
            logger.error(error.args[0])
            return Response({
                "data": [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):

    permission_classes = (IsAuthenticated, )

    def get_object(self, queryset=None):
        return self.request.user

    @swagger_auto_schema(request_body=change_password_schema, operation_description='Change Password')
    def post(self, request, *args, **kwargs):
        User = get_user_model()
        serializer = PasswordchangeSerializer(data=request.data)
        if serializer.is_valid():
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            user = User.objects.get(email=request.user.email)
            if not user.check_password(current_password):
                return Response({
                    "detail": resp_msg.INCORRECT_PASSWORD
                },status=status.HTTP_400_BAD_REQUEST)
            self.get_object().set_password(new_password)
            self.get_object().save()
            return Response({
                "detail": resp_msg.PASSWORD_CHANGED
            }, status=status.HTTP_200_OK)
        logger.error(serializer.errors)
        return Response({
            "detal": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class StaticContentView(APIView):

    def get(self,request):
        instance = StaticContent.objects.all()
        if instance is not None:
            return Response({
                "industry": instance.last().industry
            }, status=status.HTTP_200_OK)
        return Response({
            "industry": []
        }, status=status.HTTP_204_NO_CONTENT)


class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=forgot_password_schema, operation_description='Forgot Password')
    def post(self,request):
        params = request.data
        try:
            user = User.objects.get(email = params['email'])
            context = {
                'name': user.profile.full_name,
                'url':GenerateLink.generate(request,user),
                'site_url': str(SiteUrl.site_url(request)),
            }
            get_template = render_to_string(
                'email_template/forgot_password.html', context)
            SendMail.mail(
                "Forgot Password Link", user.email, get_template)
            return Response({
                "message":"Mail sent sucessfully."
            },status=status.HTTP_200_OK)
        except Exception as error:
            logger.error([error.args[0]])
            return Response({
                "detail": ["Enter email doest not exist"]
            }, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    @swagger_auto_schema(request_body=reset_password_schema, operation_description='Forgot Password')
    def post(self,request):
        params = request.data
        try:
            user,minutes = GenerateLink.decode(params['uuid'],params['time'])
            if minutes > 15:
                return Response({"message":"Link is Expired."
                },status=status.HTTP_400_BAD_REQUEST)
            user.set_password(params['password'])
            user.save()
            return Response({
                "message":"Password has been reset sucessfully."
            },status=status.HTTP_200_OK)
        except Exception as error:
            logger.error([error.args[0]])
            return Response({
                "detail": [error.args[0]]
            }, status=status.HTTP_400_BAD_REQUEST)

class DashboardView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_collection_time(self,queryset):
        queryset = queryset.filter(invoice_status='PAYMENT_DONE')
        total = 0
        for invoice in queryset:
            payment = invoice.invoice_transaction.all().last()
            total += (payment.payment_date-invoice.due_date).days
        if total == 0:
            return "N/A"
        return "{} Days".format(int(total/queryset.count()))

    def get(self,request):
        import  datetime
        params = request.GET
        admin_user = request.user.parent if request.user.parent else request.user
        customer_id = Customer.objects.filter(organization=admin_user.profile.organization).values_list('id', flat=True)
        queryset = Invoice.objects.filter(customer__id__in=list(customer_id))
        avg_c_t = self.get_collection_time(queryset)
        outstanding_invoice = queryset.filter(~Q(invoice_status='PAYMENT_DONE')).count()
        outstanding_balance = queryset.filter(~Q(invoice_status='PAYMENT_DONE')).aggregate(Sum('due_amount'))
        queryset = queryset.exclude(invoice_status='PAYMENT_DONE')
        current_amount = queryset.filter(due_date__gt = date.today()).aggregate(Sum('due_amount'))
        overdue_amount = queryset.filter(due_date__lt = date.today()).aggregate(Sum('due_amount'))
        if 'date' in params and params['date'] !='':
            queryset = queryset.filter(created_on__lte = params['date'])
        else:
            queryset = queryset.filter(created_on__lte = date.today())
        graph_current_amount = queryset.filter(due_date__gt = date.today()).aggregate(Sum('due_amount'))
        graph_overdue_amount = queryset.filter(due_date__lt = date.today()).aggregate(Sum('due_amount'))
        one_to_thirty_days = queryset.filter(
            due_date__range = [date.today() - timedelta(days=30),date.today() - timedelta(days=2)]
        ).aggregate(Sum('due_amount'))
        thirty_to_sixty_days = queryset.filter(
            due_date__range = [date.today() - timedelta(days=60),date.today()- timedelta(days=30)]
        ).aggregate(Sum('due_amount'))
        sixty_to_ninty_days = queryset.filter(
            due_date__range = [date.today() - timedelta(days=90),date.today()- timedelta(days=60)]
        ).aggregate(Sum('due_amount'))
        ninty_plus_days = queryset.filter(
            due_date__lt = date.today()- timedelta(days=90)
        ).aggregate(Sum('due_amount'))

        
        graph_data = [
            { 'name': "Current", 'value': graph_current_amount['due_amount__sum'] if graph_current_amount['due_amount__sum'] else 00 },
            { 'name': "Overdue", 'value': graph_overdue_amount['due_amount__sum'] if graph_overdue_amount['due_amount__sum'] else 00 },
            { 'name': "0 - 30 Days Overdue", 'value': one_to_thirty_days['due_amount__sum'] if one_to_thirty_days['due_amount__sum'] else 00 },
            { 'name': "31 - 60 Days Overdue", 'value': thirty_to_sixty_days['due_amount__sum'] if thirty_to_sixty_days['due_amount__sum'] else 00 },
            { 'name': "61 - 90 Days Overdue", 'value': sixty_to_ninty_days['due_amount__sum'] if sixty_to_ninty_days['due_amount__sum'] else 00 },
            { 'name': ">91 Days Overdue", 'value':  ninty_plus_days['due_amount__sum'] if ninty_plus_days['due_amount__sum'] else 00 },
        ]
        current_per, overdue_per, one_to_thord_per,thirty_to_sixty_per,sixty_to_ninty_per,ninty_plus_per  = 0.0,0.0,0.0,0.0,0.0,0.0

        if outstanding_balance['due_amount__sum'] > 0 and current_amount['due_amount__sum'] and current_amount['due_amount__sum'] > 0:
            current_per = current_amount['due_amount__sum'] * (100/outstanding_balance['due_amount__sum'])

        if outstanding_balance['due_amount__sum'] > 0 and overdue_amount['due_amount__sum'] and overdue_amount['due_amount__sum'] > 0:
            overdue_per = overdue_amount['due_amount__sum'] * (100/outstanding_balance['due_amount__sum'])
        
        if outstanding_balance['due_amount__sum'] > 0 and one_to_thirty_days['due_amount__sum'] and one_to_thirty_days['due_amount__sum'] > 0:
            one_to_thord_per = one_to_thirty_days['due_amount__sum'] * (100/outstanding_balance['due_amount__sum'])
        
        if outstanding_balance['due_amount__sum'] > 0 and thirty_to_sixty_days['due_amount__sum'] and thirty_to_sixty_days['due_amount__sum'] > 0:
            thirty_to_sixty_per = thirty_to_sixty_days['due_amount__sum'] * (100/outstanding_balance['due_amount__sum'])

        if outstanding_balance['due_amount__sum'] > 0 and sixty_to_ninty_days['due_amount__sum'] and sixty_to_ninty_days['due_amount__sum'] > 0:
            sixty_to_ninty_per = sixty_to_ninty_days['due_amount__sum'] * (100/outstanding_balance['due_amount__sum'])

        if outstanding_balance['due_amount__sum'] > 0 and ninty_plus_days['due_amount__sum'] and ninty_plus_days['due_amount__sum'] > 0:
            ninty_plus_per = ninty_plus_days['due_amount__sum'] * (100/outstanding_balance['due_amount__sum'])

        return Response({
            'message': "Data Fetched Successfully.",
            'graph_data':graph_data,
            'avg_c_t':avg_c_t,
            'current_per':current_per,
            'overdue_per':overdue_per,
            'one_to_thord_per':one_to_thord_per,
            'thirty_to_sixty_per':thirty_to_sixty_per,
            'sixty_to_ninty_per':sixty_to_ninty_per,
            'ninty_plus_per':ninty_plus_per,
            'outstanding_invoice':outstanding_invoice,
            'outstanding_balance':outstanding_balance['due_amount__sum'] if outstanding_balance['due_amount__sum'] else 00,
            'current_amount':current_amount['due_amount__sum'] if current_amount['due_amount__sum'] else 00,
            'overdue_amount':overdue_amount['due_amount__sum'] if overdue_amount['due_amount__sum'] else 00,
        }, status=status.HTTP_200_OK)


class GetSubscription(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self,request):
        admin_user = request.user.parent if request.user.parent else request.user
        message  = ''
        is_trial_account = True
        is_block = False
        if hasattr(admin_user, 'subscription_user') :
            is_trial_account = False
            if admin_user.subscription_user.end_date >= date.today():
                message = "Your subscription plan has been expired on {}. Purchase a subscription for unwanted interruption.".format(admin_user.subscription_user.end_date)
            elif admin_user.subscription_user.end_date + timedelta(days=7) >= date.today():
                is_block = True
                message = "Your subscription plan has been expired on {}. Purchase a subscription for unwanted interruption.".format(admin_user.subscription_user.end_date)
        else:
            is_trial_account = True
            message = "Purchase a subscription for unwanted interruption."

        return Response({
            'is_trial_account':is_trial_account,
            'ending_date':admin_user.subscription_user.end_date if hasattr(admin_user, 'subscription_user') else '',
            "is_block":is_block,
            "message":message
        })

class GetDetailsView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self,request):
        response={}
        payment_method = {}
        admin_user = request.user.parent if request.user.parent else request.user
        serializer = UserProfileSerializer(request.user.profile)
        response['is_editable'] = False if request.user.parent else True
        response['profile'] = serializer.data
        response['organization'] = admin_user.profile.organization.company_name
        response['phone_number'] = request.user.profile.organization.phone_number
        response['user_type'] = request.user.user_type
        response['last_login'] = request.user.last_login
        response['due_payment_reminder'] = PaymentReminderSerializer(admin_user.reminder_user.filter(reminder_type='Due In').order_by("days"),many=True).data
        response['overdue_payment_reminder'] = PaymentReminderSerializer(admin_user.reminder_user.filter(reminder_type='Overdue By').order_by("days"),many=True).data
        payment_method['is_bank_transfer']= admin_user.payment_method.is_bank_transfer if hasattr(admin_user,'payment_method') else False
        payment_method['is_card_payment']= admin_user.payment_method.is_card_payment if hasattr( admin_user,'payment_method') else False
        payment_method['is_mobile_money']= admin_user.payment_method.is_mobile_money if hasattr(admin_user,'payment_method') else False
        payment_method['auto_payment_reminder']= admin_user.payment_method.auto_payment_reminder if hasattr(admin_user,'payment_method') else False
        roles = []
        if request.user.get_user_type_display() == 'Admin':
            roles = request.user.roles_permission_user.roles
        else:
            roles = request.user.parent.roles_permission_user.roles
        response['roles'] = roles
        response['subscription'] = SubscriptionSerializer(Subscription.objects.all().last()).data
        response['payment_method'] = payment_method
        response['card_details'] = CardSerializer(admin_user.card_details_user).data if hasattr(admin_user, 'card_details_user') else {}
        return Response(response,status=status.HTTP_200_OK)

class NotificationView(generics.ListAPIView):
    pagination_class = CustomPagination
    pagination_class.page_size = 5
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        admin_user = self.request.user.parent if self.request.user.parent else self.request.user
        queryset = admin_user.notification_user.all().order_by('is_seen')
        queryset = queryset.order_by('-id')
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(NotificationView, self).list(request, *args, **kwargs)
        admin_user = request.user.parent if request.user.parent else request.user
        queryset = admin_user.notification_user.filter(is_seen = False).count()
        response.data['notification_count'] = queryset
        return Response(response.data,
        status=status.HTTP_200_OK)

class NotificationMarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        admin_user = request.user.parent if request.user.parent else request.user
        admin_user.notification_user.filter(is_seen=False).update(is_seen=True)
        return Response({
            'message': "Notification marked as seen Successfully."
        })

class NotificationSendView(APIView):
    def get(self,request):
        admin_user = request.user.parent if request.user.parent else request.user
        from apps.utility.helpers import triger_socket
        instance = Notification.objects.create(
            user = admin_user,
            title = "Payment Failed",
            message = "HI You have a message",
            icon_class = 'fa fa-clock-o',
            icon_colour = 'red'
        )
        serializer = NotificationSerializer(instance).data
        queryset = admin_user.notification_user.filter(is_seen = False).count()
        serializer['notification_count'] = queryset
        triger_socket(str(admin_user.uuid),serializer)
        return Response({
            'message': "Notification send Successfully."
        })

# from apps.invoice.models import PaymentReminder
# subject = "Invoice No {{invoice_no}} from {{my_company_name}} is {{due_date_status}}"
# body ="""<p>Dear {{customer}},</p>
# <p>We want to remind you that invoice {{invoice_no}} , is {{due_date_status}} , with an outstanding balance of {{amount_due}}</p><br>
# <p>Please review your invoice and promptly remit payment at your earliest convenience. Let us know if you have any questions.</p>
# <p>Best,<br />
# {{my_company_name}}</p>"""

# for reminder in PaymentReminder.objects.all():
#     reminder.subject=subject
#     reminder.body=body
#     reminder.save()


# import json
# data = json.load(open('json/roles.json'))
# for role in RolesAndPermissions.objects.all():
#     role.roles = data
#     role.save()

# user = User.objects.get(email='akshay@oodles.io')
# for data in range(0,35):
#     Notification.objects.create(
#         user = user,
#         title = "Payment Failed",
#         message = "HI You have a message",
#         icon_class = 'fa fa-clock-o',
#         icon_colour = 'red'
#     )
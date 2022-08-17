import logging

from django.template.loader import render_to_string
from django.shortcuts import render
from django.views.generic import View

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

from apps.utility.helpers import SiteUrl,SendMail,GenerateLink
from .permissions import IsAdminOnly
from .schema import (
    login_schema,
    change_password_schema,
    forgot_password_schema,reset_password_schema,
    profile_update_schema,create_user_schema
)
from apps.invoice.serializer import PaymentReminderSerializer,CardSerializer
from apps.invoice.models import RolesAndPermissions,PaymentReminder
logger = logging.getLogger(__name__)


class PaymentView(View):
    def get(self,request):
        return render(request,'payment.html')


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
        subject = "Invoice No {{invoice_no}} from {{organization}} is {{reminder_type}} {{day}} day"
        body = """<p>Dear {{customer}},</p>

<p>We want to remind you that invoice {{invoice_no}} is due, with an outstanding balance of {{amount}} due.</p>

<p>Please see the link below to quick and securely remit payment electronically at no cost to you. Feel free to contact us if you have any questions.</p>

<p>Best,<br />
{{organization}}</p>"""
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
            org = user_service.create_organization(request)
            user_type = 2

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
                roles = []
                if user.get_user_type_display() == 'Admin':
                    roles = user.roles_permission_user.roles
                else:
                    roles = user.parent.roles_permission_user.roles
                response['profile'] = serializer.data
                response['organization'] = queryset.organization.company_name
                response['phone_number'] = queryset.organization.phone_number
                response['user_type'] = user.get_user_type_display()
                response['access'] = token.get('access')
                response['refresh'] = token.get('refresh')
                response['roles'] = roles
                response['last_login'] = user.last_login.strftime("%m/%d/%Y, %H:%M:%S")
                # response['permission'] =  user.parent.roles_permission_user if hasattr(user.parent,'roles_permission_user') else None
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
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user_org = UserProfile.objects.get(user=request.user).organization
            try:
                user = user_service.create_user_with_role(request)
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
                instance.user.set_password(params['password'])
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
        try:
            if params['email'] != request.user.email:
                if User.objects.filter(email = params['email']).exists():
                    return Response({
                        "message": resp_msg.USER_ALREADY_EXISTS
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if params['company_name'] != request.user.profile.organization.company_name:
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
            request.user.profile.organization.email = params['email']
            request.user.profile.organization.phone_number = params['phone_number']
            request.user.profile.organization.company_name = params['company_name']
            request.user.save()
            request.user.profile.save()
            request.user.profile.organization.save()

            serializer = UserProfileSerializer(request.user.profile)
            response={}
            response['profile'] = serializer.data
            response['organization'] = request.user.profile.organization.company_name
            response['user_type'] = request.user.user_type
            response['last_login'] = request.user.last_login.strftime("%m/%d/%Y, %H:%M:%S")
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


class GetDetailsView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self,request):
        response={}
        payment_method = {}
        admin_user = request.user.parent if request.user.parent else request.user

        serializer = UserProfileSerializer(request.user.profile)
        response['profile'] = serializer.data
        response['organization'] = admin_user.profile.organization.company_name
        response['phone_number'] = request.user.profile.organization.phone_number
        response['user_type'] = request.user.user_type
        response['last_login'] = request.user.last_login.strftime("%m/%d/%Y, %H:%M:%S")
        response['payment_reminder'] = PaymentReminderSerializer(admin_user.reminder_user.all(),many=True).data
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
        response['payment_method'] = payment_method
        response['card_details'] = CardSerializer(admin_user.card_details_user).data if hasattr(admin_user, 'card_details_user') else {}
        return Response(response, status=status.HTTP_200_OK)


# from apps.account.models import User
# user= User.objects.get(email='akshay@oodles.io')
# user.set_password('1234578aA')
# user.save()
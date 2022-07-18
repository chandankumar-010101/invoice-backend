import logging



from django.template.loader import render_to_string

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
    UserProfileListSerializer, ProfileupdateSerializer,
    PasswordchangeSerializer
)

from apps.utility.helpers import SiteUrl,SendMail,GenerateForgotLink
from .permissions import IsAdminOnly
from .schema import (
    login_schema,
    change_password_schema,
    forgot_password_schema,reset_password_schema
)

logger = logging.getLogger(__name__)

# Create your views here.

class OrganizationListView(generics.ListAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class SignupView(APIView):
    """ Create new User and organization.

    Register a user and organization and create
    a user profile.
    """

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
                response['profile'] = serializer.data
                response['organization'] = queryset.organization.company_name
                response['user_type'] = user.user_type
                response['access'] = token.get('access')
                response['refresh'] = token.get('refresh')
                response['last_login'] = user.last_login.strftime("%m/%d/%Y, %H:%M:%S")
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


class UserListView(generics.ListAPIView):
    """ List of user from an organization.

    List of user from an organization, only admin user
    are allowed.
    """

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileListSerializer
    permission_classes = (IsAuthenticated & IsAdminOnly,)

    def get_queryset(self):
        user = self.request.user
        organization = UserProfile.objects.get(user=user).organization
        queryset = UserProfile.objects.filter(organization=organization)
        return queryset


class LogoutView(APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request):
        logout(request)
        return Response({
            'success': True
        }, status=status.HTTP_200_OK)


class ProfileupdateView(APIView):

    def post(self, request, *args, **kwargs):
        user_name = request.data.get('user_name')
        name = request.data.get('name')
        email = request.data.get('email')
        company = request.data.get('company')
        role = request.data.get('role')
        profile_status = request.data.get('status')

        serializer = ProfileupdateSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            logger.error(serializer.errors)
            return Response({
                "data": serializer.errors
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
            else:
                print(self)
                self.get_object().set_password(new_password)
                self.get_object().save()
            return Response({
                "detail": resp_msg.PASSWORD_CHANGED
            }, status=status.HTTP_200_OK)
        else:
            logger.error(serializer.errors)
            return Response({
                "data": serializer.errors
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
                'url':GenerateForgotLink.generate(request,user),
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
            user,minutes = GenerateForgotLink.decode(params['uuid'],params['time'])
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



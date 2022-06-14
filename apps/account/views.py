from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
import apps.account.user_service as user_service
import apps.account.response_messages as resp_msg
from .utils import get_jwt_tokens_for_user
from .models import UserProfile
from .models import Organization
from .serializer import OrganizationSerializer
from .serializer import SignupSerializer
from .serializer import LoginSerializers
from .serializer import UserProfileSerializer
from .serializer import UserCreateSerializer
from .serializer import UserProfileListSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOnly


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
        serializer = SignupSerializer(data = request.data)
        if serializer.is_valid():

            # create Organization
            org = user_service.create_organization(request)
            user_type = 2

            #create user
            try:
                user = user_service.create_admin_user(request,user_type)
            except Exception as e:
                print(str(e))
                return Response({'error':resp_msg.USER_CREATION_UNSUCCESSFULL}, 
                status=status.HTTP_400_BAD_REQUEST)

            #create profile
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
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
class LoginView(APIView):
    """ Login a user in the platform.
    
    Login the user in the platform and generate access and 
    refresh jwt token for users.
    """
    def post(self, request, *args, **kwargs):
        response = {}
        email = request.data.get('email')
        password = request.data.get('password')
        serializer = LoginSerializers(data = request.data)
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
                response['last_login'] = user.last_login.strftime("%H:%M %P, %d %b %Y")
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCreateView(APIView):
    """ Create new User for an organization.
    
    Register a user and create a user profile.
    validation for only admin user can create new user.
    """

    permission_classes = (IsAuthenticated & IsAdminOnly,)

    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data = request.data)
        if serializer.is_valid():
            user_org = UserProfile.objects.get(user=request.user).organization

            try:
                user =  user_service.create_user_with_role(request)
            except Exception as e:
                print(str(e))
                return Response({'error':resp_msg.USER_CREATION_UNSUCCESSFULL}, 
                status=status.HTTP_400_BAD_REQUEST)

            if user:
                profile = user_service.create_user_profile(request, user, user_org)
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
        return Response({'success': True}, status=status.HTTP_200_OK)
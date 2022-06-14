from rest_framework import generics
from .models import Organization
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate, login
import apps.account.user_service as user_service
import apps.account.response_messages as resp_msg
from .utils import get_jwt_tokens_for_user
from .models import UserProfile
from .models import Organization
from .serializer import OrganizationSerializer
from .serializer import SignupSerializer
from .serializer import LoginSerializers
from .serializer import UserProfileSerializer


# Create your views here.
class OrganizationListView(generics.ListAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class OrganizationCreateView(generics.CreateAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class SignupView(APIView):
    
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
       

        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):

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
      




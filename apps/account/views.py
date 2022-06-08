from rest_framework import generics
from .models import Organization
from .serializer import OrganizationSerializer
from rest_framework.response import Response


# Create your views here.
class OrganizationListView(generics.ListAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class OrganizationCreateView(generics.CreateAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

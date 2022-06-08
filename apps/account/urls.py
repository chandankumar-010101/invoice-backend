from django.urls import path
from .views import OrganizationListView
from .views import OrganizationCreateView


app_name= 'account'

urlpatterns = [
    path('org/list', OrganizationListView.as_view(), name="org_list"),
    path('org/create', OrganizationCreateView.as_view(), name="org_create"),
]

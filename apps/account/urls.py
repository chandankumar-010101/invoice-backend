from django.urls import path
from .views import OrganizationListView
from .views import OrganizationCreateView
from .views import SignupView
from .views import LoginView
from .views import ProfileupdateView

app_name= 'account'

urlpatterns = [
    path('org/list', OrganizationListView.as_view(), name="org_list"),
    path('org/create', OrganizationCreateView.as_view(), name="org_create"),
    path('signup', SignupView.as_view(), name="signup"),
    path('login', LoginView.as_view(), name="login"),
    path('profileupdate', ProfileupdateView.as_view(), name="profileupdate"),
]

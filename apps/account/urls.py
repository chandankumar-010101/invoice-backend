from django.urls import path
from .views import OrganizationListView
from .views import SignupView
from .views import LoginView
from .views import UserCreateView
from .views import UserListView

app_name= 'account'

urlpatterns = [
    path('org/list', OrganizationListView.as_view(), name="org_list"),
    path('signup', SignupView.as_view(), name="signup"),
    path('login', LoginView.as_view(), name="login"),
    path('create_user', UserCreateView.as_view(), name="create_user"),
    path('users/list', UserListView.as_view(), name="users_list"),
]

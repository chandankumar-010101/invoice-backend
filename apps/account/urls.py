from django.urls import path

from apps.account import views


app_name = 'account'

urlpatterns = [
    path('org/list', views.OrganizationListView.as_view(), name="org_list"),
    path('signup', views.SignupView.as_view(), name="signup"),
    path('login', views.LoginView.as_view(), name="login"),
    path('create_user', views.UserCreateView.as_view(), name="create_user"),
    path('users/list', views.UserListView.as_view(), name="users_list"),
    path('logout', views.LogoutView.as_view(), name="logout"),
    path('profileupdate', views.ProfileupdateView.as_view(), name="profileupdate"),
    path('change_password', views.ChangePasswordView.as_view(), name="change_password"),

    path('forgot-password', views.ForgotPasswordView.as_view(), name="change_password"),
    path('reset-password', views.ResetPasswordView.as_view(), name="change_password"),


    path('static-content', views.StaticContentView.as_view(), name="change_password"),

]

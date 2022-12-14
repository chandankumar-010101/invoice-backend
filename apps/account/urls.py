from django.urls import path

from apps.account import views


app_name = 'account'

urlpatterns = [
    path('', views.PaymentView.as_view(), name="org_list"),


    path('org/list', views.OrganizationListView.as_view(), name="org_list"),
    path('signup', views.SignupView.as_view(), name="signup"),
    path('login', views.LoginView.as_view(), name="login"),
    path('dashboard', views.DashboardView.as_view(), name="login"),
    path('subscription-details', views.GetSubscription.as_view(),name='subscription'),
    path('get-details', views.GetDetailsView.as_view(), name="login"),

    path('create-user', views.UserCreateView.as_view(), name="create_user"),
    path('update-user/<int:pk>', views.UserUpdateView.as_view(), name="create_user"),

    path('users/list', views.UserListView.as_view(), name="users_list"),
    path('logout', views.LogoutView.as_view(), name="logout"),
    path('profileupdate', views.ProfileupdateView.as_view(), name="profileupdate"),
    path('change-password', views.ChangePasswordView.as_view(), name="change_password"),

    path('forgot-password', views.ForgotPasswordView.as_view(),),
    path('reset-password', views.ResetPasswordView.as_view(),),
    path('static-content', views.StaticContentView.as_view(),),
    path('notification', views.NotificationView.as_view(),),
    path('notification/mark-as-read', views.NotificationMarkAsReadView.as_view(),),
    path('notification/send', views.NotificationSendView.as_view(),),


]

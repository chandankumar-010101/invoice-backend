from django.urls import path

from apps.invoice import views

app_name= 'invoice'

urlpatterns = [
    path('csv', views.CsvInvoiceListView.as_view()),
    path('list', views.InvoiceListView.as_view()),
    path('create', views.InvoiceCreateView.as_view()),
    path('update/<str:pk>', views.InvoiceUpdateView.as_view()),
    path('delete/<int:id>', views.DeleteInvoiceView.as_view()),
    path('details/<str:id>', views.RetrieveInvoiceView.as_view()),
    path('send-email-invoice/<str:id>', views.SendInvoiceEmailView.as_view()),
    path('send-whats-invoice/<str:id>', views.SendInvoiceWhatsView.as_view()),
    path('attachment/delete/<int:id>', views.DeleteInvoiceAttachmentView.as_view()),
    path('record-payment/<str:id>', views.RecordPaymentView.as_view()),
    path('send-reminder/<str:id>', views.SendReminderView.as_view()),

    path('payment-method', views.PaymentMethodeView.as_view()),
    path('payment-reminder', views.PaymentReminderView.as_view({
        "post": "create",
        "get": "list",
    })),
    path('payment-reminder/<int:id>', views.PaymentReminderView.as_view({
        "get": "retrieve",
        "put":"partial_update",
        "delete":"destroy",
    })),
    path('schedule-payment/<str:uuid>', views.SchedulePaymentView.as_view()),
    path('update-role-permissions', views.UpdateRolesAndPermissionsView.as_view()),
    path('card-details', views.BillingPaymentView.as_view()),

    # path('peach-webhook', views.peach_webhook),
    path('peach-webhook', views.PeachWebhookView.as_view()),

    path('payment/list', views.PaymentListView.as_view()),
    path('payment/csv', views.CsvPaymentListView.as_view()),


    path('ageing-report/list', views.AgeingReportsListView.as_view()),
    path('ageing-report/csv', views.AgeingReportsCSVView.as_view()),



]

from django.urls import path

from apps.invoice import views

app_name= 'invoice'

urlpatterns = [
    path('list', views.InvoiceListView.as_view()),
    path('create', views.InvoiceCreateView.as_view()),
    path('update/<str:pk>', views.InvoiceUpdateView.as_view()),
    path('delete/<int:id>', views.DeleteInvoiceView.as_view()),
    path('details/<str:id>', views.RetrieveInvoiceView.as_view()),
    path('attachment/delete/<int:id>', views.DeleteInvoiceAttachmentView.as_view()),

    path('send-email-invoice/<str:id>', views.SendInvoiceEmailView.as_view()),

]

from django.urls import path

from apps.invoice import views



app_name= 'account'

urlpatterns = [
    path('list', views.InvoiceListView.as_view(), name="invoice_list"),
    path('create', views.InvoiceCreateView.as_view(), name="invoice_create"),
]

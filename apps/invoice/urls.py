from django.urls import path
from .views import InvoiceListView
from .views import InvoiceCreateView


app_name= 'account'

urlpatterns = [
    path('list', InvoiceListView.as_view(), name="invoice_list"),
    path('create', InvoiceCreateView.as_view(), name="invoice_create"),
]

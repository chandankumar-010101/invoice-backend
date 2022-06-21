from django.urls import path
from .views import CustomerListView
from .views import CustomerCreateView
from .views import RetrieveDeleteCustomer
from .views import CustomerFilterView
from .views import DeleteMultipleCustomerView

app_name= 'customer'

urlpatterns = [
    path('list', CustomerListView.as_view(), name="customer_list"),
    path('create', CustomerCreateView.as_view(), name="customer_create"),
    path('detail/<int:id>', RetrieveDeleteCustomer.as_view(), name="customer_detail"),
    path('multiple/delete', DeleteMultipleCustomerView.as_view(), name="customer_delete_multiple"),
    path('filter', CustomerFilterView.as_view(), name="customer_filter"),
]

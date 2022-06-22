from django.urls import path

from apps.customer import views


app_name= 'customer'

urlpatterns = [
    path('list', views.CustomerListView.as_view(), name="customer_list"),
    path('create', views.CustomerCreateView.as_view(), name="customer_create"),
    path('update/<int:pk>', views.UpdateCustomerView.as_view()),

    path('detail/<int:id>', views.RetrieveDeleteCustomer.as_view(), name="customer_detail"),
    path('multiple/delete', views.DeleteMultipleCustomerView.as_view(), name="customer_delete_multiple"),
    path('filter', views.CustomerFilterView.as_view(), name="customer_filter"),
]

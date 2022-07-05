from django.urls import path

from apps.invoice import views



app_name= 'account'

urlpatterns = [
    path('list', views.InvoiceListView.as_view()),
    path('create', views.InvoiceCreateView.as_view()),
    path('update', views.InvoiceUpdateView.as_view()),
    path('delete/<int:id>', views.DeleteInvoiceView.as_view()),
    path('attachment/delete/<int:id>', views.DeleteInvoiceAttachmentView.as_view()),

]

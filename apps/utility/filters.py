from datetime import datetime, date,timedelta

import django_filters



from apps.invoice.models import Invoice
from psycopg2.extras import DateRange


def invoice_payment_filter(request,queryset):
    if 'customer' in params and params['customer'] !='':
        queryset = queryset.filter(
            invoice__customer= params['customer']
        )
    if 'payment_method' in params and params['payment_method'] !='':
        queryset = queryset.filter(
            payment_mode= params['payment_method']
        )
    return queryset

def invoice_filter(request,queryset):
    params = request.GET

    if 'invoice_status' in params and params['invoice_status'] !='':
        queryset = queryset.filter(
            invoice_status= params['invoice_status'].upper()
        )
    
    if 'customer' in params and params['customer'] !='':
        queryset = queryset.filter(
            customer= params['customer']
        )

    # try:
    if 'due_date' in params and params['due_date'] !='':
        due_date = int(params['due_date'])
        if due_date == 1:
            queryset = queryset.filter(
                due_date__gt = date.today()
            )
        elif due_date == 2:
            queryset = queryset.filter(
                due_date__range = [date.today(),date.today() +  timedelta(days=30)]
            )
        elif due_date == 3:
            queryset = queryset.filter(
                due_date__lt = date.today()-  timedelta(days=1)
            )
        elif due_date == 4:
            queryset = queryset.filter(
                due_date__range = [date.today() -  timedelta(days=30),date.today() -  timedelta(days=2)]
            )
        elif due_date == 5:
            queryset = queryset.filter(
                due_date__range = [date.today() -  timedelta(days=60),date.today()-  timedelta(days=30)]
            )
        elif due_date == 6:
            queryset = queryset.filter(
                due_date__range = [date.today() -  timedelta(days=90),date.today()-  timedelta(days=60)]
            )
        elif due_date == 7:
            queryset = queryset.filter(
                due_date__lt = date.today()-  timedelta(days=90)
            )
    # except Exception as e:
    #     print("EXception",e)
    #     pass

    return queryset

class InvoiceFilter(django_filters.FilterSet):
    invoice_status = django_filters.CharFilter(lookup_expr='iexact')
    due_date = django_filters.CharFilter(method='filter_due_date')
    # customer = django_filters.CharFilter(method='filter_customer')

    def filter_due_date(self, queryset, name, value):
        print("due date")
        return queryset

    # def filter_customer(self, queryset, name, value):
    #     return queryset

    class Meta:
        model = Invoice
        fields = ('invoice_status','due_date')
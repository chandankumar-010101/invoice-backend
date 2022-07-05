import django_filters


from apps.invoice.models import Invoice
from psycopg2.extras import DateRange



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

    try:
        if 'due_date' in params and params['due_date'] !='':
            due_date = int(params['due_date'])

            if due_date == 1:
                pass
            elif due_date == 2:
                pass
            elif due_date == 3:
                pass
            elif due_date == 4:
                pass
            elif due_date == 5:
                pass
            elif due_date == 6:
                pass
            elif due_date == 7:
                pass
    except:
        pass

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
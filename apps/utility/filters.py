import django_filters


from apps.invoice.models import Invoice
from psycopg2.extras import DateRange


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
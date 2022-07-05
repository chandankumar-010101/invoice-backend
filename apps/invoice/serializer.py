from rest_framework import serializers

from .models import Invoice 


class GetInvoiceSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    def get_customer(self,obj):
        return obj.customer.full_name
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('customer','untaxed_amount','vat_amount','notes','curreny')


class InvoiceSerializer(serializers.ModelSerializer):
    attachment = serializers.FileField(required=True)
    invoice_number = serializers.CharField(required=True)
    due_date = serializers.DateField(required=True)
    total_amount = serializers.FloatField(required=True)
    due_amount = serializers.FloatField(required=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('customer','untaxed_amount','vat_amount','notes','curreny')

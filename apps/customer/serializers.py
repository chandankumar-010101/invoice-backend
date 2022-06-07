from rest_framework import serializers
from apps.customer.models import Customer 


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'

class CustomerFilterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id','full_name','email',)
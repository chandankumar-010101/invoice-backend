from unittest.util import _MAX_LENGTH
from rest_framework import serializers
from apps.customer.models import Customer 


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'

    def validate_phone(self,phone):
        print(phone)
        
        if len(phone) > 10 or len(phone) < 10:
            raise serializers .ValidationError('number cannot be less or greater than 10')
            return validate_data     

class CustomerFilterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id','full_name','email',)

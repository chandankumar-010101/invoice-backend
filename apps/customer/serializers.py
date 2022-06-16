from rest_framework import serializers
from apps.customer.models import Customer 
from apps.customer.models import AlternateContact


class ALternateContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlternateContact
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):

    alternate_contact = ALternateContactSerializer()

    class Meta:
        model = Customer
        fields = '__all__'

    def validate_phone(self,phone):
        
        if len(phone) > 10 or len(phone) < 10:
            raise serializers .ValidationError('number cannot be less or greater than 10')
        return phone     

    def create(self, validated_data):
        # print(validated_data)
        alternate_record = validated_data.get('alternate_contact')
        print('==================')
        print(alternate_record)
        instance = Customer.objects.create(**validated_data)
        AlternateContact.objects.create(**alternate_record)
        # alternate_obj.customer = instance
        # alternate_obj.save()
        instance.save()
        return instance

class CustomerFilterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id','full_name','email',)

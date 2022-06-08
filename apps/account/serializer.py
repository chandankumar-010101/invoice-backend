from rest_framework import serializers
from .models import Organization 
from .utils import generate_organization_code


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('code',)

    def create(self, validated_data):
        """ Overrirde serializer save method.
        
        Override the method for saving organization code,
        organization code is auto-generated 10 charcter unique code
        for every organization.
        """
        validated_data['code'] = generate_organization_code()
        return super(OrganizationSerializer, self).create(validated_data)
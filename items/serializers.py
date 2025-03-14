from rest_framework import serializers
from .models import Listing, Category

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__' # get all fields
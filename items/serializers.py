from rest_framework import serializers
from .models import Listing, Category

class ItemSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    class Meta:
        model = Listing
        fields = '__all__' # get all fields
    
    def get_is_favorited(self, obj):
        context = self.context
        return context.get('is_favorited', False)
from rest_framework import serializers
from .models import Listing

class ItemSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    class Meta:
        model = Listing
        fields = '__all__' # get all fields
    
    #checks if the user has favorited a listing
    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return obj in user.profile.favorites.all()
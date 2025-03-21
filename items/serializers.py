from rest_framework import serializers
from .models import Listing


class ItemSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "category",
            "category_name",
            "description",
            "price",
            "image",
            "is_sold",
            "seller",
            "seller_name",
            "created_at",
            "is_favorited",
        ]  # get all fields
        read_only_fields = ["id", "seller_name", "category_name", "created_at"]

    # checks if the user has favorited a listing
    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        return obj in user.profile.favorites.all()

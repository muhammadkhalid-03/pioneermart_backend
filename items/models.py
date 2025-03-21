from django.db import models
from django.contrib.auth.models import User

from categories.models import Category
# Create your models here.

class Listing(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE) #if category is deleted, all items in that category are also deleted
    category_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True) #text field for long er than 255 characters, blank & null if user doesn't wanna add description
    price = models.FloatField()
    image = models.ImageField(upload_to='item_images', blank=True, null=True) #django will create item_images if folder doesn't exist
    is_sold = models.BooleanField(default=False)
    seller = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE) #if user is deleted, all items are also deleted
    seller_name = models.CharField(max_length=255, blank=True, editable=False)  # New field to store the seller's name
    created_at = models.DateTimeField(auto_now_add=True) #add date/time automatically
    # updated_at = models.DateTimeField(auto_now=True)  #TODO: do this after editing functionality

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto-populate seller_name based on the User model
        if self.seller:
            self.seller_name = self.seller.username
        if self.category:
            self.category_name = self.category.name
        super().save(*args, **kwargs)

    #To show the name of the categories
    def __str__(self):
        return self.title
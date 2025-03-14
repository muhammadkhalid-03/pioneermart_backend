# from django.urls import path

# from . import views

# app_name = 'items'

# urlpatterns = [
#     # path('', views.items, name='items'),
#     path('new/', views.new, name='new'), #adding items form
#     path('<int:pk>/', views.detail, name='detail'), #for item details
#     path('<int:pk>/delete/', views.delete, name='delete'), #for deleting items
#     path('<int:pk>/edit/', views.edit, name='edit'),
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet) #if using ViewSet!! this registers all CRUD operations for items
# POST /items/{id}/toggle_favorite/ - Toggles favorite status for a listing.
# GET /items/favorites/ - Retrieves all favorite listings.

urlpatterns = [
    path('', include(router.urls)), #if using ViewSet
]
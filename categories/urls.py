from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet) #if using ViewSet

urlpatterns = [
    path('', include(router.urls)), #if using ViewSet
]
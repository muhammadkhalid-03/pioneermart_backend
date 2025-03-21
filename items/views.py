from rest_framework import viewsets
from categories.serializers import CategorySerializer
from .models import Listing
from .serializers import ItemSerializer
from .permissions import IsSellerOrReadOnly
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser #parse form content + media files
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q #for searching stuff



class ItemViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]  # Use JWT authentication
    permission_classes = [IsAuthenticated, IsSellerOrReadOnly]  # Ensure authentication is required
    parser_classes = [MultiPartParser, FormParser]  # Ensure media files are handled

    def perform_create(self, serializer):
        """Set seller to current user when creating listing."""
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated]) #detail True cause we're doing smth to one single instance of the model
    def toggle_favorite(self, request, pk=None):
        """This function toggles a listing as favorite for the user."""
        user_profile = request.user.profile #get instance of currently logged-in user
        try:
            listing = Listing.objects.get(pk=pk) #get the Listing object from the db where primary key == pk provided 
        except Listing.DoesNotExist:
            return Response({"error": "Listing not found."}, status=404)
        if user_profile.favorites.filter(pk=pk).exists():
            user_profile.favorites.remove(listing) #if item is already in favorites, remove it
            return Response({"message": "Listing removed from favorites."})
        else:
            user_profile.favorites.add(listing) #if item is not in favorites, add it
            return Response({"message": "Listing added to favorites."})
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        """This function returns all favorites for the user."""
        user_profile = request.user.profile
        favorites = user_profile.favorites.all()
        serializer = ItemSerializer(favorites, many=True, context={'request': request}) # serialize a queryset of Listing objects into JSON...many=True iterates over queryset to serialize each Listing object, without many=True seriealizer expects single Listing instance
        return Response(serializer.data) # create response to be sent back to client
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def search_favorites(self, request):
        """This function searches favorites for the user."""
        query = request.GET.get("q", "")
        user_profile = request.user.profile
        favorites = user_profile.favorites.all()
        if query:
            items = favorites.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)  # search in title, description, and category name
            )
        else:
            items = favorites.all()
        serializer = ItemSerializer(items, many=True, context={'request': request}) # serialize a queryset of Listing objects into JSON...many=True iterates over queryset to serialize each Listing object, without many=True seriealizer expects single Listing instance
        return Response(serializer.data) # create response to be sent back to client
    
    # @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    # def favorites_categories(self, request):
    #     """This function returns all favorites for the user."""
    #     user_profile = request.user.profile
    #     favorites_listings = user_profile.favorites.all()
    #     cats = set(listing.category for listing in favorites_listings)
    #     serializer = CategorySerializer(list(cats), many=True, context={'request': request}) # serialize a queryset of Listing objects into JSON...many=True iterates over queryset to serialize each Listing object, without many=True seriealizer expects single Listing instance
    #     return Response(serializer.data) # create response to be sent back to client
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def search_items(self, request, pk=None):
        """This function returns all items for the given category."""
        query = request.GET.get("q", "")
        if query:
            items = Listing.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)  # search in title, description, and category name
            )
        else:
            items = Listing.objects.all() #we didn't find anything so return nothing
        serializer = ItemSerializer(items, many=True, context={'request': request}) #serialize the data to return in a Response
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def my_items(self, request):
        user = request.user  # Get the logged-in user
        items = Listing.objects.filter(seller=user)  # Get only their listings
        serializer = ItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def search_my_items(self, request):
        user = request.user  # Get the logged-in user
        query = request.GET.get("q", "")
        if query:
            items = Listing.objects.filter(seller=user).filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )  # Get only their listings
        else:
            items = Listing.objects.filter(seller=user)
        serializer = ItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    # @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], parser_classes=[MultiPartParser, FormParser])
    # def create_item(self, request):
    #     """Handles creating a new listing at /api/items/create/"""
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(seller=request.user)  # Ensure seller is set
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     print(serializer.errors)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import viewsets
from categories.serializers import CategorySerializer
from .models import Listing
from .serializers import ItemSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q #for searching stuff



class ItemViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]  # Use JWT authentication
    permission_classes = [IsAuthenticated]  # Ensure authentication is required

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
            return Response({"error": "Listing not found."})
        else:
            user_profile.favorites.add(listing) #if item is not in favorites, add it
            return Response({"message": "Listing added to favorites."})
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        """This function returns all favorites for the user."""
        print("\n\nrequest:", request.GET.get("q", ""), "\n\n")
        user_profile = request.user.profile
        favorites = user_profile.favorites.all()
        serializer = ItemSerializer(favorites, many=True, context={'request': request}) # serialize a queryset of Listing objects into JSON...many=True iterates over queryset to serialize each Listing object, without many=True seriealizer expects single Listing instance
        print(serializer.data)
        return Response(serializer.data) # create response to be sent back to client
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def favorites_categories(self, request):
        """This function returns all favorites for the user."""
        user_profile = request.user.profile
        favorites_listings = user_profile.favorites.all()
        cats = set(listing.category for listing in favorites_listings)
        serializer = CategorySerializer(list(cats), many=True, context={'request': request}) # serialize a queryset of Listing objects into JSON...many=True iterates over queryset to serialize each Listing object, without many=True seriealizer expects single Listing instance
        return Response(serializer.data) # create response to be sent back to client
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def search_items(self, request, pk=None):
        """This function returns all items for the given category."""
        # try:
        #     category = Category.objects.get(pk=pk)
        # except Category.DoesNotExist:
        #     return Response({"error": "Category not found."}, status=404)
        # items = Listing.objects.filter(category=category)
        # serializer = ItemSerializer(items, many=True, context={'request': request}) # serialize a queryset of Listing objects into JSON...many=True iterates over queryset to serialize each Listing object, without many=True seriealizer expects single Listing instance
        # return Response(serializer.data) # create response to be sent back to client
        # print("\n\n\n", request, "\n\n\n")
        # query = ""
        query = request.GET.get("q", "")
        if query:
            items = Listing.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)  # search in title, description, and category name
            )
        else:
            items = Listing.objects.none() #we didn't find anything so return nothing
        serializer = ItemSerializer(items, many=True, context={'request': request}) #serialize the data to return in a Response
        print("\n\n\n", serializer.data, "\n\n\n")
        return Response(serializer.data)
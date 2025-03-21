from rest_framework import viewsets
from categories.serializers import CategorySerializer
from .models import Listing
from .serializers import ItemSerializer
from .permissions import IsSellerOrReadOnly
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)  # parse form content + media files
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q  # for searching stuff
from django_filters.rest_framework import DjangoFilterBackend


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]  # Use JWT authentication
    permission_classes = [
        IsAuthenticated,
        IsSellerOrReadOnly,
    ]  # Ensure authentication is required
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "seller"]
    search_fields = ["title", "description", "category__name"]
    ordering_fields = ["created_at", "price", "title"]
    ordering = ["-created_at"]  # order by creation date in descending order
    parser_classes = [MultiPartParser, FormParser]  # Ensure media files are handled

    def perform_create(self, serializer):
        """Set seller to current user when creating listing."""
        serializer.save(seller=self.request.user)

    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        return context

    @action(
        detail=True, methods=["POST"], permission_classes=[IsAuthenticated]
    )  # detail True cause we're doing smth to one single instance of the model
    def toggle_favorite(self, request, pk=None):
        """This function toggles a listing as favorite for the user."""
        try:
            user_profile = (
                request.user.profile
            )  # get instance of currently logged-in user
            listing = self.get_object()

            # listing = Listing.objects.get(pk=pk) #get the Listing object from the db where primary key == pk provided
            if user_profile.favorites.filter(pk=listing.pk).exists():
                user_profile.favorites.remove(
                    listing
                )  # if item is already in favorites, remove it
                return Response({"message": "Listing removed from favorites."})
            else:
                user_profile.favorites.add(
                    listing
                )  # if item is not in favorites, add it
                return Response({"message": "Listing added to favorites."})
        except Listing.DoesNotExist:
            return Response({"error": "Listing not found."}, status=404)

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        """This function returns all favorites for the user."""
        user_profile = request.user.profile
        favorites = user_profile.favorites.all()
        page = self.paginate_queryset(favorites)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            favorites, many=True
        )  # serialize a queryset of Listing objects into JSON...many=True iterates over queryset to serialize each Listing object, without many=True seriealizer expects single Listing instance
        return Response(serializer.data)  # create response to be sent back to client

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def search_favorites(self, request):
        """This function searches favorites for the user."""
        # query = request.GET.get("q", "")
        query = request.query_params.get("q", "")
        user_profile = request.user.profile
        favorites = user_profile.favorites.all()
        if query:
            items = favorites.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(
                    category__name__icontains=query
                )  # search in title, description, and category name
            )
        else:
            items = favorites
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        # serializer = ItemSerializer(items, many=True, context={'request': request}) # serialize a queryset of Listing objects into JSON...many=True iterates over queryset to serialize each Listing object, without many=True seriealizer expects single Listing instance
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)  # create response to be sent back to client

    # @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    # def favorites_categories(self, request):
    #     """This function returns all favorites for the user."""
    #     user_profile = request.user.profile
    #     favorites_listings = user_profile.favorites.all()
    #     cats = set(listing.category for listing in favorites_listings)
    #     serializer = CategorySerializer(list(cats), many=True, context={'request': request}) # serialize a queryset of Listing objects into JSON...many=True iterates over queryset to serialize each Listing object, without many=True seriealizer expects single Listing instance
    #     return Response(serializer.data) # create response to be sent back to client

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def search_items(self, request, pk=None):
        """This function returns all items for the given category."""
        # query = request.GET.get("q", "")
        query = request.query_params.get("q", "")
        if query:
            items = self.queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(
                    category__name__icontains=query
                )  # search in title, description, and category name
            )
        else:
            # items = Listing.objects.all() #we didn't find anything so return nothing
            items = self.queryset
        # serializer = ItemSerializer(items, many=True, context={'request': request}) #serialize the data to return in a Response
        # return Response(serializer.data)
        return self.get_paginated_response(
            self.get_serializer(self.paginate_queryset(items), many=True).data
        )

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def my_items(self, request):
        # user = request.user  # Get the logged-in user
        # items = Listing.objects.filter(seller=user)  # Get only their listings
        items = self.queryset.filter(seller=request.user)
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        # serializer = ItemSerializer(items, many=True, context={'request': request})
        serializer = self.get_serializer(
            items, many=True
        )  # serialize the data to return in a Response
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def search_my_items(self, request):
        # user = request.user  # Get the logged-in user
        # query = request.GET.get("q", "")
        query = request.query_params.get("q", "")
        base_queryset = self.queryset.filter(seller=request.user)
        if query:
            items = base_queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
            )  # Get only their listings
        else:
            # items = Listing.objects.filter(seller=user)
            items = base_queryset
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        # serializer = ItemSerializer(items, many=True, context={'request': request})
        serializer = self.get_serializer(items, many=True)
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

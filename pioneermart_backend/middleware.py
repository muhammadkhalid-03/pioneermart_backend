
from django.utils.deprecation import MiddlewareMixin

class DebugMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Incoming Request Headers:", dict(request.headers))  # Print headers
        return self.get_response(request)
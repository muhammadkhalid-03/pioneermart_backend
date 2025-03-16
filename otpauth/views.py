from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from userprofile.models import UserProfile
from userprofile.serializers import UserSerializer
from .models import OTP
from .serializers import EmailSerializer, OTPVerificationSerializer, TokenSerializer

class RequestOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Create or get user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email}
            )
            # Create new OTP
            otp = OTP.objects.create(email=email)
            
            # Send email with OTP
            subject = 'Your OTP for authentication'
            message = f'Your OTP is {otp.otp}. It will expire in 10 minutes.'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            
            return Response({"detail": "OTP sent to your email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp']
            
            # get latest OTP for this email
            try:
                otp = OTP.objects.filter(email=email).latest('created_at')
                
                if otp.otp == otp_code and otp.is_valid():
                    user = User.objects.get(email=email)
                    profile = user.profile
                    profile.is_verified = True
                    profile.save()
                    
                    # generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    
                    response_data = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': UserSerializer(user).data
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            except (OTP.DoesNotExist, User.DoesNotExist):
                return Response({"detail": "Invalid email or OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import RegisterSerializer, UserProfileSerializer, LoginSerializer, UserUpdateSerializer
from django.db.models import F, Q
from math import radians, cos, sin, asin, sqrt
from django.middleware.csrf import get_token
from django.http import JsonResponse
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class CSRFTokenView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return JsonResponse({'csrfToken': get_token(request)})

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"detail": "Registration failed", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Create the user
            user = serializer.save()
            
            # Authenticate and login the user
            auth_user = authenticate(
                username=request.data['username'],
                password=request.data['password']
            )
            
            if auth_user:
                login(request, auth_user)
                
                # Get the user profile
                profile = UserProfile.objects.get(user_id=user.id)
                
                return Response({
                    "detail": "Registration successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "profile_id": str(profile.id) if profile else None
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                raise Exception("Failed to authenticate user after creation")
                
        except Exception as e:
            return Response(
                {"detail": "Registration failed", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response(
                    {'error': 'Both username and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_active:
                login(request, user)
                
                try:
                    profile = UserProfile.objects.get(user_id=user.id)
                except UserProfile.DoesNotExist:
                    profile = UserProfile(
                        user_id=user.id,
                        username=user.username,
                        email=user.email,
                        first_name=user.first_name,
                        last_name=user.last_name
                    )
                    profile.save()

                return Response({
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'location': profile.location,
                        'profile_id': str(profile.id)
                    }
                })
            else:
                return Response(
                    {'error': 'Invalid username or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': f'Login failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user.userprofile

class UserUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

class NearbyUsersView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        radius = float(self.request.query_params.get('radius', 50))  # Default 50km
        
        try:
            user_location = user.userprofile.location
            user_lat = float(user_location.get('latitude', 0))
            user_lon = float(user_location.get('longitude', 0))
        except (AttributeError, ValueError):
            return UserProfile.objects.none()

        # Simple distance calculation (approximate)
        lat_range = radius / 111.0  # 1 degree = ~111km
        lon_range = radius / (111.0 * cos(radians(user_lat)))

        nearby_profiles = UserProfile.objects.exclude(user=user).filter(
            Q(location__contains={'latitude': True}) & 
            Q(location__contains={'longitude': True})
        ).extra(
            where=[
                """
                ABS(CAST(location->>'latitude' AS FLOAT) - %s) <= %s
                AND ABS(CAST(location->>'longitude' AS FLOAT) - %s) <= %s
                """
            ],
            params=[user_lat, lat_range, user_lon, lon_range]
        )

        return nearby_profiles 
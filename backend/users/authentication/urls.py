from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView,
    UserProfileView, UserUpdateView, NearbyUsersView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile-update'),
    path('nearby-users/', NearbyUsersView.as_view(), name='nearby-users'),
] 
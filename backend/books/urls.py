from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import BookViewSet, BookRentalViewSet, BookReviewViewSet

# Create a router for the main endpoints
router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'rentals', BookRentalViewSet, basename='rental')
router.register(r'reviews', BookReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
] 
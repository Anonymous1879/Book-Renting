from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Book, BookRental, BookReview
from .serializers import BookSerializer, BookRentalSerializer, BookReviewSerializer
from mongoengine.queryset.visitor import Q
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return str(obj.owner_id) == str(request.user.id)

class MongoModelViewSet(viewsets.ViewSet):
    """
    Base viewset for MongoDB models.
    """
    serializer_class = None
    document_class = None
    
    def get_queryset(self):
        return self.document_class.objects.all()

    def list(self, request):
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in list view: {str(e)}")
            return Response(
                {"error": "Failed to retrieve items"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in create view: {str(e)}")
            return Response(
                {"error": "Failed to create item"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        try:
            instance = self.document_class.objects.get(id=pk)
            serializer = self.serializer_class(instance)
            return Response(serializer.data)
        except self.document_class.DoesNotExist:
            return Response(
                {"error": "Item not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in retrieve view: {str(e)}")
            return Response(
                {"error": "Failed to retrieve item"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        try:
            instance = self.document_class.objects.get(id=pk)
            serializer = self.serializer_class(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except self.document_class.DoesNotExist:
            return Response(
                {"error": "Item not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in update view: {str(e)}")
            return Response(
                {"error": "Failed to update item"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        try:
            instance = self.document_class.objects.get(id=pk)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except self.document_class.DoesNotExist:
            return Response(
                {"error": "Item not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in destroy view: {str(e)}")
            return Response(
                {"error": "Failed to delete item"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BookViewSet(MongoModelViewSet):
    serializer_class = BookSerializer
    document_class = Book
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'author', 'description', 'category', 'tags']
    ordering_fields = ['title', 'publication_year', 'price_per_day', 'rating', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Apply search and ordering filters
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def perform_create(self, serializer):
        try:
            serializer.validated_data['owner_id'] = str(self.request.user.id)
            serializer.save()
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            raise ValidationError("Failed to create book")

    @action(detail=False, methods=['get'])
    def my_books(self, request):
        try:
            queryset = self.get_queryset().filter(owner_id=str(request.user.id))
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in my_books: {str(e)}")
            return Response(
                {"error": "Failed to retrieve your books"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def available(self, request):
        try:
            queryset = self.get_queryset().filter(
                available_for_rent=True,
                owner_id__ne=str(request.user.id)
            )
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in available books: {str(e)}")
            return Response(
                {"error": "Failed to retrieve available books"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BookRentalViewSet(MongoModelViewSet):
    serializer_class = BookRentalSerializer
    document_class = BookRental
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = str(self.request.user.id)
        return self.document_class.objects.filter(
            Q(renter_id=user_id) | Q(book_owner_id=user_id)
        )

    def perform_create(self, serializer):
        try:
            # Get the book details first
            book_id = serializer.validated_data.get('book_id')
            book = Book.objects.get(id=book_id)
            
            if not book.available_for_rent:
                raise ValidationError("This book is not available for rent")
            
            # Set required fields
            serializer.validated_data['renter_id'] = str(self.request.user.id)
            serializer.validated_data['book_owner_id'] = str(book.owner_id)
            serializer.validated_data['status'] = 'PENDING'
            
            # Create the rental
            serializer.save()
            
        except Book.DoesNotExist:
            raise ValidationError("Book not found")
        except Exception as e:
            logger.error(f"Error in rental creation: {str(e)}")
            raise ValidationError("Failed to create rental")

    @action(detail=True, methods=['post'])
    def approve_rental(self, request, pk=None):
        try:
            rental = self.get_object()
            
            if str(rental.book_owner_id) != str(request.user.id):
                return Response(
                    {'error': 'Only the book owner can approve rentals'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if rental.status != 'PENDING':
                return Response(
                    {'error': 'This rental cannot be approved'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            rental.status = 'ACTIVE'
            rental.owner_approval = True
            rental.save()

            # Update book availability
            book = rental.book
            book.available_for_rent = False
            book.save()

            serializer = self.serializer_class(rental)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in approve_rental: {str(e)}")
            return Response(
                {"error": "Failed to approve rental"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def reject_rental(self, request, pk=None):
        try:
            rental = self.get_object()
            
            if str(rental.book_owner_id) != str(request.user.id):
                return Response(
                    {'error': 'Only the book owner can reject rentals'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if rental.status != 'PENDING':
                return Response(
                    {'error': 'This rental cannot be rejected'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            rental.status = 'REJECTED'
            rental.save()

            serializer = self.serializer_class(rental)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in reject_rental: {str(e)}")
            return Response(
                {"error": "Failed to reject rental"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        try:
            rental = self.get_object()
            
            if rental.status != 'ACTIVE':
                return Response(
                    {'error': 'This rental cannot be returned'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if str(rental.renter_id) != str(request.user.id):
                return Response(
                    {'error': 'Only the renter can return the book'},
                    status=status.HTTP_403_FORBIDDEN
                )

            rental.actual_return_date = timezone.now()
            rental.status = 'RETURNED'
            rental.save()

            # Update book availability
            book = rental.book
            book.available_for_rent = True
            book.save()

            serializer = self.serializer_class(rental)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in return_book: {str(e)}")
            return Response(
                {"error": "Failed to return book"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def my_rentals(self, request):
        try:
            rentals = self.get_queryset().filter(renter_id=str(request.user.id))
            serializer = self.serializer_class(rentals, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in my_rentals: {str(e)}")
            return Response(
                {"error": "Failed to retrieve your rentals"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def rental_requests(self, request):
        try:
            rentals = self.get_queryset().filter(
                book_owner_id=str(request.user.id),
                status='PENDING'
            )
            serializer = self.serializer_class(rentals, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in rental_requests: {str(e)}")
            return Response(
                {"error": "Failed to retrieve rental requests"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        try:
            active_rentals = self.get_queryset().filter(status='ACTIVE')
            serializer = self.serializer_class(active_rentals, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in active rentals: {str(e)}")
            return Response(
                {"error": "Failed to retrieve active rentals"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        try:
            overdue_rentals = self.get_queryset().filter(
                status='ACTIVE',
                return_date__lt=timezone.now()
            )
            serializer = self.serializer_class(overdue_rentals, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in overdue rentals: {str(e)}")
            return Response(
                {"error": "Failed to retrieve overdue rentals"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BookReviewViewSet(MongoModelViewSet):
    serializer_class = BookReviewSerializer
    document_class = BookReview
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        try:
            # Check if user has already reviewed this book
            book_id = serializer.validated_data.get('book_id')
            existing_review = BookReview.objects.filter(
                book_id=book_id,
                reviewer_id=str(self.request.user.id)
            ).first()
            
            if existing_review:
                raise ValidationError("You have already reviewed this book")
            
            serializer.validated_data['reviewer_id'] = str(self.request.user.id)
            serializer.save()
            
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"Error in create review: {str(e)}")
            raise ValidationError("Failed to create review")

    @action(detail=True, methods=['post'])
    def vote_helpful(self, request, pk=None):
        try:
            review = self.get_object()
            review.helpful_votes += 1
            review.save()
            return Response({'status': 'vote recorded'})
        except Exception as e:
            logger.error(f"Error in vote_helpful: {str(e)}")
            return Response(
                {"error": "Failed to record vote"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        review = self.get_object()
        review.reported = True
        review.review_metadata = review.review_metadata or {}
        review.review_metadata.update({
            'report_reason': request.data.get('reason', ''),
            'reported_by': str(request.user.id),
            'reported_at': timezone.now().isoformat()
        })
        review.save()
        return Response({'status': 'review reported'})
# serializers.py

from rest_framework import serializers
from .models import Book, BookRental, BookReview
from users.serializers import UserProfileSerializer

class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class BookSerializer(serializers.Serializer):
    id = serializers.CharField(source='_id', read_only=True)
    title = serializers.CharField(max_length=200, required=True)
    author = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(allow_blank=True, required=False)
    isbn = serializers.CharField(max_length=13, required=True)
    cover_image = serializers.URLField(allow_blank=True, required=False)
    publication_year = serializers.IntegerField(allow_null=True, required=False)
    owner_id = serializers.CharField(required=False)  # Changed to CharField
    available_for_rent = serializers.BooleanField(default=True)
    price_per_day = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    category = serializers.CharField(max_length=100, allow_blank=True, required=False)
    language = serializers.CharField(max_length=50, default='English', required=False)
    condition = serializers.CharField(max_length=50, default='GOOD', required=False)
    tags = serializers.ListField(child=serializers.CharField(), default=list, required=False)
    location = serializers.DictField(default=dict, required=False)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    total_ratings = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        if 'owner_id' not in validated_data:
            raise serializers.ValidationError({'owner_id': 'This field is required.'})
        return Book(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BookRentalSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    book = BookSerializer(read_only=True)
    book_id = serializers.CharField(write_only=True)
    renter_id = serializers.CharField()  # Changed to CharField
    book_owner_id = serializers.CharField(read_only=True)  # New field
    rental_start_date = serializers.DateTimeField()
    rental_end_date = serializers.DateTimeField()
    actual_return_date = serializers.DateTimeField(allow_null=True, required=False)
    status = serializers.CharField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    owner_approval = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        if data['rental_start_date'] >= data['rental_end_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data

    def create(self, validated_data):
        book_id = validated_data.pop('book_id')
        try:
            book = Book.objects.get(id=book_id)
            if not book.available_for_rent:
                raise serializers.ValidationError("This book is not available for rent")
            validated_data['book'] = book
            validated_data['book_owner_id'] = str(book.owner_id)
            validated_data['status'] = 'PENDING'
            return BookRental.objects.create(**validated_data)
        except Book.DoesNotExist:
            raise serializers.ValidationError("Invalid book_id")

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BookReviewSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    book = BookSerializer(read_only=True)
    book_id = serializers.CharField(write_only=True)
    reviewer_id = serializers.CharField()  # Changed to CharField
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review_text = serializers.CharField(allow_blank=True)
    helpful_votes = serializers.IntegerField(read_only=True, default=0)
    reported = serializers.BooleanField(read_only=True, default=False)
    review_metadata = serializers.DictField(read_only=True, default=dict)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        book_id = validated_data.pop('book_id')
        try:
            book = Book.objects.get(id=book_id)
            review = BookReview.objects.create(book=book, **validated_data)
            
            # Update book rating
            book_reviews = BookReview.objects.filter(book=book)
            total_ratings = book_reviews.count()
            avg_rating = sum(r.rating for r in book_reviews) / total_ratings if total_ratings > 0 else 0
            
            book.rating = round(avg_rating, 2)
            book.total_ratings = total_ratings
            book.save()
            
            return review
        except Book.DoesNotExist:
            raise serializers.ValidationError("Invalid book_id")

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
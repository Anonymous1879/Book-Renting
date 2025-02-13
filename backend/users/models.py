from django.contrib.auth.models import User
from mongoengine import Document, StringField, DictField, DecimalField, IntField, DateTimeField, ObjectIdField
from datetime import datetime
from bson import ObjectId

class UserProfile(Document):
    _id = ObjectIdField(primary_key=True, default=ObjectId)
    user_id = IntField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    first_name = StringField(default='')
    last_name = StringField(default='')
    location = DictField(default=dict)  # Store location data (city, state, coordinates)
    rating = DecimalField(precision=2, default=0.0)
    total_ratings = IntField(default=0)
    joined_date = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'user_profiles',
        'indexes': [
            'user_id',
            'username',
            'email',
            'rating'
        ]
    }

    def __str__(self):
        return f"{self.username}'s profile" 
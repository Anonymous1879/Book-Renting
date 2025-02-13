from django.db import models
from django.contrib.auth.models import User
from djongo import models as djongo_models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    location = djongo_models.JSONField(default=dict)  # Store location data (city, state, coordinates)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_ratings = models.IntegerField(default=0)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['joined_date']),
        ] 
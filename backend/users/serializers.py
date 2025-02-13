from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile
from django.db import transaction

class UserProfileSerializer(serializers.Serializer):
    id = serializers.CharField(source='_id', read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    location = serializers.DictField(required=False, default=dict)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    total_ratings = serializers.IntegerField(read_only=True)
    joined_date = serializers.DateTimeField(read_only=True)

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    location = serializers.DictField(required=False, default=dict)

    def validate_password(self, value):
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username already exists"})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
        if UserProfile.objects.filter(username=data['username']).count() > 0:
            raise serializers.ValidationError({"username": "Username already exists in profiles"})
        if UserProfile.objects.filter(email=data['email']).count() > 0:
            raise serializers.ValidationError({"email": "Email already exists in profiles"})
        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():
                # Remove password2 and location from the data
                validated_data.pop('password2')
                location = validated_data.pop('location', {})
                password = validated_data.pop('password')
                
                # Create Django user
                user = User.objects.create_user(
                    username=validated_data['username'],
                    email=validated_data['email'],
                    password=password,
                    first_name=validated_data.get('first_name', ''),
                    last_name=validated_data.get('last_name', '')
                )

                # Create MongoDB UserProfile
                try:
                    profile = UserProfile(
                        user_id=user.id,
                        username=user.username,
                        email=user.email,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        location=location
                    )
                    profile.save()
                except Exception as profile_error:
                    # If profile creation fails, delete the user
                    user.delete()
                    raise serializers.ValidationError({
                        "profile": f"Failed to create user profile: {str(profile_error)}"
                    })

                return user

        except Exception as e:
            # Clean up any partial data if needed
            username = validated_data.get('username')
            email = validated_data.get('email')
            if username:
                User.objects.filter(username=username).delete()
                UserProfile.objects.filter(username=username).delete()
            if email:
                User.objects.filter(email=email).delete()
                UserProfile.objects.filter(email=email).delete()
            
            raise serializers.ValidationError({
                "error": f"Failed to create user: {str(e)}"
            })
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            data['user'] = user
            return data
        raise serializers.ValidationError("Invalid credentials")

class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    location = serializers.DictField(required=False)

    def validate(self, data):
        if 'new_password' in data and not data.get('current_password'):
            raise serializers.ValidationError("Current password is required to set a new password")
        if 'current_password' in data and not self.instance.check_password(data['current_password']):
            raise serializers.ValidationError("Current password is incorrect")
        return data

    def update(self, instance, validated_data):
        if 'new_password' in validated_data:
            instance.set_password(validated_data.pop('new_password'))
        validated_data.pop('current_password', None)
        
        # Update User model fields
        for attr, value in validated_data.items():
            if attr != 'location':
                setattr(instance, attr, value)
        instance.save()
        
        # Update UserProfile location if provided
        if 'location' in validated_data:
            profile = UserProfile.objects.get(user_id=instance.id)
            profile.location = validated_data['location']
            profile.save()
        
        return instance 
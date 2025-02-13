from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    location = serializers.DictField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'location')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        password2 = validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()

        # Create user profile
        UserProfile.objects.create(
            user=user,
            location=location_data
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    location = serializers.DictField()

    class Meta:
        model = UserProfile
        fields = ('user', 'location', 'rating', 'total_ratings', 'joined_date')
        read_only_fields = ('rating', 'total_ratings', 'joined_date')

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserUpdateSerializer(serializers.ModelSerializer):
    location = serializers.DictField(required=False)
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'location', 'current_password', 'new_password')

    def validate(self, attrs):
        if 'new_password' in attrs and not attrs.get('current_password'):
            raise serializers.ValidationError({"current_password": "Current password is required to set new password"})
        return attrs

    def update(self, instance, validated_data):
        if 'current_password' in validated_data and 'new_password' in validated_data:
            if not instance.check_password(validated_data['current_password']):
                raise serializers.ValidationError({"current_password": "Wrong password"})
            instance.set_password(validated_data['new_password'])

        if 'location' in validated_data:
            profile = instance.userprofile
            profile.location = validated_data.pop('location')
            profile.save()

        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance 
"""
Serializers for the User API view
"""

# serialize is just the way to co nvert objects to and from python objects


from django.contrib.auth import (get_user_model, authenticate)
from rest_framework import serializers

from django.utils.translation import gettext as _

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    # additional information we are passing to serialize, the model, fields and the extra_kwargs
    class Meta:
        model = get_user_model()
        # parameters which user can change themselves
        fields = ['email', 'password', 'name']
        # extra info we want to provide. Such as password as write_only ie user can only write and won't be able to get the password in return. Hence won't be able to read the password back
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # after the data is validated, the function will create the user with the input data
    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return the user"""
        # once password is retrieved remove from the dictionary
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password (password)
            user.save()
        return user
    

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False,)

    # validate method for the token serializer
    def validate(self, attrs):
        """validate and authenticate the user"""
        # retrieve the password and email
        email = attrs.get('email')
        password = attrs.get('password')
        
        # authenticate the user by checking the password and the email
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            msg = _('Unable to authenticate with the provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
    

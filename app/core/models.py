"""
Database Models
"""
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
# Abstract base user class has the functionality for auth system but not any field
# Permission Mixin consists the fields and the permissions required for any model
# Extra fields will include extra fields such as name, phone number etc and will be saved in the database. In this way we are not required to update the create_user() method, whenever we want to include any extra fields

class UserManager(BaseUserManager):
    """Manager for the user model"""
    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new user"""
        if not email:
            raise ValueError('User must have an email address.')
        # normalizing means, converting the email address to correct format and casing
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        # this is the best method to save the data, if in later stage we are using multiple db in our project
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password):
        """Create and return a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """User in the System"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # define the UserManager to our model
    objects = UserManager()

    # this is how we replace the default username field with default user model to our custom email field
    USERNAME_FIELD = 'email'


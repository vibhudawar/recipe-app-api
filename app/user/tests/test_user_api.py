"""
Test for the user api
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

# this function will create user with all the parameters we have passed in
def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

# unauthenticated request ie registering a new user
class PublicUserApiTests(TestCase):
    """Test the public features of the user api"""
    def setUp(self):
        # this makes the APIClient for testing purposes
        self.client = APIClient()
    
    def test_create_user_success(self) :
        """Test creating a user is successful."""
        payload = {
                'email': 'test@example.com',
                'password': 'testpass123',
                'name': 'Test Name',
        }

        # http post request to create a user on the CREATE_USER_URL
        res = self.client.post(CREATE_USER_URL, payload)
        # now check the statuses
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # retrieve the email address from the payload
        user = get_user_model().objects.get(email=payload['email'])
        # check the password, by checking the hash code same or not?
        self.assertTrue(user.check_password(payload['password']))
        # this ensures that there is not key as the password in the response, so that we won't be returning the password hash to the user 
        self.assertNotIn('password', res.data)
    
    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        # if the password is very small, then send the bad_request code
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # first see if the user exists in the database or not using email address.
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        # checking if the user exists or not
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        # creates the user
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)
        
        # extract the payload: email and password
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        # serve the payload to the TOKEN_URL
        res = self.client. post (TOKEN_URL, payload)
        # return the token
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_0K)

    def test_create_token_bad_credentials (self) :
        """Test returns error if credentials invalid"""
        create_user(email='test@example.com', password='goodpass')
        
        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client. post (TOKEN_URL, payload)
        
        self.assertNotIn('token', res.data)
        self.assertEqual(res. status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_blank_password(self): 
        """Test posting a blank password returns an error."""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client. post (TOKEN_URL, payload)
        
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests (TestCase):
    """Test API requests that require authentication."""
    
    def setUp(self):
        self.user = create_user(
            email='test@example.com', 
            password='testpass123', 
            name='Test Name',
        )
        
        self.client = APIClient ()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        # retrieve the details of the current authenticated user
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_0K)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })
    
    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post (ME_URL, {})
        
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'name': 'Updated name', 'password': 'newpassword123'}
        res = self.client.patch(ME_URL, payload)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload ['name'])
        self.assertTrue(self.user.check_password(payload['password'])) 
        self.assertEqual(res.status_code, status.HTTP_200_0K)

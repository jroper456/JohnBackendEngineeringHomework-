from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from snippets.models import APIAction

class CreateUserListTests(TestCase):
    def setUp(self):
        # Set up a test user with staff status for authentication
        self.user = User.objects.create_user(username='testuser', password='password', is_staff=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_user(self):
        """
        Ensure we can create a new user object.
        """
        url = reverse('user-create')
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            'is_staff': False,  # Ensure is_staff is set correctly
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # Adjust the count based on your initial users
        self.assertEqual(User.objects.last().username, 'newuser')

    def test_api_action_logging(self):
        """
        Ensure API actions are logged correctly when creating a user.
        """
        initial_actions_count = APIAction.objects.count()
        
        url = reverse('user-create')
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            'is_staff': False,  # Ensure is_staff is set correctly
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(APIAction.objects.count(), initial_actions_count + 1)

        # Verify the last logged action
        last_action = APIAction.objects.last()
        self.assertEqual(last_action.user, self.user)
        self.assertEqual(last_action.model_name, 'User')
        self.assertEqual(last_action.model_id, User.objects.last().id)
        self.assertEqual(last_action.action, 'create')

class NonStaffUserTests(TestCase):
    def setUp(self):
        # Create a non-staff user for testing
        self.user = User.objects.create_user(username='JohnTest10', password='whatishere', is_staff=False)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_user_permission(self):
        """
        Ensure a non-staff user cannot create a new user.
        """
        url = reverse('user-create')
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            'is_staff': False,  # Ensure is_staff is set correctly
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_api_action_permission(self):
        """
        Ensure a non-staff user cannot view API actions.
        """
        url = reverse('api-action-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


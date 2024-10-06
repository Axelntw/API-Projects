from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Task

class APITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass123'}, format='json')
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_create_task(self):
        url = '/tasks/'
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'due_date': '2023-12-31',
            'priority': 'Medium',
            'status': 'Pending'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'New Task')

    def test_get_tasks(self):
        Task.objects.create(title='Test Task', description='Test Description', user=self.user, due_date='2023-12-31', priority='Medium', status='Pending')
        url = '/tasks/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Task')

    def test_update_task(self):
        task = Task.objects.create(title='Test Task', description='Test Description', user=self.user, due_date='2023-12-31', priority='medium', status='pending')
        url = f'/tasks/{task.id}/'
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'due_date': '2024-01-01',
            'priority': 'high',
            'status': 'pending'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Task')

    def test_delete_task(self):
        task = Task.objects.create(title='Test Task', description='Test Description', user=self.user, due_date='2023-12-31', priority='medium', status='pending')
        url = f'/tasks/{task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_mark_task_complete(self):
        task = Task.objects.create(title='Test Task', description='Test Description', user=self.user, due_date='2023-12-31', priority='medium', status='pending')
        url = f'/tasks/{task.id}/complete/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.completed_at)
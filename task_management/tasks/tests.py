from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Task, Category

class TaskManagementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Work', user=self.user)
        self.task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='Test Description',
            due_date='2023-12-31',
            priority='Medium',
            status='Pending',
            category=self.category
        )

    def test_create_category(self):
        url = reverse('category-list')
        data = {'name': 'Personal'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task(self):
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'Task Description',
            'due_date': '2023-12-31',
            'priority': 'Medium',
            'status': 'Pending',
            'category': self.category.id
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_read_tasks(self):
        url = reverse('task-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_task(self):
        url = reverse('task-detail', args=[self.task.id])
        data = {
            'title': 'Updated Task Title',
            'description': 'Updated Task Description',
            'due_date': '2023-12-31',
            'priority': 'High',
            'status': 'Pending',
            'category': self.category.id
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_task(self):
        url = reverse('task-detail', args=[self.task.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_mark_task_complete(self):
        url = reverse('task-mark-complete', args=[self.task.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_task_incomplete(self):
        url = reverse('task-mark-incomplete', args=[self.task.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
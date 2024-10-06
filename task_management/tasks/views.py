from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task, Category, TaskHistory, Collaborator
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import TaskSerializer, UserSerializer, CategorySerializer, TaskHistorySerializer, CollaboratorSerializer
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from datetime import timedelta, date

class IsOwner(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		return obj.user == request.user

class TaskViewSet(viewsets.ModelViewSet):
	queryset = Task.objects.all()  # Add this line
	serializer_class = TaskSerializer
	permission_classes = [permissions.IsAuthenticated, IsOwner]
	filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
	filterset_fields = ['status', 'priority', 'due_date']
	ordering_fields = ['due_date', 'priority']

	def get_queryset(self):
		return Task.objects.filter(user=self.request.user)

	def perform_create(self, serializer):
		task = serializer.save(user=self.request.user)
		if task.is_recurring:
			if not task.due_date:
				task.due_date = date.today()
			self.create_recurring_task(task)

	def create_recurring_task(self, task):
		if task.recurrence_interval == 'daily':
			next_due_date = task.due_date + timedelta(days=1)
		elif task.recurrence_interval == 'weekly':
			next_due_date = task.due_date + timedelta(weeks=1)
		else:
			return  # Unsupported interval

		Task.objects.create(
            user=task.user,
            title=task.title,
            description=task.description,
            due_date=next_due_date,
            priority=task.priority,
            status='Pending',
            is_recurring=task.is_recurring,
            recurrence_interval=task.recurrence_interval,
            category=task.category
        )
	def perform_update(self, serializer):
		task = serializer.save()
		self.log_task_history(task, "Task updated")

	def perform_destroy(self, instance):
		self.log_task_history(instance, "Task deleted")
		instance.delete()

	def update(self, request, *args, **kwargs):
		task = self.get_object()
		if task.status == 'Completed' and task.is_recurring:
			self.create_recurring_task(task)
		return super().update(request, *args, **kwargs)

	@action(detail=True, methods=['post'], url_path='mark_complete')
	def mark_complete(self, request, pk=None):
		task = self.get_object()
		task.status = 'Completed'
		task.save()
		self.log_task_history(task, "Task marked as complete")
		if task.is_recurring:
			self.create_recurring_task(task)
		return Response({'status': 'Task marked as complete'})

	@action(detail=True, methods=['post'], url_path='mark_incomplete')
	def mark_incomplete(self, request, pk=None):
		task = self.get_object()
		task.status = 'Pending'
		task.save()
		self.log_task_history(task, "Task marked as incomplete")
		return Response({'status': 'Task marked as incomplete'})
	
	def log_task_history(self, task, description):
		TaskHistory.objects.create(task=task, change_description=description)

	def destroy(self, request, *args, **kwargs):
		task = self.get_object()
		self.log_task_history(task, "Task deleted")
		task.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
	
	
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [permissions.AllowAny]
	permission_classes = [permissions.AllowAny]

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskHistoryViewSet(viewsets.ModelViewSet):
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskHistory.objects.filter(task__user=self.request.user)
	
class CollaboratorViewSet(viewsets.ModelViewSet):
    serializer_class = CollaboratorSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Collaborator.objects.all()

    def get_queryset(self):
        return Collaborator.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
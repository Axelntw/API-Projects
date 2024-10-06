from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

class IsOwner(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		return obj.user == request.user

class TaskViewSet(viewsets.ModelViewSet):
	queryset = Task.objects.all()  # Add this line
	serializer_class = TaskSerializer
	permission_classes = [permissions.IsAuthenticated, IsOwner]

	def get_queryset(self):
		return Task.objects.filter(user=self.request.user)

	def perform_create(self, serializer):
		try:
			serializer.save(user=self.request.user)
		except ValidationError as e:
			raise ValidationError({'error': str(e)})
		
	def update(self, request, *args, **kwargs):
		task = self.get_object()
		if task.status == 'Completed':
			return Response({'error': 'Cannot edit a completed task.'}, status=status.HTTP_400_BAD_REQUEST)
		return super().update(request, *args, **kwargs)

	@action(detail=True, methods=['post'])
	def mark_complete(self, request, pk=None):
		task = self.get_object()
		task.status = 'Completed'
		task.save()
		return Response({'status': 'Task marked as complete'})

	@action(detail=True, methods=['post'])
	def mark_incomplete(self, request, pk=None):
		task = self.get_object()
		task.status = 'Pending'
		task.save()
		return Response({'status': 'Task marked as incomplete'})
	
	def destroy(self, request, *args, **kwargs):
		task = self.get_object()
		task.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
	
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [permissions.AllowAny]
	permission_classes = [permissions.AllowAny]

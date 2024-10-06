from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Category(models.Model):
	name = models.CharField(max_length=255)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

class Task(models.Model):
	PRIORITY_CHOICES = [
		('Low', 'Low'),
		('Medium', 'Medium'),
		('High', 'High'),
	]

	STATUS_CHOICES = [
		('Pending', 'Pending'),
		('Completed', 'Completed'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=255)
	description = models.TextField()
	due_date = models.DateField(null=True, blank=True)
	priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
	completed_at = models.DateTimeField(null=True, blank=True)
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
	is_recurring = models.BooleanField(default=False)
	recurrence_interval = models.CharField(max_length=10, choices=[('daily', 'Daily'), ('weekly', 'Weekly')], null=True, blank=True)

	
	def save(self, *args, **kwargs):
		if self.status == 'Completed' and not self.completed_at:
			self.completed_at = timezone.now()
		elif self.status == 'Pending':
			self.completed_at = None
		super().save(*args, **kwargs)

	def clean(self):
		if self.due_date < timezone.now().date():
			raise ValidationError('Due date must be in the future.')
		

class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    change_date = models.DateTimeField(auto_now_add=True)
    change_description = models.TextField()

    def __str__(self):
        return f"History for {self.task.title} on {self.change_date}"

class Collaborator(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return f'{self.user.username} on {self.task.title}'
	
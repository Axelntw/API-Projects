from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

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
	due_date = models.DateField()
	priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
	completed_at = models.DateTimeField(null=True, blank=True)

    
	def save(self, *args, **kwargs):
		if self.status == 'Completed' and not self.completed_at:
			self.completed_at = timezone.now()
		elif self.status == 'Pending':
			self.completed_at = None
		super().save(*args, **kwargs)

	def clean(self):
		if self.due_date < timezone.now().date():
			raise ValidationError('Due date must be in the future.')
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = (
        ('developer', 'Developer'),
        ('shop_owner', 'Shop Owner'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)  # Matches form now
    github = models.URLField(blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Job(models.Model):
    CATEGORY_CHOICES = (
        ('Website', 'Website'),
        ('App', 'App'),
        ('Tutoring', 'Tutoring'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100,choices=CATEGORY_CHOICES)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
   
class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    developer = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('successful', 'Successful'),
        ('rejected', 'Rejected'),
    ], default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)


class SavedJob(models.Model):
    developer = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('developer', 'job')

    def __str__(self):
        return f"{self.developer.username} saved {self.job.title}"
# models.py

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    room_name = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:20]}"
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)



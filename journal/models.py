from django.utils import timezone
from django.db import models

from django.contrib.auth.models import User
from django.urls import reverse


class Thought(models.Model):

    title = models.CharField(max_length=150)
    content = models.CharField(max_length=400)
    date_posted = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def get_absolute_url(self):
        return reverse('thought-detail', args=[str(self.id)])

class Profile(models.Model):

    profile_pic = models.ImageField(null=True, blank=True, default='Default.png', upload_to='media/')

    user = models.ForeignKey(User, max_length=10, on_delete=models.CASCADE, null=True)



class Comment(models.Model):
    thought = models.ForeignKey(Thought, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)


#models.py 내용 
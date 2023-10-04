from django.db import models

# Create your models here.
from django.db import models

class UploadedClip(models.Model):
    clip = models.FileField(upload_to='clips/')



class SecondaryClip(models.Model):
    name = models.CharField(max_length=100, default='clip')
    clip = models.FileField(upload_to='secondary_clips/')


class VideoClip(models.Model):
    title = models.CharField(max_length=200)
    clip_file = models.FileField(upload_to='clips/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
from django.contrib import admin
from .models import UploadedClip, SecondaryClip

# Register your models here.

admin.site.register(UploadedClip)
admin.site.register(SecondaryClip)

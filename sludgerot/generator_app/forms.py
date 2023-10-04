from django import forms
from .models import UploadedClip, SecondaryClip

class UploadClipForm(forms.ModelForm):
    class Meta:
        model = UploadedClip
        fields = ['clip']

    def clean_clip(self):
        clip = self.cleaned_data.get("clip")
        if clip:
            if not clip.content_type.startswith('video/'):
                raise forms.ValidationError("File type is not a video.")
        return clip

class SelectSecondaryClipForm(forms.Form):
    CHOICES = [
        ('upload', 'Upload Your Own Clip'),
        ('select', 'Select From Available Clips'),
    ]
    option = forms.ChoiceField(choices=CHOICES)
    secondary_clip = forms.ModelChoiceField(queryset=SecondaryClip.objects.all())

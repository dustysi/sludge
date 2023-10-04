from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import UploadedClip, SecondaryClip
from .forms import UploadClipForm, SelectSecondaryClipForm
from moviepy.editor import VideoFileClip, clips_array
import logging

logger = logging.getLogger(__name__)

def home(request):
    if request.method == 'POST':
        if 'clip' in request.FILES:  # Assuming 'clip' is the name of the file field in your form
            upload_form = UploadClipForm(request.POST, request.FILES)
            if upload_form.is_valid():
                primary_clip = upload_form.save()
                request.session['primary_clip_id'] = primary_clip.id
                logger.info(f"Saved primary_clip_id in session: {primary_clip.id}")
                return JsonResponse({'status': 'success', 'form': 'upload_form'})

        else:
            select_form = SelectSecondaryClipForm(request.POST)
            if select_form.is_valid():
                selected_clip_id = select_form.cleaned_data.get("secondary_clip", None).id
                logger.info(f"Debug: selected_clip_id: {selected_clip_id}")
                request.session['secondary_clip_id'] = selected_clip_id
                return JsonResponse({'status': 'success', 'form': 'select_form'})

        return JsonResponse({'status': 'failure', 'message': 'Invalid form'})

    upload_form = UploadClipForm()
    select_form = SelectSecondaryClipForm()
    secondary_clips = SecondaryClip.objects.all()

    return render(request, 'generator_app/upload_clip.html', {
        'upload_form': upload_form,
        'select_form': select_form,
        'secondary_clips': secondary_clips,
    })

# ... your `generate_video` function remains the same



def generate_video(request):
    try:
        print("Session Data:", request.session.items())  # Debug print

        primary_clip_id = request.session.get('primary_clip_id')
        secondary_clip_id = request.session.get('secondary_clip_id')

        if not primary_clip_id or not secondary_clip_id:
            return JsonResponse({'status': 'failure', 'message': 'Missing clips'})

        primary_clip = UploadedClip.objects.get(id=primary_clip_id)
        secondary_clip = SecondaryClip.objects.get(id=secondary_clip_id)

        primary_clip = VideoFileClip(primary_clip.clip.path).resize(width=1080)
        secondary_clip = VideoFileClip(secondary_clip.clip.path).resize(width=1080).volume(0)

        final_video = clips_array([[primary_clip], [secondary_clip]], method='vstack')
        output_path = "media/generated_clips/final.mp4"
        final_video.write_videofile(output_path, codec="libx264", size=(1080, 1920))

        return JsonResponse({'status': 'success', 'download_url': output_path})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'failure', 'message': 'Clip does not exist'})
    except Exception as e:
        return JsonResponse({'status': 'failure', 'message': f'An error occurred: {str(e)}'})

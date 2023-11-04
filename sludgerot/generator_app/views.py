import logging

from django.http import JsonResponse
from django.shortcuts import render
from moviepy.editor import VideoFileClip, clips_array

from sludgerot.settings import MEDIA_ROOT
from .forms import UploadClipForm, SelectSecondaryClipForm
from .models import UploadedClip, SecondaryClip

logger = logging.getLogger(__name__)


def home(request):
    if request.method == 'POST':
        try:
            sec = request.POST.get('secondary_clip')
            if sec is None:
                return JsonResponse({'status': 'failure', 'message': 'Invalid form'})
            sec = int(sec)
            if 'clip' in request.FILES:  # Assuming 'clip' is the name of the file field in your form
                upload_form = UploadClipForm(request.POST, request.FILES)
                if upload_form.is_valid():
                    primary_clip = upload_form.save()
                    request.session['primary_clip_id'] = primary_clip.id
                    request.session['secondary_clip_id'] = sec
                    logger.info(f"Saved primary_clip_id in session: {primary_clip.id}")
                    out_path = generate_video(request)
                    if out_path['status'] == 'success':
                        return JsonResponse({'status': 'success', 'url': out_path['url']})
                    else:
                        return JsonResponse(out_path)
            return JsonResponse({'status': 'failure', 'message': 'Invalid form'})

        except Exception as e:
            return {'status': 'failure', 'message': str(e)}

    upload_form = UploadClipForm()
    select_form = SelectSecondaryClipForm()
    secondary_clips = SecondaryClip.objects.all()

    return render(request, 'generator_app/upload_clip.html', {
        'upload_form': upload_form,
        'select_form': select_form,
        'secondary_clips': secondary_clips,
    })


def generate_video(request):
    try:
        print("Session Data:", request.session.items())  # Debug print

        primary_clip_id = request.session.get('primary_clip_id')
        secondary_clip_id = request.session.get('secondary_clip_id')

        primary_clip = UploadedClip.objects.get(id=primary_clip_id)
        secondary_clip = SecondaryClip.objects.get(id=secondary_clip_id)

        primary_clip = VideoFileClip(primary_clip.clip.path)
        secondary_clip = VideoFileClip(secondary_clip.clip.path)

        # Determine the shorter of the two video durations
        min_duration = min(primary_clip.duration, secondary_clip.duration)

        # Trim both videos to the shorter duration
        primary_clip = primary_clip.subclip(0, min_duration)
        secondary_clip = secondary_clip.subclip(0, min_duration)

        # Set the desired width for both videos
        final_width = (500 * 9) // 16

        primary_clip = primary_clip.resize(width=final_width)
        # secondary_clip = secondary_clip.without_audio().resize(width=final_width)
        secondary_clip = secondary_clip.set_audio(None).resize(width=final_width)

        final_video = clips_array([[primary_clip], [secondary_clip]])
        output_path = MEDIA_ROOT + "/generated_clips/final" + str(primary_clip_id) + ".mp4"
        final_video.write_videofile(output_path, fps=30, threads=5, codec="libx264", audio_codec="aac",
                                    ffmpeg_params=["-crf", "23"])
        # final_video.write_videofile(output_path, fps=30, threads=5, codec="libx264", audio_codec="aac", ffmpeg_params=["-crf", "23"], logger=None)

        return {'status': 'success', "url": "/media/generated_clips/final" + str(primary_clip_id) + ".mp4"}

    except Exception as e:
        return {'status': 'failure', 'message': str(e)}

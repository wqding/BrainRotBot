from typing import List
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from pydub import AudioSegment

from utils import concatenate_mp3_files 

def create_video(scene_paths: List[List[str]], audio_paths: List[str], output_video_path, output_audio_path):

    image_clips = []
    for scene_image_paths, audio_path in zip(scene_paths, audio_paths):
        audio_duration = AudioSegment.from_mp3(audio_path).duration_seconds
        duration_per_image = audio_duration/len(scene_image_paths)
        
        for img_path in scene_image_paths:
            clip = ImageClip(img_path).set_duration(duration_per_image)
            image_clips.append(clip)
    
    video = concatenate_videoclips(image_clips, method="compose")

    concatenate_mp3_files(audio_paths, output_audio_path)
    audio = AudioFileClip(output_audio_path)
    video = video.set_audio(audio)
    video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=1)

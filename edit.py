from typing import List
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

from utils import concatenate_mp3_files, remove_file_extension 

def create_video(image_paths: List[List[str]], audio_paths: List[str], output_video_path, output_audio_path):
    image_clips = []
    for path in image_paths:
        path_without_ext = remove_file_extension(path)
        start_ms, end_ms = path_without_ext.split('/')[-1].split('_')
        clip = ImageClip(path).set_duration((int(end_ms)-int(start_ms))/1000)
        image_clips.append(clip)
    
    video = concatenate_videoclips(image_clips, method="compose")

    concatenate_mp3_files(audio_paths, output_audio_path)
    audio = AudioFileClip(output_audio_path)
    video = video.set_audio(audio)
    video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=1)

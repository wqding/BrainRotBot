import json
import os
from typing import List
from pydub import AudioSegment

from models import Scene

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")
    else:
        print(f"Directory '{directory_path}' already exists.")

def concatenate_mp3_files(file_list, output_file):
    combined = AudioSegment.empty()
    
    for file in file_list:
        audio = AudioSegment.from_mp3(file)
        combined += audio
    
    combined.export(output_file, format="mp3")
    print(f"Concatenated MP3 saved as {output_file}")

def load_scenes_from_json(file_path: str) -> List[Scene]:
    with open(file_path, 'r') as file:
        data = json.load(file)
        scenes = [Scene(**item) for item in data]
    return scenes

def write_scenes_to_json(scenes: List[Scene], filepath):
    ensure_directory_exists(os.path.dirname(filepath))
    with open(filepath, "w") as processed_scenes:
        json.dump([scene.model_dump() for scene in scenes], processed_scenes)
        
def remove_file_extension(filename):
    return os.path.splitext(filename)[0]
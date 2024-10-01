import argparse
import json
import os
import sys
import csv
from typing import List
from constants import AUDIO_GENERATED_SCENES_PATH, IMAGE_GENERATED_SCENES_PATH, PREPROCESSED_SCENES_PATH, PARAGRAPH_SEPARATOR, FULL_SCRIPT_PATH, PROMPT_GENERATED_SCENES_PATH
from edit import create_video
from models import Dialog, PromptData, Scene
from text_to_image import TextToImage
from text_to_speech import TextToSpeech
from utils import ensure_directory_exists, load_scenes_from_json, write_scenes_to_json


def populate_scene_lines(scenes: List[Scene], story_with_speaker):
    prev_line_start = 0
    prev_scene_id = 0
    for scene in scenes[1:]:
        scenes[prev_scene_id].lines = story_with_speaker[int(prev_line_start):int(scene.start)]
        prev_line_start = scene.start
        prev_scene_id = scene.id
    
    scenes[-1].lines = story_with_speaker[int(prev_line_start):]

def preprocess():
    script = ""
    scenes = []
    with open(FULL_SCRIPT_PATH, "r", encoding="utf8") as script_file:
        script = " ".join(script_file.readlines())
    
    paragraphs = script.split(PARAGRAPH_SEPARATOR)
    for p_num, paragraph in enumerate(paragraphs):
        ensure_directory_exists(f"output/p{p_num}/texts")
        
        processed_dialog = []
        scene_script = []
        for line_no, speaker_dialog in enumerate(paragraph.split(":|")):
            speaker_dialog = speaker_dialog.strip()
            if not speaker_dialog:
                continue
            
            scene_script.append(speaker_dialog)
            speaker, text = speaker_dialog.split(" | ")
            dialog_path = f'output/p{p_num}/audio/{line_no}_{speaker}'
            processed_dialog.append(Dialog(speaker=speaker, text=text, speech_path=f'{dialog_path}.wav', aligned_path=f'{dialog_path}.tsv'))
            
        script_path = f'output/p{p_num}/texts/script.txt'
        with open(script_path, 'w', encoding='utf8') as scene_script_file:
            scene_script_file.write('\n'.join(scene_script))
        
        scenes.append(Scene(id=p_num, script_path=script_path, dialogs=processed_dialog))

    return scenes

def process_images(scenes: List[Scene]):
    # temp
    with open('finetune_prompter.jsonl', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            data = json.loads(line)
            prompts_data = json.loads(data['messages'][2]['content'])
            prompts = prompts_data['prompts']
            scenes[i].image_prompts = [PromptData(**p) for p in prompts]
    
    # write_scenes_to_json(scenes, PROMPT_GENERATED_SCENES_PATH)
    
    tti = TextToImage()
    for scene in scenes:
        tti.generate_images(scene)
    write_scenes_to_json(scenes, IMAGE_GENERATED_SCENES_PATH)


def process_audio(scenes: List[Scene]):
    tts = TextToSpeech()
    for scene in scenes:
        tts.generate_speech(scene)
        
        aligned_script = []
        for dialog in scene.dialogs:
            for segment in dialog.segments:
                aligned_script.append(f"{dialog.speaker} | {dialog.start_ms + segment.start_ms} | {dialog.start_ms + segment.end_ms} | {segment.text}")
                
        scene.aligned_script = aligned_script
        
    write_scenes_to_json(scenes, AUDIO_GENERATED_SCENES_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an image or audio file based on the step parameter.")
    parser.add_argument('--step', choices=['preprocess', 'image', 'audio', 'combine'], required=True, help="Specify the type of file to process: 'image' or 'audio'.")
    args = parser.parse_args()
    
    if args.step == 'preprocess':
        scenes = preprocess()
        write_scenes_to_json(scenes, PREPROCESSED_SCENES_PATH)
        
    elif args.step == 'audio':
        if not os.path.exists(PREPROCESSED_SCENES_PATH):
            print("Please run the script with the 'preprocess' step first.")
            sys.exit(1)
        
        scenes = load_scenes_from_json(PREPROCESSED_SCENES_PATH)
        process_audio(scenes)

    elif args.step == 'image':
        if not os.path.exists(AUDIO_GENERATED_SCENES_PATH):
            print("Please run the script with the 'audio' step first.")
            sys.exit(1)
            
        scenes = load_scenes_from_json(AUDIO_GENERATED_SCENES_PATH)
        process_images(scenes)
        
    elif args.step == 'combine':
        if not os.path.exists(IMAGE_GENERATED_SCENES_PATH):
            print("Please run the script with the 'image' and 'audio' steps first.")
            sys.exit(1)
        
        scenes = load_scenes_from_json(IMAGE_GENERATED_SCENES_PATH)
        
        img_paths = []
        audio_paths = []
        
        for scene in scenes:
            for prompt in scene.image_prompts:
                img_paths.append(prompt.path) 
            for dialog in scene.dialogs:
                audio_paths.append(dialog.speech_path)
                
        create_video(
            image_paths=img_paths,
            audio_paths=audio_paths,
            output_audio_path="final_audio.mp3",
            output_video_path="final.mp4"
        )
    else:
        print("Invalid step. Please choose 'image' or 'audio'.")
        sys.exit(1)
        
    
    
    
    
    

    

import logging

from constants import OUTPUT_DIR
from models import Scene
from utils import ensure_directory_exists
from forced_alignment import ForcedAligner
from pydub import AudioSegment

SPEAKER_TO_VOICE = {
    "B": "Abrahan Mack",
    "A": "Gracie Wise",
}

class TextToSpeech:
    def __init__(self) -> None:
        # import torch
        # from TTS.api import TTS
        # # Get device
        # device = "cuda" if torch.cuda.is_available() else "cpu"
        # print(f"Using device: {device}")
        
        # self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        self.aligner = ForcedAligner()
        

    def generate(self, voice, text, output_path):
        print(f"GENERATING: {voice} | {output_path} | {text}\n\n")
        try:
            self.tts.tts_to_file(text=text, speaker=voice, language="en", file_path=output_path)
            # get wav file duration
            audio = AudioSegment.from_wav(output_path)
            return len(audio)
        except Exception as e:
            logging.exception(e)


    def generate_speech(self, scene: Scene):
        prev_dialog_end_ms = 0
        ensure_directory_exists(f'{OUTPUT_DIR}/p{scene.id}/audio')
        for dialog in scene.dialogs:
            duration_ms = self.generate(voice=SPEAKER_TO_VOICE[dialog.voice], text=dialog.text, output_path=dialog.speech_path)
            
            segments = self.aligner.align(audio_path=dialog.speech_path, text=dialog.text)
            
            dialog.segments = segments
            dialog.start_ms = prev_dialog_end_ms
            dialog.end_ms = dialog.start_ms + duration_ms
            
            prev_dialog_end_ms = dialog.end_ms

        
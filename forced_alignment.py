import stable_whisper

from models import AlignmentSegment

class ForcedAligner:
  def __init__(self):
    self.model = stable_whisper.load_model('base')

  def align(self, audio_path: str, text: str):
    result = self.model.align(audio_path, text, language='en')
    
    segments = []
    for segment in result.segments:
      segments.append(AlignmentSegment(start_ms=int(segment.start*1000), end_ms=int(segment.end*1000), text=segment.text))
      
    return segments
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Shot(str, Enum):
    CLOSE_UP = "close up shot"
    MEDIUM = "medium shot"
    FULL_BODY = "full body shot"

class Angle(str, Enum):
    FRONT = "front view"
    SIDE = "side view"
    BACK = "back view"
    WIDE_ANGEL = "wide angle view"
    TOP = "top view"

class AlignmentSegment(BaseModel):
    start_ms: int
    end_ms: int
    text: str
    
class Dialog(BaseModel):
    speaker: str
    text: str
    speech_path: str
    segments: Optional[List[AlignmentSegment]] = []
    start_ms: Optional[int] = 0
    end_ms: Optional[int] = 0
    
class PromptData(BaseModel):
    start_ms: int
    end_ms: int
    prompt: str
    path: Optional[str] = ''

class Scene(BaseModel):
    id: int
    script_path: str
    aligned_path: Optional[str] = None
    aligned_script: Optional[List[str]] = []
    dialogs: List[Dialog] = []
    image_prompts: Optional[List[PromptData]] = []
    speech_path: Optional[str] = None
    start_ms: Optional[int] = 0
    end_ms: Optional[int] = 0
    # image_file_paths: Optional[List[str]] = []

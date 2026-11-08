"""
Scene and script element data models.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class TimedElement(BaseModel):
    """Represents an individual timed unit in a screenplay (dialogue, action, camera shot)."""
    element_type: str = Field(..., description="Element type: DIALOGUE, ACTION, CAMERA, SOUND FX, etc.")
    speaker: Optional[str] = Field(None, description="Character name if dialogue, else None")
    emotion: Optional[str] = Field(None, description="Parenthetical emotion or delivery direction")
    text: str = Field(..., description="Full text or action description")
    start_str: str = Field(..., description="Original start timestamp, e.g. '00:11.30'")
    end_str: str = Field(..., description="Original end timestamp, e.g. '00:13.10'")
    start_seconds: float = Field(..., ge=0.0, description="Start timestamp in seconds")
    end_seconds: float = Field(..., ge=0.0, description="End timestamp in seconds")

    @property
    def duration_seconds(self) -> float:
        return max(0.0, self.end_seconds - self.start_seconds)


class Scene(BaseModel):
    """Represents a scene within an episode."""
    scene_id: str = Field(..., description="Scene identifier, e.g. 'EP01_SC01'")
    episode_id: str = Field(..., description="Parent episode identifier, e.g. 'EP01'")
    scene_number: int = Field(..., ge=1, description="Sequential scene number within episode")
    heading: str = Field(..., description="Scene slugline / heading")
    original_timestamp: str = Field(..., description="Original timestamp range string")
    start_seconds: float = Field(..., ge=0.0, description="Scene start in seconds")
    end_seconds: float = Field(..., ge=0.0, description="Scene end in seconds")
    characters: List[str] = Field(default_factory=list, description="Characters appearing in this scene")
    elements: List[TimedElement] = Field(default_factory=list, description="All timed elements in scene")

    @property
    def duration_seconds(self) -> float:
        return max(0.0, self.end_seconds - self.start_seconds)

    @property
    def dialogues(self) -> List[TimedElement]:
        return [el for el in self.elements if el.element_type == "DIALOGUE"]

    @property
    def actions(self) -> List[TimedElement]:
        return [el for el in self.elements if el.element_type == "ACTION"]

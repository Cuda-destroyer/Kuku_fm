"""
Episode data model and associated narrative metadata.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from models.scene import Scene


class CharacterProfile(BaseModel):
    """Character extracted from episode analysis."""
    name: str = Field(..., description="Character name")
    role: str = Field("supporting", description="Role in episode: protagonist, antagonist, supporting")
    description: str = Field("", description="Character description / traits")
    relationships: Dict[str, str] = Field(default_factory=dict, description="Key relationships to other characters")


class StoryEvent(BaseModel):
    """Key dramatic event in an episode."""
    event_id: str = Field(..., description="Unique event identifier")
    episode_id: str = Field(..., description="Episode identifier")
    timestamp_str: str = Field(..., description="Timestamp of the event")
    start_seconds: float = Field(0.0, ge=0.0)
    end_seconds: float = Field(0.0, ge=0.0)
    description: str = Field(..., description="Description of the event")
    event_type: str = Field("conflict", description="Type: conflict, betrayal, revelation, climax, resolution")
    intensity_score: float = Field(50.0, ge=0.0, le=100.0, description="Dramatic intensity 0-100")
    characters_involved: List[str] = Field(default_factory=list)


class Episode(BaseModel):
    """Full episode model with parsed script elements and AI analysis."""
    episode_id: str = Field(..., description="Normalized episode identifier, e.g. 'EP01'")
    filename: str = Field(..., description="Original filename")
    episode_number: Optional[int] = Field(None, ge=1, description="Episode integer number")
    logline: Optional[str] = Field(None, description="Episode logline")
    continuity_notes: Optional[str] = Field(None, description="Continuity notes from screenplay header")
    scenes: List[Scene] = Field(default_factory=list, description="All parsed scenes")
    characters: List[str] = Field(default_factory=list, description="All character names detected")
    character_profiles: List[CharacterProfile] = Field(default_factory=list, description="Extracted character profiles")
    events: List[StoryEvent] = Field(default_factory=list, description="Major narrative events")
    total_duration_seconds: float = Field(0.0, ge=0.0, description="Total runtime of episode in seconds")
    processing_status: str = Field("PARSED", description="Status: PARSED, ANALYZED, FAILED")
    warnings: List[str] = Field(default_factory=list, description="Parser and analysis warnings")

    @property
    def total_dialogue_count(self) -> int:
        return sum(len(sc.dialogues) for sc in self.scenes)

    @property
    def total_action_count(self) -> int:
        return sum(len(sc.actions) for sc in self.scenes)

    @property
    def scene_count(self) -> int:
        return len(self.scenes)

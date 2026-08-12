from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Identifier = Annotated[str, Field(min_length=1)]
Vector3 = tuple[float, float, float]


class StrictSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class EvidenceInput(StrictSchema):
    id: Identifier
    claim: str
    source: str
    confidence: float = Field(ge=0, le=100)
    entities: list[str] = Field(default_factory=list)
    location: Optional[str] = None
    datetime: Optional[str] = None


class TimelineEventInput(StrictSchema):
    id: Identifier
    sequence: int
    event: str
    timestamp: Optional[str] = None
    evidence_ids: list[Identifier]


class TheoryInput(StrictSchema):
    id: Identifier
    title: str
    confidence: float = Field(ge=0, le=100)
    narrative: str
    timeline_event_ids: list[Identifier]
    supporting_evidence_ids: list[Identifier]
    contradicting_evidence_ids: list[Identifier] = Field(default_factory=list)


class ReconstructionContext(StrictSchema):
    investigation_id: Identifier
    evidence: list[EvidenceInput]
    timeline: list[TimelineEventInput]
    selected_theory: TheoryInput


class Environment(StrictSchema):
    preset: Literal[
        "urban_street",
        "residential_street",
        "intersection",
        "building_exterior",
        "office_room",
        "parking_area",
        "corridor",
    ]
    time_of_day: Literal["day", "dusk", "night"]
    weather: Optional[str] = None


class TransformKeyframe(StrictSchema):
    time: float = Field(ge=0)
    position: Vector3
    rotation: Optional[Vector3] = None

    @field_validator("position", "rotation")
    @classmethod
    def validate_world_coordinates(cls, value: Optional[Vector3]) -> Optional[Vector3]:
        if value is None:
            return value
        if any(axis < -50 or axis > 50 for axis in value):
            raise ValueError("world coordinates must be between -50 and 50")
        return value


class ActorAction(StrictSchema):
    type: Literal["idle", "walk", "run", "turn", "interact", "fall", "sit", "stand"]
    start: float = Field(ge=0)
    end: Optional[float] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_end_after_start(self) -> "ActorAction":
        if self.end is not None and self.end < self.start:
            raise ValueError("action end must be greater than or equal to start")
        return self


class Actor(StrictSchema):
    id: Identifier
    label: str
    role: str
    model_key: str
    spawn: Vector3
    motion_track: list[TransformKeyframe]
    actions: list[ActorAction]

    @field_validator("spawn")
    @classmethod
    def validate_spawn(cls, value: Vector3) -> Vector3:
        if any(axis < -50 or axis > 50 for axis in value):
            raise ValueError("world coordinates must be between -50 and 50")
        return value

    @field_validator("motion_track")
    @classmethod
    def validate_ordered_motion_track(cls, value: list[TransformKeyframe]) -> list[TransformKeyframe]:
        if any(current.time > nxt.time for current, nxt in zip(value, value[1:])):
            raise ValueError("motion_track keyframes must be ordered by time")
        return value


class VehicleAction(StrictSchema):
    type: Literal["idle", "drive", "stop"]
    start: float = Field(ge=0)
    end: Optional[float] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_end_after_start(self) -> "VehicleAction":
        if self.end is not None and self.end < self.start:
            raise ValueError("action end must be greater than or equal to start")
        return self


class Vehicle(StrictSchema):
    id: Identifier
    label: str
    model_key: str
    spawn: Vector3
    motion_track: list[TransformKeyframe]
    actions: list[VehicleAction]

    @field_validator("spawn")
    @classmethod
    def validate_spawn(cls, value: Vector3) -> Vector3:
        if any(axis < -50 or axis > 50 for axis in value):
            raise ValueError("world coordinates must be between -50 and 50")
        return value

    @field_validator("motion_track")
    @classmethod
    def validate_ordered_motion_track(cls, value: list[TransformKeyframe]) -> list[TransformKeyframe]:
        if any(current.time > nxt.time for current, nxt in zip(value, value[1:])):
            raise ValueError("motion_track keyframes must be ordered by time")
        return value


class SimulationEvent(StrictSchema):
    id: Identifier
    time: float = Field(ge=0)
    duration: Optional[float] = Field(default=None, ge=0)
    type: str
    label: str
    certainty: Literal["supported", "inferred"]
    evidence_ids: list[Identifier]
    timeline_event_ids: list[Identifier]


class CameraShot(StrictSchema):
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    type: Literal["establishing", "follow", "tracking", "wide", "overhead", "static"]
    target_id: Optional[str] = None
    position: Optional[Vector3] = None
    offset: Optional[Vector3] = None
    look_at: Optional[Vector3] = None

    @field_validator("position", "offset", "look_at")
    @classmethod
    def validate_world_coordinates(cls, value: Optional[Vector3]) -> Optional[Vector3]:
        if value is None:
            return value
        if any(axis < -50 or axis > 50 for axis in value):
            raise ValueError("world coordinates must be between -50 and 50")
        return value

    @model_validator(mode="after")
    def validate_end_after_start(self) -> "CameraShot":
        if self.end <= self.start:
            raise ValueError("camera end must be greater than start")
        return self


class SimulationScreenplay(StrictSchema):
    schema_version: Identifier
    title: str
    duration_seconds: float = Field(gt=0)
    environment: Environment
    actors: list[Actor]
    vehicles: list[Vehicle]
    events: list[SimulationEvent]
    camera_shots: list[CameraShot]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "SimulationScreenplay":
        _ensure_unique_ids("actor", [actor.id for actor in self.actors])
        _ensure_unique_ids("vehicle", [vehicle.id for vehicle in self.vehicles])
        _ensure_unique_ids("event", [event.id for event in self.events])
        return self


def _ensure_unique_ids(label: str, ids: list[str]) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise ValueError(f"{label} IDs must be unique")
        seen.add(item_id)

"""Public contracts for the reconstruction and simulation boundary."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator


NonEmptyString = Annotated[str, Field(min_length=1)]
Confidence = Annotated[float, Field(ge=0, le=1)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceInput(StrictModel):
    id: NonEmptyString
    claim: NonEmptyString
    source: NonEmptyString
    confidence: Confidence
    entities: list[NonEmptyString] = Field(default_factory=list)
    location: str | None = None
    datetime: str | None = None


class TimelineEventInput(StrictModel):
    id: NonEmptyString
    sequence: int
    event: NonEmptyString
    timestamp: str | None = None
    evidence_ids: list[NonEmptyString]


class TheoryInput(StrictModel):
    id: NonEmptyString
    title: NonEmptyString
    confidence: Confidence
    narrative: NonEmptyString
    timeline_event_ids: list[NonEmptyString]
    supporting_evidence_ids: list[NonEmptyString]
    contradicting_evidence_ids: list[NonEmptyString] = Field(default_factory=list)


class ReconstructionContext(StrictModel):
    """Normalized Module 7 input; adapters own upstream model conversion."""

    investigation_id: NonEmptyString
    evidence: list[EvidenceInput]
    timeline: list[TimelineEventInput]
    selected_theory: TheoryInput


class Vector3(RootModel[tuple[float, float, float]]):
    """A public three-dimensional vector serialized as ``[x, y, z]``."""

    @model_validator(mode="after")
    def validate_bounds(self) -> "Vector3":
        if any(value < -50 or value > 50 for value in self.root):
            raise ValueError("Vector3 coordinates must be between -50 and 50")
        return self


class TransformKeyframe(StrictModel):
    time: float = Field(ge=0)
    position: Vector3
    rotation: Vector3 | None = None


class ActorAction(StrictModel):
    type: Literal["idle", "walk", "run", "turn", "interact", "fall", "sit", "stand"]
    start: float = Field(ge=0)
    end: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_time_range(self) -> "ActorAction":
        if self.end is not None and self.end < self.start:
            raise ValueError("action end must be greater than or equal to start")
        return self


class VehicleAction(StrictModel):
    type: Literal["idle", "drive", "stop"]
    start: float = Field(ge=0)
    end: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_time_range(self) -> "VehicleAction":
        if self.end is not None and self.end < self.start:
            raise ValueError("action end must be greater than or equal to start")
        return self


def _motion_track_is_ordered(track: list[TransformKeyframe]) -> bool:
    return all(previous.time <= current.time for previous, current in zip(track, track[1:]))


class Actor(StrictModel):
    id: NonEmptyString
    label: NonEmptyString
    role: NonEmptyString
    model_key: NonEmptyString
    spawn: TransformKeyframe
    motion_track: list[TransformKeyframe]
    actions: list[ActorAction]

    @model_validator(mode="after")
    def validate_motion_track(self) -> "Actor":
        if not _motion_track_is_ordered(self.motion_track):
            raise ValueError("motion_track keyframes must be ordered by time")
        return self


class Vehicle(StrictModel):
    id: NonEmptyString
    label: NonEmptyString
    model_key: NonEmptyString
    spawn: TransformKeyframe
    motion_track: list[TransformKeyframe]
    actions: list[VehicleAction]

    @model_validator(mode="after")
    def validate_motion_track(self) -> "Vehicle":
        if not _motion_track_is_ordered(self.motion_track):
            raise ValueError("motion_track keyframes must be ordered by time")
        return self


class SimulationEvent(StrictModel):
    id: NonEmptyString
    time: float = Field(ge=0)
    duration: float | None = Field(default=None, ge=0)
    type: NonEmptyString
    label: NonEmptyString
    certainty: Literal["supported", "inferred"]
    evidence_ids: list[NonEmptyString]
    timeline_event_ids: list[NonEmptyString]


class CameraShot(StrictModel):
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    type: Literal["establishing", "follow", "tracking", "wide", "overhead", "static"]
    target_id: str | None = None
    position: Vector3 | None = None
    offset: Vector3 | None = None
    look_at: Vector3 | None = None

    @model_validator(mode="after")
    def validate_time_range(self) -> "CameraShot":
        if self.end <= self.start:
            raise ValueError("camera end must be greater than start")
        return self


class Environment(StrictModel):
    preset: Literal[
        "urban_street", "residential_street", "intersection", "building_exterior",
        "office_room", "parking_area", "corridor",
    ]
    time_of_day: Literal["day", "dusk", "night"]
    weather: str | None = None


class SimulationScreenplay(StrictModel):
    schema_version: NonEmptyString
    id: NonEmptyString
    investigation_id: NonEmptyString
    title: NonEmptyString
    duration_seconds: float = Field(gt=0)
    environment: Environment
    actors: list[Actor]
    vehicles: list[Vehicle]
    events: list[SimulationEvent]
    camera_shots: list[CameraShot]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "SimulationScreenplay":
        for label, records in (("actor", self.actors), ("vehicle", self.vehicles), ("event", self.events)):
            ids = [record.id for record in records]
            if len(ids) != len(set(ids)):
                raise ValueError(f"{label} IDs must be unique")
        return self


class GenerateSimulationRequest(StrictModel):
    """Temporary API input until upstream modules expose a persisted context loader."""

    investigation_id: NonEmptyString
    selected_theory_id: NonEmptyString
    context: ReconstructionContext

    @model_validator(mode="after")
    def validate_context_identity(self) -> "GenerateSimulationRequest":
        if self.context.investigation_id != self.investigation_id:
            raise ValueError("investigation_id must match context.investigation_id")
        if self.context.selected_theory.id != self.selected_theory_id:
            raise ValueError("selected_theory_id must match context.selected_theory.id")
        return self

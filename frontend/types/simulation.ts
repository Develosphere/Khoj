export type Vector3 = [number, number, number]

export type EvidenceInput = {
  id: string
  claim: string
  source: string
  confidence: number
  entities: string[]
  location?: string
  datetime?: string
}

export type TimelineEventInput = {
  id: string
  sequence: number
  event: string
  timestamp?: string
  evidence_ids: string[]
}

export type TheoryInput = {
  id: string
  title: string
  confidence: number
  narrative: string
  timeline_event_ids: string[]
  supporting_evidence_ids: string[]
  contradicting_evidence_ids: string[]
}

export type ReconstructionContext = {
  investigation_id: string
  evidence: EvidenceInput[]
  timeline: TimelineEventInput[]
  selected_theory: TheoryInput
}

export type GenerateSimulationRequest = {
  investigation_id: string
  selected_theory_id: string
  context: ReconstructionContext
}

export type EnvironmentPreset =
  | 'urban_street' | 'residential_street' | 'intersection' | 'building_exterior'
  | 'office_room' | 'parking_area' | 'corridor'
export type TimeOfDay = 'day' | 'dusk' | 'night'
export type ActorActionType = 'idle' | 'walk' | 'run' | 'turn' | 'interact' | 'fall' | 'sit' | 'stand'
export type VehicleActionType = 'idle' | 'drive' | 'stop'
export type CameraType = 'establishing' | 'follow' | 'tracking' | 'wide' | 'overhead' | 'static'

export type Environment = { preset: EnvironmentPreset; time_of_day: TimeOfDay; weather?: string }
export type TransformKeyframe = { time: number; position: Vector3; rotation?: Vector3 }
export type ActorAction = { type: ActorActionType; start: number; end?: number }
export type VehicleAction = { type: VehicleActionType; start: number; end?: number }
export type Actor = { id: string; label: string; role: string; model_key: string; spawn: TransformKeyframe; motion_track: TransformKeyframe[]; actions: ActorAction[] }
export type Vehicle = { id: string; label: string; model_key: string; spawn: TransformKeyframe; motion_track: TransformKeyframe[]; actions: VehicleAction[] }
export type SimulationEvent = { id: string; time: number; duration?: number; type: string; label: string; certainty: 'supported' | 'inferred'; evidence_ids: string[]; timeline_event_ids: string[] }
export type CameraShot = { start: number; end: number; type: CameraType; target_id?: string; position?: Vector3; offset?: Vector3; look_at?: Vector3 }

export type SimulationScreenplay = {
  schema_version: string
  id: string
  investigation_id: string
  title: string
  duration_seconds: number
  environment: Environment
  actors: Actor[]
  vehicles: Vehicle[]
  events: SimulationEvent[]
  camera_shots: CameraShot[]
}

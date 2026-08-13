import { apiRequest } from './api'
import type { GenerateSimulationRequest, ReconstructionContext, SimulationScreenplay } from '../types/simulation'

export const DEVELOPMENT_SCREENPLAY_ID = 'development-roadside-robbery'

export type UpstreamEvidence = { id: string; claim: string; source: string; confidence: number }
export type UpstreamTimelineEvent = { id: string; time: string; event: string; confidence: number; supporting_evidence: string[] }
export type UpstreamTheory = { id: string; theory: string; confidence: number; summary: string; supporting_evidence: string[]; timeline_events: string[] }

const matchesReference = (reference: string, id: string, text: string) => reference === id || reference === text

/** The single adapter boundary between teammate investigation records and Module 7. */
export function toReconstructionContext(
  investigationId: string,
  evidence: UpstreamEvidence[],
  timeline: UpstreamTimelineEvent[],
  theory: UpstreamTheory,
): ReconstructionContext {
  const evidenceId = (reference: string) => evidence.find((item) => matchesReference(reference, item.id, item.claim))?.id
  const timelineId = (reference: string) => timeline.find((item) => matchesReference(reference, item.id, item.event) || reference === item.time)?.id
  const unique = (values: Array<string | undefined>) => [...new Set(values.filter((value): value is string => Boolean(value)))]

  return {
    investigation_id: investigationId,
    evidence: evidence.map((item) => ({
      id: item.id,
      claim: item.claim,
      source: item.source,
      confidence: item.confidence,
      entities: [],
    })),
    timeline: timeline.map((item, sequence) => ({
      id: item.id,
      sequence,
      event: item.event,
      timestamp: item.time || undefined,
      evidence_ids: unique(item.supporting_evidence.map(evidenceId)),
    })),
    selected_theory: {
      id: theory.id,
      title: theory.theory,
      confidence: theory.confidence,
      narrative: theory.summary || theory.theory,
      timeline_event_ids: unique(theory.timeline_events.map(timelineId)),
      supporting_evidence_ids: unique(theory.supporting_evidence.map(evidenceId)),
      contradicting_evidence_ids: [],
    },
  }
}

const developmentScreenplay: SimulationScreenplay = {
  schema_version: '1.0', id: DEVELOPMENT_SCREENPLAY_ID,
  investigation_id: 'development-fixture-investigation', title: 'Roadside Motorcycle Robbery', duration_seconds: 38,
  environment: { preset: 'urban_street', time_of_day: 'dusk', weather: 'clear' },
  actors: [
    { id: 'victim', label: 'Victim', role: 'victim', model_key: 'person_adult', spawn: { time: 0, position: [-10, 0, 2] }, motion_track: [{ time: 0, position: [-10, 0, 2] }, { time: 5, position: [-6, 0, 2] }, { time: 16, position: [-5, 0, 2] }, { time: 21, position: [-5, 0, 2] }, { time: 38, position: [-5, 0, 2] }], actions: [{ type: 'walk', start: 0, end: 5 }, { type: 'idle', start: 5, end: 16 }, { type: 'interact', start: 16, end: 21 }, { type: 'fall', start: 21, end: 24 }, { type: 'sit', start: 24, end: 38 }] },
    { id: 'suspect_1', label: 'Suspect 1', role: 'suspect', model_key: 'person_adult', spawn: { time: 0, position: [-18, 0, -1] }, motion_track: [{ time: 0, position: [-18, 0, -1] }, { time: 10, position: [-7, 0, -1] }, { time: 16, position: [-5, 0, 1] }, { time: 27, position: [-7, 0, -1] }, { time: 34, position: [12, 0, -1] }], actions: [{ type: 'sit', start: 0, end: 12 }, { type: 'walk', start: 12, end: 16 }, { type: 'interact', start: 16, end: 21 }, { type: 'walk', start: 23, end: 27 }, { type: 'sit', start: 27, end: 34 }] },
    { id: 'suspect_2', label: 'Suspect 2', role: 'suspect', model_key: 'person_adult', spawn: { time: 0, position: [-19, 0, -1] }, motion_track: [{ time: 0, position: [-19, 0, -1] }, { time: 10, position: [-8, 0, -1] }, { time: 27, position: [-8, 0, -1] }, { time: 34, position: [11, 0, -1] }], actions: [{ type: 'sit', start: 0, end: 34 }] },
  ],
  vehicles: [{ id: 'motorcycle', label: 'Motorcycle', model_key: 'motorcycle_standard', spawn: { time: 0, position: [-18, 0, -1] }, motion_track: [{ time: 0, position: [-18, 0, -1] }, { time: 4, position: [-18, 0, -1] }, { time: 10, position: [-8, 0, -1] }, { time: 12, position: [-7, 0, -1] }, { time: 27, position: [-7, 0, -1] }, { time: 34, position: [12, 0, -1] }, { time: 38, position: [18, 0, -1] }], actions: [{ type: 'idle', start: 0, end: 4 }, { type: 'drive', start: 4, end: 10 }, { type: 'stop', start: 10, end: 27 }, { type: 'drive', start: 27, end: 34 }, { type: 'idle', start: 34, end: 38 }] }],
  events: [
    { id: 'victim-walks', time: 0, duration: 5, type: 'movement', label: 'Victim walks roadside', certainty: 'supported', evidence_ids: ['dev-evidence-01'], timeline_event_ids: ['dev-timeline-01'] },
    { id: 'approach', time: 4, duration: 6, type: 'vehicle_arrival', label: 'Motorcycle approaches', certainty: 'supported', evidence_ids: ['dev-evidence-02'], timeline_event_ids: ['dev-timeline-02'] },
    { id: 'confrontation', time: 16, duration: 5, type: 'confrontation', label: 'Roadside confrontation', certainty: 'inferred', evidence_ids: ['dev-evidence-03'], timeline_event_ids: ['dev-timeline-03'] },
    { id: 'shooting', time: 21, duration: 0.35, type: 'non_graphic_shooting', label: 'Non-graphic shooting event', certainty: 'supported', evidence_ids: ['dev-evidence-04'], timeline_event_ids: ['dev-timeline-04'] },
    { id: 'departure', time: 27, duration: 7, type: 'vehicle_departure', label: 'Motorcycle departs', certainty: 'supported', evidence_ids: ['dev-evidence-05'], timeline_event_ids: ['dev-timeline-05'] },
    { id: 'aftermath', time: 34, duration: 4, type: 'aftermath', label: 'Aftermath at roadside', certainty: 'inferred', evidence_ids: [], timeline_event_ids: [] },
  ],
  camera_shots: [{ start: 0, end: 5, type: 'establishing' }, { start: 5, end: 11, type: 'tracking', target_id: 'motorcycle' }, { start: 11, end: 17, type: 'wide' }, { start: 17, end: 23, type: 'static', position: [2, 4.5, 9], look_at: [-5, 1, 1] }, { start: 23, end: 28, type: 'overhead' }, { start: 28, end: 35, type: 'tracking', target_id: 'motorcycle' }, { start: 35, end: 38, type: 'wide' }],
}

function parseScreenplay(value: unknown): SimulationScreenplay {
  if (!value || typeof value !== 'object') throw new Error('The simulation response is malformed.')
  const screenplay = value as Partial<SimulationScreenplay>
  if (
    typeof screenplay.id !== 'string' || typeof screenplay.investigation_id !== 'string' ||
    typeof screenplay.title !== 'string' || typeof screenplay.duration_seconds !== 'number' ||
    !Number.isFinite(screenplay.duration_seconds) || screenplay.duration_seconds <= 0 ||
    !screenplay.environment || typeof screenplay.environment !== 'object'
  ) throw new Error('The simulation response is missing required screenplay data.')
  return {
    ...screenplay,
    schema_version: screenplay.schema_version || '1.0',
    actors: Array.isArray(screenplay.actors) ? screenplay.actors : [],
    vehicles: Array.isArray(screenplay.vehicles) ? screenplay.vehicles : [],
    events: Array.isArray(screenplay.events) ? screenplay.events : [],
    camera_shots: Array.isArray(screenplay.camera_shots) ? screenplay.camera_shots : [],
  } as SimulationScreenplay
}

export async function getSimulationScreenplay(id: string): Promise<SimulationScreenplay> {
  if (id === DEVELOPMENT_SCREENPLAY_ID) return structuredClone(developmentScreenplay)
  return parseScreenplay(await apiRequest<unknown>(`/api/v1/simulation/${encodeURIComponent(id)}`))
}

export async function generateSimulation(request: GenerateSimulationRequest): Promise<SimulationScreenplay> {
  return parseScreenplay(await apiRequest<unknown>('/api/v1/simulation/generate', {
    method: 'POST',
    body: JSON.stringify(request),
  }))
}

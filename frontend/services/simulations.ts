import type { SimulationScreenplay } from '../types/simulation'

export const DEVELOPMENT_SCREENPLAY_ID = 'development-roadside-robbery'

const developmentScreenplay: SimulationScreenplay = {
  schema_version: '1.0', id: DEVELOPMENT_SCREENPLAY_ID,
  investigation_id: 'development-fixture-investigation', title: 'Roadside Motorcycle Robbery', duration_seconds: 38,
  environment: { preset: 'urban_street', time_of_day: 'dusk', weather: 'clear' },
  actors: [
    { id: 'victim', label: 'Victim', role: 'victim', model_key: 'person_adult', spawn: { time: 0, position: [-10, 0, 2] }, motion_track: [{ time: 0, position: [-10, 0, 2] }, { time: 5, position: [-6, 0, 2] }, { time: 16, position: [-5, 0, 2] }, { time: 21, position: [-5, 0, 2] }, { time: 38, position: [-5, 0, 2] }], actions: [{ type: 'walk', start: 0, end: 5 }, { type: 'idle', start: 5, end: 16 }, { type: 'interact', start: 16, end: 21 }, { type: 'fall', start: 21, end: 24 }] },
    { id: 'suspect_1', label: 'Suspect 1', role: 'suspect', model_key: 'person_adult', spawn: { time: 0, position: [-18, 0, -1] }, motion_track: [{ time: 0, position: [-18, 0, -1] }, { time: 10, position: [-7, 0, -1] }, { time: 16, position: [-5, 0, 1] }, { time: 27, position: [-7, 0, -1] }, { time: 34, position: [12, 0, -1] }], actions: [{ type: 'sit', start: 0, end: 12 }, { type: 'walk', start: 12, end: 16 }, { type: 'interact', start: 16, end: 21 }, { type: 'walk', start: 23, end: 27 }, { type: 'sit', start: 27, end: 34 }] },
    { id: 'suspect_2', label: 'Suspect 2', role: 'suspect', model_key: 'person_adult', spawn: { time: 0, position: [-19, 0, -1] }, motion_track: [{ time: 0, position: [-19, 0, -1] }, { time: 10, position: [-8, 0, -1] }, { time: 27, position: [-8, 0, -1] }, { time: 34, position: [11, 0, -1] }], actions: [{ type: 'sit', start: 0, end: 34 }] },
  ],
  vehicles: [{ id: 'motorcycle', label: 'Motorcycle', model_key: 'motorcycle_standard', spawn: { time: 0, position: [-18, 0, -1] }, motion_track: [{ time: 0, position: [-18, 0, -1] }, { time: 4, position: [-18, 0, -1] }, { time: 10, position: [-8, 0, -1] }, { time: 12, position: [-7, 0, -1] }, { time: 27, position: [-7, 0, -1] }, { time: 34, position: [12, 0, -1] }, { time: 38, position: [18, 0, -1] }], actions: [{ type: 'idle', start: 0, end: 4 }, { type: 'drive', start: 4, end: 10 }, { type: 'stop', start: 10, end: 27 }, { type: 'drive', start: 27, end: 34 }] }],
  events: [
    { id: 'victim-walks', time: 0, duration: 5, type: 'movement', label: 'Victim walks roadside', certainty: 'supported', evidence_ids: ['dev-evidence-01'], timeline_event_ids: ['dev-timeline-01'] },
    { id: 'approach', time: 4, duration: 6, type: 'vehicle_arrival', label: 'Motorcycle approaches', certainty: 'supported', evidence_ids: ['dev-evidence-02'], timeline_event_ids: ['dev-timeline-02'] },
    { id: 'confrontation', time: 16, duration: 5, type: 'confrontation', label: 'Roadside confrontation', certainty: 'inferred', evidence_ids: ['dev-evidence-03'], timeline_event_ids: ['dev-timeline-03'] },
    { id: 'departure', time: 27, duration: 7, type: 'vehicle_departure', label: 'Motorcycle departs', certainty: 'supported', evidence_ids: ['dev-evidence-04'], timeline_event_ids: ['dev-timeline-04'] },
  ],
  camera_shots: [{ start: 0, end: 5, type: 'establishing' }, { start: 5, end: 11, type: 'tracking', target_id: 'motorcycle' }, { start: 11, end: 17, type: 'wide' }, { start: 17, end: 23, type: 'static' }, { start: 23, end: 28, type: 'overhead' }, { start: 28, end: 35, type: 'tracking', target_id: 'motorcycle' }, { start: 35, end: 38, type: 'wide' }],
}

export async function getSimulationScreenplay(id: string): Promise<SimulationScreenplay> {
  if (process.env.NODE_ENV === 'development' && id === DEVELOPMENT_SCREENPLAY_ID) return structuredClone(developmentScreenplay)
  const response = await fetch(`/api/v1/simulation/${encodeURIComponent(id)}`)
  if (!response.ok) throw new Error('Unable to load simulation')
  return response.json() as Promise<SimulationScreenplay>
}

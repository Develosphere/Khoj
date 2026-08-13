import type { CameraShot, SimulationScreenplay, Vector3 } from '../types/simulation'
import { resolveOrientationAtTime, resolveTransformAtTime } from './simulation-runtime'

export type ResolvedCameraShot = { shot: CameraShot | null; index: number }
export type CameraState = { position: Vector3; lookAt: Vector3; shotType: CameraShot['type'] | 'default' }

const DEFAULT_POSITION: Vector3 = [12, 12, 20]
const DEFAULT_LOOK_AT: Vector3 = [-4, 1, 0]
const TRANSITION_SECONDS = 0.65

const clamp = (value: number, minimum: number, maximum: number) => Math.min(maximum, Math.max(minimum, value))
const clampPosition = (value: Vector3): Vector3 => [clamp(value[0], -48, 48), clamp(value[1], 1.8, 42), clamp(value[2], -48, 48)]
const add = (a: Vector3, b: Vector3): Vector3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
const mix = (a: Vector3, b: Vector3, amount: number): Vector3 => [a[0] + (b[0] - a[0]) * amount, a[1] + (b[1] - a[1]) * amount, a[2] + (b[2] - a[2]) * amount]
const smoothstep = (value: number) => value * value * (3 - 2 * value)

export function resolveCameraShot(cameraShots: CameraShot[], currentTime: number): ResolvedCameraShot {
  if (cameraShots.length === 0) return { shot: null, index: -1 }
  const ordered = [...cameraShots].sort((a, b) => a.start - b.start)
  if (currentTime <= ordered[0].start) return { shot: ordered[0], index: 0 }
  const activeIndex = ordered.findIndex((shot) => currentTime >= shot.start && currentTime < shot.end)
  if (activeIndex >= 0) return { shot: ordered[activeIndex], index: activeIndex }
  const previousIndex = ordered.findLastIndex((shot) => shot.start <= currentTime)
  const index = previousIndex >= 0 ? previousIndex : 0
  return { shot: ordered[index], index }
}

function entityPosition(screenplay: SimulationScreenplay, targetId: string | undefined, currentTime: number): Vector3 | null {
  if (!targetId) return null
  const entity = [...screenplay.actors, ...screenplay.vehicles].find((item) => item.id === targetId)
  if (!entity) return null
  return resolveTransformAtTime([entity.spawn, ...entity.motion_track], currentTime).position
}

function entityHeading(screenplay: SimulationScreenplay, targetId: string | undefined, currentTime: number) {
  if (!targetId) return 0
  const entity = [...screenplay.actors, ...screenplay.vehicles].find((item) => item.id === targetId)
  return entity ? resolveOrientationAtTime([entity.spawn, ...entity.motion_track], currentTime)[1] : 0
}

function sceneCentroid(screenplay: SimulationScreenplay, currentTime: number): Vector3 {
  const entities = [...screenplay.actors, ...screenplay.vehicles]
  if (entities.length === 0) return [...DEFAULT_LOOK_AT]
  const sum = entities.reduce<Vector3>((total, entity) => {
    const position = resolveTransformAtTime([entity.spawn, ...entity.motion_track], currentTime).position
    return [total[0] + position[0], total[1] + position[1], total[2] + position[2]]
  }, [0, 0, 0])
  return [sum[0] / entities.length, 1, sum[2] / entities.length]
}

function rotateOffset(offset: Vector3, heading: number): Vector3 {
  const sine = Math.sin(heading)
  const cosine = Math.cos(heading)
  return [offset[0] * cosine + offset[2] * sine, offset[1], -offset[0] * sine + offset[2] * cosine]
}

function semanticOffset(type: CameraShot['type']): Vector3 {
  switch (type) {
    case 'follow': return [0, 4.2, -9]
    case 'tracking': return [7.5, 3.8, -7]
    case 'overhead': return [5, 18, 8]
    case 'wide': return [11, 8, 16]
    case 'static': return [8, 5, 11]
    case 'establishing': return [15, 12, 21]
  }
}

function rawCameraState(screenplay: SimulationScreenplay, shot: CameraShot | null, currentTime: number): CameraState {
  if (!shot) return { position: [...DEFAULT_POSITION], lookAt: [...DEFAULT_LOOK_AT], shotType: 'default' }
  const target = entityPosition(screenplay, shot.target_id, currentTime)
  const lookAt: Vector3 = shot.look_at ? [...shot.look_at] : target ? [target[0], target[1] + 1, target[2]] : sceneCentroid(screenplay, currentTime)
  const heading = entityHeading(screenplay, shot.target_id, currentTime)
  const offset = shot.offset ? [...shot.offset] as Vector3 : semanticOffset(shot.type)
  const anchor = target ?? lookAt
  const position = shot.position ? [...shot.position] as Vector3 : add(anchor, target ? rotateOffset(offset, heading) : offset)
  const safePosition = clampPosition(position)
  const distanceSquared = (safePosition[0] - lookAt[0]) ** 2 + (safePosition[1] - lookAt[1]) ** 2 + (safePosition[2] - lookAt[2]) ** 2
  return { position: distanceSquared < 4 ? add(safePosition, [0, 2, 5] as Vector3) : safePosition, lookAt, shotType: shot.type }
}

export function resolveCameraState(screenplay: SimulationScreenplay, currentTime: number): CameraState {
  const ordered = [...screenplay.camera_shots].sort((a, b) => a.start - b.start)
  const resolved = resolveCameraShot(ordered, currentTime)
  const current = rawCameraState(screenplay, resolved.shot, currentTime)
  if (!resolved.shot || resolved.index <= 0) return current
  const elapsed = currentTime - resolved.shot.start
  if (elapsed >= TRANSITION_SECONDS) return current
  const previous = rawCameraState(screenplay, ordered[resolved.index - 1], currentTime)
  const amount = smoothstep(clamp(elapsed / TRANSITION_SECONDS, 0, 1))
  return { position: mix(previous.position, current.position, amount), lookAt: mix(previous.lookAt, current.lookAt, amount), shotType: current.shotType }
}

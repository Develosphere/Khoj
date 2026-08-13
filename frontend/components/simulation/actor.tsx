'use client'

import { useMemo } from 'react'
import type { Actor } from '../../types/simulation'
import { resolveActionAtTime, resolveOrientationAtTime, resolveTransformAtTime } from '../../lib/simulation-runtime'
import { resolveActorModel } from '../../lib/model-registry'

function Limb({ position, rotation }: { position: [number, number, number]; rotation: [number, number, number] }) {
  return <group position={position} rotation={rotation}><mesh castShadow position={[0, -0.28, 0]}><capsuleGeometry args={[0.09, 0.42, 6, 10]} /><meshStandardMaterial color="#263447" roughness={0.8} /></mesh></group>
}

export default function SimulationActor({ actor, currentTime }: { actor: Actor; currentTime: number }) {
  resolveActorModel(actor.model_key)
  const track = useMemo(() => [actor.spawn, ...actor.motion_track], [actor])
  const transform = useMemo(() => resolveTransformAtTime(track, currentTime), [track, currentTime])
  const orientation = useMemo(() => resolveOrientationAtTime(track, currentTime), [track, currentTime])
  const action = resolveActionAtTime(actor.actions, currentTime)
  const type = action?.type ?? 'idle'
  const phase = currentTime * (type === 'run' ? 10 : 6)
  const gait = type === 'walk' || type === 'run' ? Math.sin(phase) * (type === 'run' ? 0.8 : 0.48) : 0
  const fall = type === 'fall' ? action?.progress ?? 0 : type === 'sit' ? 1 : 0
  const interaction = type === 'interact' ? 0.25 : 0
  const bodyColor = actor.role === 'victim' ? '#90c9df' : '#b8606d'
  const opacity = actor.role === 'suspect' && type === 'interact' ? 0.82 : 1
  return <group position={[transform.position[0], transform.position[1] + 0.06, transform.position[2]]} rotation={[fall * Math.PI / 2, orientation[1], orientation[2]]}>
    <group rotation={[0, interaction, 0]}>
      <mesh castShadow position={[0, 1.68, 0]}><sphereGeometry args={[0.22, 16, 16]} /><meshStandardMaterial color="#d6b29a" roughness={0.8} transparent opacity={opacity} /></mesh>
      <mesh castShadow position={[0, 1.12, 0]}><boxGeometry args={[0.46, 0.76, 0.25]} /><meshStandardMaterial color={bodyColor} roughness={0.82} transparent opacity={opacity} /></mesh>
      <Limb position={[-0.32, 1.4, 0]} rotation={[gait - interaction, 0, 0.12]} /><Limb position={[0.32, 1.4, 0]} rotation={[-gait - interaction, 0, -0.12]} />
      <Limb position={[-0.17, 0.72, 0]} rotation={[-gait, 0, 0]} /><Limb position={[0.17, 0.72, 0]} rotation={[gait, 0, 0]} />
    </group>
  </group>
}

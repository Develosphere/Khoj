'use client'

import { useMemo } from 'react'
import type { Actor } from '../../types/simulation'
import { resolveTransformAtTime } from '../../lib/simulation-runtime'

export default function SimulationActor({ actor, currentTime }: { actor: Actor; currentTime: number }) {
  const transform = useMemo(() => resolveTransformAtTime([actor.spawn, ...actor.motion_track], currentTime), [actor, currentTime])
  const color = actor.role === 'victim' ? '#7dd3fc' : '#fb7185'
  return <group position={transform.position} rotation={transform.rotation} castShadow>
    <mesh castShadow position={[0, 1.45, 0]}><sphereGeometry args={[0.28, 20, 20]} /><meshStandardMaterial color={color} roughness={0.65} /></mesh>
    <mesh castShadow position={[0, 0.85, 0]}><capsuleGeometry args={[0.28, 0.85, 8, 16]} /><meshStandardMaterial color={color} roughness={0.8} /></mesh>
    <mesh castShadow position={[-0.16, 0.25, 0]}><boxGeometry args={[0.18, 0.7, 0.18]} /><meshStandardMaterial color="#1e293b" /></mesh>
    <mesh castShadow position={[0.16, 0.25, 0]}><boxGeometry args={[0.18, 0.7, 0.18]} /><meshStandardMaterial color="#1e293b" /></mesh>
  </group>
}

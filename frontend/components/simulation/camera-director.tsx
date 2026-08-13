'use client'

import { useMemo, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Vector3 } from 'three'
import type { SimulationScreenplay } from '../../types/simulation'
import { resolveCameraState } from '../../lib/camera-runtime'

export default function CameraDirector({ screenplay, currentTime, enabled }: { screenplay: SimulationScreenplay; currentTime: number; enabled: boolean }) {
  const camera = useThree((state) => state.camera)
  const state = useMemo(() => resolveCameraState(screenplay, currentTime), [screenplay, currentTime])
  const position = useRef(new Vector3())
  const target = useRef(new Vector3())
  useFrame(() => {
    if (!enabled) return
    position.current.set(...state.position)
    target.current.set(...state.lookAt)
    camera.position.copy(position.current)
    camera.up.set(0, 1, 0)
    camera.lookAt(target.current)
    camera.updateMatrixWorld()
  })
  return null
}

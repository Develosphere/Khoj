'use client'

import { OrbitControls } from '@react-three/drei/core/OrbitControls'
import type { SimulationScreenplay } from '../../types/simulation'
import { getActiveEvents } from '../../lib/simulation-runtime'
import SimulationActor from './actor'
import EnvironmentScene from './environment'
import SimulationVehicle from './vehicle'
import CameraDirector from './camera-director'

export default function SimulationScene({ screenplay, currentTime, inspectMode }: { screenplay: SimulationScreenplay; currentTime: number; inspectMode: boolean }) {
  const shootingActive = getActiveEvents(screenplay.events, currentTime).some((event) => event.type === 'non_graphic_shooting')
  return <><EnvironmentScene environment={screenplay.environment} />
    <CameraDirector screenplay={screenplay} currentTime={currentTime} enabled={!inspectMode} />
    {shootingActive && <pointLight color="#f8e7ba" intensity={7} distance={8} position={[-5, 2, 1]} />}
    {screenplay.actors.map((actor) => <SimulationActor key={actor.id} actor={actor} currentTime={currentTime} />)}
    {screenplay.vehicles.map((vehicle) => <SimulationVehicle key={vehicle.id} vehicle={vehicle} currentTime={currentTime} />)}
    <OrbitControls makeDefault enabled={inspectMode} target={[-4, 0.8, 0]} maxPolarAngle={Math.PI / 2.1} minDistance={6} maxDistance={38} />
  </>
}

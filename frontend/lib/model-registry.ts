/** Local asset boundary. No remote models are required for reliable rendering. */
const actorModels = new Set(['person_adult'])
const vehicleModels = new Set(['motorcycle_standard'])

export const resolveActorModel = (modelKey: string) => ({ key: modelKey, kind: actorModels.has(modelKey) ? 'procedural_humanoid' : 'procedural_humanoid' })
export const resolveVehicleModel = (modelKey: string) => ({ key: modelKey, kind: vehicleModels.has(modelKey) ? 'procedural_motorcycle' : 'procedural_motorcycle' })

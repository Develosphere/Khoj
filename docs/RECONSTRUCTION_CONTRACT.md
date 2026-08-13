# Reconstruction Contract

`ReconstructionContext` is Module 7's normalized input boundary: investigation ID, evidence, timeline, and one selected theory. Upstream modules are converted at the explicit reconstruction adapter boundary.

`SimulationScreenplay` contains `schema_version`, IDs, title, duration, environment, actors, vehicles, events, and camera shots. Motion tracks describe where an entity is; actions describe what it is doing.

- Environment presets: `urban_street`, `residential_street`, `intersection`, `building_exterior`, `office_room`, `parking_area`, `corridor`
- Actor actions: `idle`, `walk`, `run`, `turn`, `interact`, `fall`, `sit`, `stand`
- Vehicle actions: `idle`, `drive`, `stop`
- Camera types: `establishing`, `follow`, `tracking`, `wide`, `overhead`, `static`
- `supported` events have supplied evidence and timeline provenance; `inferred` represents minimal visual continuity only.

Authenticated API endpoints:

- `POST /api/v1/simulation/generate` accepts investigation ID, selected-theory ID, and a normalized `ReconstructionContext`; it generates, validates, and persists a screenplay.
- `GET /api/v1/simulation/{id}` returns a persisted `SimulationScreenplay` directly.

Module 8 consumes only `GET /simulation/{id} → SimulationScreenplay` deterministically. It does not call Gemini or depend on Evidence, Timeline, or Theory internals.

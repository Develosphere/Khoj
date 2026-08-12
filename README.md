# Khoj - AI Investigation & Reconstruction Platform

## Overview

Khoj is an AI-powered investigation platform that helps users understand complex real-world events by collecting information from multiple sources, extracting evidence, generating timelines, comparing theories, and creating visual reconstructions.

Instead of reading dozens of articles and manually connecting information, users can use Khoj to view a structured investigation generated from available public information.

---

# Problem

When major incidents occur, information becomes fragmented across:

- News websites
- Blogs
- Social media discussions
- Public statements
- Independent reports

Users often struggle to:

- Understand what happened
- Compare conflicting narratives
- Verify evidence
- Build timelines
- Research efficiently

Khoj solves this by organizing information into a single investigation workspace.

---

# Vision

Build an AI-powered investigation platform capable of:

1. Collecting information from multiple sources
2. Extracting evidence
3. Identifying contradictions
4. Generating timelines
5. Creating competing theories
6. Producing visual reconstructions

Khoj does NOT claim to determine absolute truth.

Khoj helps users understand available evidence and competing explanations.

---

# Target Users

## Journalists

- Research investigations faster
- Collect evidence
- Build timelines

## YouTubers

- Documentary research
- Crime analysis videos
- Case breakdowns

## Content Creators

- Current affairs analysis
- Story research

## Students

- Research projects
- Debate preparation

## General Public

- Understanding complex incidents

---

# MVP Goal

A user should be able to:

1. Create an account
2. Login
3. Open a case
4. View AI-generated evidence
5. View AI-generated timeline
6. Compare AI-generated theories
7. Generate reconstruction
8. Watch visual simulation

---

# Tech Stack

## Frontend

### Next.js

Purpose:
- Main application framework
- Routing
- UI rendering

### TypeScript

Purpose:
- Type safety
- Maintainability

### Tailwind CSS

Purpose:
- Styling
- Rapid development

### shadcn/ui

Purpose:
- Modern UI components

### Framer Motion

Purpose:
- Smooth animations
- Page transitions
- Loading states

### React Three Fiber

Purpose:
- 3D rendering

### Three.js

Purpose:
- Simulation engine
- Scene rendering

---

## Backend

### FastAPI

Purpose:
- API layer
- Investigation orchestration
- Business logic

---

## Database & Authentication

### Supabase

Purpose:
- Authentication
- PostgreSQL database
- Data storage

Features:
- Sign Up
- Sign In
- User sessions
- Investigation storage

---

## AI Layer

### Primary Model

Gemini Flash Lite Latest

Purpose:
- Evidence extraction
- Timeline generation
- Theory generation
- Summarization
- Structured JSON outputs

Priority:
- Primary AI provider

---

### Secondary Provider

OpenRouter

Purpose:
- Fallback AI provider
- Reliability backup

Only used when Gemini fails or becomes unavailable.

---

# System Architecture

```text
User
  |
  v
Authentication
  |
  v
Dashboard
  |
  v
Case Selection
  |
  v
Investigation Engine
  |
  +----------------+
  |                |
  v                v
Evidence      Timeline
  |                |
  +--------+-------+
           |
           v
      Theory Engine
           |
           v
 Reconstruction Engine
           |
           v
 Simulation Viewer
```

# Database Schema

## users

```sql
id
email
name
created_at
```

## cases

```sql
id
title
description
status
created_at
```

## investigations

```sql
id
user_id
case_id
summary
created_at
```

## evidence

```sql
id
investigation_id
claim
source
confidence
```

## timelines

```sql
id
investigation_id
timestamp
event
```

## theories

```sql
id
investigation_id
title
confidence
```

## simulations

```sql
id
investigation_id
simulation_json
created_at
```

---

# Product Flow

## Step 1

User signs up or logs in.

---

## Step 2

User enters dashboard.

---

## Step 3

User selects a case.

Example:

```text
Mir Raza Ali Case
```

---

## Step 4

Khoj begins investigation.

Pipeline:

```text
Collect Sources
    ↓
Extract Evidence
    ↓
Generate Timeline
    ↓
Generate Theories
    ↓
Generate Summary
```

---

## Step 5

Dashboard displays:

- Summary
- Evidence
- Timeline
- Theories

---

## Step 6

User clicks:

```text
Generate Reconstruction
```

---

## Step 7

Khoj generates simulation data.

---

## Step 8

Simulation viewer displays reconstruction.

---

# Project Structure

khoj/
│
├── frontend/                         # Next.js Frontend
│
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── signup/
│   │   │
│   │   ├── dashboard/
│   │   │   ├── page.tsx
│   │   │   └── loading.tsx
│   │   │
│   │   ├── investigations/
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   │
│   │   ├── simulation/
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   │
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   ├── components/
│   │
│   │   ├── auth/
│   │   │   ├── login-form.tsx
│   │   │   └── signup-form.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── case-card.tsx
│   │   │   ├── overview-panel.tsx
│   │   │   └── stats-panel.tsx
│   │   │
│   │   ├── investigation/
│   │   │   ├── summary-card.tsx
│   │   │   ├── evidence-board.tsx
│   │   │   ├── evidence-card.tsx
│   │   │   ├── theory-card.tsx
│   │   │   ├── timeline.tsx
│   │   │   └── source-list.tsx
│   │   │
│   │   ├── simulation/
│   │   │   ├── simulation-viewer.tsx
│   │   │   ├── scene.tsx
│   │   │   ├── actor.tsx
│   │   │   ├── vehicle.tsx
│   │   │   ├── controls.tsx
│   │   │   └── timeline-controller.tsx
│   │   │
│   │   └── shared/
│   │       ├── navbar.tsx
│   │       ├── sidebar.tsx
│   │       ├── loader.tsx
│   │       └── button.tsx
│   │
│   ├── services/
│   │   ├── auth.ts
│   │   ├── investigations.ts
│   │   ├── simulations.ts
│   │   └── api.ts
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useInvestigation.ts
│   │   └── useSimulation.ts
│   │
│   ├── types/
│   │   ├── case.ts
│   │   ├── evidence.ts
│   │   ├── theory.ts
│   │   ├── timeline.ts
│   │   └── simulation.ts
│   │
│   └── lib/
│       ├── supabase.ts
│       └── utils.ts
│
│
├── backend/                          # FastAPI Backend
│
│   ├── app/
│   │
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── cases.py
│   │   │   ├── investigations.py
│   │   │   └── simulations.py
│   │   │
│   │   ├── services/
│   │   │
│   │   │   ├── source_collector.py
│   │   │   ├── evidence_engine.py
│   │   │   ├── timeline_engine.py
│   │   │   ├── theory_engine.py
│   │   │   ├── summary_engine.py
│   │   │   ├── reconstruction_engine.py
│   │   │   └── simulation_engine.py
│   │   │
│   │   ├── models/
│   │   │   ├── case.py
│   │   │   ├── evidence.py
│   │   │   ├── theory.py
│   │   │   ├── timeline.py
│   │   │   └── simulation.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── case.py
│   │   │   ├── evidence.py
│   │   │   ├── theory.py
│   │   │   ├── timeline.py
│   │   │   └── simulation.py
│   │   │
│   │   ├── database/
│   │   │   ├── client.py
│   │   │   └── supabase.py
│   │   │
│   │   ├── ai/
│   │   │   ├── gemini.py
│   │   │   ├── openrouter.py
│   │   │   └── prompts/
│   │   │       ├── evidence_prompt.py
│   │   │       ├── timeline_prompt.py
│   │   │       ├── theory_prompt.py
│   │   │       └── summary_prompt.py
│   │   │
│   │   └── main.py
│   │
│   └── requirements.txt
│
│
├── data/
│
│   ├── cases/
│   │   ├── mir_raza_ali.json
│   │   └── sample_case.json
│   │
│   ├── sources/
│   │   ├── source_1.json
│   │   ├── source_2.json
│   │   └── source_3.json
│   │
│   └── simulations/
│       └── generated/
│
│
├── docs/
│
│   ├── PRD.md
│   ├── API_SPEC.md
│   ├── DATABASE_SCHEMA.md
│   └── SYSTEM_FLOW.md
│
│
├── .env.example
├── docker-compose.yml
├── README.md
└── LICENSE

# Development Phases

---

# Phase 1 - Foundation

## Objective

Setup project infrastructure.

## Modules

### Module 1.1 Project Setup

Tasks:

- Create Next.js app
- Create FastAPI backend
- Setup Supabase
- Setup environment variables

Deliverable:

Working project structure.

---

### Module 1.2 Authentication

Features:

- Sign Up
- Login
- Logout
- Protected routes

Deliverable:

Working authentication system.

---

### Module 1.3 Database Setup

Features:

- Create schema
- Create tables
- Connect Supabase

Deliverable:

Working database connection.

---

# Phase 2 - Case Management

## Objective

Manage investigations.

## Modules

### Module 2.1 Dashboard

Features:

- User dashboard
- Investigation listing

Deliverable:

Dashboard UI.

---

### Module 2.2 Case Listing

Features:

- Display available cases
- Case cards

Deliverable:

Case selection screen.

---

### Module 2.3 Case Details

Features:

- Case overview
- Investigation metadata

Deliverable:

Case details page.

---

# Phase 3 - Investigation Engine

## Objective

Generate structured investigation data.

## Modules

### Module 3.1 Source Collection

Input:

Case name

Tasks:

- Gather articles
- Gather reports
- Gather references

Output:

```json
{
  "sources": []
}
```

---

### Module 3.2 Evidence Extraction

Input:

Collected sources

Output:

```json
{
  "claim": "",
  "source": "",
  "confidence": 0
}
```

Purpose:

Extract evidence from sources.

---

### Module 3.3 Timeline Generator

Output:

```json
[
  {
    "time": "",
    "event": ""
  }
]
```

Purpose:

Generate chronological sequence.

---

### Module 3.4 Theory Generator

Output:

```json
[
  {
    "theory": "",
    "confidence": 0
  }
]
```

Purpose:

Generate competing explanations.

---

### Module 3.5 Summary Generator

Output:

```json
{
  "summary": ""
}
```

Purpose:

Generate concise investigation summary.

---

# Phase 4 - Investigation Dashboard

## Objective

Visualize investigation data.

## Modules

### Module 4.1 Overview Panel

Displays:

- Sources analyzed
- Theories generated
- Investigation summary

---

### Module 4.2 Evidence Board

Displays:

- Evidence cards
- Confidence levels
- Sources

---

### Module 4.3 Timeline View

Displays:

- Chronological events

---

### Module 4.4 Theory Comparison

Displays:

- Theory cards
- Confidence scores

---

# Phase 5 - Reconstruction Engine

## Objective

Convert investigation into visual simulation.

## Modules

### Module 5.1 Reconstruction Generator

Input:

Timeline

Output:

```json
{
  "actors": [],
  "vehicles": [],
  "events": []
}
```

Purpose:

Generate simulation instructions.

---

### Module 5.2 Simulation Scene Builder

Creates:

- Environment
- Actors
- Vehicles
- Camera

Purpose:

Render reconstruction.

---

### Module 5.3 Playback Controls

Features:

- Play
- Pause
- Restart

Purpose:

Control simulation.

---

# Phase 6 - Storage Layer

## Objective

Persist investigations.

## Modules

### Module 6.1 Investigation Storage

Store:

- Summary
- Evidence
- Timeline
- Theories

---

### Module 6.2 Simulation Storage

Store:

- Simulation JSON
- Reconstruction data

---

# Phase 7 - Integration

## Objective

Connect all modules.

## Modules

### Module 7.1 End-to-End Flow

```text
Login
 ↓
Dashboard
 ↓
Case Selection
 ↓
Source Collection
 ↓
Evidence Extraction
 ↓
Timeline Generation
 ↓
Theory Generation
 ↓
Summary Generation
 ↓
Generate Reconstruction
 ↓
Simulation Viewer
```

Deliverable:

Complete working workflow.

---

# Simulation MVP Requirements

The simulation DOES NOT need:

- Bullet physics
- Rewind
- AAA graphics
- Unreal Engine quality

The simulation SHOULD:

- Display a scene
- Display actors
- Animate movement
- Follow timeline events
- Support play/pause/restart

---

# Success Criteria

The MVP is successful if:

✅ User can register

✅ User can login

✅ User can select a case

✅ AI generates evidence

✅ AI generates timeline

✅ AI generates theories

✅ AI generates summary

✅ User can generate reconstruction

✅ Simulation plays successfully

---

# Priority Matrix

## P0 - Must Have

- Authentication
- Database
- Dashboard
- Evidence Engine
- Timeline Generator
- Theory Generator
- Summary Generator
- Reconstruction Generator
- Simulation Viewer

---

## P1 - Nice To Have

- Source credibility scoring
- Contradiction detection
- Better animations
- Additional cases

---

## P2 - Future Scope

- User-created theories
- Video export
- Voice narration
- Rewind system
- Multi-case investigations
- Mobile optimization
- AI-generated cinematic videos
- Public sharing system

---

# Final Deliverable

Khoj should demonstrate:

AI Investigation → Evidence → Timeline → Theories → Reconstruction → Simulation

in one complete and seamless workflow.

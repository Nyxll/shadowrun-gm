# Campaign Management UI Design - DRAFT (PARKED)

**Status:** Initial design - needs simplification  
**Date:** 2025-10-29  
**Note:** This design became too complex. Parking for future reference.

---

## Original Design Concept

### Epic Campaign Management UI for Grok-4 Story Generation

The goal was to create a UI system that enables Grok-4 to create epic Shadowrun campaigns by providing rich context and narrative control.

---

## Core Design Philosophy

**"The UI is Grok's Memory Palace"**
- Every UI element feeds context to Grok-4's system prompt
- Visual organization mirrors narrative structure
- Real-time updates create a living, breathing campaign world
- The GM orchestrates, Grok improvises within the framework

---

## Proposed UI Components

### 1. Campaign Creation Wizard (Modal)
**Purpose:** Set the narrative foundation that Grok will build upon

Features:
- Campaign title and description
- Theme selection (cyberpunk heist, corporate espionage, etc.)
- Campaign scope (one-shot, short arc, campaign, sandbox)
- Tone sliders (gritty/heroic, serious/humorous, tactical/narrative)
- Starting situation for Grok to expand
- Hidden GM notes (secrets only Grok sees)

### 2. Campaign Dashboard (Main View)
**Purpose:** Living narrative control center

Components:
- Current Situation panel (Grok updates this)
- Active Objectives list (player-facing goals)
- Complications panel (active threats)
- Location tracker with split party support
- Milestones (completed achievements)

### 3. NPC Tracker Sidebar (Collapsible Panel)
**Purpose:** Dynamic cast of characters Grok can reference

Features:
- Current NPCs (in scene)
- Background NPCs (known but not present)
- Future NPCs (mentioned but not met)
- Quick-add from chat when Grok mentions new NPCs
- NPC stats and notes

### 4. Narrative Prompt Builder (Advanced Feature)
**Purpose:** Give GM fine control over Grok's next response

Features:
- Scene type selection (combat, social, investigation, etc.)
- Intensity slider
- Element checkboxes (introduce NPC, reveal clue, etc.)
- GM direction text field for specific narrative beats

### 5. Session Timeline (Bottom Panel)
**Purpose:** Visual history and continuity tracker

Features:
- Session-by-session timeline
- Click to view full recap
- Restore context from previous sessions
- Helps Grok maintain long-term continuity

---

## Advanced Features (Scene Management)

### Multi-Scene State Tracking

Proposed schema additions:
```sql
CREATE TABLE campaign_scenes (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    scene_name TEXT NOT NULL,
    scene_type TEXT,
    is_active BOOLEAN DEFAULT true,
    location TEXT NOT NULL,
    participants JSONB,
    situation TEXT,
    tension_level INTEGER,
    in_game_time TIMESTAMP,
    real_time_started TIMESTAMP,
    parent_scene_id UUID REFERENCES campaign_scenes(id),
    will_merge_with UUID REFERENCES campaign_scenes(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE scene_transitions (
    id UUID PRIMARY KEY,
    from_scene_id UUID REFERENCES campaign_scenes(id),
    to_scene_id UUID REFERENCES campaign_scenes(id),
    transition_type TEXT,
    trigger_event TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Split Party Handling

UI Component: Scene Switcher
- Shows multiple active scenes side-by-side
- Each scene has its own situation, participants, tension level
- GM can switch between scenes
- Cross-scene events affect multiple scenes
- Merge opportunities when scenes converge

### Dynamic Plot Twist Generation

Features:
- Detect unexpected player actions
- Grok improvises using existing campaign state
- Generate 2-3 possible outcomes
- Auto-update campaign state with new NPCs, complications, plot threads
- Plot twist generator UI for GM approval

---

## Technical Implementation (Proposed)

### Database Schema Enhancements
```sql
ALTER TABLE campaigns ADD COLUMN theme TEXT;
ALTER TABLE campaigns ADD COLUMN scope TEXT;
ALTER TABLE campaigns ADD COLUMN tone_settings JSONB;
ALTER TABLE campaigns ADD COLUMN gm_secrets TEXT;

CREATE TABLE campaign_sessions (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    session_number INTEGER,
    context_snapshot JSONB,
    recap TEXT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);
```

### API Endpoints (Proposed)
```
POST   /api/campaign/create
GET    /api/campaign/:id
PUT    /api/campaign/:id/state
DELETE /api/campaign/:id

POST   /api/campaign/:id/npc
PUT    /api/campaign/:id/npc/:npc_id
GET    /api/campaign/:id/npcs?relevance=current

POST   /api/campaign/:id/objective
PUT    /api/campaign/:id/objective/:obj_id
POST   /api/campaign/:id/complication
DELETE /api/campaign/:id/complication/:comp_id

POST   /api/campaign/:id/session/start
POST   /api/campaign/:id/session/end
GET    /api/campaign/:id/sessions

POST   /api/campaign/:id/scene/create
PUT    /api/campaign/:id/scene/:scene_id/update
POST   /api/campaign/:id/scene/split
POST   /api/campaign/:id/scene/merge
GET    /api/campaign/:id/scenes/active
POST   /api/campaign/:id/scene/:scene_id/switch

POST   /api/campaign/:id/event/cross-scene
POST   /api/campaign/:id/improvise
GET    /api/campaign/:id/plot-twists/suggest
```

### Grok-4 Context Injection Pattern
```javascript
const campaignContext = {
    theme: campaign.theme,
    tone: campaign.tone_settings,
    current_situation: campaign.current_situation,
    location: campaign.location,
    objectives: campaign.objectives,
    complications: campaign.active_complications,
    npcs_current: getNPCs('current'),
    npcs_background: getNPCs('background'),
    recent_milestones: campaign.completed_milestones.slice(-3),
    gm_secrets: campaign.gm_secrets
};

const systemPrompt = `
You are the GM for a Shadowrun campaign: "${campaign.title}"
Theme: ${campaignContext.theme}
Tone: Gritty(${tone.gritty}), Serious(${tone.serious})

CURRENT SITUATION:
${campaignContext.current_situation}

LOCATION: ${campaignContext.location}

ACTIVE OBJECTIVES:
${formatObjectives(campaignContext.objectives)}

COMPLICATIONS:
${formatComplications(campaignContext.complications)}

NPCS IN SCENE:
${formatNPCs(campaignContext.npcs_current)}

GM SECRETS (weave these in subtly):
${campaignContext.gm_secrets}

Respond in character as the GM, advancing the story while respecting the current state.
`;
```

---

## Why This Design Was Parked

**Complexity Issues:**
1. Too many UI components for initial implementation
2. Scene management system is overly complex
3. Split party handling requires significant backend work
4. Plot twist generator might be too "magic box" for GMs
5. Multi-scene state tracking adds database complexity

**Better Approach Needed:**
- Start simpler with basic campaign state
- Add complexity incrementally based on actual use
- Focus on core GM needs first
- Let features emerge from real gameplay

---

## What to Keep for Simpler V1

**Essential Features:**
1. Basic campaign creation (title, description, theme)
2. Current situation text (Grok updates this)
3. Simple objectives list
4. Basic NPC tracking (name, role, status)
5. Session notes/history

**Skip for V1:**
- Multi-scene management
- Split party UI
- Plot twist generator
- Tone sliders
- Scene transitions
- Cross-scene events

---

## Next Steps

1. Design simpler campaign UI focused on core needs
2. Start with existing schema (campaigns, campaign_npcs tables)
3. Build basic UI components first
4. Test with real gameplay
5. Add complexity only when needed

---

**End of Draft Document**

# Campaign Management UI - Epic Story Design

**Version:** 2.0  
**Date:** 2025-10-29  
**Status:** Active Design - Ready for Implementation  
**Philosophy:** "Simple Interface, Epic Stories"

---

## 🎯 Design Philosophy

### Core Principle: "The Storyteller's Canvas"

**The UI should:**
1. **Inspire** Grok to create epic narratives
2. **Guide** without constraining creativity
3. **Remember** everything so Grok can improvise
4. **Evolve** as the story unfolds

**The UI should NOT:**
- Overwhelm with complexity
- Force rigid story structures
- Require constant GM micromanagement
- Hide important context from Grok

---

## 🎨 The Three-Panel Design

### Layout Overview
```
┌─────────────────────────────────────────────────────────────┐
│  CAMPAIGN HEADER (Collapsible)                              │
│  [Title] [Theme Badge] [Session #3] [Last: 2 days ago]     │
└─────────────────────────────────────────────────────────────┘
┌──────────────────┬──────────────────────┬──────────────────┐
│                  │                      │                  │
│  LEFT PANEL      │   CENTER PANEL       │   RIGHT PANEL    │
│  (25%)           │   (50%)              │   (25%)          │
│                  │                      │                  │
│  CAST            │   THE STORY          │   THREADS        │
│  ────            │   ─────────          │   ───────        │
│                  │                      │                  │
│  [NPCs]          │   Current Scene      │   [Objectives]   │
│  [Factions]      │   ─────────────      │   [Secrets]      │
│  [Locations]     │                      │   [Clues]        │
│                  │   [Narrative]        │   [Complications]│
│                  │                      │                  │
│                  │   Quick Actions      │                  │
│                  │   ──────────────     │                  │
│                  │   [Add NPC]          │                  │
│                  │   [Add Objective]    │                  │
│                  │   [Add Complication] │                  │
│                  │                      │                  │
└──────────────────┴──────────────────────┴──────────────────┘
```

---

## 📋 Component Specifications

### 1. Campaign Header (Collapsible)

**Purpose:** Quick campaign identity and status

**Fields:**
```javascript
{
  title: "Shadows of the Arcology",
  theme: "Corporate Espionage",  // Badge with icon
  session_number: 3,
  last_session: "2 days ago",
  total_runtime: "12 hours",
  status: "active" | "paused" | "completed"
}
```

**Visual Design:**
- Large, bold title (editable inline)
- Theme as colored badge (cyberpunk heist 🏢, street survival 🌃, etc.)
- Session counter with "Start New Session" button
- Collapse arrow to hide when not needed

---

### 2. LEFT PANEL: The Cast

**Purpose:** Living directory of people, places, and powers

#### 2.1 NPCs Section

**Three-Tier Relevance System:**

```
┌─────────────────────────┐
│ 🎭 CURRENT (In Scene)   │
├─────────────────────────┤
│ ▸ Mr. Johnson          │
│   Corporate Fixer      │
│   📍 Stuffer Shack     │
│                        │
│ ▸ Lone Star Officer    │
│   Suspicious           │
│   📍 Outside           │
└─────────────────────────┘

┌─────────────────────────┐
│ 👥 BACKGROUND (Known)   │
├─────────────────────────┤
│ ▸ Raven (Contact)      │
│ ▸ Dr. Simmons          │
│ ▸ Gang Leader Tusk     │
└─────────────────────────┘

┌─────────────────────────┐
│ 🔮 FUTURE (Mentioned)   │
├─────────────────────────┤
│ ▸ The Dragon           │
│ ▸ Aztechnology VP      │
└─────────────────────────┘
```

**NPC Card (Expandable):**
```javascript
{
  name: "Mr. Johnson",
  role: "Corporate Fixer",
  location: "Stuffer Shack",
  status: "active",
  relevance: "current",
  description: "Nervous, sweating, keeps checking his commlink",
  stats: { body: 3, quickness: 4, ... },  // Optional
  notes: "Offered 50k¥ for data extraction. Seems desperate.",
  first_encountered: "Session 1",
  last_mentioned: "Just now"
}
```

**Quick Actions:**
- Click to expand full details
- Drag to change relevance tier
- Right-click for "Move to Background" / "Mark Deceased"
- "+" button to quick-add from chat

#### 2.2 Factions Section (Collapsible)

**Purpose:** Track corporate/gang/political power structures

```
┌─────────────────────────┐
│ 🏢 FACTIONS             │
├─────────────────────────┤
│ ▸ Aztechnology         │
│   Hostile              │
│                        │
│ ▸ Lone Star            │
│   Investigating        │
│                        │
│ ▸ Street Samurai Gang  │
│   Neutral              │
└─────────────────────────┘
```

**Faction Card:**
```javascript
{
  name: "Aztechnology",
  type: "Megacorp",
  stance: "hostile" | "neutral" | "friendly",
  power_level: 5,  // 1-5 scale
  current_action: "Hunting the team",
  notes: "Blood magic division involved"
}
```

#### 2.3 Locations Section (Collapsible)

**Purpose:** Track where things happen

```
┌─────────────────────────┐
│ 📍 LOCATIONS            │
├─────────────────────────┤
│ ▸ Stuffer Shack         │
│   Current              │
│                        │
│ ▸ Abandoned Warehouse  │
│   Visited              │
│                        │
│ ▸ Aztechnology Tower   │
│   Target               │
└─────────────────────────┘
```

---

### 3. CENTER PANEL: The Story

**Purpose:** The living narrative that Grok reads and updates

#### 3.1 Current Scene Display

**Visual Design:**
```
┌─────────────────────────────────────────┐
│ 📍 Stuffer Shack - Back Alley          │
│ ⏰ 23:47, November 15, 2054            │
├─────────────────────────────────────────┤
│                                         │
│  The neon signs flicker overhead as    │
│  rain hammers the pavement. Mr.        │
│  Johnson's hands shake as he slides    │
│  the credstick across the table.       │
│                                         │
│  "The data's in Aztechnology's         │
│  downtown server farm," he whispers.   │
│  "You've got 48 hours before they      │
│  move it."                             │
│                                         │
│  Behind you, a Lone Star cruiser       │
│  pulls into the parking lot...         │
│                                         │
└─────────────────────────────────────────┘
```

**Fields:**
```javascript
{
  location: "Stuffer Shack - Back Alley",
  in_game_time: "23:47, November 15, 2054",
  situation: "Full narrative text (Grok updates this)",
  tension_level: 7,  // 1-10 scale (visual indicator)
  participants: ["Team", "Mr. Johnson", "Lone Star (approaching)"]
}
```

**Grok Updates This Automatically:**
- After each player action
- When introducing new NPCs
- When complications arise
- When scene changes

#### 3.2 Quick Action Buttons

**Purpose:** Let GM inject story elements mid-session

```
┌─────────────────────────────────────────┐
│  [+ Add NPC]  [+ Objective]  [+ Twist]  │
│  [⚡ Complication]  [🎲 Random Event]   │
└─────────────────────────────────────────┘
```

**Add NPC Modal:**
```
Name: _______________
Role: [Dropdown: Contact, Enemy, Neutral, Authority, etc.]
Relevance: [Current / Background / Future]
Quick Description: _______________
[Add to Scene]
```

**Add Objective Modal:**
```
Objective: _______________
Type: [Primary / Secondary / Personal]
Difficulty: [Easy / Medium / Hard / Extreme]
Reward: _______________
[Add]
```

**Add Twist Button:**
- Prompts Grok: "Generate an unexpected complication based on current scene"
- Grok suggests 2-3 options
- GM picks one or edits

---

### 4. RIGHT PANEL: Story Threads

**Purpose:** Track what players are trying to do and what's working against them

#### 4.1 Objectives Section

**Visual Design:**
```
┌─────────────────────────────────────────┐
│ 🎯 OBJECTIVES                           │
├─────────────────────────────────────────┤
│ PRIMARY                                 │
│ ☐ Extract Aztechnology data            │
│   Reward: 50,000¥                       │
│   Deadline: 48 hours                    │
│                                         │
│ SECONDARY                               │
│ ☐ Identify the mole                    │
│ ☐ Avoid Lone Star                      │
│                                         │
│ COMPLETED ✓                             │
│ ✓ Meet Mr. Johnson                     │
│ ✓ Scout the target                     │
└─────────────────────────────────────────┘
```

**Objective Card:**
```javascript
{
  text: "Extract Aztechnology data",
  type: "primary" | "secondary" | "personal",
  status: "active" | "completed" | "failed",
  difficulty: "hard",
  reward: "50,000¥",
  deadline: "48 hours",
  progress: 30,  // 0-100%
  added_session: 1
}
```

#### 4.2 Secrets Section (GM Only)

**Purpose:** Hidden information Grok weaves into the story

```
┌─────────────────────────────────────────┐
│ 🔒 SECRETS (Hidden from Players)        │
├─────────────────────────────────────────┤
│ ▸ Mr. Johnson is being blackmailed     │
│ ▸ The data contains blood magic ritual │
│ ▸ One team member is being watched     │
└─────────────────────────────────────────┘
```

**Secret Card:**
```javascript
{
  secret: "Mr. Johnson is being blackmailed",
  revealed: false,
  reveal_trigger: "If players investigate his behavior",
  impact: "Changes the mission parameters",
  added_session: 1
}
```

**Grok's Instructions:**
- Weave secrets into narrative subtly
- Drop hints without revealing directly
- Mark as revealed when players discover
- Create new secrets as story evolves

#### 4.3 Clues Section

**Purpose:** Track what players have discovered

```
┌─────────────────────────────────────────┐
│ 🔍 CLUES DISCOVERED                     │
├─────────────────────────────────────────┤
│ ✓ Credstick has Aztechnology serial    │
│ ✓ Mr. Johnson's commlink is bugged     │
│ ✓ Server farm has 3 security layers    │
└─────────────────────────────────────────┘
```

#### 4.4 Complications Section

**Purpose:** Active threats and obstacles

```
┌─────────────────────────────────────────┐
│ ⚠️ ACTIVE COMPLICATIONS                 │
├─────────────────────────────────────────┤
│ 🚨 Lone Star investigating             │
│    Severity: Medium                     │
│                                         │
│ ⏰ 48-hour deadline                     │
│    Severity: High                       │
│                                         │
│ 🩸 Team mage is wounded                │
│    Severity: Low                        │
└─────────────────────────────────────────┘
```

**Complication Card:**
```javascript
{
  description: "Lone Star investigating",
  severity: "low" | "medium" | "high" | "critical",
  type: "time_pressure" | "enemy_action" | "resource" | "injury",
  status: "active" | "resolved",
  escalation_trigger: "If players are spotted",
  added_session: 3
}
```

---

## 🎬 Campaign Creation Wizard

### Step 1: The Hook

**Purpose:** Give Grok the narrative foundation

```
┌─────────────────────────────────────────────────┐
│  CREATE EPIC CAMPAIGN                           │
├─────────────────────────────────────────────────┤
│                                                 │
│  Campaign Title:                                │
│  ┌─────────────────────────────────────────┐   │
│  │ Shadows of the Arcology                 │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Theme: (Select one or more)                    │
│  ☑ Corporate Espionage                          │
│  ☐ Street Survival                              │
│  ☐ Magical Mystery                              │
│  ☐ Cyberpunk Heist                              │
│  ☐ Political Intrigue                           │
│  ☐ Gang Warfare                                 │
│                                                 │
│  Campaign Scope:                                │
│  ○ One-Shot (Single session)                    │
│  ● Short Arc (3-5 sessions)                     │
│  ○ Campaign (10+ sessions)                      │
│  ○ Sandbox (Open-ended)                         │
│                                                 │
│  [Next: The Setup]                              │
└─────────────────────────────────────────────────┘
```

### Step 2: The Setup

**Purpose:** Initial situation for Grok to expand

```
┌─────────────────────────────────────────────────┐
│  THE OPENING SCENE                              │
├─────────────────────────────────────────────────┤
│                                                 │
│  Starting Situation:                            │
│  ┌─────────────────────────────────────────┐   │
│  │ The team is contacted by a nervous      │   │
│  │ corporate fixer who needs data          │   │
│  │ extracted from Aztechnology before      │   │
│  │ it's moved in 48 hours...               │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Starting Location:                             │
│  ┌─────────────────────────────────────────┐   │
│  │ Stuffer Shack - Back Alley              │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Initial Objective:                             │
│  ┌─────────────────────────────────────────┐   │
│  │ Extract corporate data                  │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  [Next: GM Secrets]                             │
└─────────────────────────────────────────────────┘
```

### Step 3: GM Secrets (Optional)

**Purpose:** Hidden plot elements for Grok to weave in

```
┌─────────────────────────────────────────────────┐
│  GM SECRETS (Hidden from Players)               │
├─────────────────────────────────────────────────┤
│                                                 │
│  Add secrets that Grok will subtly reveal:      │
│                                                 │
│  Secret #1:                                     │
│  ┌─────────────────────────────────────────┐   │
│  │ Mr. Johnson is being blackmailed        │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Secret #2:                                     │
│  ┌─────────────────────────────────────────┐   │
│  │ The data contains blood magic ritual    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  [+ Add Another Secret]                         │
│                                                 │
│  [Skip] [Create Campaign]                       │
└─────────────────────────────────────────────────┘
```

---

## 🤖 Grok Integration: The Epic Story Engine

### System Prompt Template

**Purpose:** Transform UI state into narrative context for Grok

```javascript
const buildGrokContext = (campaign) => {
  return `
# SHADOWRUN CAMPAIGN: ${campaign.title}

## CAMPAIGN OVERVIEW
Theme: ${campaign.theme}
Scope: ${campaign.scope}
Session: ${campaign.session_number}

## CURRENT SCENE
Location: ${campaign.location}
Time: ${campaign.in_game_time}
Tension Level: ${campaign.tension_level}/10

${campaign.current_situation}

## ACTIVE CAST

### NPCs in Scene (CURRENT)
${formatNPCs(campaign.npcs.filter(n => n.relevance === 'current'))}

### Known NPCs (BACKGROUND)
${formatNPCs(campaign.npcs.filter(n => n.relevance === 'background'))}

### Mentioned NPCs (FUTURE)
${formatNPCs(campaign.npcs.filter(n => n.relevance === 'future'))}

### Factions
${formatFactions(campaign.factions)}

## STORY THREADS

### Active Objectives
${formatObjectives(campaign.objectives.filter(o => o.status === 'active'))}

### Active Complications
${formatComplications(campaign.complications.filter(c => c.status === 'active'))}

### Clues Discovered
${formatClues(campaign.clues)}

## GM SECRETS (Weave these in subtly)
${formatSecrets(campaign.secrets.filter(s => !s.revealed))}

## INSTRUCTIONS
You are the GM for this Shadowrun campaign. Based on the player's action:
1. Update the Current Scene narrative
2. Introduce or update NPCs as needed
3. Progress objectives or add complications
4. Drop subtle hints about unrevealed secrets
5. Maintain tension level appropriate to the scene
6. Keep the story moving forward

Respond with:
- Updated narrative for Current Scene
- Any new NPCs to add (with relevance tier)
- Any objective/complication updates
- Any secrets revealed (if appropriate)
`;
};
```

### Grok Response Parser

**Purpose:** Extract structured updates from Grok's narrative response

```javascript
const parseGrokResponse = (response) => {
  return {
    narrative: extractNarrative(response),
    npc_updates: extractNPCUpdates(response),
    objective_updates: extractObjectiveUpdates(response),
    complication_updates: extractComplicationUpdates(response),
    secrets_revealed: extractSecretsRevealed(response),
    new_clues: extractNewClues(response)
  };
};
```

### Auto-Update Flow

```
Player Action
     ↓
Send to Grok with Campaign Context
     ↓
Grok Generates Narrative + Updates
     ↓
Parse Response
     ↓
Update UI Components:
  - Current Scene (narrative)
  - NPCs (add/update/move)
  - Objectives (progress/complete)
  - Complications (add/resolve)
  - Clues (add discovered)
  - Secrets (mark revealed)
     ↓
Display to Players
```

---

## 📊 Database Schema Extensions

### New Tables Needed

```sql
-- Campaign factions
CREATE TABLE campaign_factions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT,  -- 'megacorp', 'gang', 'government', 'magical'
    stance TEXT DEFAULT 'neutral',  -- 'hostile', 'neutral', 'friendly'
    power_level INTEGER DEFAULT 3,  -- 1-5
    current_action TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Campaign locations
CREATE TABLE campaign_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT,  -- 'safehouse', 'target', 'neutral', 'hostile'
    status TEXT DEFAULT 'unvisited',  -- 'current', 'visited', 'unvisited'
    description TEXT,
    security_level INTEGER,  -- 1-10
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Campaign secrets
CREATE TABLE campaign_secrets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    secret TEXT NOT NULL,
    revealed BOOLEAN DEFAULT FALSE,
    reveal_trigger TEXT,
    impact TEXT,
    added_session INTEGER,
    revealed_session INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Campaign clues
CREATE TABLE campaign_clues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    clue TEXT NOT NULL,
    discovered_session INTEGER,
    relates_to TEXT,  -- Which objective/secret
    created_at TIMESTAMP DEFAULT NOW()
);

-- Extend campaigns table
ALTER TABLE campaigns ADD COLUMN scope TEXT;  -- 'one-shot', 'short-arc', 'campaign', 'sandbox'
ALTER TABLE campaigns ADD COLUMN in_game_time TEXT;
ALTER TABLE campaigns ADD COLUMN tension_level INTEGER DEFAULT 5;
ALTER TABLE campaigns ADD COLUMN gm_secrets TEXT;  -- Deprecated, use campaign_secrets table
```

---

## 🎮 Implementation Roadmap

### Phase 1: Core UI (Week 1)
- [ ] Campaign creation wizard (3 steps)
- [ ] Three-panel layout
- [ ] Basic NPC tracking (current/background/future)
- [ ] Current scene display
- [ ] Objectives list
- [ ] Complications list

### Phase 2: Grok Integration (Week 2)
- [ ] Build Grok context injection
- [ ] Parse Grok responses
- [ ] Auto-update UI from Grok
- [ ] Test narrative flow

### Phase 3: Advanced Features (Week 3)
- [ ] Factions tracking
- [ ] Locations tracking
- [ ] Secrets system
- [ ] Clues tracking
- [ ] Quick action buttons
- [ ] Session history

### Phase 4: Polish (Week 4)
- [ ] Drag-and-drop NPC relevance
- [ ] Inline editing
- [ ] Visual tension indicator
- [ ] Theme badges and icons
- [ ] Mobile responsive design

---

## 🎯 Success Metrics

### For Players
- **Immersion:** Does the UI fade into the background?
- **Clarity:** Can players see objectives and threats at a glance?
- **Engagement:** Does the narrative pull them in?

### For GM (Grok)
- **Context:** Does Grok have all the information it needs?
- **Consistency:** Does Grok maintain continuity across sessions?
- **Creativity:** Does Grok generate epic, unexpected moments?

### For the System
- **Performance:** Updates in < 2 seconds
- **Reliability:** No lost data between sessions
- **Scalability:** Handles 10+ NPCs, 20+ objectives

---

## 💡 Key Design Decisions

### Why Three Panels?
- **Left (Cast):** Who's involved
- **Center (Story):** What's happening now
- **Right (Threads):** What matters

This mirrors how GMs think: characters, scene, goals.

### Why Three NPC Tiers?
- **Current:** Grok focuses here for immediate narrative
- **Background:** Grok can pull from for callbacks
- **Future:** Grok knows to foreshadow

### Why Secrets System?
- Gives Grok dramatic irony
- Creates "aha!" moments for players
- Enables plot twists that feel earned

### Why Tension Level?
- Guides Grok's tone (action vs. downtime)
- Helps pace the session
- Visual feedback for GM

---

## 🚀 Next Steps

1. **Review this design** with stakeholders
2. **Create wireframes** for each component
3. **Build database migrations** for new tables
4. **Implement Phase 1** (core UI)
5. **Test with real gameplay** session
6. **Iterate based on feedback**

---

**End of Epic Campaign UI Design v2.0**

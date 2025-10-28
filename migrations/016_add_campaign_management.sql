-- Migration 016: Add Campaign Management System
-- Adds campaigns, campaign_npcs, and campaign_characters tables
-- Supports dynamic NPC tracking and fluid narrative state

-- Campaigns table - stores campaign overview and current state
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,              -- Full campaign background (hidden from players)
    theme TEXT,                    -- User-selected theme (cyberpunk heist, corporate espionage, etc.)
    current_situation TEXT,        -- Living narrative state (updated by AI)
    location TEXT,                 -- Current location(s) - can be "Team A: Sewers, Team B: Building"
    objectives JSONB DEFAULT '[]', -- [{objective: "text", completed: false, order: 1}]
    active_complications JSONB DEFAULT '[]', -- Current threats/challenges
    completed_milestones JSONB DEFAULT '[]', -- What's been accomplished
    session_id TEXT,               -- Link to active WebSocket session
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Campaign NPCs - dynamically tracked as they're introduced
CREATE TABLE IF NOT EXISTS campaign_npcs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    role TEXT,                     -- guard, bartender, johnson, contact, rival, etc.
    location TEXT,                 -- Where they were last seen
    status TEXT DEFAULT 'active',  -- active, inactive, deceased, unknown
    relevance TEXT DEFAULT 'current', -- current (active now), background (encountered before), future (mentioned but not met)
    stats JSONB,                   -- Combat stats if needed: {body: 5, quickness: 4, etc.}
    notes TEXT,                    -- AI-generated notes about interactions
    first_encountered TIMESTAMP DEFAULT NOW(),
    last_mentioned TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Campaign character membership
CREATE TABLE IF NOT EXISTS campaign_characters (
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (campaign_id, character_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_campaign_npcs_campaign ON campaign_npcs(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_npcs_status ON campaign_npcs(campaign_id, status);
CREATE INDEX IF NOT EXISTS idx_campaign_npcs_relevance ON campaign_npcs(campaign_id, relevance);
CREATE INDEX IF NOT EXISTS idx_campaign_npcs_location ON campaign_npcs(campaign_id, location);
CREATE INDEX IF NOT EXISTS idx_campaign_characters_campaign ON campaign_characters(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_session ON campaigns(session_id);

-- Function to update campaign updated_at timestamp
CREATE OR REPLACE FUNCTION update_campaign_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update campaign timestamp
CREATE TRIGGER campaign_update_timestamp
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_campaign_timestamp();

-- Comments for documentation
COMMENT ON TABLE campaigns IS 'Stores campaign overview and current narrative state';
COMMENT ON TABLE campaign_npcs IS 'Dynamically tracks NPCs as they are introduced during play';
COMMENT ON TABLE campaign_characters IS 'Links characters to campaigns';
COMMENT ON COLUMN campaigns.description IS 'Full campaign background - hidden from players, only GM (Grok) knows';
COMMENT ON COLUMN campaigns.current_situation IS 'Living narrative state updated by AI as story progresses';
COMMENT ON COLUMN campaign_npcs.relevance IS 'current=active now, background=encountered before, future=mentioned but not met';
COMMENT ON COLUMN campaign_npcs.stats IS 'Combat stats in JSONB format for quick access during combat';

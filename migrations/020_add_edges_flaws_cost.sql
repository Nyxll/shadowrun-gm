-- Add cost field to character_edges_flaws table
-- Edges have negative costs (they cost karma to buy)
-- Flaws have positive costs (they give karma back)

ALTER TABLE character_edges_flaws 
ADD COLUMN IF NOT EXISTS cost INTEGER;

COMMENT ON COLUMN character_edges_flaws.cost IS 'Karma cost: negative for edges (cost karma), positive for flaws (gain karma)';

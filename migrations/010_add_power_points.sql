-- Add power_points field for Physical Adepts and Mystical Adepts
-- Power points are used to purchase adept powers
-- Only Physical Adepts and Mystical Adepts have these

ALTER TABLE characters 
ADD COLUMN IF NOT EXISTS power_points_total DECIMAL(3,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS power_points_used DECIMAL(3,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS power_points_available DECIMAL(3,2) DEFAULT 0;

COMMENT ON COLUMN characters.power_points_total IS 'Total adept power points (for Physical/Mystical Adepts)';
COMMENT ON COLUMN characters.power_points_used IS 'Power points spent on adept powers';
COMMENT ON COLUMN characters.power_points_available IS 'Remaining power points available';

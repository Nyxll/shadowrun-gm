-- Migration 024: Add pool columns to characters table
-- Adds combat_pool, task_pool, and hacking_pool columns

-- Add pool columns
ALTER TABLE characters 
ADD COLUMN IF NOT EXISTS combat_pool INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS task_pool INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS hacking_pool INTEGER DEFAULT 0;

-- Add comments
COMMENT ON COLUMN characters.combat_pool IS 'Combat Pool = (Quickness + Intelligence + Willpower) / 2';
COMMENT ON COLUMN characters.task_pool IS 'Task Pool from cyberware/bioware (e.g., Datajack, Cerebral Booster)';
COMMENT ON COLUMN characters.hacking_pool IS 'Hacking Pool = (Intelligence + Computer Skill) / 3';

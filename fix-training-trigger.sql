-- Fix missing trigger for training system
-- This adds the trigger that was missing from migration 005

-- Just create the trigger (function should already exist)
DROP TRIGGER IF EXISTS trigger_update_query_correctness ON query_logs;
CREATE TRIGGER trigger_update_query_correctness
  BEFORE INSERT OR UPDATE ON query_logs
  FOR EACH ROW
  EXECUTE FUNCTION update_query_correctness();

-- Verify trigger was created
SELECT 
  tgname as trigger_name,
  tgrelid::regclass as table_name,
  tgenabled as enabled
FROM pg_trigger
WHERE tgname = 'trigger_update_query_correctness';

-- Migration 019: Add audit system and enhanced spell fields
-- Adds user tracking, audit logging, soft deletes, and enhanced spell data

-- 1. Users table for tracking who makes changes
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Insert default user
INSERT INTO users (email, display_name) 
VALUES ('rickstjean@gmail.com', 'Rick St Jean')
ON CONFLICT (email) DO NOTHING;

-- 2. Audit log table for tracking all changes
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    changed_by UUID REFERENCES users(id),
    changed_by_type VARCHAR(20) DEFAULT 'USER', -- 'USER', 'AI', 'SYSTEM'
    changed_at TIMESTAMP DEFAULT NOW(),
    old_values JSONB,
    new_values JSONB,
    change_reason TEXT,
    session_info JSONB -- Additional context (IP, user agent, etc.)
);

-- Index for efficient audit queries
CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log(changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_by ON audit_log(changed_by);

-- 3. Add audit fields to character_spells
ALTER TABLE character_spells 
    ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS modified_by UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES users(id);

-- 4. Add enhanced spell fields
ALTER TABLE character_spells 
    ADD COLUMN IF NOT EXISTS drain_code VARCHAR(20),
    ADD COLUMN IF NOT EXISTS target_type VARCHAR(20),
    ADD COLUMN IF NOT EXISTS totem_modifier INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS spell_notes TEXT;

-- 5. Add audit fields to other character tables
ALTER TABLE character_modifiers
    ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS modified_by UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES users(id);

ALTER TABLE character_gear
    ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS modified_by UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES users(id);

ALTER TABLE character_vehicles
    ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS modified_by UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES users(id);

-- 6. Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    current_user_id UUID;
    current_user_type VARCHAR(20);
    change_reason TEXT;
BEGIN
    -- Get current user from session variables (set by application)
    BEGIN
        current_user_id := current_setting('app.current_user_id', true)::UUID;
    EXCEPTION WHEN OTHERS THEN
        current_user_id := NULL;
    END;
    
    BEGIN
        current_user_type := current_setting('app.current_user_type', true);
    EXCEPTION WHEN OTHERS THEN
        current_user_type := 'SYSTEM';
    END;
    
    BEGIN
        change_reason := current_setting('app.change_reason', true);
    EXCEPTION WHEN OTHERS THEN
        change_reason := NULL;
    END;
    
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (
            table_name, record_id, operation, 
            changed_by, changed_by_type, old_values, change_reason
        )
        VALUES (
            TG_TABLE_NAME, OLD.id, 'DELETE', 
            current_user_id, current_user_type, row_to_json(OLD), change_reason
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (
            table_name, record_id, operation, 
            changed_by, changed_by_type, old_values, new_values, change_reason
        )
        VALUES (
            TG_TABLE_NAME, NEW.id, 'UPDATE', 
            current_user_id, current_user_type, row_to_json(OLD), row_to_json(NEW), change_reason
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (
            table_name, record_id, operation, 
            changed_by, changed_by_type, new_values, change_reason
        )
        VALUES (
            TG_TABLE_NAME, NEW.id, 'INSERT', 
            current_user_id, current_user_type, row_to_json(NEW), change_reason
        );
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 7. Apply audit triggers to character tables
DROP TRIGGER IF EXISTS audit_character_spells ON character_spells;
CREATE TRIGGER audit_character_spells 
AFTER INSERT OR UPDATE OR DELETE ON character_spells
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

DROP TRIGGER IF EXISTS audit_character_modifiers ON character_modifiers;
CREATE TRIGGER audit_character_modifiers 
AFTER INSERT OR UPDATE OR DELETE ON character_modifiers
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

DROP TRIGGER IF EXISTS audit_character_gear ON character_gear;
CREATE TRIGGER audit_character_gear 
AFTER INSERT OR UPDATE OR DELETE ON character_gear
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

DROP TRIGGER IF EXISTS audit_character_vehicles ON character_vehicles;
CREATE TRIGGER audit_character_vehicles 
AFTER INSERT OR UPDATE OR DELETE ON character_vehicles
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

-- 8. Create helper function to get AI user ID
CREATE OR REPLACE FUNCTION get_ai_user_id()
RETURNS UUID AS $$
DECLARE
    ai_user_id UUID;
BEGIN
    SELECT id INTO ai_user_id 
    FROM users 
    WHERE email = 'ai@shadowrun-gm.system'
    LIMIT 1;
    
    IF ai_user_id IS NULL THEN
        INSERT INTO users (email, display_name)
        VALUES ('ai@shadowrun-gm.system', 'AI Assistant')
        RETURNING id INTO ai_user_id;
    END IF;
    
    RETURN ai_user_id;
END;
$$ LANGUAGE plpgsql;

-- 9. Create helper function to get system user ID
CREATE OR REPLACE FUNCTION get_system_user_id()
RETURNS UUID AS $$
DECLARE
    system_user_id UUID;
BEGIN
    SELECT id INTO system_user_id 
    FROM users 
    WHERE email = 'system@shadowrun-gm.internal'
    LIMIT 1;
    
    IF system_user_id IS NULL THEN
        INSERT INTO users (email, display_name)
        VALUES ('system@shadowrun-gm.internal', 'System')
        RETURNING id INTO system_user_id;
    END IF;
    
    RETURN system_user_id;
END;
$$ LANGUAGE plpgsql;

-- 10. Create view for active (non-deleted) spells
CREATE OR REPLACE VIEW active_character_spells AS
SELECT * FROM character_spells
WHERE deleted_at IS NULL;

-- 11. Create view for active modifiers
CREATE OR REPLACE VIEW active_character_modifiers AS
SELECT * FROM character_modifiers
WHERE deleted_at IS NULL;

-- 12. Create view for active gear
CREATE OR REPLACE VIEW active_character_gear AS
SELECT * FROM character_gear
WHERE deleted_at IS NULL;

-- 13. Create view for active vehicles
CREATE OR REPLACE VIEW active_character_vehicles AS
SELECT * FROM character_vehicles
WHERE deleted_at IS NULL;

-- Migration complete
COMMENT ON TABLE users IS 'User accounts for audit tracking';
COMMENT ON TABLE audit_log IS 'Complete audit trail of all data changes';
COMMENT ON COLUMN character_spells.drain_code IS 'Spell drain code (e.g., 6S, (F/2)M)';
COMMENT ON COLUMN character_spells.target_type IS 'Spell target type (e.g., M/S/D)';
COMMENT ON COLUMN character_spells.totem_modifier IS 'Totem bonus dice for this spell';
COMMENT ON COLUMN character_spells.spell_notes IS 'Additional spell notes from character sheet';

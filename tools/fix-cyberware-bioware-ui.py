#!/usr/bin/env python3
"""
Fix cyberware/bioware UI to use pre-grouped arrays from backend
"""

# Read the file
with open('www/character-sheet-renderer.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: hasCyberware() detection method
content = content.replace(
    '''    hasCyberware() {
        const modifiers = this.characterData.modifiers || [];
        return modifiers.some(m => m.source_type === 'cyberware');
    }''',
    '''    hasCyberware() {
        const cyberware = this.characterData.cyberware || [];
        return cyberware.length > 0;
    }'''
)

# Fix 2: hasBioware() detection method
content = content.replace(
    '''    hasBioware() {
        const modifiers = this.characterData.modifiers || [];
        return modifiers.some(m => m.source_type === 'bioware');
    }''',
    '''    hasBioware() {
        const bioware = this.characterData.bioware || [];
        return bioware.length > 0;
    }'''
)

# Fix 3: renderCyberware() - replace the entire method
old_render_cyber = '''    renderCyberware() {
        // CRUD API returns modifiers array - filter for cyberware
        const modifiers = this.characterData.modifiers || [];
        const cyberware = modifiers.filter(m => m.source_type === 'cyberware');
        
        const cyberItems = cyberware.map(item => {
            // Extract effects from modifier_data JSONB
            const modData = item.modifier_data || {};
            const effects = modData.special_abilities || [];
            
            // Format effects as bullet list
            const effectsList = effects.length > 0 
                ? effects.map(effect => `<li>${effect}</li>`).join('')
                : '';
            
            // Build details
            let details = [];
            if (item.modifier_value) {
                details.push(`${item.target_name}: ${item.modifier_value > 0 ? '+' : ''}${item.modifier_value}`);
            }
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${item.source}</div>
                        ${details.length > 0 ? `<div class="item-details">${details.join(' • ')}</div>` : ''}
                        ${effectsList ? `<ul class="item-effects">${effectsList}</ul>` : ''}
                    </div>
                    ${modData.essence_cost ? `<span class="item-rating">${modData.essence_cost} ESS</span>` : ''}
                </div>
            `;
        }).join('\\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Cyberware</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${cyberItems}</div>
                </div>
            </div>
        `;
    }'''

new_render_cyber = '''    renderCyberware() {
        // Use pre-grouped cyberware array from backend
        const cyberware = this.characterData.cyberware || [];
        
        const cyberItems = cyberware.map(item => {
            // Format effects as bullet list
            const effects = item.effects || [];
            const effectsList = effects.length > 0 
                ? `<ul class="item-effects">${effects.map(e => `<li>${e}</li>`).join('')}</ul>`
                : '';
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${item.name}</div>
                        ${effectsList}
                    </div>
                    ${item.essence_cost ? `<span class="item-rating">${item.essence_cost}</span>` : ''}
                </div>
            `;
        }).join('\\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Cyberware</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${cyberItems}</div>
                </div>
            </div>
        `;
    }'''

content = content.replace(old_render_cyber, new_render_cyber)

# Fix 4: renderBioware() - replace the entire method
old_render_bio = '''    renderBioware() {
        // CRUD API returns modifiers array - filter for bioware
        const modifiers = this.characterData.modifiers || [];
        const bioware = modifiers.filter(m => m.source_type === 'bioware');
        
        const bioItems = bioware.map(item => {
            // Extract effects from modifier_data JSONB
            const modData = item.modifier_data || {};
            const effects = modData.special_abilities || [];
            
            // Format effects as bullet list
            const effectsList = effects.length > 0 
                ? effects.map(effect => `<li>${effect}</li>`).join('')
                : '';
            
            // Build details
            let details = [];
            if (item.modifier_value) {
                details.push(`${item.target_name}: ${item.modifier_value > 0 ? '+' : ''}${item.modifier_value}`);
            }
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${item.source}</div>
                        ${details.length > 0 ? `<div class="item-details">${details.join(' • ')}</div>` : ''}
                        ${effectsList ? `<ul class="item-effects">${effectsList}</ul>` : ''}
                    </div>
                    ${modData.body_index_cost ? `<span class="item-rating">${modData.body_index_cost} B.I.</span>` : ''}
                </div>
            `;
        }).join('\\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Bioware</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${bioItems}</div>
                </div>
            </div>
        `;
    }'''

new_render_bio = '''    renderBioware() {
        // Use pre-grouped bioware array from backend
        const bioware = this.characterData.bioware || [];
        
        const bioItems = bioware.map(item => {
            // Format effects as bullet list
            const effects = item.effects || [];
            const effectsList = effects.length > 0 
                ? `<ul class="item-effects">${effects.map(e => `<li>${e}</li>`).join('')}</ul>`
                : '';
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${item.name}</div>
                        ${effectsList}
                    </div>
                    ${item.body_index_cost ? `<span class="item-rating">${item.body_index_cost}</span>` : ''}
                </div>
            `;
        }).join('\\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Bioware</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${bioItems}</div>
                </div>
            </div>
        `;
    }'''

content = content.replace(old_render_bio, new_render_bio)

# Write the fixed file
with open('www/character-sheet-renderer.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Updated hasCyberware() detection method")
print("✓ Updated hasBioware() detection method")
print("✓ Updated renderCyberware() to use pre-grouped array")
print("✓ Updated renderBioware() to use pre-grouped array")
print("\nAll 4 methods now use the pre-grouped cyberware/bioware arrays from backend")

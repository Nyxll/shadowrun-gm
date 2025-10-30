#!/usr/bin/env python3
"""
Fix the corrupted character-sheet-renderer.js file
Rebuilds it with proper cyberware/bioware rendering using pre-grouped arrays
"""

# Read the backup file to get the good parts
with open('www/character-sheet-renderer-backup.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where renderCyberware starts (the corrupted part)
cyber_start = content.find('    renderCyberware() {')
if cyber_start == -1:
    print("Could not find renderCyberware function")
    exit(1)

# Find where renderWeapons starts (after bioware)
weapons_start = content.find('    renderWeapons() {')
if weapons_start == -1:
    print("Could not find renderWeapons function")
    exit(1)

# Take everything before renderCyberware
good_start = content[:cyber_start]

# Take everything from renderWeapons onward
good_end = content[weapons_start:]

# Create the fixed renderCyberware and renderBioware functions
fixed_cyber_bio = '''    renderCyberware() {
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
                    ${item.essence_cost ? `<span class="item-rating">${item.essence_cost} ESS</span>` : ''}
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
    }
    
    renderBioware() {
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
                    ${item.body_index_cost ? `<span class="item-rating">${item.body_index_cost} B.I.</span>` : ''}
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
    }
    
'''

# Combine the parts
fixed_content = good_start + fixed_cyber_bio + good_end

# Write the fixed file
with open('www/character-sheet-renderer.js', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✓ Fixed character-sheet-renderer.js")
print("✓ Cyberware now uses pre-grouped 'cyberware' array from backend")
print("✓ Bioware now uses pre-grouped 'bioware' array from backend")

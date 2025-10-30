#!/usr/bin/env python3
"""
Rebuild ONLY the renderCyberware and renderBioware functions - FIXED VERSION
"""
import re

# Read the current file
with open('www/character-sheet-renderer.js', 'r', encoding='utf-8') as f:
    content = f.read()

# The clean renderCyberware function - use raw string to avoid escaping issues
clean_cyberware = r'''    renderCyberware() {
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
        }).join('');
        
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

# The clean renderBioware function - use raw string to avoid escaping issues
clean_bioware = r'''    renderBioware() {
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
        }).join('');
        
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

# Find and replace renderCyberware - match from start to renderBioware
cyber_pattern = r'    renderCyberware\(\) \{.*?(?=    renderBioware\(\) \{)'
content = re.sub(cyber_pattern, clean_cyberware + '\n    \n', content, flags=re.DOTALL)

# Find and replace renderBioware - match from start to renderWeapons
bio_pattern = r'    renderBioware\(\) \{.*?(?=    renderWeapons\(\) \{)'
content = re.sub(bio_pattern, clean_bioware + '\n    \n', content, flags=re.DOTALL)

# Write the fixed file
with open('www/character-sheet-renderer.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Rebuilt renderCyberware() and renderBioware() functions")
print("✓ Both now use pre-grouped arrays from backend")
print("✓ Fixed escaping issues")

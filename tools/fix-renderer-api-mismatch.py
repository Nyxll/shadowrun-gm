#!/usr/bin/env python3
"""
Fix character-sheet-renderer.js to match actual API response structure
"""

# Read the current renderer
with open('www/character-sheet-renderer.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix cyberware rendering - API returns 'source' not 'name', essence_cost in modifier_data
old_cyber = '''    renderCyberware() {
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
        }).join('\\n');'''

new_cyber = '''    renderCyberware() {
        // Use pre-grouped cyberware array from backend
        const cyberware = this.characterData.cyberware || [];
        
        const cyberItems = cyberware.map(item => {
            // API returns 'source' as the name
            const name = item.source || item.name || 'Unknown Cyberware';
            
            // Essence cost is in modifier_data
            const essenceCost = item.modifier_data?.essence_cost || item.essence_cost;
            
            // Format effects as bullet list (if present)
            const effects = item.effects || [];
            const effectsList = effects.length > 0 
                ? `<ul class="item-effects">${effects.map(e => `<li>${e}</li>`).join('')}</ul>`
                : '';
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${name}</div>
                        ${effectsList}
                    </div>
                    ${essenceCost ? `<span class="item-rating">${essenceCost} Essence</span>` : ''}
                </div>
            `;
        }).join('\\n');'''

content = content.replace(old_cyber, new_cyber)

# Fix bioware rendering
old_bio = '''    renderBioware() {
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
        }).join('\\n');'''

new_bio = '''    renderBioware() {
        // Use pre-grouped bioware array from backend
        const bioware = this.characterData.bioware || [];
        
        const bioItems = bioware.map(item => {
            // API returns 'source' as the name
            const name = item.source || item.name || 'Unknown Bioware';
            
            // Body index cost is in modifier_data
            const bodyIndexCost = item.modifier_data?.body_index_cost || item.body_index_cost;
            
            // Format effects as bullet list (if present)
            const effects = item.effects || [];
            const effectsList = effects.length > 0 
                ? `<ul class="item-effects">${effects.map(e => `<li>${e}</li>`).join('')}</ul>`
                : '';
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${name}</div>
                        ${effectsList}
                    </div>
                    ${bodyIndexCost ? `<span class="item-rating">${bodyIndexCost} BI</span>` : ''}
                </div>
            `;
        }).join('\\n');'''

content = content.replace(old_bio, new_bio)

# Fix contacts rendering - API returns archetype, loyalty, connection
old_contacts = '''    renderContacts() {
        const contacts = this.characterData.contacts || [];
        
        const contactItems = contacts.map(contact => {
            let details = [];
            if (contact.role) details.push(contact.role);
            if (contact.level) details.push(`Level ${contact.level}`);
            if (contact.notes) details.push(contact.notes);
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${contact.name}</div>
                        ${details.length > 0 ? `<div class="item-details">${details.join(' • ')}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('\\n');'''

new_contacts = '''    renderContacts() {
        const contacts = this.characterData.contacts || [];
        
        const contactItems = contacts.map(contact => {
            let details = [];
            
            // API returns archetype, loyalty, connection
            if (contact.archetype) details.push(contact.archetype);
            if (contact.loyalty !== undefined) details.push(`Loyalty ${contact.loyalty}`);
            if (contact.connection !== undefined) details.push(`Connection ${contact.connection}`);
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${contact.name}</div>
                        ${details.length > 0 ? `<div class="item-details">${details.join(' • ')}</div>` : ''}
                        ${contact.notes ? `<div class="item-details">${contact.notes}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('\\n');'''

content = content.replace(old_contacts, new_contacts)

# Fix vehicles - parse notes field for stats
old_vehicles = '''    renderVehicles() {
        const vehicles = this.characterData.vehicles || [];
        
        const vehicleItems = vehicles.map(vehicle => {
            let details = [];
            if (vehicle.vehicle_type) details.push(vehicle.vehicle_type);
            if (vehicle.handling) details.push(`Handling: ${vehicle.handling}`);
            if (vehicle.speed) details.push(`Speed: ${vehicle.speed}`);
            if (vehicle.body) details.push(`Body: ${vehicle.body}`);
            if (vehicle.armor) details.push(`Armor: ${vehicle.armor}`);
            if (vehicle.signature) details.push(`Signature: ${vehicle.signature}`);
            if (vehicle.pilot) details.push(`Pilot: ${vehicle.pilot}`);
            
            // Extract modifications description from JSONB object
            let modsText = '';
            if (vehicle.modifications) {
                if (typeof vehicle.modifications === 'object' && vehicle.modifications.description) {
                    modsText = vehicle.modifications.description;
                } else if (typeof vehicle.modifications === 'string') {
                    modsText = vehicle.modifications;
                }
            }
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${vehicle.vehicle_name}</div>
                        <div class="item-details">${details.join(' • ')}</div>
                        ${modsText ? `<div class="item-details">Modifications: ${modsText}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('\\n');'''

new_vehicles = '''    renderVehicles() {
        const vehicles = this.characterData.vehicles || [];
        
        const vehicleItems = vehicles.map(vehicle => {
            // Parse notes field which contains all the stats
            const notes = vehicle.notes || '';
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${vehicle.vehicle_name}</div>
                        ${notes ? `<div class="item-details">${notes.replace(/\\n/g, '<br>')}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('\\n');'''

content = content.replace(old_vehicles, new_vehicles)

# Write the fixed version
with open('www/character-sheet-renderer.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed character-sheet-renderer.js to match API response structure")
print("   - Cyberware: now reads 'source' field and modifier_data.essence_cost")
print("   - Bioware: now reads 'source' field and modifier_data.body_index_cost")
print("   - Contacts: now reads archetype, loyalty, connection fields")
print("   - Vehicles: now displays notes field with all stats")

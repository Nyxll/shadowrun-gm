// Character Sheet Renderer
// Renders comprehensive Shadowrun 2E character sheets with ALL data

class CharacterSheetRenderer {
    constructor() {
        this.characterData = null;
    }

    render(characterData) {
        this.characterData = characterData;
        
        // Update header
        document.getElementById('sheet-character-name').textContent = 
            characterData.street_name || characterData.name;
        document.getElementById('sheet-character-subtitle').textContent = 
            `${characterData.metatype || 'Unknown'} ${characterData.archetype || 'Character'}`;
        
        // Build sections
        const sections = [];
        
        sections.push(this.renderBasicInfo());
        sections.push(this.renderPhysicalDescription());
        sections.push(this.renderAttributes());
        sections.push(this.renderDerivedStats());
        sections.push(this.renderPools());
        
        // Edges and Flaws
        if (this.hasEdgesFlaws()) {
            sections.push(this.renderEdgesFlaws());
        }
        
        // Skills grouped by type
        sections.push(this.renderSkills());
        
        // Cyberware and Bioware
        if (this.hasCyberware()) {
            sections.push(this.renderCyberware());
        }
        
        if (this.hasBioware()) {
            sections.push(this.renderBioware());
        }
        
        // Gear sections
        if (this.hasWeapons()) {
            sections.push(this.renderWeapons());
        }
        
        if (this.hasArmor()) {
            sections.push(this.renderArmor());
        }
        
        if (this.hasEquipment()) {
            sections.push(this.renderEquipment());
        }
        
        // Vehicles
        if (this.hasVehicles()) {
            sections.push(this.renderVehicles());
        }
        
        // Cyberdecks
        if (this.hasCyberdecks()) {
            sections.push(this.renderCyberdecks());
        }
        
        // Magic
        if (this.hasMagic()) {
            sections.push(this.renderMagic());
        }
        
        // Bound Spirits
        if (this.hasSpirits()) {
            sections.push(this.renderSpirits());
        }
        
        // Contacts
        if (this.hasContacts()) {
            sections.push(this.renderContacts());
        }
        
        // Background
        if (this.characterData.background) {
            sections.push(this.renderBackground());
        }
        
        // Notes
        sections.push(this.renderNotes());
        
        // Combine all sections
        return sections.join('\n');
    }
    
    renderBasicInfo() {
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Basic Information</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="stat-grid">
                        ${this.statBox('Name', this.characterData.name || 'Unknown')}
                        ${this.statBox('Street Name', this.characterData.street_name || 'N/A')}
                        ${this.statBox('Archetype', this.characterData.archetype || 'Unknown')}
                        ${this.statBox('Metatype', this.characterData.metatype || 'Human')}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderPhysicalDescription() {
        const char = this.characterData;
        
        // Only show if we have at least some physical data
        if (!char.sex && !char.age && !char.height && !char.weight && !char.hair && !char.eyes && !char.skin) {
            return '';
        }
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Physical Description</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="stat-grid">
                        ${char.sex ? this.statBox('Sex', char.sex) : ''}
                        ${char.age ? this.statBox('Age', char.age) : ''}
                        ${char.height ? this.statBox('Height', char.height) : ''}
                        ${char.weight ? this.statBox('Weight', char.weight) : ''}
                        ${char.hair ? this.statBox('Hair', char.hair) : ''}
                        ${char.eyes ? this.statBox('Eyes', char.eyes) : ''}
                        ${char.skin ? this.statBox('Skin', char.skin) : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderAttributes() {
        const char = this.characterData;
        
        // Helper to format attribute - ALWAYS show base value
        // API returns base_X and current_X at top level
        const formatAttr = (attrName) => {
            const current = char[`current_${attrName}`];
            const base = char[`base_${attrName}`];
            
            // Always show base value if it exists (even if 0)
            if (base !== undefined && base !== null) {
                return `${current !== undefined && current !== null ? current : base} (${base})`;
            }
            // Return current value, or 1 if undefined/null (but NOT if 0)
            return current !== undefined && current !== null ? current : 1;
        };
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Attributes</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="stat-grid">
                        ${this.statBox('Body', formatAttr('body'))}
                        ${this.statBox('Quickness', formatAttr('quickness'))}
                        ${this.statBox('Strength', formatAttr('strength'))}
                        ${this.statBox('Charisma', formatAttr('charisma'))}
                        ${this.statBox('Intelligence', formatAttr('intelligence'))}
                        ${this.statBox('Willpower', formatAttr('willpower'))}
                        ${this.statBox('Essence', formatAttr('essence'))}
                        ${char.current_magic ? this.statBox('Magic', formatAttr('magic')) : ''}
                        ${this.statBox('Reaction', formatAttr('reaction'))}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderDerivedStats() {
        const char = this.characterData;
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Resources & Status</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="stat-grid">
                        ${this.statBox('Nuyen', this.formatNumber(char.nuyen || 0) + '¥')}
                        ${this.statBox('Karma Pool', char.karma_pool || 0)}
                        ${this.statBox('Total Karma', char.karma_total || 0)}
                        ${char.karma_available ? this.statBox('Karma Available', char.karma_available) : ''}
                        ${char.lifestyle ? this.statBox('Lifestyle', this.formatLifestyle(char)) : ''}
                        ${char.essence_hole ? this.statBox('Essence Hole', char.essence_hole) : ''}
                        ${char.body_index_current ? this.statBox('Body Index', `${char.body_index_current}/${char.body_index_max}`) : ''}
                        ${this.statBox('Initiative', char.initiative || 'N/A')}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderPools() {
        const char = this.characterData;
        const pools = [];
        
        // Combat Pool
        if (char.combat_pool !== undefined) {
            pools.push(this.statBox('Combat Pool', char.combat_pool));
        }
        
        // Magic Pool (for magical characters)
        if (char.magic_pool) {
            pools.push(this.statBox('Magic Pool', char.magic_pool));
        }
        
        // Task Pool (for deckers)
        if (char.task_pool) {
            pools.push(this.statBox('Task Pool', char.task_pool));
        }
        
        // Hacking Pool (for deckers)
        if (char.hacking_pool) {
            pools.push(this.statBox('Hacking Pool', char.hacking_pool));
        }
        
        if (pools.length === 0) {
            return '';
        }
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Dice Pools</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="stat-grid">
                        ${pools.join('\n')}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderEdgesFlaws() {
        const edges = this.characterData.edges || [];
        const flaws = this.characterData.flaws || [];
        
        let content = '';
        
        if (edges.length > 0) {
            const edgeItems = edges.map(edge => `
                <div class="list-item">
                    <div>
                        <div class="item-name">${edge.name}</div>
                        ${edge.description ? `<div class="item-details">${edge.description}</div>` : ''}
                    </div>
                </div>
            `).join('\n');
            
            content += `
                <div class="subsection">
                    <h4>Edges</h4>
                    <div class="item-list">${edgeItems}</div>
                </div>
            `;
        }
        
        if (flaws.length > 0) {
            const flawItems = flaws.map(flaw => `
                <div class="list-item">
                    <div>
                        <div class="item-name">${flaw.name}</div>
                        ${flaw.description ? `<div class="item-details">${flaw.description}</div>` : ''}
                    </div>
                </div>
            `).join('\n');
            
            content += `
                <div class="subsection">
                    <h4>Flaws</h4>
                    <div class="item-list">${flawItems}</div>
                </div>
            `;
        }
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Edges & Flaws</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    ${content}
                </div>
            </div>
        `;
    }
    
    renderSkills() {
        // CRUD API returns flat array of skills
        const allSkills = this.characterData.skills || [];
        
        // Group by skill_type
        const activeSkills = allSkills.filter(s => s.skill_type === 'active' || !s.skill_type);
        const knowledgeSkills = allSkills.filter(s => s.skill_type === 'knowledge');
        const languageSkills = allSkills.filter(s => s.skill_type === 'language');
        
        let content = '';
        
        // Active Skills
        if (activeSkills.length > 0) {
            const skillItems = activeSkills.map(skill => {
                // Format as "current (base)" - always show both
                const current = skill.current_rating !== undefined ? skill.current_rating : skill.rating;
                const base = skill.base_rating;
                const ratingDisplay = base !== undefined ? `${current} (${base})` : current;
                
                return `
                    <div class="skill-item">
                        <span class="skill-name">${skill.skill_name}</span>
                        <span class="skill-rating">${ratingDisplay}</span>
                        ${skill.specialization ? `<span class="skill-bonus">(${skill.specialization})</span>` : ''}
                    </div>
                `;
            }).join('\n');
            
            content += `
                <div class="subsection">
                    <h4>Active Skills</h4>
                    <div class="skill-grid">${skillItems}</div>
                </div>
            `;
        }
        
        // Knowledge Skills
        if (knowledgeSkills.length > 0) {
            const skillItems = knowledgeSkills.map(skill => {
                // Format as "current (base)" - always show both
                const current = skill.current_rating !== undefined ? skill.current_rating : skill.rating;
                const base = skill.base_rating;
                const ratingDisplay = base !== undefined ? `${current} (${base})` : current;
                
                return `
                    <div class="skill-item">
                        <span class="skill-name">${skill.skill_name}</span>
                        <span class="skill-rating">${ratingDisplay}</span>
                        ${skill.specialization ? `<span class="skill-bonus">(${skill.specialization})</span>` : ''}
                    </div>
                `;
            }).join('\n');
            
            content += `
                <div class="subsection">
                    <h4>Knowledge Skills</h4>
                    <div class="skill-grid">${skillItems}</div>
                </div>
            `;
        }
        
        // Language Skills
        if (languageSkills.length > 0) {
            const skillItems = languageSkills.map(skill => {
                // Format as "current (base)" - always show both
                const current = skill.current_rating !== undefined ? skill.current_rating : skill.rating;
                const base = skill.base_rating;
                const ratingDisplay = base !== undefined ? `${current} (${base})` : current;
                
                return `
                    <div class="skill-item">
                        <span class="skill-name">${skill.skill_name}</span>
                        <span class="skill-rating">${ratingDisplay}</span>
                        ${skill.specialization ? `<span class="skill-bonus">(${skill.specialization})</span>` : ''}
                    </div>
                `;
            }).join('\n');
            
            content += `
                <div class="subsection">
                    <h4>Language Skills</h4>
                    <div class="skill-grid">${skillItems}</div>
                </div>
            `;
        }
        
        if (!content) {
            content = '<div class="empty-section">No skills recorded</div>';
        }
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Skills</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    ${content}
                </div>
            </div>
        `;
    }
    
    renderCyberware() {
        // CRCDDAPI APturns menifidiss array-  ilte- f ricylerwtr r cyberware
        const modifiifs = this.characterData.modifiers || [];
        monst codifiers = modifiers.filter(m => m.source_type === 'cyberware');
        const cyberware = modifiers.filter(m => m.source_type === 'cyberware');
        
        const cExteIctems = cybfrom modifier_deta JSONB
            conrtwmodDaaap= ieem.modifier_data || {};m => {
            // Extract effecfodDatarspooial_abilidieifier_data JSONB
            
            // Format effects as bullet list
            const modData = item.modifier_data || {};
            const aspecia || []ffect;ffect
                : '';
            
            / Bid details
            letdetails=[];
           if (item.modifier_value) {
                details.push(`${item.target_name}${item.modifier_value > 0 ? + : ''}${item.modifier_value}`)
            }
            // Format effects as bullet list
            const effectsList = effects.length > 0 
                ? effects.map(effect => `<li>${effect}</li>`).join('')
                : '';
            .source}</div>
                        ${detailslegth > 0 ? `<div clss="ite-details">${dtails.join(' • ')` : ''}
               // Build ${effectsListd?e`<ultclass="item-effects">ails}</ul>` : ''
            let details = [];
            if (item.mmodDadaier_value) {modDaa
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
        }).join('\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
           CR D API   tu<ns ms ifae"section --tiltei ftre"iow>rbware</span>
              modif e sspan class="section-tomodifiers || [];
        const ggle"re = modifiers.filter(m => m.sou>ce_typ▼<===p'bioware')>
                </div>
                <div class="section-content">
               Ext  c<div clas fromsmodifier_dat= JSONB
            con"timodDaia =sitem.modif"er_da$a || {};{cyberItems}</div>
                </div>modData.special_abilis || [];
            
            // Forat s abulletlist
            </div>
        `;effcteffct
                : '';
            
            / Bild details
            let details = [];
            if (item.modifier_vaue) {
     }details.push(`${item.target_name}:${item.modifier_value > 0 ? '+' }${item.modifier_value}`)
            }
    
    renderBioware() {
        // CRUD API returns modifiers array - filter for bioware
        const modifiers = this.characterData.modifiers || [];
        const bioware = modifiers.filter(m => m.sourcesource}</div>
                        ${details.le_gth > 0 ? `<div cltss="itey-dptails">${details.join(' • ')e === '` : ''}bioware');
         ? `<ul class="item-effects">${effectsList</ul>` : ''}
        const bioItems = bioware.map(item => {
            // ExtractfodDataects from modifier_data JSONBmodDaa
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
        }).join('\n');
        
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
    
    renderWeapons() {
        // CRUD API returns gear array - filter for weapons
        const gear = this.characterData.gear || [];
        const weapons = gear.filter(g => g.gear_type === 'weapon');
        
        const weaponItems = weapons.map(weapon => {
            let details = [];
            if (weapon.damage) details.push(`Damage: ${weapon.damage}`);
            if (weapon.conceal) details.push(`Conceal: ${weapon.conceal}`);
            if (weapon.ammo_capacity) details.push(`Ammo: ${weapon.ammo_capacity}`);
            
            // Add modifications if present
            const mods = weapon.modifications || {};
            if (Object.keys(mods).length > 0) {
                const modList = Object.entries(mods).map(([key, val]) => 
                    val === true ? key : `${key}: ${val}`
                ).join(', ');
                details.push(`Mods: ${modList}`);
            }
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${weapon.gear_name}</div>
                        <div class="item-details">${details.join(' • ')}</div>
                        ${weapon.notes ? `<div class="item-details">${weapon.notes}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Weapons</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${weaponItems}</div>
                </div>
            </div>
        `;
    }
    
    renderArmor() {
        // CRUD API returns gear array - filter for armor
        const gear = this.characterData.gear || [];
        const armor = gear.filter(g => g.gear_type === 'armor');
        
        const armorItems = armor.map(item => {
            let details = [];
            if (item.ballistic_rating !== undefined || item.impact_rating !== undefined) {
                details.push(`Rating: ${item.ballistic_rating || 0}/${item.impact_rating || 0}`);
            }
            if (item.conceal) details.push(`Conceal: ${item.conceal}`);
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${item.gear_name}</div>
                        <div class="item-details">${details.join(' • ')}</div>
                        ${item.notes ? `<div class="item-details">${item.notes}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Armor</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${armorItems}</div>
                </div>
            </div>
        `;
    }
    
    renderEquipment() {
        // CRUD API returns gear array - filter for equipment
        const gear = this.characterData.gear || [];
        const equipment = gear.filter(g => g.gear_type === 'equipment');
        
        const equipItems = equipment.map(item => `
            <div class="list-item">
                <div>
                    <div class="item-name">${item.gear_name}</div>
                    ${item.notes ? `<div class="item-details">${item.notes}</div>` : ''}
                </div>
                ${item.quantity > 1 ? `<span class="item-rating">×${item.quantity}</span>` : ''}
            </div>
        `).join('\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Equipment</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${equipItems}</div>
                </div>
            </div>
        `;
    }
    
    renderVehicles() {
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
        }).join('\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Vehicles & Drones</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${vehicleItems}</div>
                </div>
            </div>
        `;
    }
    
    renderMagic() {
        const spells = this.characterData.spells || [];
        const foci = this.characterData.foci || [];
        const totem = this.characterData.totem;
        const magic = this.characterData.current_magic;
        
        // Don't show section if character has no magic
        if (!magic && spells.length === 0 && foci.length === 0) {
            return '';
        }
        
        let content = '';
        
        // Totem information
        if (totem) {
            // Get totem info from tradition field if available
            const tradition = this.characterData.tradition || '';
            
            content += `
                <div class="subsection">
                    <h4>Totem: ${totem}</h4>
                    ${tradition ? `<div class="item-details">${tradition}</div>` : ''}
                </div>
            `;
        }
        
        // Spells grouped by category
        if (spells.length > 0) {
            // Group spells by category
            const spellsByCategory = {};
            spells.forEach(spell => {
                const category = spell.spell_category || 'Other';
                if (!spellsByCategory[category]) {
                    spellsByCategory[category] = [];
                }
                spellsByCategory[category].push(spell);
            });
            
            // Render each category
            Object.keys(spellsByCategory).sort().forEach(category => {
                const categorySpells = spellsByCategory[category];
                const spellItems = categorySpells.map(spell => {
                    let details = [];
                    
                    // Learned Force (MOST IMPORTANT - show first)
                    if (spell.learned_force) {
                        details.push(`<strong>Force:</strong> ${spell.learned_force}`);
                    }
                    
                    // Type (Mana/Physical)
                    if (spell.spell_type) {
                        details.push(`<strong>Type:</strong> ${spell.spell_type}`);
                    }
                    
                    // Target
                    if (spell.target_type) {
                        details.push(`<strong>Target:</strong> ${spell.target_type}`);
                    }
                    
                    // Duration
                    if (spell.duration) {
                        details.push(`<strong>Duration:</strong> ${spell.duration}`);
                    }
                    
                    // Drain modifier
                    if (spell.drain_modifier !== undefined && spell.drain_modifier !== null) {
                        const drainText = spell.drain_modifier > 0 
                            ? `+${spell.drain_modifier}` 
                            : spell.drain_modifier;
                        details.push(`<strong>Drain:</strong> (Force ÷ 2)${drainText}`);
                    } else {
                        details.push(`<strong>Drain:</strong> (Force ÷ 2)`);
                    }
                    
                    return `
                        <div class="spell-item">
                            <div class="spell-name">${spell.spell_name}${spell.learned_force ? ` (Force ${spell.learned_force})` : ''}</div>
                            ${details.length > 0 ? `<div class="spell-details">${details.join(' • ')}</div>` : ''}
                            ${spell.description ? `<div class="spell-description">${spell.description}</div>` : ''}
                            ${spell.notes ? `<div class="spell-details"><em>${spell.notes}</em></div>` : ''}
                        </div>
                    `;
                }).join('\n');
                
                content += `
                    <div class="subsection">
                        <h4>${category.charAt(0).toUpperCase() + category.slice(1)} Spells</h4>
                        <div class="spell-list">${spellItems}</div>
                    </div>
                `;
            });
        }
        
        // Foci
        if (foci.length > 0) {
            const fociItems = foci.map(focus => {
                let details = [];
                details.push(`Force ${focus.force}`);
                
                if (focus.focus_type === 'spell') {
                    if (focus.specific_spell) {
                        details.push(`Specific: ${focus.specific_spell}`);
                    } else if (focus.spell_category) {
                        details.push(`Category: ${focus.spell_category}`);
                    }
                } else {
                    details.push(focus.focus_type);
                }
                
                if (focus.bonus_dice) details.push(`+${focus.bonus_dice} dice`);
                if (focus.tn_modifier) details.push(`${focus.tn_modifier} TN`);
                if (!focus.bonded) details.push('(Not bonded)');
                
                return `
                    <div class="list-item">
                        <div>
                            <div class="item-name">${focus.focus_name}</div>
                            <div class="item-details">${details.join(' • ')}</div>
                            ${focus.description ? `<div class="item-details">${focus.description}</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('\n');
            
            content += `
                <div class="subsection">
                    <h4>Magical Foci</h4>
                    <div class="item-list">${fociItems}</div>
                </div>
            `;
        }
        
        if (!content) {
            content = '<div class="empty-section">No spells or foci</div>';
        }
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Magic & Spellcasting</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    ${content}
                </div>
            </div>
        `;
    }
    
    renderSpirits() {
        const spirits = this.characterData.spirits || [];
        
        const spiritItems = spirits.map(spirit => {
            let details = [];
            
            // Spirit type (formatted nicely)
            if (spirit.spirit_type) {
                const spiritType = String(spirit.spirit_type).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                details.push(spiritType);
            }
            
            // Force
            details.push(`Force ${spirit.force}`);
            
            // Services
            if (spirit.services === -1) {
                details.push('Permanent');
            } else if (spirit.services > 0) {
                details.push(`${spirit.services} service${spirit.services !== 1 ? 's' : ''}`);
            }
            
            // Special abilities
            const abilities = spirit.special_abilities || [];
            if (abilities.length > 0) {
                const abilitiesList = abilities.map(ability => `<li>${ability}</li>`).join('');
                
                return `
                    <div class="list-item">
                        <div>
                            <div class="item-name">${spirit.spirit_name}</div>
                            <div class="item-details">${details.join(' • ')}</div>
                            <ul class="item-effects">${abilitiesList}</ul>
                            ${spirit.notes ? `<div class="item-details">${spirit.notes}</div>` : ''}
                        </div>
                    </div>
                `;
            }
            
            return `
                <div class="list-item">
                    <div>
                        <div class="item-name">${spirit.spirit_name}</div>
                        <div class="item-details">${details.join(' • ')}</div>
                        ${spirit.notes ? `<div class="item-details">${spirit.notes}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Bound Spirits</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${spiritItems}</div>
                </div>
            </div>
        `;
    }
    
    renderContacts() {
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
        }).join('\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Contacts</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${contactItems}</div>
                </div>
            </div>
        `;
    }
    
    renderBackground() {
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Background</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="notes-content">${this.escapeHtml(this.characterData.background)}</div>
                </div>
            </div>
        `;
    }
    
    renderNotes() {
        const notes = this.characterData.notes || 'No additional notes.';
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Notes</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="notes-content">${this.escapeHtml(notes)}</div>
                </div>
            </div>
        `;
    }
    
    // Helper methods
    statBox(label, value, detail = '') {
        return `
            <div class="stat-box">
                <div class="stat-label">${label}</div>
                <div class="stat-value">${value}</div>
                ${detail ? `<div class="stat-detail">${detail}</div>` : ''}
            </div>
        `;
    }
    
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
    
    formatLifestyle(char) {
        let lifestyle = char.lifestyle || 'Unknown';
        if (char.lifestyle_cost) {
            lifestyle += ` (${this.formatNumber(char.lifestyle_cost)}¥/month`;
            if (char.lifestyle_months_prepaid) {
                lifestyle += `, ${char.lifestyle_months_prepaid} months prepaid`;
            }
            lifestyle += ')';
        }
        return lifestyle;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Detection methods
    hasEdgesFlaws() {
        const edgesFlaws = this.characterData.edges_flaws || [];
        return edgesFlaws.length > 0;
    }
    
    hasCyberware() {
        const modifiers = this.characterData.modifiers || [];
        return modifiers.some(m => m.source_type === 'cyberware');
    }
    
    hasBioware() {
        const modifiers = this.characterData.modifiers || [];
        return modifiers.some(m => m.source_type === 'bioware');
    }
    
    hasWeapons() {
        const gear = this.characterData.gear || [];
        return gear.some(g => g.gear_type === 'weapon');
    }
    
    hasArmor() {
        const gear = this.characterData.gear || [];
        return gear.some(g => g.gear_type === 'armor');
    }
    
    hasEquipment() {
        const gear = this.characterData.gear || [];
        return gear.some(g => g.gear_type === 'equipment');
    }
    
    hasVehicles() {
        const vehicles = this.characterData.vehicles || [];
        return vehicles.length > 0;
    }
    
    hasMagic() {
        const spells = this.characterData.spells || [];
        return spells.length > 0;
    }
    
    hasSpirits() {
        const spirits = this.characterData.spirits || [];
        return spirits.length > 0;
    }
    
    hasContacts() {
        const contacts = this.characterData.contacts || [];
        return contacts.length > 0;
    }
    
    hasCyberdecks() {
        const cyberdecks = this.characterData.cyberdecks || [];
        return cyberdecks.length > 0;
    }
    
    renderCyberdecks() {
        const cyberdecks = this.characterData.cyberdecks || [];
        
        const deckItems = cyberdecks.map(deck => {
            let details = [];
            
            // Basic stats
            if (deck.mpcp) details.push(`MPCP ${deck.mpcp}`);
            if (deck.hardening) details.push(`Hardening ${deck.hardening}`);
            if (deck.memory) details.push(`${deck.memory} MP`);
            if (deck.storage) details.push(`Storage: ${deck.storage} MP`);
            if (deck.io_speed) details.push(`I/O: ${deck.io_speed}`);
            if (deck.response_increase) details.push(`Response +${deck.response_increase}`);
            
            // Persona programs
            const persona = deck.persona_programs || {};
            const personaList = Object.entries(persona)
                .filter(([key]) => !key.includes('_effective')) // Skip effective ratings
                .map(([prog, rating]) => {
                    const effective = persona[`${prog}_effective`];
                    return effective && effective !== rating 
                        ? `${prog.charAt(0).toUpperCase() + prog.slice(1)}: ${rating} (${effective})`
                        : `${prog.charAt(0).toUpperCase() + prog.slice(1)}: ${rating}`;
                });
            
            // Utilities
            const utilities = deck.utilities || {};
            const utilityList = Object.entries(utilities).map(([util, data]) => {
                const utilName = String(util).replace(/_/g, ' ');
                if (typeof data === 'object') {
                    const parts = [];
                    if (data.rating) parts.push(`Rating ${data.rating}`);
                    if (data.dice) parts.push(`${data.dice} dice`);
                    if (data.persistent) parts.push('Persistent');
                    return `${utilName}: ${parts.join(', ')}`;
                }
                return `${utilName}: ${data}`;
            });
            
            // AI companions
            const aiList = deck.ai_companions || [];
            
             <div clam>
                        ${deck.notes ? `<div class="item-details">${deck.notes}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('\n');
        
        return `
            <div class="sheet-section">
                <div class="section-header">
                    <span class="section-title">Cyberdecks</span>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content">
                    <div class="item-list">${deckItems}</div>
                </div>
            </div>
        `;
    }
}

// Make available globally
window.CharacterSheetRenderer = CharacterSheetRenderer;

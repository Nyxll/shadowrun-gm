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

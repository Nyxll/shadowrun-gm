import React from 'react';
import type { Character } from '../types';
import { Panel } from './common/Panel';
import { Button } from './common/Button';

interface CharacterSheetModalProps {
  character: Character;
  onClose: () => void;
}

const StatBox: React.FC<{ label: string; value: string | number }> = ({ label, value }) => (
  <div className="stat-box-compact">
    <div className="stat-label-compact">{label}</div>
    <div className="stat-value-compact">{value}</div>
  </div>
);

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
    <div className="compact-section">
        <h3 className="section-header-compact" style={{ fontFamily: "'Orbitron', sans-serif" }}>
            {title}
        </h3>
        {children}
    </div>
);

export const CharacterSheetModal: React.FC<CharacterSheetModalProps> = ({ character, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4 character-sheet-modal">
      <Panel className="w-full max-w-4xl h-[90vh] flex flex-col panel-compact">
        <div className="flex justify-between items-start pb-4 border-b border-cyan-500/30">
            <div>
                 <h2 className="text-3xl font-bold text-cyan-300 text-glow-primary tracking-widest" style={{ fontFamily: "'Orbitron', sans-serif" }}>{character.name}</h2>
                 <p className="text-cyan-400">{character.role}</p>
            </div>
            <Button onClick={onClose} variant="secondary">Close</Button>
        </div>
        
        <div className="flex-1 overflow-y-auto compact-padding -mr-4 pr-8 compact-scrollbar">
            <Section title="Attributes">
                <div className="stat-grid-compact">
                    {Object.entries(character.stats).map(([key, value]) => (
                        <StatBox key={key} label={key} value={value} />
                    ))}
                </div>
            </Section>

            <div className="two-column-compact">
                <div>
                    <Section title="Skills">
                        <ul>
                            {character.skills.map(skill => (
                                <li key={skill.name} className="skill-item-compact">
                                    <span className="skill-name">{skill.name}</span>
                                    <span className="skill-rating">{skill.rating}</span>
                                </li>
                            ))}
                        </ul>
                    </Section>
                </div>
                <div>
                    <Section title="Cyberware">
                        <ul>
                            {character.cyberware.map(ware => (
                                <li key={ware.name} className="cyberware-item-compact">
                                    <p className="cyberware-name">{ware.name}</p>
                                    <p className="cyberware-description">{ware.description}</p>
                                </li>
                            ))}
                        </ul>
                    </Section>
                    
                    <Section title="Gear">
                        <ul className="gear-list-compact">
                            {character.gear.map(item => (
                                <li key={item}>{item}</li>
                            ))}
                        </ul>
                    </Section>
                </div>
            </div>
        </div>
      </Panel>
    </div>
  );
};

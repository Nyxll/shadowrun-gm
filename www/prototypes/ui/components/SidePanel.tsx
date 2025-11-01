
import React, { useState } from 'react';
import { Panel } from './common/Panel';
import { Button } from './common/Button';
import type { Character, ToolCallLog } from '../types';
import { PREMADE_CHARACTERS } from '../constants';

interface SidePanelProps {
  activeCharacters: Character[];
  onAddCharacter: (name: string) => void;
  onRemoveCharacter: (name: string) => void;
  onViewSheet: (name: string) => void;
  onCreateScenario: () => void;
  toolCallLogs: ToolCallLog[];
  onClearLogs: () => void;
  isLoading: boolean;
  isScenarioSet: boolean;
  onTabChange: (tab: 'chat' | 'imageGen' | 'imageAnalyze') => void;
  selectedTab: 'chat' | 'imageGen' | 'imageAnalyze';
}

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-4">
        <h3 className="text-lg font-bold text-cyan-400 text-glow border-b-2 border-cyan-500/30 pb-1 mb-3 tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>
            {title}
        </h3>
        {children}
    </div>
);

const TabButton: React.FC<{ active: boolean; onClick: () => void; children: React.ReactNode }> = ({ active, onClick, children }) => (
    <button
        onClick={onClick}
        className={`flex-1 p-2 text-xs font-bold uppercase tracking-widest transition-colors ${active ? 'bg-cyan-500/80 text-gray-900' : 'bg-black/50 hover:bg-cyan-500/20'}`}
    >
        {children}
    </button>
);


export const SidePanel: React.FC<SidePanelProps> = ({
  activeCharacters,
  onAddCharacter,
  onRemoveCharacter,
  onViewSheet,
  onCreateScenario,
  toolCallLogs,
  onClearLogs,
  isLoading,
  isScenarioSet,
  onTabChange,
  selectedTab
}) => {
    const [selectedCharacter, setSelectedCharacter] = useState<string>(PREMADE_CHARACTERS[0]?.name || '');

    const handleAddClick = () => {
        if (selectedCharacter) {
            onAddCharacter(selectedCharacter);
        }
    };

    const handleViewClick = () => {
        if (selectedCharacter) {
            onViewSheet(selectedCharacter);
        }
    }

    return (
        <aside className="w-full md:w-1/3 lg:w-1/4 flex-shrink-0 hidden md:flex flex-col">
            <Panel className="flex-1 flex flex-col holographic-bg overflow-y-auto">
                <Section title="Main Display">
                    <div className="flex border border-cyan-700">
                        <TabButton active={selectedTab === 'chat'} onClick={() => onTabChange('chat')}>Chat</TabButton>
                        <TabButton active={selectedTab === 'imageGen'} onClick={() => onTabChange('imageGen')}>Image Gen</TabButton>
                        <TabButton active={selectedTab === 'imageAnalyze'} onClick={() => onTabChange('imageAnalyze')}>Analyze</TabButton>
                    </div>
                </Section>
                <Section title="Game Setup">
                    <Button onClick={onCreateScenario} disabled={isLoading || isScenarioSet} className="w-full">
                        {isLoading ? 'Generating...' : isScenarioSet ? 'Scenario Active' : 'Create Scenario'}
                    </Button>
                </Section>

                <Section title="Team Roster">
                    <ul className="space-y-2 mb-4">
                        {activeCharacters.map(char => (
                            <li key={char.name} className="flex items-center justify-between bg-black/40 p-2 border-l-2 border-cyan-500">
                                <div>
                                    <p className="font-bold text-cyan-300">{char.name}</p>
                                    <p className="text-xs text-cyan-500">{char.role}</p>
                                </div>
                                <button onClick={() => onRemoveCharacter(char.name)} className="text-red-500 hover:text-red-400 text-xs px-2">REMOVE</button>
                            </li>
                        ))}
                         {activeCharacters.length === 0 && <p className="text-sm text-cyan-200/50 italic">No active runners.</p>}
                    </ul>
                    <div className="flex flex-col gap-2">
                        <select
                            value={selectedCharacter}
                            onChange={(e) => setSelectedCharacter(e.target.value)}
                            className="bg-black/50 border border-cyan-700 text-cyan-300 p-2 focus:outline-none focus:ring-1 focus:ring-cyan-500 w-full"
                        >
                            {PREMADE_CHARACTERS.map(char => <option key={char.name} value={char.name}>{char.name} ({char.role})</option>)}
                        </select>
                        <div className="flex gap-2">
                            <Button onClick={handleAddClick} className="w-full" variant="secondary">Add Runner</Button>
                            <Button onClick={handleViewClick} className="w-full" variant="secondary">View Sheet</Button>
                        </div>
                    </div>
                </Section>
                 
                <Section title="Data Monitor">
                    <div className="h-40 bg-black/50 p-2 border border-cyan-900 overflow-y-auto text-xs font-mono">
                        <h4 className="text-cyan-400">Tool Call Log:</h4>
                        {toolCallLogs.length > 0 ? toolCallLogs.map(log => (
                             <div key={log.id} className="border-l border-cyan-600 pl-2 mb-1">
                                <p className="text-cyan-500">{log.toolName} ({log.type})</p>
                                <p className="text-cyan-600 truncate">{JSON.stringify(log.args)}</p>
                             </div>
                        )) : <p className="text-cyan-200/50 italic mt-2">Waiting for tool calls...</p>}
                    </div>
                    <Button onClick={onClearLogs} className="w-full mt-2" variant="secondary">Clear Log</Button>
                </Section>
            </Panel>
        </aside>
    );
};

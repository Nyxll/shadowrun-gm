
import React, { useState, useCallback, useEffect, useRef } from 'react';
import { GoogleGenAI } from "@google/genai";

import type { Character, Message, ToolCallLog } from './types';
import { PREMADE_CHARACTERS, MOCK_SCENARIO } from './constants';
import { generateScenario, generateImage, analyzeImage } from './services/geminiService';

import { Header } from './components/Header';
import { MainDisplay } from './components/MainDisplay';
import { SidePanel } from './components/SidePanel';
import { CharacterSheetModal } from './components/CharacterSheetModal';
import { StatusBar } from './components/StatusBar';

const App: React.FC = () => {
    const [activeCharacters, setActiveCharacters] = useState<Character[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [scenario, setScenario] = useState<string>('');
    const [isLoading, setIsLoading] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [toolCallLogs, setToolCallLogs] = useState<ToolCallLog[]>([]);

    const [selectedCharacterSheet, setSelectedCharacterSheet] = useState<Character | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const [selectedTab, setSelectedTab] = useState<'chat' | 'imageGen' | 'imageAnalyze'>('chat');

    const chatSession = useRef<any>(null); // Using `any` for Gemini Chat object

    useEffect(() => {
        setMessages([{
            role: 'system',
            text: 'SYSTEM OFFLINE. Add characters and generate a scenario to begin.'
        }]);
    }, []);

    const handleAddCharacter = (characterName: string) => {
        if (activeCharacters.find(c => c.name === characterName)) return;
        const character = PREMADE_CHARACTERS.find(c => c.name === characterName);
        if (character) {
            setActiveCharacters(prev => [...prev, character]);
            logSystemMessage(`Character [${characterName}] added to the team.`);
        }
    };

    const handleRemoveCharacter = (characterName: string) => {
        setActiveCharacters(prev => prev.filter(c => c.name !== characterName));
        logSystemMessage(`Character [${characterName}] removed from the team.`);
    };

    const handleViewSheet = (characterName: string) => {
        const character = PREMADE_CHARACTERS.find(c => c.name === characterName);
        if (character) {
            setSelectedCharacterSheet(character);
            setIsModalOpen(true);
        }
    };
    
    const logSystemMessage = (text: string) => {
        setMessages(prev => [...prev, { role: 'system', text }]);
    };

    const handleCreateScenario = useCallback(async () => {
        if (activeCharacters.length === 0) {
            logSystemMessage('Error: Add at least one character before generating a scenario.');
            return;
        }
        setIsLoading(true);
        logSystemMessage('Generating scenario with Gemini... This may take a moment.');
        try {
            const newScenario = await generateScenario(activeCharacters);
            setScenario(newScenario);
            setMessages([{ role: 'system', text: `SCENARIO LOADED: ${newScenario}` }]);
            
            // Initialize chat
            const ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });
            const systemInstruction = `You are a creative and descriptive Game Master for a Shadowrun tabletop roleplaying game. The current scenario is: '${newScenario}'. The players are: ${activeCharacters.map(c => c.name).join(', ')}. Your role is to describe the world, react to player actions, control non-player characters, and create an engaging cyberpunk narrative. Be descriptive and keep responses concise but immersive.`;

            chatSession.current = ai.chats.create({
              model: 'gemini-2.5-pro',
              config: { systemInstruction },
            });

            const initialMessage = await chatSession.current.sendMessage({ message: "Set the scene. Describe our immediate surroundings and what's happening." });
            setMessages(prev => [...prev, { role: 'assistant', text: initialMessage.text }]);

        } catch (error) {
            console.error("Error creating scenario:", error);
            logSystemMessage('Error: Failed to generate scenario. Please check your API key and try again.');
            setScenario('Error: Failed to connect to Gemini.');
        } finally {
            setIsLoading(false);
        }
    }, [activeCharacters]);
    
    const handleSendMessage = useCallback(async (text: string) => {
        if (!chatSession.current || isLoading) return;
    
        const userMessage: Message = { role: 'user', text };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
    
        try {
            const result = await chatSession.current.sendMessage({ message: text });
            const assistantMessage: Message = { role: 'assistant', text: result.text };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error("Error sending message:", error);
            logSystemMessage('Error: Failed to get response from Gemini.');
        } finally {
            setIsLoading(false);
        }
    }, [isLoading]);

    const handleGenerateImage = async (prompt: string) => {
        setIsGenerating(true);
        try {
            const imageData = await generateImage(prompt);
            return imageData;
        } catch (error) {
            console.error("Error generating image:", error);
            logSystemMessage('Error: Failed to generate image.');
            return null;
        } finally {
            setIsGenerating(false);
        }
    };

    const handleAnalyzeImage = async (imageData: string, mimeType: string, prompt: string) => {
        setIsGenerating(true);
        try {
            const analysis = await analyzeImage(imageData, mimeType, prompt);
            return analysis;
        } catch (error) {
            console.error("Error analyzing image:", error);
            logSystemMessage('Error: Failed to analyze image.');
            return "Analysis failed.";
        } finally {
            setIsGenerating(false);
        }
    };


    return (
        <div className="flex flex-col h-screen bg-gray-950 text-cyan-300 overflow-hidden">
            <Header />
            <div className="flex flex-1 min-h-0 p-2 md:p-4 gap-4">
                <MainDisplay 
                    messages={messages}
                    onSendMessage={handleSendMessage}
                    isLoading={isLoading}
                    isScenarioSet={!!scenario}
                    selectedTab={selectedTab}
                    onGenerateImage={handleGenerateImage}
                    onAnalyzeImage={handleAnalyzeImage}
                    isGenerating={isGenerating}
                />
                <SidePanel
                    activeCharacters={activeCharacters}
                    onAddCharacter={handleAddCharacter}
                    onRemoveCharacter={handleRemoveCharacter}
                    onViewSheet={handleViewSheet}
                    onCreateScenario={handleCreateScenario}
                    toolCallLogs={toolCallLogs}
                    onClearLogs={() => setToolCallLogs([])}
                    isLoading={isLoading}
                    isScenarioSet={!!scenario}
                    onTabChange={setSelectedTab}
                    selectedTab={selectedTab}
                />
            </div>
            <StatusBar online={!!scenario} statusText={scenario || "Offline"} />
            {isModalOpen && selectedCharacterSheet && (
                <CharacterSheetModal
                    character={selectedCharacterSheet}
                    onClose={() => setIsModalOpen(false)}
                />
            )}
        </div>
    );
};

export default App;

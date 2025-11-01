
import type { Character } from './types';

export const PREMADE_CHARACTERS: Character[] = [
  {
    name: "Kestrel",
    role: "Street Samurai",
    description: "A former corporate enforcer, Kestrel is a master of blades and close-quarters combat. Her body is a canvas of chrome and scars.",
    stats: { body: 6, agility: 7, reaction: 6, strength: 5, willpower: 4, logic: 3, intuition: 5, charisma: 3, edge: 4, essence: 2.5 },
    skills: [{ name: "Blades", rating: 7 }, { name: "Automatics", rating: 5 }, { name: "Athletics", rating: 4 }],
    cyberware: [{name: "Wired Reflexes Lvl 2", description: "Enhanced reaction speed."}, {name: "Cybereyes w/ Smartlink", description: "Improved vision and weapon accuracy."}],
    gear: ["Katana", "Ares Predator V Pistol", "Armor Jacket"],
  },
  {
    name: "Glitch",
    role: "Decker",
    description: "A prodigy who lives more in the Matrix than the real world. Glitch can bypass the toughest ICE with elegance and speed.",
    stats: { body: 3, agility: 4, reaction: 5, strength: 2, willpower: 5, logic: 7, intuition: 6, charisma: 2, edge: 3, essence: 5.1 },
    skills: [{ name: "Hacking", rating: 7 }, { name: "Cybercombat", rating: 6 }, { name: "Electronics", rating: 5 }],
    cyberware: [{name: "Datajack", description: "Direct neural interface to the Matrix."}, {name: "Headware Computer", description: "Internal storage and processing."}],
    gear: ["Custom Cyberdeck (Ono-Sendai Cyberspace 7)", "Pistol", "Data Chips"],
  },
  {
    name: "Whisper",
    role: "Infiltrator / Face",
    description: "A ghost in the system and a siren in the flesh. Whisper can talk her way into or out of anything, and disappear when words fail.",
    stats: { body: 4, agility: 6, reaction: 5, strength: 3, willpower: 4, logic: 4, intuition: 6, charisma: 7, edge: 5, essence: 4.8 },
    skills: [{ name: "Influence", rating: 7 }, { name: "Stealth", rating: 6 }, { name: "Pistols", rating: 5 }],
    cyberware: [{name: "Tailored Pheromones", description: "Subtle biochemical manipulation to influence others."}, {name: "Voice Modulator", description: "Alter vocal patterns and mimic voices."}],
    gear: ["Silenced Pistol", "Chameleon Suit", "High-fashion clothing"],
  },
  {
    name: "Oracle",
    role: "Hermetic Mage",
    description: "A scholar of the arcane arts, Oracle sees the flows of mana that bind the world, wielding powerful magic with disciplined precision.",
    stats: { body: 3, agility: 3, reaction: 4, strength: 2, willpower: 7, logic: 6, intuition: 5, charisma: 4, edge: 2, essence: 6.0 },
    skills: [{ name: "Spellcasting", rating: 7 }, { name: "Summoning", rating: 6 }, { name: "Assensing", rating: 5 }],
    cyberware: [],
    gear: ["Spell Foci", "Reagents", "Robes"],
  },
];


export const MOCK_SCENARIO = "The team is hired by a mysterious Johnson to extract a data-chip from a high-security Saeder-Krupp facility in the Seattle metroplex. The catch? The facility is rumored to be protected by a rogue AI.";

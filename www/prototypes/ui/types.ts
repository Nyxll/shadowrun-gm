
export interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool';
  text: string;
}

export interface Character {
  name: string;
  role: string;
  description: string;
  stats: {
    body: number;
    agility: number;
    reaction: number;
    strength: number;
    willpower: number;
    logic: number;
    intuition: number;
    charisma: number;
    edge: number;
    essence: number;
  };
  skills: { name: string; rating: number }[];
  cyberware: { name:string; description: string }[];
  gear: string[];
}

export interface ToolCallLog {
    id: string;
    type: 'request' | 'response';
    toolName: string;
    args: any;
    content?: any;
}


import { GoogleGenAI } from "@google/genai";
import type { Character } from '../types';

const getAI = () => {
    const apiKey = process.env.API_KEY;
    if (!apiKey) {
        throw new Error("API_KEY environment variable is not set.");
    }
    return new GoogleGenAI({ apiKey });
};

export const generateScenario = async (characters: Character[]): Promise<string> => {
    const ai = getAI();
    const characterDescriptions = characters.map(c => `- ${c.name} (${c.role}): ${c.description}`).join('\n');

    const prompt = `
    Create a compelling, one-sentence mission objective for a Shadowrun tabletop RPG session.
    The team consists of the following characters:
    ${characterDescriptions}

    The scenario should be a classic cyberpunk heist or operation with a clear goal and a hint of complication.
    Examples:
    - "Infiltrate a Renraku black site to extract a defecting scientist before they are terminated."
    - "Steal a prototype cybernetic limb from an Aztechnology motorcade during the downtown rush."
    - "Sabotage the grand opening of a new Ares Entertainment simsense parlor that's brainwashing its customers."

    Generate a new, unique scenario in that style.
    `;

    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-pro',
            contents: prompt
        });
        return response.text.trim();
    } catch (error) {
        console.error("Error in generateScenario:", error);
        throw new Error("Failed to communicate with the Gemini API.");
    }
};

export const generateImage = async (prompt: string): Promise<string> => {
    const ai = getAI();
    try {
        const response = await ai.models.generateImages({
            model: 'imagen-4.0-generate-001',
            prompt: `cyberpunk, shadowrun, futuristic, neon-drenched, cinematic lighting, high detail. ${prompt}`,
            config: {
              numberOfImages: 1,
              outputMimeType: 'image/jpeg',
              aspectRatio: '16:9',
            },
        });

        if (response.generatedImages && response.generatedImages.length > 0) {
            return response.generatedImages[0].image.imageBytes;
        } else {
            throw new Error("No image was generated.");
        }
    } catch (error) {
        console.error("Error in generateImage:", error);
        throw new Error("Failed to generate image with the Gemini API.");
    }
};

export const analyzeImage = async (base64ImageData: string, mimeType: string, prompt: string): Promise<string> => {
    const ai = getAI();
    try {
        const imagePart = {
            inlineData: {
                mimeType: mimeType,
                data: base64ImageData,
            },
        };
        const textPart = {
            text: `Analyze this image from a Shadowrun Game Master's perspective. ${prompt}`
        };
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: { parts: [imagePart, textPart] },
        });

        return response.text.trim();
    } catch (error) {
        console.error("Error in analyzeImage:", error);
        throw new Error("Failed to analyze image with the Gemini API.");
    }
};

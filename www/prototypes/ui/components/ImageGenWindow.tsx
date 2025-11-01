
import React, { useState } from 'react';
import { Button } from './common/Button';

interface ImageGenWindowProps {
    onGenerateImage: (prompt: string) => Promise<string | null>;
    isGenerating: boolean;
}

export const ImageGenWindow: React.FC<ImageGenWindowProps> = ({ onGenerateImage, isGenerating }) => {
    const [prompt, setPrompt] = useState('');
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!prompt.trim() || isGenerating) return;
        setGeneratedImage(null);
        const imageData = await onGenerateImage(prompt);
        if (imageData) {
            setGeneratedImage(`data:image/jpeg;base64,${imageData}`);
        }
    };

    return (
        <div className="flex flex-col h-full p-4 gap-4">
            <h2 className="text-2xl font-bold text-cyan-400 text-glow tracking-widest" style={{ fontFamily: "'Orbitron', sans-serif" }}>VISUALIZE SCENE</h2>
            <p className="text-sm text-cyan-200/80">Use the Imagen model to generate a visual representation of a scene, character, or object. The system will automatically add cyberpunk styling.</p>
            <div className="flex gap-4">
                <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="e.g., A street samurai facing down a corporate drone..."
                    disabled={isGenerating}
                    className="flex-1 bg-black/50 border border-cyan-700 text-cyan-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50"
                />
                <Button onClick={handleGenerate} disabled={isGenerating || !prompt.trim()}>
                    {isGenerating ? 'Generating...' : 'Generate'}
                </Button>
            </div>
            <div className="flex-1 mt-4 border border-cyan-500/30 bg-black/30 flex items-center justify-center p-4">
                {isGenerating && (
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-400 mx-auto mb-4"></div>
                        <p className="text-cyan-400">Generating image with Imagen 4.0...</p>
                        <p className="text-xs text-cyan-400/70">This can take a minute.</p>
                    </div>
                )}
                {!isGenerating && generatedImage && (
                    <img src={generatedImage} alt="Generated Scene" className="max-h-full max-w-full object-contain" />
                )}
                {!isGenerating && !generatedImage && (
                    <div className="text-center text-cyan-500/70">
                         <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                         </svg>
                        <p>Generated image will appear here</p>
                    </div>
                )}
            </div>
        </div>
    );
};

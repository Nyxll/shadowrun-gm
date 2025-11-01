
import React, { useState, useRef } from 'react';
import { Button } from './common/Button';

interface ImageAnalyzeWindowProps {
    onAnalyzeImage: (imageData: string, mimeType: string, prompt: string) => Promise<string>;
    isGenerating: boolean;
}

const fileToBase64 = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve((reader.result as string).split(',')[1]);
    reader.onerror = (error) => reject(error);
  });

export const ImageAnalyzeWindow: React.FC<ImageAnalyzeWindowProps> = ({ onAnalyzeImage, isGenerating }) => {
    const [prompt, setPrompt] = useState('');
    const [image, setImage] = useState<{ file: File; dataUrl: string } | null>(null);
    const [analysisResult, setAnalysisResult] = useState<string>('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const dataUrl = URL.createObjectURL(file);
            setImage({ file, dataUrl });
            setAnalysisResult('');
        }
    };
    
    const handleAnalyze = async () => {
        if (!image || !prompt.trim() || isGenerating) return;
        setAnalysisResult('');
        const base64Data = await fileToBase64(image.file);
        const result = await onAnalyzeImage(base64Data, image.file.type, prompt);
        setAnalysisResult(result);
    };

    return (
        <div className="flex flex-col h-full p-4 gap-4">
            <h2 className="text-2xl font-bold text-cyan-400 text-glow tracking-widest" style={{ fontFamily: "'Orbitron', sans-serif" }}>ANALYZE INTEL</h2>
            <p className="text-sm text-cyan-200/80">Upload an image (e.g., a map, a portrait, a piece of evidence) and ask the GM to analyze it.</p>
            
            <div className="flex flex-col md:flex-row gap-4 h-full min-h-0">
                <div className="flex-1 flex flex-col gap-4">
                    <div className="h-1/2 flex flex-col border border-cyan-500/30 bg-black/30 p-4">
                        <Button onClick={() => fileInputRef.current?.click()} className="mb-4">
                            {image ? 'Change Image' : 'Upload Image'}
                        </Button>
                        <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" className="hidden" />
                        <div className="flex-1 flex items-center justify-center">
                            {image ? (
                                <img src={image.dataUrl} alt="For analysis" className="max-h-full max-w-full object-contain" />
                            ) : (
                                <div className="text-center text-cyan-500/70">
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                    </svg>
                                    <p>Select an image to analyze</p>
                                </div>
                            )}
                        </div>
                    </div>
                    <div className="h-1/2 flex flex-col gap-2">
                         <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="What should I look for? e.g., 'Are there any hidden security features?' or 'What can you tell me about this person?'"
                            disabled={isGenerating || !image}
                            className="flex-1 w-full bg-black/50 border border-cyan-700 text-cyan-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50 resize-none"
                        />
                        <Button onClick={handleAnalyze} disabled={isGenerating || !image || !prompt.trim()}>
                            {isGenerating ? 'Analyzing...' : 'Analyze'}
                        </Button>
                    </div>
                </div>

                <div className="flex-1 border border-cyan-500/30 bg-black/30 p-4 overflow-y-auto">
                    {isGenerating && (
                        <div className="text-center">
                            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-400 mx-auto mb-4"></div>
                            <p className="text-cyan-400">Analyzing with Gemini...</p>
                        </div>
                    )}
                    {!isGenerating && analysisResult && (
                        <div className="whitespace-pre-wrap font-mono text-cyan-300">{analysisResult}</div>
                    )}
                    {!isGenerating && !analysisResult && (
                        <div className="text-center text-cyan-500/70 h-full flex flex-col justify-center">
                             <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                             </svg>
                            <p>Analysis will appear here</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

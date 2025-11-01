
import React, { useState } from 'react';
import type { Message } from '../types';
import { Panel } from './common/Panel';
import { ChatWindow } from './ChatWindow';
import { ImageGenWindow } from './ImageGenWindow';
import { ImageAnalyzeWindow } from './ImageAnalyzeWindow';

interface MainDisplayProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  isScenarioSet: boolean;
  selectedTab: 'chat' | 'imageGen' | 'imageAnalyze';
  onGenerateImage: (prompt: string) => Promise<string | null>;
  onAnalyzeImage: (imageData: string, mimeType: string, prompt: string) => Promise<string>;
  isGenerating: boolean;
}

export const MainDisplay: React.FC<MainDisplayProps> = (props) => {
  return (
    <main className="flex-1 flex flex-col min-w-0">
      <Panel className="flex-1 flex flex-col holographic-bg">
        {props.selectedTab === 'chat' && (
          <ChatWindow
            messages={props.messages}
            onSendMessage={props.onSendMessage}
            isLoading={props.isLoading}
            isScenarioSet={props.isScenarioSet}
          />
        )}
        {props.selectedTab === 'imageGen' && (
          <ImageGenWindow 
            onGenerateImage={props.onGenerateImage}
            isGenerating={props.isGenerating}
          />
        )}
        {props.selectedTab === 'imageAnalyze' && (
            <ImageAnalyzeWindow
                onAnalyzeImage={props.onAnalyzeImage}
                isGenerating={props.isGenerating}
            />
        )}
      </Panel>
    </main>
  );
};

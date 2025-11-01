
import React from 'react';

interface StatusBarProps {
  online: boolean;
  statusText: string;
}

export const StatusBar: React.FC<StatusBarProps> = ({ online, statusText }) => {
  return (
    <footer className="flex-shrink-0 bg-black/50 border-t border-cyan-500/30 p-2 text-xs flex justify-between items-center">
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${online ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
        <span className={online ? 'text-green-400' : 'text-red-400'}>{online ? 'ONLINE' : 'OFFLINE'}</span>
        <span className="text-cyan-500">|</span>
        <span className="text-cyan-400 truncate">{statusText}</span>
      </div>
      <div className="hidden md:block">
        <span className="text-cyan-600">EH ACOMNH.PL PRO/TGCSR // ORLINE</span>
      </div>
    </footer>
  );
};

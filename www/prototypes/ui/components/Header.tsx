
import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="flex-shrink-0 p-3 md:p-4 bg-black/50 border-b border-cyan-500/30">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-cyan-400 text-glow">
            <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 7L12 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M12 22V12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M22 7L12 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M17 4.5L7 9.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <h1 className="text-xl md:text-2xl font-bold text-cyan-400 text-glow tracking-widest" style={{ fontFamily: "'Orbitron', sans-serif" }}>
            SHADOWRUN PROTOCOL
          </h1>
        </div>
        <nav className="hidden md:flex items-center gap-6 text-sm font-bold tracking-wider">
          <a href="#" className="hover:text-cyan-300 hover:text-glow transition-all">GM DASHBOARD</a>
          <a href="#" className="text-gray-500 cursor-not-allowed">TEAM STATS</a>
          <a href="#" className="text-gray-500 cursor-not-allowed">MISSIONS</a>
        </nav>
        <div className="flex items-center gap-3">
          <div className="text-xs uppercase">B3CKETTMIN</div>
          <div className="w-8 h-8 rounded-full bg-cyan-900 border border-cyan-500 flex items-center justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-cyan-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
      </div>
    </header>
  );
};

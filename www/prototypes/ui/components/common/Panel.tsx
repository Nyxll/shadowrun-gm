
import React from 'react';

interface PanelProps {
  children: React.ReactNode;
  className?: string;
}

export const Panel: React.FC<PanelProps> = ({ children, className = '' }) => {
  return (
    <div className={`panel-border bg-black/40 backdrop-blur-sm p-4 ${className}`}>
      {children}
    </div>
  );
};

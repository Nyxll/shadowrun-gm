
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

export const Button: React.FC<ButtonProps> = ({ children, className = '', variant = 'primary', ...props }) => {
  const baseClasses = 'px-4 py-2 text-sm font-bold tracking-widest uppercase transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-cyan-500/80 text-gray-900 hover:bg-cyan-400 hover:shadow-[0_0_15px_#00ffff] disabled:bg-gray-600',
    secondary: 'border border-cyan-500 text-cyan-400 hover:bg-cyan-500/20 disabled:border-gray-600 disabled:text-gray-500',
  };

  return (
    <button className={`${baseClasses} ${variantClasses[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
};

import React from 'react';

interface LogoProps {
  className?: string;
  showText?: boolean;
}

const Logo: React.FC<LogoProps> = ({ className = "h-8 w-8", showText = true }) => {
  return (
    <div className="flex items-center gap-3">
      <div className={`${className} relative`}>
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {/* Shield outline */}
          <path
            d="M50 5 L85 20 L85 45 Q85 70 50 95 Q15 70 15 45 L15 20 Z"
            fill="none"
            stroke="#14b8a6"
            strokeWidth="3"
            className="drop-shadow-sm"
          />
          
          {/* Circuit pattern inside shield */}
          <g fill="none" stroke="#14b8a6" strokeWidth="2" strokeLinecap="round">
            {/* Central vertical line */}
            <line x1="50" y1="25" x2="50" y2="75" />
            
            {/* Circuit nodes */}
            <circle cx="35" cy="35" r="3" fill="#14b8a6" />
            <circle cx="65" cy="35" r="3" fill="#14b8a6" />
            <circle cx="30" cy="50" r="3" fill="#14b8a6" />
            <circle cx="70" cy="50" r="3" fill="#14b8a6" />
            <circle cx="35" cy="65" r="3" fill="#14b8a6" />
            <circle cx="65" cy="65" r="3" fill="#14b8a6" />
            
            {/* Connecting lines */}
            <line x1="35" y1="35" x2="45" y2="35" />
            <line x1="55" y1="35" x2="65" y2="35" />
            <line x1="30" y1="50" x2="45" y2="50" />
            <line x1="55" y1="50" x2="70" y2="50" />
            <line x1="35" y1="65" x2="45" y2="65" />
            <line x1="55" y1="65" x2="65" y2="65" />
            
            {/* Vertical connections */}
            <line x1="35" y1="35" x2="35" y2="40" />
            <line x1="65" y1="35" x2="65" y2="40" />
            <line x1="35" y1="60" x2="35" y2="65" />
            <line x1="65" y1="60" x2="65" y2="65" />
          </g>
        </svg>
      </div>
      
      {showText && (
        <div className="flex flex-col">
          <span className="text-xl font-bold text-gray-800 leading-none">
            BIG DEFEND
          </span>
          <span className="text-sm font-medium text-primary-600 leading-none">
            AI
          </span>
        </div>
      )}
    </div>
  );
};

export default Logo;
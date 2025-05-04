import React from 'react';
import { cn } from '../../utils/cn';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

/**
 * LoadingSpinner component for indicating loading states
 * @param props Component properties
 * @returns LoadingSpinner component
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className,
  label = 'Loading...'
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div 
        className={cn(
          'rounded-full border-transparent border-t-primary-600 animate-spin',
          sizeClasses[size],
          className
        )}
        role="status"
        aria-label={label}
      />
      {label && (
        <span className="mt-2 text-sm text-gray-700 dark:text-gray-300">{label}</span>
      )}
    </div>
  );
};

export default LoadingSpinner;
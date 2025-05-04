import React from 'react';
import { cn } from '../../utils/cn'; // Assuming cn utility exists

export interface TabsProps extends React.HTMLAttributes<HTMLDivElement> {}

/**
 * Tabs container component
 * @param props Tabs container properties
 * @returns Tabs container component
 */
const Tabs = React.forwardRef<HTMLDivElement, TabsProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('', className)}
        {...props}
      />
    );
  }
);

Tabs.displayName = 'Tabs';

export interface TabListProps extends React.HTMLAttributes<HTMLDivElement> {}

/**
 * TabList component for housing tab triggers
 * @param props TabList properties
 * @returns TabList component
 */
const TabList = React.forwardRef<HTMLDivElement, TabListProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex border-b border-gray-200', className)}
        {...props}
      />
    );
  }
);

TabList.displayName = 'TabList';

export interface TabTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isActive?: boolean;
}

/**
 * TabTrigger component for individual tab buttons
 * @param props TabTrigger properties
 * @returns TabTrigger component
 */
const TabTrigger = React.forwardRef<HTMLButtonElement, TabTriggerProps>(
  ({ className, isActive, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'px-4 py-3 text-sm font-medium border-b-2 -mb-px whitespace-nowrap',
          isActive
            ? 'border-primary-500 text-primary-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
          className
        )}
        {...props}
      />
    );
  }
);

TabTrigger.displayName = 'TabTrigger';

export interface TabContentProps extends React.HTMLAttributes<HTMLDivElement> {
  isActive?: boolean;
}

/**
 * TabContent component for tab panel content
 * @param props TabContent properties
 * @returns TabContent component
 */
const TabContent = React.forwardRef<HTMLDivElement, TabContentProps>(
  ({ className, isActive, ...props }, ref) => {
    if (!isActive) return null;
    
    return (
      <div
        ref={ref}
        className={cn('py-4', className)}
        {...props}
      />
    );
  }
);

TabContent.displayName = 'TabContent';

export { Tabs, TabList, TabTrigger, TabContent };

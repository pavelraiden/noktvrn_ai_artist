import { useCallback, useEffect, useState, KeyboardEvent as ReactKeyboardEvent } from 'react';

/**
 * Hook that provides keyboard accessibility utilities
 * 
 * @returns Object with accessibility helpers
 */
export function useAccessibility() {
  const [focusVisible, setFocusVisible] = useState(false);

  // Handle keyboard interaction events
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Tab') {
      setFocusVisible(true);
    }
  }, []);

  // Handle mouse interaction events
  const handleMouseDown = useCallback(() => {
    setFocusVisible(false);
  }, []);

  // Set up global event listeners
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, [handleKeyDown, handleMouseDown]);

  /**
   * Handler for keyboard navigation of items in a list or menu
   * 
   * @param options Options for key handling
   * @returns Key down event handler
   */
  const createKeyboardNavigationHandler = ({
    onUp,
    onDown, 
    onLeft,
    onRight,
    onEnter,
    onEscape,
    onHome,
    onEnd,
    onTab,
  }: {
    onUp?: () => void;
    onDown?: () => void;
    onLeft?: () => void;
    onRight?: () => void;
    onEnter?: () => void;
    onEscape?: () => void;
    onHome?: () => void;
    onEnd?: () => void;
    onTab?: (event: ReactKeyboardEvent) => void;
  }) => {
    return (event: ReactKeyboardEvent) => {
      switch (event.key) {
        case 'ArrowUp':
          if (onUp) {
            event.preventDefault();
            onUp();
          }
          break;
        case 'ArrowDown':
          if (onDown) {
            event.preventDefault();
            onDown();
          }
          break;
        case 'ArrowLeft':
          if (onLeft) {
            event.preventDefault();
            onLeft();
          }
          break;
        case 'ArrowRight':
          if (onRight) {
            event.preventDefault();
            onRight();
          }
          break;
        case 'Enter':
        case ' ':
          if (onEnter) {
            event.preventDefault();
            onEnter();
          }
          break;
        case 'Escape':
          if (onEscape) {
            event.preventDefault();
            onEscape();
          }
          break;
        case 'Home':
          if (onHome) {
            event.preventDefault();
            onHome();
          }
          break;
        case 'End':
          if (onEnd) {
            event.preventDefault();
            onEnd();
          }
          break;
        case 'Tab':
          if (onTab) {
            onTab(event);
          }
          break;
        default:
          break;
      }
    };
  };

  return {
    focusVisible,
    createKeyboardNavigationHandler,
  };
}
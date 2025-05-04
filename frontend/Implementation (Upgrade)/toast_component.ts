import React, { createContext, useContext, useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../utils/cn';

// Toast types
type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

// Toast context
interface ToastContextType {
  addToast: (type: ToastType, message: string, duration?: number) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

/**
 * Custom hook for using the toast system
 * @returns Toast functions for adding and removing toasts
 */
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

/**
 * ToastProvider component for the toast notification system
 * @param props Component properties
 * @returns ToastProvider component
 */
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (type: ToastType, message: string, duration = 5000) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prevToasts) => [...prevToasts, { id, type, message, duration }]);
  };

  const removeToast = (id: string) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <Toaster toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
};

/**
 * Single toast notification component
 * @param props Toast properties
 * @returns Toast component
 */
const Toast: React.FC<{
  toast: Toast;
  onClose: () => void;
}> = ({ toast, onClose }) => {
  const { type, message } = toast;

  useEffect(() => {
    if (toast.duration) {
      const timer = setTimeout(() => {
        onClose();
      }, toast.duration);
      return () => clearTimeout(timer);
    }
  }, [toast.duration, onClose]);

  const typeClasses = {
    success: 'bg-green-100 border-green-500 text-green-800',
    error: 'bg-red-100 border-red-500 text-red-800',
    warning: 'bg-yellow-100 border-yellow-500 text-yellow-800',
    info: 'bg-blue-100 border-blue-500 text-blue-800',
  };

  const iconMap = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  return (
    <div
      className={cn(
        'flex items-center p-4 mb-3 rounded-md border-l-4 shadow-md transform transition-all duration-300 ease-in-out',
        typeClasses[type]
      )}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex-shrink-0 mr-3">
        <span className="font-bold">{iconMap[type]}</span>
      </div>
      <div className="flex-grow">{message}</div>
      <button
        onClick={onClose}
        className="ml-3 p-1 rounded-full hover:bg-gray-200 hover:bg-opacity-50 transition-colors duration-200"
        aria-label="Close"
      >
        <span className="sr-only">Close</span>
        <span aria-hidden="true">×</span>
      </button>
    </div>
  );
};

/**
 * Toaster component that renders all active toasts
 * @param props Toaster properties
 * @returns Toaster component
 */
export const Toaster: React.FC<{
  toasts?: Toast[];
  removeToast?: (id: string) => void;
}> = ({ toasts = [], removeToast = () => {} }) => {
  // Create portal for toast container
  return createPortal(
    <div
      className="fixed top-4 right-4 z-50 max-w-sm w-full flex flex-col items-end"
      aria-live="polite"
      aria-atomic="true"
    >
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          toast={toast}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>,
    document.body
  );
};
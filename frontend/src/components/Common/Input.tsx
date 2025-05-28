// frontend/src/components/Common/Input.tsx
import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import { LucideIcon } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    label, 
    error, 
    icon: Icon, 
    iconPosition = 'left', 
    fullWidth = false, 
    className, 
    ...props 
  }, ref) => {
    const inputClasses = [
      'block px-3 py-2 border border-gray-300 rounded-lg',
      'placeholder-gray-400 text-gray-900',
      'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
      'disabled:bg-gray-50 disabled:text-gray-500',
      error && 'border-red-300 focus:ring-red-500 focus:border-red-500',
      Icon && iconPosition === 'left' && 'pl-10',
      Icon && iconPosition === 'right' && 'pr-10',
      fullWidth && 'w-full',
    ];

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
        )}
        <div className="relative">
          {Icon && (
            <div className={clsx(
              'absolute inset-y-0 flex items-center pointer-events-none',
              iconPosition === 'left' ? 'left-3' : 'right-3'
            )}>
              <Icon className="w-5 h-5 text-gray-400" />
            </div>
          )}
          <input
            ref={ref}
            className={clsx(inputClasses, className)}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';


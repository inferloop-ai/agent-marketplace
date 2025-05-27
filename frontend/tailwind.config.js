/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
      './src/components/**/*.{js,ts,jsx,tsx,mdx}',
      './src/app/**/*.{js,ts,jsx,tsx,mdx}',
      './src/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
      extend: {
        colors: {
          // Custom color palette for Agent Workflow Builder
          primary: {
            50: '#eff6ff',
            100: '#dbeafe',
            200: '#bfdbfe',
            300: '#93c5fd',
            400: '#60a5fa',
            500: '#3b82f6',
            600: '#2563eb',
            700: '#1d4ed8',
            800: '#1e40af',
            900: '#1e3a8a',
            950: '#172554',
          },
          secondary: {
            50: '#f8fafc',
            100: '#f1f5f9',
            200: '#e2e8f0',
            300: '#cbd5e1',
            400: '#94a3b8',
            500: '#64748b',
            600: '#475569',
            700: '#334155',
            800: '#1e293b',
            900: '#0f172a',
          },
          success: {
            50: '#f0fdf4',
            100: '#dcfce7',
            200: '#bbf7d0',
            300: '#86efac',
            400: '#4ade80',
            500: '#22c55e',
            600: '#16a34a',
            700: '#15803d',
            800: '#166534',
            900: '#14532d',
          },
          warning: {
            50: '#fffbeb',
            100: '#fef3c7',
            200: '#fde68a',
            300: '#fcd34d',
            400: '#fbbf24',
            500: '#f59e0b',
            600: '#d97706',
            700: '#b45309',
            800: '#92400e',
            900: '#78350f',
          },
          error: {
            50: '#fef2f2',
            100: '#fee2e2',
            200: '#fecaca',
            300: '#fca5a5',
            400: '#f87171',
            500: '#ef4444',
            600: '#dc2626',
            700: '#b91c1c',
            800: '#991b1b',
            900: '#7f1d1d',
          },
          // Agent type colors
          llm: {
            50: '#f0f9ff',
            500: '#0ea5e9',
            600: '#0284c7',
          },
          tool: {
            50: '#fefce8',
            500: '#eab308',
            600: '#ca8a04',
          },
          crewai: {
            50: '#fdf4ff',
            500: '#a855f7',
            600: '#9333ea',
          },
          langchain: {
            50: '#fef2f2',
            500: '#ef4444',
            600: '#dc2626',
          },
          monitoring: {
            50: '#f9fafb',
            500: '#6b7280',
            600: '#4b5563',
          },
        },
        fontFamily: {
          sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
          mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
        },
        fontSize: {
          '2xs': ['0.625rem', { lineHeight: '0.75rem' }],
        },
        spacing: {
          '18': '4.5rem',
          '88': '22rem',
          '128': '32rem',
        },
        borderRadius: {
          '4xl': '2rem',
        },
        boxShadow: {
          'node': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          'node-selected': '0 10px 15px -3px rgba(59, 130, 246, 0.4), 0 4px 6px -2px rgba(59, 130, 246, 0.05)',
          'connection': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        },
        animation: {
          'fade-in': 'fadeIn 0.5s ease-in-out',
          'slide-in': 'slideIn 0.3s ease-out',
          'bounce-subtle': 'bounceSubtle 2s infinite',
          'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
          'connection-flow': 'connectionFlow 2s linear infinite',
        },
        keyframes: {
          fadeIn: {
            '0%': { opacity: '0' },
            '100%': { opacity: '1' },
          },
          slideIn: {
            '0%': { transform: 'translateY(10px)', opacity: '0' },
            '100%': { transform: 'translateY(0)', opacity: '1' },
          },
          bounceSubtle: {
            '0%, 100%': { transform: 'translateY(0)' },
            '50%': { transform: 'translateY(-5px)' },
          },
          connectionFlow: {
            '0%': { strokeDashoffset: '10' },
            '100%': { strokeDashoffset: '0' },
          },
        },
        backdropBlur: {
          xs: '2px',
        },
        zIndex: {
          '60': '60',
          '70': '70',
          '80': '80',
          '90': '90',
          '100': '100',
        },
      },
    },
    plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
      // Custom plugin for agent workflow specific utilities
      function({ addUtilities, theme }) {
        const newUtilities = {
          '.node-shadow': {
            boxShadow: theme('boxShadow.node'),
          },
          '.node-shadow-selected': {
            boxShadow: theme('boxShadow.node-selected'),
          },
          '.connection-line': {
            stroke: theme('colors.gray.400'),
            strokeWidth: '2',
            fill: 'none',
          },
          '.connection-line-active': {
            stroke: theme('colors.primary.500'),
            strokeWidth: '2',
            fill: 'none',
            animation: theme('animation.connection-flow'),
          },
          '.canvas-grid': {
            backgroundImage: `
              linear-gradient(rgba(0,0,0,.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0,0,0,.1) 1px, transparent 1px)
            `,
            backgroundSize: '20px 20px',
          },
          '.agent-glow': {
            boxShadow: `0 0 20px ${theme('colors.primary.500')}40`,
          },
        }
        addUtilities(newUtilities)
      }
    ],
    darkMode: 'class',
  }
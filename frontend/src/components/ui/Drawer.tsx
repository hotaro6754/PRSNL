'use client'

import React, { useEffect } from 'react'
import { X } from 'lucide-react'

interface DrawerProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  description?: string
  children: React.ReactNode
  footer?: React.ReactNode
  width?: string
}

export function Drawer({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  width = 'max-w-md'
}: DrawerProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-hidden font-mono">
      {/* Liquid Glass Backdrop */}
      <div 
        onClick={onClose}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity animate-in fade-in duration-200"
      />

      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div className={`w-screen ${width} transform transition ease-in-out duration-200 animate-in slide-in-from-right`}>
          {/* Drawer Liquid Glass Surface */}
          <div className="glass-drawer flex h-full flex-col">
            
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/[0.08] bg-[#0c0e14]/60">
              <div>
                {title && (
                  <h2 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                    {title}
                  </h2>
                )}
                {description && (
                  <p className="text-[11px] text-zinc-400 font-sans mt-0.5">
                    {description}
                  </p>
                )}
              </div>
              <button
                onClick={onClose}
                className="p-1 rounded-md text-zinc-400 hover:text-white hover:bg-white/[0.08] transition-colors cursor-pointer"
                title="Close drawer (Esc)"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Content Body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {children}
            </div>

            {/* Footer */}
            {footer && (
              <div className="p-4 border-t border-white/[0.08] bg-[#0c0e14]/60">
                {footer}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

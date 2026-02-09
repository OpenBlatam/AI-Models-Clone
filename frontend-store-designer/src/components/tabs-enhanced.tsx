'use client'

import { useState, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface Tab {
  id: string
  label: string
  content: ReactNode
  icon?: ReactNode
  badge?: string | number
}

interface TabsEnhancedProps {
  tabs: Tab[]
  defaultTab?: string
  className?: string
}

export function TabsEnhanced({
  tabs,
  defaultTab,
  className,
}: TabsEnhancedProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id)

  const activeTabContent = tabs.find((tab) => tab.id === activeTab)?.content

  return (
    <div className={className}>
      <div className="flex border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 font-medium text-sm transition-colors border-b-2',
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            )}
          >
            {tab.icon}
            {tab.label}
            {tab.badge && (
              <span className="px-2 py-0.5 text-xs bg-gray-100 rounded-full">
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>
      <div className="mt-4">{activeTabContent}</div>
    </div>
  )
}



'use client';

import { useState } from 'react';
import {
  Dashboard,
  TaskMonitor,
  TaskHistory,
  HealthIndicator,
  ToastContainer,
  HelpDialog,
  OfflineIndicator,
  SkipLink,
  QuickActions,
  KeyboardShortcutsModal,
  QuickSearch,
  ThemeSelector,
  AccessibilityAnnouncer,
  Confetti,
  CommandPalette,
  PreferencesModal,
  CalendarView,
  StatsCard,
} from '@/components';
import {
  useToast,
  useAnalytics,
  useAppCommands,
  useAppKeyboardShortcuts,
} from '@/lib';

export default function Home() {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showQuickSearch, setShowQuickSearch] = useState(false);
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);
  const [announcement, setAnnouncement] = useState<string | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const { toasts, removeToast, success } = useToast();
  const analytics = useAnalytics();

  const { commands, quickActions } = useAppCommands({
    showHistory,
    showCalendar,
    setShowHistory,
    setShowCalendar,
    setShowHelp,
    setShowPreferences,
    setShowShortcuts,
    setActiveTaskId,
  });

  useAppKeyboardShortcuts({
    setShowHistory,
    setShowShortcuts,
    setShowQuickSearch,
    setShowCommandPalette,
    setActiveTaskId,
    showHistory,
  });

  const handleTaskCreated = (taskId: string) => {
    setActiveTaskId(taskId);
    success('Tarea creada exitosamente. Monitoreando progreso...');
    setAnnouncement('Tarea creada exitosamente');
    analytics.track('task_created', 'tasks', 'new_task');
  };


  return (
    <>
      <SkipLink />
      <main id="main-content" className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-4 md:py-8">
        <header className="mb-4 md:mb-8">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
            <div className="flex items-center gap-2 md:gap-4 flex-wrap">
              <h1 className="text-2xl md:text-4xl font-bold text-gray-900 dark:text-white">
                Contabilidad Mexicana AI
              </h1>
              <HealthIndicator />
            </div>
            <div className="flex items-center gap-2 md:gap-3 flex-wrap">
              <button
                onClick={() => setShowHelp(true)}
                className="px-4 py-2 bg-blue-100 dark:bg-blue-900 hover:bg-blue-200 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-300 rounded-lg transition-colors text-sm font-medium"
                aria-label="Ayuda"
              >
                ❓ Ayuda
              </button>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium"
              >
                {showHistory ? 'Ocultar' : 'Mostrar'} Historial
              </button>
              <button
                onClick={() => setShowCalendar(!showCalendar)}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium"
              >
                📅 {showCalendar ? 'Ocultar' : 'Mostrar'} Calendario
              </button>
              <button
                onClick={() => setShowShortcuts(true)}
                className="px-3 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium"
                title="Atajos de teclado (Ctrl+/)"
              >
                ⌨️
              </button>
              <button
                onClick={() => setShowPreferences(true)}
                className="px-3 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium"
                title="Preferencias"
                aria-label="Preferencias"
              >
                ⚙️
              </button>
              <ThemeSelector />
            </div>
          </div>
          <p className="text-sm md:text-lg text-gray-600 dark:text-gray-300 text-center md:text-left">
            Sistema inteligente de asesoría fiscal y contable
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Dashboard onTaskCreated={handleTaskCreated} />
            {showHistory && (
              <>
                <TaskHistory
                  onSelectTask={setActiveTaskId}
                  selectedTaskId={activeTaskId}
                />
                <StatsCard />
              </>
            )}
            {showCalendar && <CalendarView />}
          </div>
          <div className="lg:col-span-1">
            <TaskMonitor taskId={activeTaskId} />
          </div>
        </div>
      </div>
      
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <HelpDialog isOpen={showHelp} onClose={() => setShowHelp(false)} />
      <KeyboardShortcutsModal
        isOpen={showShortcuts}
        onClose={() => setShowShortcuts(false)}
      />
      <QuickSearch
        isOpen={showQuickSearch}
        onClose={() => setShowQuickSearch(false)}
        onSelect={setActiveTaskId}
      />
      <CommandPalette
        commands={commands}
        isOpen={showCommandPalette}
        onClose={() => setShowCommandPalette(false)}
      />
      <PreferencesModal
        isOpen={showPreferences}
        onClose={() => setShowPreferences(false)}
      />
      <OfflineIndicator />
      <QuickActions actions={quickActions} />
      <AccessibilityAnnouncer message={announcement} />
      <Confetti trigger={showConfetti} />
    </main>
    </>
  );
}


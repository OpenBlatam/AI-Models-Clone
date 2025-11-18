'use client';

import { useState } from 'react';
import ChatPanel from './ChatPanel';
import RobotControl from './RobotControl';
import StatusPanel from './StatusPanel';
import MetricsPanel from './MetricsPanel';
import Robot3DView from './Robot3DView';
import MovementHistory from './MovementHistory';
import TrajectoryOptimizer from './TrajectoryOptimizer';
import RecordingPanel from './RecordingPanel';
import SettingsPanel from './SettingsPanel';
import LogsPanel from './LogsPanel';
import AlertsPanel from './AlertsPanel';
import AdvancedMetrics from './AdvancedMetrics';
import TrajectoryComparison from './TrajectoryComparison';
import CustomCommands from './CustomCommands';
import HelpPanel from './HelpPanel';
import Fullscreen3D from './Fullscreen3D';
import SearchBar from './SearchBar';
import WidgetDashboard from './WidgetDashboard';
import ReportsPanel from './ReportsPanel';
import PredictiveAnalysis from './PredictiveAnalysis';
import CollaborationPanel from './CollaborationPanel';
import AuthPanel from './AuthPanel';
import PerformanceMonitor from './PerformanceMonitor';
import BackendIntegrations from './BackendIntegrations';
import DataExport from './DataExport';
import SystemDiagnostics from './SystemDiagnostics';
import RealTimeVisualization from './RealTimeVisualization';
import EnergyOptimization from './EnergyOptimization';
import SafetyMonitor from './SafetyMonitor';
import CommandHistory from './CommandHistory';
import PresetPositions from './PresetPositions';
import SystemBackup from './SystemBackup';
import NotificationCenter from './NotificationCenter';
import ShortcutsGuide from './ShortcutsGuide';
import SystemInfo from './SystemInfo';
import ActivityTimeline from './ActivityTimeline';
import QuickStats from './QuickStats';
import ThemeCustomizer from './ThemeCustomizer';
import DataVisualization from './DataVisualization';
import RemoteControl from './RemoteControl';
import CalibrationPanel from './CalibrationPanel';
import MaintenancePanel from './MaintenancePanel';
import DocumentationViewer from './DocumentationViewer';
import LicenseManager from './LicenseManager';
import UpdateChecker from './UpdateChecker';
import FeedbackPanel from './FeedbackPanel';
import AboutPanel from './AboutPanel';
import OnboardingTour from './OnboardingTour';
import FavoritesManager from './FavoritesManager';
import UsageStatistics from './UsageStatistics';
import AccessibilityPanel from './AccessibilityPanel';
import KeyboardNavigation from './KeyboardNavigation';
import PerformanceOptimizer from './PerformanceOptimizer';
import TemplatesManager from './TemplatesManager';
import AdvancedSearch from './AdvancedSearch';
import PluginManager from './PluginManager';
import WorkspaceManager from './WorkspaceManager';
import SessionRecorder from './SessionRecorder';
import QuickAccess from './QuickAccess';
import DataAnalytics from './DataAnalytics';
import AutomationPanel from './AutomationPanel';
import CloudSync from './CloudSync';
import AIAssistant from './AIAssistant';
import LearningCenter from './LearningCenter';
import Marketplace from './Marketplace';
import VoiceControl from './VoiceControl';
import GestureControl from './GestureControl';
import ARView from './ARView';
import TrajectorySimulator from './TrajectorySimulator';
import CodeEditor from './CodeEditor';
import Terminal from './Terminal';
import VersionControl from './VersionControl';
import TestSuite from './TestSuite';
import PermissionsManager from './PermissionsManager';
import APIIntegrations from './APIIntegrations';
import BackupScheduler from './BackupScheduler';
import SmartAlerts from './SmartAlerts';
import RealTimeDashboard from './RealTimeDashboard';
import EventLog from './EventLog';
import SystemHealth from './SystemHealth';
import NotificationSettings from './NotificationSettings';
import DataSync from './DataSync';
import ResourceMonitor from './ResourceMonitor';
import ActivityFeed from './ActivityFeed';
import AuditLog from './AuditLog';
import UserManagement from './UserManagement';
import ReportGenerator from './ReportGenerator';
import ServiceStatus from './ServiceStatus';
import AdvancedAnalytics from './AdvancedAnalytics';
import ConfigurationManager from './ConfigurationManager';
import DataBackup from './DataBackup';
import NetworkMonitor from './NetworkMonitor';
import SecurityCenter from './SecurityCenter';
import PerformanceTuning from './PerformanceTuning';
import ErrorTracker from './ErrorTracker';
import SystemMetrics from './SystemMetrics';
import TaskScheduler from './TaskScheduler';
import DataExplorer from './DataExplorer';
import LogAnalyzer from './LogAnalyzer';
import SystemDiagnostics from './SystemDiagnostics';
import APIDocumentation from './APIDocumentation';
import QuickActionsPanel from './QuickActionsPanel';
import SystemInfo from './SystemInfo';
import CommandPalette from './CommandPalette';
import WorkflowBuilder from './WorkflowBuilder';
import DataPipeline from './DataPipeline';
import MonitoringDashboard from './MonitoringDashboard';
import SettingsAdvanced from './SettingsAdvanced';
import DataVisualization from './DataVisualization';
import AlertManager from './AlertManager';
import PerformanceProfiler from './PerformanceProfiler';
import SystemTweaks from './SystemTweaks';
import QuickActions from './QuickActions';
import LanguageSelector from './LanguageSelector';
import ToastContainer from './ToastContainer';
import { useRobotStore } from '@/lib/store/robotStore';
import { Activity, MessageSquare, Settings, BarChart3, Box, History, Sparkles, Record, Cog, Terminal as TerminalIcon, Bell, TrendingUp, GitCompare, Command, HelpCircle, LayoutDashboard, FileText, Brain, Users, Lock, Gauge, Plug, Database, Stethoscope, Radio, Battery, Shield, Clock, MapPin, HardDrive, Keyboard, Info, Timeline, Palette, BarChart, Gamepad2, Target, Wrench, Book, Key, RefreshCw, MessageSquare as MessageSquareIcon, Star, BarChart as BarChartIcon, Accessibility, Zap, FileTemplate, Search as SearchIcon, Puzzle, FolderOpen, Video, Zap as ZapIcon, TrendingUp as TrendingUpIcon, Bot, Cloud, Sparkles as SparklesIcon, GraduationCap, Store, Mic, Hand, Camera, Play, Code, GitBranch, TestTube, Shield as ShieldIcon, Calendar, Bell as BellIcon, Activity as ActivityIcon, FileText as FileTextIcon, Heart, Bell as BellSettingsIcon, RefreshCw as RefreshCwIcon, Monitor, Activity as ActivityFeedIcon, Shield as AuditIcon, Users as UsersIcon, FileText as ReportIcon, Server, TrendingUp as AnalyticsIcon, Settings as ConfigIcon, HardDrive as BackupIcon, Network, Shield as SecurityIcon, Gauge as TuningIcon, Bug, BarChart3 as MetricsIcon, Calendar as TaskIcon, Database as DataIcon, FileSearch, Stethoscope as DiagIcon, Book as BookIcon, Zap as ZapPanelIcon, Info as InfoIcon, Command as CommandIcon, Workflow, GitBranch as PipelineIcon, Monitor as MonitorIcon, Settings as SettingsAdvancedIcon, BarChart3 as DataVizIcon, Bell as AlertMgrIcon, Gauge as ProfilerIcon, Sliders } from 'lucide-react';

type Tab = 'control' | 'chat' | 'status' | 'metrics' | '3d' | 'history' | 'optimize' | 'recording' | 'settings' | 'logs' | 'alerts' | 'advanced' | 'compare' | 'commands' | 'help' | 'widgets' | 'reports' | 'predictive' | 'collaboration' | 'auth' | 'performance' | 'integrations' | 'export' | 'diagnostics' | 'realtime' | 'energy' | 'safety' | 'cmdhistory' | 'presets' | 'backup' | 'notifications' | 'shortcuts' | 'systeminfo' | 'timeline' | 'theme' | 'visualization' | 'remote' | 'calibration' | 'maintenance' | 'docs' | 'license' | 'updates' | 'feedback' | 'about' | 'favorites' | 'usage' | 'accessibility' | 'optimizer' | 'templates' | 'advanced-search' | 'plugins' | 'workspaces' | 'sessions' | 'quick-access' | 'analytics' | 'automation' | 'cloud' | 'ai-assistant' | 'learning' | 'marketplace' | 'voice' | 'gestures' | 'ar' | 'simulator' | 'code' | 'terminal' | 'versions' | 'tests' | 'permissions' | 'api-integrations' | 'backup-scheduler' | 'smart-alerts' | 'realtime-dashboard' | 'event-log' | 'system-health' | 'notification-settings' | 'data-sync' | 'resource-monitor' | 'activity-feed' | 'audit-log' | 'user-management' | 'report-generator' | 'service-status' | 'advanced-analytics' | 'configuration-manager' | 'data-backup' | 'network-monitor' | 'security-center' | 'performance-tuning' | 'error-tracker' | 'system-metrics' | 'task-scheduler' | 'data-explorer' | 'log-analyzer' | 'system-diagnostics' | 'api-docs' | 'quick-actions-panel' | 'system-info' | 'command-palette' | 'workflow-builder' | 'data-pipeline' | 'monitoring-dashboard' | 'settings-advanced' | 'data-visualization' | 'alert-manager' | 'performance-profiler' | 'system-tweaks';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<Tab>('control');
  const { status, error } = useRobotStore();

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'control', label: 'Control', icon: <Activity className="w-5 h-5" /> },
    { id: 'chat', label: 'Chat', icon: <MessageSquare className="w-5 h-5" /> },
    { id: '3d', label: '3D View', icon: <Box className="w-5 h-5" /> },
    { id: 'status', label: 'Estado', icon: <Settings className="w-5 h-5" /> },
    { id: 'metrics', label: 'Métricas', icon: <BarChart3 className="w-5 h-5" /> },
    { id: 'history', label: 'Historial', icon: <History className="w-5 h-5" /> },
    { id: 'optimize', label: 'Optimizar', icon: <Sparkles className="w-5 h-5" /> },
    { id: 'recording', label: 'Grabación', icon: <Record className="w-5 h-5" /> },
    { id: 'advanced', label: 'Métricas Avanzadas', icon: <TrendingUp className="w-5 h-5" /> },
    { id: 'compare', label: 'Comparar', icon: <GitCompare className="w-5 h-5" /> },
    { id: 'commands', label: 'Comandos', icon: <Command className="w-5 h-5" /> },
    { id: 'widgets', label: 'Widgets', icon: <LayoutDashboard className="w-5 h-5" /> },
    { id: 'reports', label: 'Reportes', icon: <FileText className="w-5 h-5" /> },
    { id: 'predictive', label: 'Predictivo', icon: <Brain className="w-5 h-5" /> },
    { id: 'collaboration', label: 'Colaboración', icon: <Users className="w-5 h-5" /> },
    { id: 'auth', label: 'Autenticación', icon: <Lock className="w-5 h-5" /> },
    { id: 'performance', label: 'Rendimiento', icon: <Gauge className="w-5 h-5" /> },
    { id: 'integrations', label: 'Integraciones', icon: <Plug className="w-5 h-5" /> },
    { id: 'export', label: 'Exportar', icon: <Database className="w-5 h-5" /> },
    { id: 'diagnostics', label: 'Diagnóstico', icon: <Stethoscope className="w-5 h-5" /> },
    { id: 'realtime', label: 'Tiempo Real', icon: <Radio className="w-5 h-5" /> },
    { id: 'energy', label: 'Energía', icon: <Battery className="w-5 h-5" /> },
    { id: 'safety', label: 'Seguridad', icon: <Shield className="w-5 h-5" /> },
    { id: 'cmdhistory', label: 'Hist. Comandos', icon: <Clock className="w-5 h-5" /> },
    { id: 'presets', label: 'Presets', icon: <MapPin className="w-5 h-5" /> },
    { id: 'backup', label: 'Backup', icon: <HardDrive className="w-5 h-5" /> },
    { id: 'notifications', label: 'Notificaciones', icon: <Bell className="w-5 h-5" /> },
    { id: 'shortcuts', label: 'Atajos', icon: <Keyboard className="w-5 h-5" /> },
    { id: 'systeminfo', label: 'Sistema', icon: <Info className="w-5 h-5" /> },
    { id: 'timeline', label: 'Línea de Tiempo', icon: <Timeline className="w-5 h-5" /> },
    { id: 'theme', label: 'Tema', icon: <Palette className="w-5 h-5" /> },
    { id: 'visualization', label: 'Visualización', icon: <BarChart className="w-5 h-5" /> },
    { id: 'remote', label: 'Control Remoto', icon: <Gamepad2 className="w-5 h-5" /> },
    { id: 'calibration', label: 'Calibración', icon: <Target className="w-5 h-5" /> },
    { id: 'maintenance', label: 'Mantenimiento', icon: <Wrench className="w-5 h-5" /> },
    { id: 'docs', label: 'Documentación', icon: <Book className="w-5 h-5" /> },
    { id: 'license', label: 'Licencias', icon: <Key className="w-5 h-5" /> },
    { id: 'updates', label: 'Actualizaciones', icon: <RefreshCw className="w-5 h-5" /> },
    { id: 'feedback', label: 'Feedback', icon: <MessageSquareIcon className="w-5 h-5" /> },
    { id: 'about', label: 'Acerca de', icon: <Info className="w-5 h-5" /> },
    { id: 'favorites', label: 'Favoritos', icon: <Star className="w-5 h-5" /> },
    { id: 'usage', label: 'Uso', icon: <BarChartIcon className="w-5 h-5" /> },
    { id: 'accessibility', label: 'Accesibilidad', icon: <Accessibility className="w-5 h-5" /> },
    { id: 'optimizer', label: 'Optimizador', icon: <Zap className="w-5 h-5" /> },
    { id: 'templates', label: 'Plantillas', icon: <FileTemplate className="w-5 h-5" /> },
    { id: 'advanced-search', label: 'Búsqueda Avanzada', icon: <SearchIcon className="w-5 h-5" /> },
    { id: 'plugins', label: 'Plugins', icon: <Puzzle className="w-5 h-5" /> },
    { id: 'workspaces', label: 'Workspaces', icon: <FolderOpen className="w-5 h-5" /> },
    { id: 'sessions', label: 'Sesiones', icon: <Video className="w-5 h-5" /> },
    { id: 'quick-access', label: 'Acceso Rápido', icon: <ZapIcon className="w-5 h-5" /> },
    { id: 'analytics', label: 'Análisis', icon: <TrendingUpIcon className="w-5 h-5" /> },
    { id: 'automation', label: 'Automatización', icon: <Bot className="w-5 h-5" /> },
    { id: 'cloud', label: 'Nube', icon: <Cloud className="w-5 h-5" /> },
    { id: 'ai-assistant', label: 'IA Asistente', icon: <SparklesIcon className="w-5 h-5" /> },
    { id: 'learning', label: 'Aprendizaje', icon: <GraduationCap className="w-5 h-5" /> },
    { id: 'marketplace', label: 'Marketplace', icon: <Store className="w-5 h-5" /> },
    { id: 'voice', label: 'Voz', icon: <Mic className="w-5 h-5" /> },
    { id: 'gestures', label: 'Gestos', icon: <Hand className="w-5 h-5" /> },
    { id: 'ar', label: 'AR', icon: <Camera className="w-5 h-5" /> },
    { id: 'simulator', label: 'Simulador', icon: <Play className="w-5 h-5" /> },
    { id: 'code', label: 'Editor', icon: <Code className="w-5 h-5" /> },
    { id: 'terminal', label: 'Terminal', icon: <TerminalIcon className="w-5 h-5" /> },
    { id: 'versions', label: 'Versiones', icon: <GitBranch className="w-5 h-5" /> },
    { id: 'tests', label: 'Pruebas', icon: <TestTube className="w-5 h-5" /> },
    { id: 'permissions', label: 'Permisos', icon: <ShieldIcon className="w-5 h-5" /> },
    { id: 'api-integrations', label: 'APIs', icon: <Plug className="w-5 h-5" /> },
    { id: 'backup-scheduler', label: 'Backups', icon: <Calendar className="w-5 h-5" /> },
    { id: 'smart-alerts', label: 'Alertas Inteligentes', icon: <BellIcon className="w-5 h-5" /> },
    { id: 'realtime-dashboard', label: 'Dashboard RT', icon: <ActivityIcon className="w-5 h-5" /> },
    { id: 'event-log', label: 'Eventos', icon: <FileTextIcon className="w-5 h-5" /> },
    { id: 'system-health', label: 'Salud', icon: <Heart className="w-5 h-5" /> },
    { id: 'notification-settings', label: 'Notificaciones', icon: <BellSettingsIcon className="w-5 h-5" /> },
    { id: 'data-sync', label: 'Sincronización', icon: <RefreshCwIcon className="w-5 h-5" /> },
    { id: 'resource-monitor', label: 'Recursos', icon: <Monitor className="w-5 h-5" /> },
    { id: 'activity-feed', label: 'Actividad', icon: <ActivityFeedIcon className="w-5 h-5" /> },
    { id: 'audit-log', label: 'Auditoría', icon: <AuditIcon className="w-5 h-5" /> },
    { id: 'user-management', label: 'Usuarios', icon: <UsersIcon className="w-5 h-5" /> },
    { id: 'report-generator', label: 'Reportes', icon: <ReportIcon className="w-5 h-5" /> },
    { id: 'service-status', label: 'Servicios', icon: <Server className="w-5 h-5" /> },
    { id: 'advanced-analytics', label: 'Análisis Avanzado', icon: <AnalyticsIcon className="w-5 h-5" /> },
    { id: 'configuration-manager', label: 'Configuración', icon: <ConfigIcon className="w-5 h-5" /> },
    { id: 'data-backup', label: 'Respaldo', icon: <BackupIcon className="w-5 h-5" /> },
    { id: 'network-monitor', label: 'Red', icon: <Network className="w-5 h-5" /> },
    { id: 'security-center', label: 'Seguridad', icon: <SecurityIcon className="w-5 h-5" /> },
    { id: 'performance-tuning', label: 'Ajuste', icon: <TuningIcon className="w-5 h-5" /> },
    { id: 'error-tracker', label: 'Errores', icon: <Bug className="w-5 h-5" /> },
    { id: 'system-metrics', label: 'Métricas', icon: <MetricsIcon className="w-5 h-5" /> },
    { id: 'task-scheduler', label: 'Tareas', icon: <TaskIcon className="w-5 h-5" /> },
    { id: 'data-explorer', label: 'Datos', icon: <DataIcon className="w-5 h-5" /> },
    { id: 'log-analyzer', label: 'Análisis Logs', icon: <FileSearch className="w-5 h-5" /> },
    { id: 'system-diagnostics', label: 'Diagnósticos', icon: <DiagIcon className="w-5 h-5" /> },
    { id: 'api-docs', label: 'API Docs', icon: <BookIcon className="w-5 h-5" /> },
    { id: 'quick-actions-panel', label: 'Acciones', icon: <ZapPanelIcon className="w-5 h-5" /> },
    { id: 'system-info', label: 'Info Sistema', icon: <InfoIcon className="w-5 h-5" /> },
    { id: 'command-palette', label: 'Paleta', icon: <CommandIcon className="w-5 h-5" /> },
    { id: 'workflow-builder', label: 'Workflows', icon: <Workflow className="w-5 h-5" /> },
    { id: 'data-pipeline', label: 'Pipeline', icon: <PipelineIcon className="w-5 h-5" /> },
    { id: 'monitoring-dashboard', label: 'Monitoreo', icon: <MonitorIcon className="w-5 h-5" /> },
    { id: 'settings-advanced', label: 'Config Avanzada', icon: <SettingsAdvancedIcon className="w-5 h-5" /> },
    { id: 'data-visualization', label: 'Visualización', icon: <DataVizIcon className="w-5 h-5" /> },
    { id: 'alert-manager', label: 'Gestor Alertas', icon: <AlertMgrIcon className="w-5 h-5" /> },
    { id: 'performance-profiler', label: 'Perfilador', icon: <ProfilerIcon className="w-5 h-5" /> },
    { id: 'system-tweaks', label: 'Ajustes', icon: <Sliders className="w-5 h-5" /> },
    { id: 'logs', label: 'Logs', icon: <TerminalIcon className="w-5 h-5" /> },
    { id: 'alerts', label: 'Alertas', icon: <Bell className="w-5 h-5" /> },
    { id: 'help', label: 'Ayuda', icon: <HelpCircle className="w-5 h-5" /> },
    { id: 'settings', label: 'Config', icon: <Cog className="w-5 h-5" /> },
  ];

  return (
    <div className="min-h-screen p-4 relative">
      <KeyboardNavigation />
      <OnboardingTour />
      <ToastContainer />
      {/* Header */}
      <header className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              Robot Movement AI
            </h1>
            <p className="text-gray-300">
              Plataforma IA de Movimiento Robótico
            </p>
          </div>
          <div className="flex items-center gap-4">
            <SearchBar
              onResultSelect={(result) => {
                if (result.type === 'tab') {
                  const tabId = result.id.replace('tab-', '') as Tab;
                  setActiveTab(tabId);
                }
              }}
              tabs={tabs.map((tab) => ({
                id: tab.id,
                label: tab.label,
                action: () => setActiveTab(tab.id),
              }))}
            />
            <LanguageSelector />
            <div
              className={`px-4 py-2 rounded-lg ${
                status?.robot_status.connected
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-red-500/20 text-red-400'
              }`}
            >
              {status?.robot_status.connected ? 'Conectado' : 'Desconectado'}
            </div>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 flex gap-2 border-b border-gray-700 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 font-medium transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'text-primary-400 border-b-2 border-primary-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            {tab.icon}
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {activeTab === 'control' && <RobotControl />}
          {activeTab === 'chat' && <ChatPanel />}
          {activeTab === '3d' && <Fullscreen3D />}
          {activeTab === 'status' && <StatusPanel />}
          {activeTab === 'metrics' && <MetricsPanel />}
          {activeTab === 'history' && <MovementHistory />}
          {activeTab === 'optimize' && <TrajectoryOptimizer />}
          {activeTab === 'recording' && <RecordingPanel />}
          {activeTab === 'advanced' && <AdvancedMetrics />}
          {activeTab === 'compare' && <TrajectoryComparison />}
          {activeTab === 'commands' && <CustomCommands />}
          {activeTab === 'widgets' && <WidgetDashboard />}
          {activeTab === 'reports' && <ReportsPanel />}
          {activeTab === 'predictive' && <PredictiveAnalysis />}
          {activeTab === 'collaboration' && <CollaborationPanel />}
          {activeTab === 'auth' && <AuthPanel />}
          {activeTab === 'performance' && <PerformanceMonitor />}
          {activeTab === 'integrations' && <BackendIntegrations />}
          {activeTab === 'export' && <DataExport />}
          {activeTab === 'diagnostics' && <SystemDiagnostics />}
          {activeTab === 'realtime' && <RealTimeVisualization />}
          {activeTab === 'energy' && <EnergyOptimization />}
          {activeTab === 'safety' && <SafetyMonitor />}
          {activeTab === 'cmdhistory' && <CommandHistory />}
          {activeTab === 'presets' && <PresetPositions />}
          {activeTab === 'backup' && <SystemBackup />}
          {activeTab === 'notifications' && <NotificationCenter />}
          {activeTab === 'shortcuts' && <ShortcutsGuide />}
          {activeTab === 'systeminfo' && <SystemInfo />}
          {activeTab === 'timeline' && <ActivityTimeline />}
          {activeTab === 'theme' && <ThemeCustomizer />}
          {activeTab === 'visualization' && <DataVisualization />}
          {activeTab === 'remote' && <RemoteControl />}
          {activeTab === 'calibration' && <CalibrationPanel />}
          {activeTab === 'maintenance' && <MaintenancePanel />}
          {activeTab === 'docs' && <DocumentationViewer />}
          {activeTab === 'license' && <LicenseManager />}
          {activeTab === 'updates' && <UpdateChecker />}
          {activeTab === 'feedback' && <FeedbackPanel />}
          {activeTab === 'about' && <AboutPanel />}
          {activeTab === 'favorites' && <FavoritesManager />}
          {activeTab === 'usage' && <UsageStatistics />}
          {activeTab === 'accessibility' && <AccessibilityPanel />}
          {activeTab === 'optimizer' && <PerformanceOptimizer />}
          {activeTab === 'templates' && <TemplatesManager />}
          {activeTab === 'advanced-search' && <AdvancedSearch />}
          {activeTab === 'plugins' && <PluginManager />}
          {activeTab === 'workspaces' && <WorkspaceManager />}
          {activeTab === 'sessions' && <SessionRecorder />}
          {activeTab === 'quick-access' && <QuickAccess />}
          {activeTab === 'analytics' && <DataAnalytics />}
          {activeTab === 'automation' && <AutomationPanel />}
          {activeTab === 'cloud' && <CloudSync />}
          {activeTab === 'ai-assistant' && <AIAssistant />}
          {activeTab === 'learning' && <LearningCenter />}
          {activeTab === 'marketplace' && <Marketplace />}
          {activeTab === 'voice' && <VoiceControl />}
          {activeTab === 'gestures' && <GestureControl />}
          {activeTab === 'ar' && <ARView />}
          {activeTab === 'simulator' && <TrajectorySimulator />}
          {activeTab === 'code' && <CodeEditor />}
          {activeTab === 'terminal' && <Terminal />}
          {activeTab === 'versions' && <VersionControl />}
          {activeTab === 'tests' && <TestSuite />}
          {activeTab === 'permissions' && <PermissionsManager />}
          {activeTab === 'api-integrations' && <APIIntegrations />}
          {activeTab === 'backup-scheduler' && <BackupScheduler />}
          {activeTab === 'smart-alerts' && <SmartAlerts />}
          {activeTab === 'realtime-dashboard' && <RealTimeDashboard />}
          {activeTab === 'event-log' && <EventLog />}
          {activeTab === 'system-health' && <SystemHealth />}
          {activeTab === 'notification-settings' && <NotificationSettings />}
          {activeTab === 'data-sync' && <DataSync />}
          {activeTab === 'resource-monitor' && <ResourceMonitor />}
          {activeTab === 'activity-feed' && <ActivityFeed />}
          {activeTab === 'audit-log' && <AuditLog />}
          {activeTab === 'user-management' && <UserManagement />}
          {activeTab === 'report-generator' && <ReportGenerator />}
          {activeTab === 'service-status' && <ServiceStatus />}
          {activeTab === 'advanced-analytics' && <AdvancedAnalytics />}
          {activeTab === 'configuration-manager' && <ConfigurationManager />}
          {activeTab === 'data-backup' && <DataBackup />}
          {activeTab === 'network-monitor' && <NetworkMonitor />}
          {activeTab === 'security-center' && <SecurityCenter />}
          {activeTab === 'performance-tuning' && <PerformanceTuning />}
          {activeTab === 'error-tracker' && <ErrorTracker />}
          {activeTab === 'system-metrics' && <SystemMetrics />}
          {activeTab === 'task-scheduler' && <TaskScheduler />}
          {activeTab === 'data-explorer' && <DataExplorer />}
          {activeTab === 'log-analyzer' && <LogAnalyzer />}
          {activeTab === 'system-diagnostics' && <SystemDiagnostics />}
          {activeTab === 'api-docs' && <APIDocumentation />}
          {activeTab === 'quick-actions-panel' && <QuickActionsPanel />}
          {activeTab === 'system-info' && <SystemInfo />}
          {activeTab === 'command-palette' && <CommandPalette />}
          {activeTab === 'workflow-builder' && <WorkflowBuilder />}
          {activeTab === 'data-pipeline' && <DataPipeline />}
          {activeTab === 'monitoring-dashboard' && <MonitoringDashboard />}
          {activeTab === 'settings-advanced' && <SettingsAdvanced />}
          {activeTab === 'data-visualization' && <DataVisualization />}
          {activeTab === 'alert-manager' && <AlertManager />}
          {activeTab === 'performance-profiler' && <PerformanceProfiler />}
          {activeTab === 'system-tweaks' && <SystemTweaks />}
          {activeTab === 'logs' && <LogsPanel />}
          {activeTab === 'alerts' && <AlertsPanel />}
          {activeTab === 'help' && <HelpPanel />}
          {activeTab === 'settings' && <SettingsPanel />}
        </div>
        <CommandPalette />
        <div className="lg:col-span-1 space-y-6">
          <QuickStats />
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">
              Información Rápida
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-gray-400 text-sm">Marca del Robot</p>
                <p className="text-white font-medium">
                  {status?.config.robot_brand || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">ROS Habilitado</p>
                <p className="text-white font-medium">
                  {status?.config.ros_enabled ? 'Sí' : 'No'}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Frecuencia de Feedback</p>
                <p className="text-white font-medium">
                  {status?.config.feedback_frequency || 0} Hz
                </p>
              </div>
              {status?.robot_status.position && (
                <div>
                  <p className="text-gray-400 text-sm">Posición Actual</p>
                  <p className="text-white font-medium text-sm">
                    X: {status.robot_status.position.x.toFixed(3)} | Y:{' '}
                    {status.robot_status.position.y.toFixed(3)} | Z:{' '}
                    {status.robot_status.position.z.toFixed(3)}
                  </p>
                </div>
              )}
            </div>
          </div>
          <QuickActions />
        </div>
      </div>
    </div>
  );
}


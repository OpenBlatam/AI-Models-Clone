'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { 
  Shield, 
  Lock, 
  Eye, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Activity,
  TrendingUp,
  TrendingDown,
  Clock,
  Zap,
  Database,
  Network,
  Users,
  Settings,
  RefreshCw,
  Filter,
  Search,
  Download,
  Upload,
  Trash2,
  Plus,
  Edit,
  Save,
  Cancel,
  Bell,
  BellOff,
  ShieldCheck,
  Key,
  FileText,
  BarChart3,
  PieChart,
  LineChart,
  Globe,
  Smartphone,
  Monitor,
  Fingerprint,
  Camera,
  Mic,
  MousePointer,
  MapPin,
  Wifi,
  AlertCircle,
  Info,
  Play,
  Pause,
  Square,
  RotateCcw,
  Target,
  Crosshair,
  Radar,
  Satellite,
  WifiOff,
  WifiIcon,
  BookOpen,
  Clipboard,
  CheckSquare,
  Square as SquareIcon,
  AlertCircle as AlertCircleIcon,
  Info as InfoIcon,
  ExternalLink,
  Calendar,
  User,
  Mail,
  Phone,
  MessageSquare,
  FileCheck,
  FileX,
  FileAlert,
  FileText as FileTextIcon,
  File,
  Folder,
  FolderOpen,
  Archive,
  Tag,
  Tags,
  Flag,
  Star,
  Heart,
  ThumbsUp,
  ThumbsDown,
  Award,
  Trophy,
  Medal,
  Crown,
  Gem,
  Diamond,
  Zap as ZapIcon,
  Lightning,
  Flame,
  Sun,
  Moon,
  Cloud,
  CloudRain,
  CloudSnow,
  Wind,
  Thermometer,
  Droplets,
  TreePine,
  Mountain,
  Waves,
  Fish,
  Bird,
  Cat,
  Dog,
  Rabbit,
  Car,
  Truck,
  Bus,
  Train,
  Plane,
  Ship,
  Bike,
  Scooter,
  Skateboard,
  Gamepad2,
  Joystick,
  Headphones,
  Speaker,
  Mic as MicIcon,
  Video,
  Camera as CameraIcon,
  Image,
  Music,
  Play as PlayIcon,
  Pause as PauseIcon,
  Stop,
  SkipBack,
  SkipForward,
  Repeat,
  Shuffle,
  Volume2,
  VolumeX,
  Volume1,
  Volume,
  Radio,
  Tv,
  Monitor as MonitorIcon,
  Laptop,
  Smartphone as SmartphoneIcon,
  Tablet,
  Watch,
  Headphones as HeadphonesIcon,
  Speaker as SpeakerIcon,
  Mic as MicIcon2,
  Video as VideoIcon,
  Camera as CameraIcon2,
  Image as ImageIcon,
  Music as MusicIcon,
  Play as PlayIcon2,
  Pause as PauseIcon2,
  Stop as StopIcon,
  SkipBack as SkipBackIcon,
  SkipForward as SkipForwardIcon,
  Repeat as RepeatIcon,
  Shuffle as ShuffleIcon,
  Volume2 as Volume2Icon,
  VolumeX as VolumeXIcon,
  Volume1 as Volume1Icon,
  Volume as VolumeIcon,
  Radio as RadioIcon,
  Tv as TvIcon,
  Monitor as MonitorIcon2,
  Laptop as LaptopIcon,
  Smartphone as SmartphoneIcon2,
  Tablet as TabletIcon,
  Watch as WatchIcon,
  Workflow,
  GitBranch,
  GitCommit,
  GitMerge,
  GitPullRequest,
  GitCompare,
  GitBranch as GitBranchIcon,
  GitCommit as GitCommitIcon,
  GitMerge as GitMergeIcon,
  GitPullRequest as GitPullRequestIcon,
  GitCompare as GitCompareIcon,
  ArrowRight,
  ArrowLeft,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
  ArrowLeftRight,
  ArrowRightLeft,
  ArrowUpLeft,
  ArrowUpRight,
  ArrowDownLeft,
  ArrowDownRight,
  ArrowUpFromLine,
  ArrowDownFromLine,
  ArrowLeftFromLine,
  ArrowRightFromLine,
  ArrowUpToLine,
  ArrowDownToLine,
  ArrowLeftToLine,
  ArrowRightToLine,
  ArrowUpFromLine as ArrowUpFromLineIcon,
  ArrowDownFromLine as ArrowDownFromLineIcon,
  ArrowLeftFromLine as ArrowLeftFromLineIcon,
  ArrowRightFromLine as ArrowRightFromLineIcon,
  ArrowUpToLine as ArrowUpToLineIcon,
  ArrowDownToLine as ArrowDownToLineIcon,
  ArrowLeftToLine as ArrowLeftToLineIcon,
  ArrowRightToLine as ArrowRightToLineIcon,
  ArrowUpFromLine as ArrowUpFromLineIcon2,
  ArrowDownFromLine as ArrowDownFromLineIcon2,
  ArrowLeftFromLine as ArrowLeftFromLineIcon2,
  ArrowRightFromLine as ArrowRightFromLineIcon2,
  ArrowUpToLine as ArrowUpToLineIcon2,
  ArrowDownToLine as ArrowDownToLineIcon2,
  ArrowLeftToLine as ArrowLeftToLineIcon2,
  ArrowRightToLine as ArrowRightToLineIcon2
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface SecurityPlaybook {
  id: string;
  name: string;
  description: string;
  trigger: {
    type: 'threat' | 'anomaly' | 'breach' | 'policy_violation' | 'system_error';
    severity: 'low' | 'medium' | 'high' | 'critical';
    conditions: string[];
  };
  actions: Array<{
    type: 'block' | 'isolate' | 'notify' | 'escalate' | 'investigate' | 'remediate';
    target: string;
    parameters: any;
    delay?: number;
  }>;
  enabled: boolean;
  createdAt: number;
  lastExecuted?: number;
  executionCount: number;
}

interface SecurityWorkflow {
  id: string;
  name: string;
  description: string;
  steps: Array<{
    id: string;
    name: string;
    type: 'action' | 'decision' | 'parallel' | 'wait';
    parameters: any;
    conditions?: string[];
    nextSteps?: string[];
  }>;
  status: 'active' | 'paused' | 'completed' | 'failed';
  createdAt: number;
  updatedAt: number;
}

interface SecurityIncident {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'contained' | 'resolved' | 'closed';
  playbookId?: string;
  workflowId?: string;
  assignedTo?: string;
  createdAt: number;
  updatedAt: number;
  resolvedAt?: number;
  metadata: any;
}

export function SecurityOrchestrationDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [playbooks, setPlaybooks] = useState<SecurityPlaybook[]>([]);
  const [workflows, setWorkflows] = useState<SecurityWorkflow[]>([]);
  const [incidents, setIncidents] = useState<SecurityIncident[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlaybook, setSelectedPlaybook] = useState<string>('');
  const [showEnabledOnly, setShowEnabledOnly] = useState(false);

  // Fetch orchestration data
  const fetchOrchestrationData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Fetch playbooks
      const playbooksResponse = await fetch('/api/security/orchestration/playbooks');
      if (playbooksResponse.ok) {
        const playbooksData = await playbooksResponse.json();
        setPlaybooks(playbooksData);
      }

      // Fetch workflows
      const workflowsResponse = await fetch('/api/security/orchestration/workflows');
      if (workflowsResponse.ok) {
        const workflowsData = await workflowsResponse.json();
        setWorkflows(workflowsData);
      }

      // Fetch incidents
      const incidentsResponse = await fetch('/api/security/orchestration/incidents');
      if (incidentsResponse.ok) {
        const incidentsData = await incidentsResponse.json();
        setIncidents(incidentsData);
      }
    } catch (error) {
      console.error('Failed to fetch orchestration data:', error);
      toast.error('Failed to fetch orchestration data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    fetchOrchestrationData();
  }, [fetchOrchestrationData]);

  // Get orchestration statistics
  const getOrchestrationStats = () => {
    const totalPlaybooks = playbooks.length;
    const enabledPlaybooks = playbooks.filter(p => p.enabled).length;
    const totalExecutions = playbooks.reduce((sum, p) => sum + p.executionCount, 0);
    const totalWorkflows = workflows.length;
    const activeWorkflows = workflows.filter(w => w.status === 'active').length;
    const totalIncidents = incidents.length;
    const openIncidents = incidents.filter(i => i.status === 'open').length;
    const resolvedIncidents = incidents.filter(i => i.status === 'resolved').length;

    return {
      totalPlaybooks,
      enabledPlaybooks,
      totalExecutions,
      totalWorkflows,
      activeWorkflows,
      totalIncidents,
      openIncidents,
      resolvedIncidents,
    };
  };

  const stats = getOrchestrationStats();

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'low': return 'text-blue-600 bg-blue-100 border-blue-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'completed': return 'text-green-600 bg-green-100';
      case 'resolved': return 'text-green-600 bg-green-100';
      case 'enabled': return 'text-green-600 bg-green-100';
      case 'in_progress': return 'text-yellow-600 bg-yellow-100';
      case 'investigating': return 'text-yellow-600 bg-yellow-100';
      case 'contained': return 'text-yellow-600 bg-yellow-100';
      case 'paused': return 'text-blue-600 bg-blue-100';
      case 'open': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'closed': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // Get action type icon
  const getActionTypeIcon = (type: string) => {
    switch (type) {
      case 'block': return <Lock className="h-4 w-4" />;
      case 'isolate': return <Shield className="h-4 w-4" />;
      case 'notify': return <Bell className="h-4 w-4" />;
      case 'escalate': return <ArrowUp className="h-4 w-4" />;
      case 'investigate': return <Search className="h-4 w-4" />;
      case 'remediate': return <CheckCircle className="h-4 w-4" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  // Filter data
  const filteredPlaybooks = playbooks.filter(playbook => {
    const matchesSearch = playbook.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         playbook.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesEnabled = !showEnabledOnly || playbook.enabled;
    return matchesSearch && matchesEnabled;
  });

  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         workflow.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  const filteredIncidents = incidents.filter(incident => {
    const matchesSearch = incident.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         incident.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Security Orchestration Dashboard</h2>
          <p className="text-muted-foreground">
            Automated security response and incident management
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchOrchestrationData} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Orchestration Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Playbooks</CardTitle>
            <Workflow className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalPlaybooks}</div>
            <p className="text-xs text-muted-foreground">
              {stats.enabledPlaybooks} enabled
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Executions</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalExecutions}</div>
            <p className="text-xs text-muted-foreground">
              Automated responses
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
            <GitBranch className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeWorkflows}</div>
            <p className="text-xs text-muted-foreground">
              {stats.totalWorkflows} total workflows
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Incidents</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalIncidents}</div>
            <p className="text-xs text-muted-foreground">
              {stats.openIncidents} open • {stats.resolvedIncidents} resolved
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="playbooks">Playbooks</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Playbook Executions */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Playbook Executions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {playbooks
                    .filter(p => p.lastExecuted)
                    .sort((a, b) => (b.lastExecuted || 0) - (a.lastExecuted || 0))
                    .slice(0, 5)
                    .map((playbook) => (
                    <div key={playbook.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Workflow className="h-4 w-4" />
                        <div>
                          <div className="font-medium">{playbook.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {playbook.executionCount} executions • {new Date(playbook.lastExecuted!).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <Badge className={getStatusColor(playbook.enabled ? 'enabled' : 'disabled')}>
                        {playbook.enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Active Workflows */}
            <Card>
              <CardHeader>
                <CardTitle>Active Workflows</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {workflows
                    .filter(w => w.status === 'active')
                    .slice(0, 5)
                    .map((workflow) => (
                    <div key={workflow.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <GitBranch className="h-4 w-4" />
                        <div>
                          <div className="font-medium">{workflow.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {workflow.steps.length} steps • {new Date(workflow.createdAt).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <Badge className={getStatusColor(workflow.status)}>
                        {workflow.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Incidents */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Security Incidents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {incidents
                  .sort((a, b) => b.createdAt - a.createdAt)
                  .slice(0, 5)
                  .map((incident) => (
                  <div key={incident.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <AlertTriangle className="h-4 w-4" />
                      <div>
                        <div className="font-medium">{incident.title}</div>
                        <div className="text-sm text-muted-foreground">
                          {incident.description} • {new Date(incident.createdAt).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getSeverityColor(incident.severity)}>
                        {incident.severity}
                      </Badge>
                      <Badge className={getStatusColor(incident.status)}>
                        {incident.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Playbooks Tab */}
        <TabsContent value="playbooks" className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Input
                  placeholder="Search playbooks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64"
                />
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  checked={showEnabledOnly}
                  onCheckedChange={setShowEnabledOnly}
                />
                <Label>Show enabled only</Label>
              </div>
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Playbook
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredPlaybooks.map((playbook) => (
              <Card key={playbook.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{playbook.name}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge className={getSeverityColor(playbook.trigger.severity)}>
                        {playbook.trigger.severity}
                      </Badge>
                      <Badge className={getStatusColor(playbook.enabled ? 'enabled' : 'disabled')}>
                        {playbook.enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">{playbook.description}</p>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Trigger:</span> {playbook.trigger.type}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Actions:</span> {playbook.actions.length}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Executions:</span> {playbook.executionCount}
                    </div>
                    {playbook.lastExecuted && (
                      <div className="text-sm">
                        <span className="font-medium">Last Executed:</span> {new Date(playbook.lastExecuted).toLocaleString()}
                      </div>
                    )}
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm font-medium">Actions:</div>
                    <div className="flex flex-wrap gap-1">
                      {playbook.actions.map((action, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {getActionTypeIcon(action.type)}
                          <span className="ml-1">{action.type}</span>
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Eye className="h-3 w-3 mr-1" />
                      View
                    </Button>
                    <Button variant="outline" size="sm">
                      <Edit className="h-3 w-3 mr-1" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm">
                      <Play className="h-3 w-3 mr-1" />
                      Test
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Input
                  placeholder="Search workflows..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64"
                />
              </div>
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Workflow
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredWorkflows.map((workflow) => (
              <Card key={workflow.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{workflow.name}</CardTitle>
                    <Badge className={getStatusColor(workflow.status)}>
                      {workflow.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">{workflow.description}</p>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Steps:</span> {workflow.steps.length}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Created:</span> {new Date(workflow.createdAt).toLocaleDateString()}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Updated:</span> {new Date(workflow.updatedAt).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm font-medium">Workflow Steps:</div>
                    <div className="space-y-1">
                      {workflow.steps.slice(0, 3).map((step, index) => (
                        <div key={step.id} className="flex items-center gap-2 text-xs">
                          <Badge variant="outline" className="text-xs">
                            {step.type}
                          </Badge>
                          <span>{step.name}</span>
                        </div>
                      ))}
                      {workflow.steps.length > 3 && (
                        <div className="text-xs text-muted-foreground">
                          +{workflow.steps.length - 3} more steps
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Eye className="h-3 w-3 mr-1" />
                      View
                    </Button>
                    <Button variant="outline" size="sm">
                      <Edit className="h-3 w-3 mr-1" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm">
                      <Play className="h-3 w-3 mr-1" />
                      Execute
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Incidents Tab */}
        <TabsContent value="incidents" className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Input
                  placeholder="Search incidents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64"
                />
              </div>
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Incident
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredIncidents.map((incident) => (
              <Card key={incident.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{incident.title}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge className={getSeverityColor(incident.severity)}>
                        {incident.severity}
                      </Badge>
                      <Badge className={getStatusColor(incident.status)}>
                        {incident.status}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">{incident.description}</p>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Created:</span> {new Date(incident.createdAt).toLocaleString()}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Updated:</span> {new Date(incident.updatedAt).toLocaleString()}
                    </div>
                    {incident.assignedTo && (
                      <div className="text-sm">
                        <span className="font-medium">Assigned to:</span> {incident.assignedTo}
                      </div>
                    )}
                    {incident.playbookId && (
                      <div className="text-sm">
                        <span className="font-medium">Playbook:</span> {playbooks.find(p => p.id === incident.playbookId)?.name}
                      </div>
                    )}
                    {incident.workflowId && (
                      <div className="text-sm">
                        <span className="font-medium">Workflow:</span> {workflows.find(w => w.id === incident.workflowId)?.name}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Eye className="h-3 w-3 mr-1" />
                      View
                    </Button>
                    <Button variant="outline" size="sm">
                      <Edit className="h-3 w-3 mr-1" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Resolve
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

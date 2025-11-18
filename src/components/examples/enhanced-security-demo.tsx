'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Shield, 
  Lock, 
  Eye, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Activity,
  TrendingUp,
  Users,
  Globe,
  Smartphone,
  Monitor,
  Zap,
  Database,
  Network,
  Fingerprint,
  Camera,
  Mic,
  MousePointer,
  Clock,
  MapPin,
  Wifi,
  ShieldCheck,
  AlertCircle,
  Info
} from 'lucide-react';
import { useBiometricAuth } from '@/hooks/security/use-biometric-auth';
import { toast } from 'react-hot-toast';

export function EnhancedSecurityDemo() {
  const [activeTab, setActiveTab] = useState('overview');
  const [trustScore, setTrustScore] = useState(85);
  const [riskLevel, setRiskLevel] = useState<'low' | 'medium' | 'high' | 'critical'>('low');
  const [securityEvents, setSecurityEvents] = useState<any[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(true);
  
  const biometricAuth = useBiometricAuth();

  // Simulate security events
  useEffect(() => {
    const events = [
      {
        id: '1',
        type: 'login',
        timestamp: Date.now() - 300000,
        severity: 'low',
        description: 'Successful login from trusted device',
        ip: '192.168.1.100',
        location: 'San Francisco, CA',
      },
      {
        id: '2',
        type: 'threat_detected',
        timestamp: Date.now() - 600000,
        severity: 'medium',
        description: 'Suspicious login attempt detected',
        ip: '203.0.113.1',
        location: 'Unknown',
      },
      {
        id: '3',
        type: 'biometric_auth',
        timestamp: Date.now() - 900000,
        severity: 'low',
        description: 'Fingerprint authentication successful',
        ip: '192.168.1.100',
        location: 'San Francisco, CA',
      },
    ];
    
    setSecurityEvents(events);
  }, []);

  // Simulate trust score updates
  useEffect(() => {
    if (isMonitoring) {
      const interval = setInterval(() => {
        setTrustScore(prev => {
          const change = (Math.random() - 0.5) * 10;
          const newScore = Math.max(0, Math.min(100, prev + change));
          
          if (newScore >= 80) setRiskLevel('low');
          else if (newScore >= 60) setRiskLevel('medium');
          else if (newScore >= 40) setRiskLevel('high');
          else setRiskLevel('critical');
          
          return newScore;
        });
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [isMonitoring]);

  const handleBiometricAuth = async (type: string) => {
    const result = await biometricAuth.authenticate(type);
    if (result?.success) {
      toast.success(`${type} authentication successful`);
    } else {
      toast.error(`${type} authentication failed`);
    }
  };

  const handleBiometricRegister = async (type: string) => {
    const result = await biometricAuth.register(`${type} credential`);
    if (result) {
      toast.success(`${type} credential registered`);
    } else {
      toast.error(`${type} registration failed`);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'low': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'medium': return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      case 'high': return <AlertTriangle className="h-4 w-4 text-orange-600" />;
      case 'critical': return <XCircle className="h-4 w-4 text-red-600" />;
      default: return <Info className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Enhanced Security Demo</h2>
          <p className="text-muted-foreground">
            Comprehensive security features and zero-trust architecture
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={getRiskColor(riskLevel)}>
            Risk Level: {riskLevel.toUpperCase()}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsMonitoring(!isMonitoring)}
          >
            {isMonitoring ? <Eye className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
            {isMonitoring ? 'Stop' : 'Start'} Monitoring
          </Button>
        </div>
      </div>

      {/* Trust Score Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trust Score</CardTitle>
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{trustScore}</div>
            <Progress value={trustScore} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">
              {trustScore >= 80 ? 'High trust' : trustScore >= 60 ? 'Medium trust' : 'Low trust'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Biometric Support</CardTitle>
            <Fingerprint className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {biometricAuth.isSupported ? 'Yes' : 'No'}
            </div>
            <p className="text-xs text-muted-foreground">
              {biometricAuth.credentials.length} credentials
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Events</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{securityEvents.length}</div>
            <p className="text-xs text-muted-foreground">
              Last 24 hours
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Threats Blocked</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">12</div>
            <p className="text-xs text-muted-foreground">
              This week
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="biometric">Biometric</TabsTrigger>
          <TabsTrigger value="zero-trust">Zero Trust</TabsTrigger>
          <TabsTrigger value="threats">Threats</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Security Status */}
            <Card>
              <CardHeader>
                <CardTitle>Security Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Zero Trust Architecture</span>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Continuous Verification</span>
                  <Badge className="text-green-600 bg-green-100">Enabled</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Threat Detection</span>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Biometric Authentication</span>
                  <Badge className={biometricAuth.isSupported ? "text-green-600 bg-green-100" : "text-red-600 bg-red-100"}>
                    {biometricAuth.isSupported ? 'Available' : 'Unavailable'}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Trust Factors */}
            <Card>
              <CardHeader>
                <CardTitle>Trust Factors</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Device Trust</span>
                    <span className="text-sm font-medium">85%</span>
                  </div>
                  <Progress value={85} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Location Trust</span>
                    <span className="text-sm font-medium">92%</span>
                  </div>
                  <Progress value={92} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Network Trust</span>
                    <span className="text-sm font-medium">78%</span>
                  </div>
                  <Progress value={78} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Behavioral Trust</span>
                    <span className="text-sm font-medium">88%</span>
                  </div>
                  <Progress value={88} className="h-2" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Security Events */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Security Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {securityEvents.map((event) => (
                  <div key={event.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {getSeverityIcon(event.severity)}
                      <div>
                        <div className="font-medium">{event.description}</div>
                        <div className="text-sm text-muted-foreground">
                          {event.ip} • {event.location} • {new Date(event.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <Badge className={getRiskColor(event.severity)}>
                      {event.severity}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Biometric Tab */}
        <TabsContent value="biometric" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Biometric Authentication */}
            <Card>
              <CardHeader>
                <CardTitle>Biometric Authentication</CardTitle>
                <CardDescription>
                  Test different biometric authentication methods
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    variant="outline"
                    onClick={() => handleBiometricAuth('webauthn')}
                    disabled={biometricAuth.isAuthenticating}
                  >
                    <Fingerprint className="h-4 w-4 mr-2" />
                    WebAuthn
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleBiometricAuth('fingerprint')}
                    disabled={biometricAuth.isAuthenticating}
                  >
                    <Fingerprint className="h-4 w-4 mr-2" />
                    Fingerprint
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleBiometricAuth('face')}
                    disabled={biometricAuth.isAuthenticating}
                  >
                    <Camera className="h-4 w-4 mr-2" />
                    Face ID
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleBiometricAuth('voice')}
                    disabled={biometricAuth.isAuthenticating}
                  >
                    <Mic className="h-4 w-4 mr-2" />
                    Voice
                  </Button>
                </div>
                
                {biometricAuth.error && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{biometricAuth.error}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* Biometric Registration */}
            <Card>
              <CardHeader>
                <CardTitle>Register Credentials</CardTitle>
                <CardDescription>
                  Register new biometric credentials
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    variant="outline"
                    onClick={() => handleBiometricRegister('webauthn')}
                    disabled={biometricAuth.isAuthenticating}
                  >
                    <Fingerprint className="h-4 w-4 mr-2" />
                    Register WebAuthn
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleBiometricRegister('fingerprint')}
                    disabled={biometricAuth.isAuthenticating}
                  >
                    <Fingerprint className="h-4 w-4 mr-2" />
                    Register Fingerprint
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleBiometricRegister('face')}
                    disabled={biometricAuth.isAuthenticating}
                  >
                    <Camera className="h-4 w-4 mr-2" />
                    Register Face ID
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleBiometricRegister('voice')}
                    disabled={biometricAuth.isAuthenticating}
                  >
                    <Mic className="h-4 w-4 mr-2" />
                    Register Voice
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Registered Credentials */}
          <Card>
            <CardHeader>
              <CardTitle>Registered Credentials</CardTitle>
            </CardHeader>
            <CardContent>
              {biometricAuth.credentials.length > 0 ? (
                <div className="space-y-3">
                  {biometricAuth.credentials.map((credential) => (
                    <div key={credential.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Fingerprint className="h-4 w-4" />
                        <div>
                          <div className="font-medium">{credential.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {credential.type} • Registered {new Date(credential.createdAt).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <Badge variant="outline">Active</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No biometric credentials registered
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Zero Trust Tab */}
        <TabsContent value="zero-trust" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Zero Trust Principles */}
            <Card>
              <CardHeader>
                <CardTitle>Zero Trust Principles</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-medium">Never Trust, Always Verify</div>
                    <div className="text-sm text-muted-foreground">
                      Every request is verified regardless of source
                    </div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Eye className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-medium">Continuous Monitoring</div>
                    <div className="text-sm text-muted-foreground">
                      Real-time security context evaluation
                    </div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Lock className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-medium">Least Privilege Access</div>
                    <div className="text-sm text-muted-foreground">
                      Minimal access rights based on trust score
                    </div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Activity className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-medium">Adaptive Authentication</div>
                    <div className="text-sm text-muted-foreground">
                      Dynamic security requirements based on risk
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Security Context */}
            <Card>
              <CardHeader>
                <CardTitle>Security Context</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Device Type</span>
                  <div className="flex items-center gap-2">
                    <Monitor className="h-4 w-4" />
                    <span className="text-sm font-medium">Desktop</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Location</span>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    <span className="text-sm font-medium">San Francisco, CA</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Network</span>
                  <div className="flex items-center gap-2">
                    <Wifi className="h-4 w-4" />
                    <span className="text-sm font-medium">Trusted Network</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Session Duration</span>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    <span className="text-sm font-medium">2h 15m</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Trust Score Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Trust Score Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Device Trust</span>
                    <span className="text-sm font-medium">85%</span>
                  </div>
                  <Progress value={85} className="h-2" />
                  <div className="text-xs text-muted-foreground">
                    Device fingerprint, encryption, and history
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Location Trust</span>
                    <span className="text-sm font-medium">92%</span>
                  </div>
                  <Progress value={92} className="h-2" />
                  <div className="text-xs text-muted-foreground">
                    Geolocation consistency and anomaly detection
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Network Trust</span>
                    <span className="text-sm font-medium">78%</span>
                  </div>
                  <Progress value={78} className="h-2" />
                  <div className="text-xs text-muted-foreground">
                    VPN, proxy, and Tor detection
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Behavioral Trust</span>
                    <span className="text-sm font-medium">88%</span>
                  </div>
                  <Progress value={88} className="h-2" />
                  <div className="text-xs text-muted-foreground">
                    Typing patterns, mouse movements, and usage habits
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Threats Tab */}
        <TabsContent value="threats" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">SQL Injection</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">3</div>
                <p className="text-xs text-muted-foreground">
                  Blocked attempts
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">XSS Attacks</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">7</div>
                <p className="text-xs text-muted-foreground">
                  Blocked attempts
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Brute Force</CardTitle>
                <Lock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">12</div>
                <p className="text-xs text-muted-foreground">
                  Blocked attempts
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Threat Detection Rules</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Database className="h-4 w-4 text-red-600" />
                    <div>
                      <div className="font-medium">SQL Injection Detection</div>
                      <div className="text-sm text-muted-foreground">
                        Pattern: /(union|select|insert|update|delete)/i
                      </div>
                    </div>
                  </div>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    <div>
                      <div className="font-medium">XSS Attack Detection</div>
                      <div className="text-sm text-muted-foreground">
                        Pattern: /<script[^>]*>.*?<\/script>/i
                      </div>
                    </div>
                  </div>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Lock className="h-4 w-4 text-yellow-600" />
                    <div>
                      <div className="font-medium">Brute Force Detection</div>
                      <div className="text-sm text-muted-foreground">
                        Threshold: 5 failed attempts per minute
                      </div>
                    </div>
                  </div>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Security Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Detection Rate</span>
                  <span className="font-semibold">98.5%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">False Positives</span>
                  <span className="font-semibold">2.1%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Response Time</span>
                  <span className="font-semibold">45ms</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Uptime</span>
                  <span className="font-semibold">99.9%</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>User Behavior</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Active Users</span>
                  <span className="font-semibold">1,247</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Trusted Devices</span>
                  <span className="font-semibold">892</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Biometric Logins</span>
                  <span className="font-semibold">3,456</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Risk Events</span>
                  <span className="font-semibold">23</span>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Geographic Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">United States</span>
                  <div className="flex items-center gap-2">
                    <Progress value={65} className="w-32 h-2" />
                    <span className="text-sm font-medium">65%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Europe</span>
                  <div className="flex items-center gap-2">
                    <Progress value={20} className="w-32 h-2" />
                    <span className="text-sm font-medium">20%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Asia</span>
                  <div className="flex items-center gap-2">
                    <Progress value={10} className="w-32 h-2" />
                    <span className="text-sm font-medium">10%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Other</span>
                  <div className="flex items-center gap-2">
                    <Progress value={5} className="w-32 h-2" />
                    <span className="text-sm font-medium">5%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

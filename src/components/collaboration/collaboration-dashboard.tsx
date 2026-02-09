'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  MessageSquare, 
  Code, 
  Bug, 
  Play, 
  Pause, 
  Square,
  Plus,
  Settings,
  Video,
  Mic,
  MicOff,
  Monitor,
  MonitorOff,
  UserPlus,
  UserMinus,
  Clock,
  CheckCircle,
  AlertCircle,
  Activity,
  Eye,
  Edit,
  Trash2,
  Reply,
  Resolve
} from 'lucide-react';
import { 
  realtimeCollaboration,
  collaborationUtils,
  type CollaborationSession,
  type CollaborationUser,
  type CollaborationComment,
  type DebugSession,
  type Breakpoint
} from '@/lib/collaboration/realtime-collaboration';

interface CollaborationDashboardProps {
  className?: string;
}

export function CollaborationDashboard({ className }: CollaborationDashboardProps) {
  const [sessions, setSessions] = useState<CollaborationSession[]>([]);
  const [currentSession, setCurrentSession] = useState<CollaborationSession | null>(null);
  const [comments, setComments] = useState<CollaborationComment[]>([]);
  const [debugSessions, setDebugSessions] = useState<DebugSession[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [showCreateSession, setShowCreateSession] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [selectedLine, setSelectedLine] = useState<number>(0);
  const [statistics, setStatistics] = useState<any>(null);

  // Mock current user
  const currentUser: CollaborationUser = {
    id: 'user-1',
    name: 'John Doe',
    email: 'john@example.com',
    color: '#3B82F6',
    cursor: { x: 0, y: 0 },
    isActive: true,
    lastSeen: new Date().toISOString(),
    permissions: {
      canEdit: true,
      canComment: true,
      canDebug: true,
      canDeploy: false,
      canManageUsers: false,
    },
  };

  useEffect(() => {
    initializeCollaboration();
    loadSessions();
    loadStatistics();
  }, []);

  const initializeCollaboration = async () => {
    try {
      await collaborationUtils.initialize(currentUser);
      setIsConnected(true);
    } catch (error) {
      console.error('Failed to initialize collaboration:', error);
    }
  };

  const loadSessions = () => {
    const activeSessions = collaborationUtils.getActiveSessions();
    setSessions(activeSessions);
  };

  const loadStatistics = () => {
    const stats = collaborationUtils.getStatistics();
    setStatistics(stats);
  };

  const handleCreateSession = async () => {
    try {
      const session = await collaborationUtils.createSession(
        'New Collaboration Session',
        'A new collaborative development session',
        {
          maxParticipants: 5,
          enableLiveCoding: true,
          enableVoiceChat: false,
          enableScreenShare: false,
        }
      );
      setSessions([...sessions, session]);
      setShowCreateSession(false);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleJoinSession = async (sessionId: string) => {
    try {
      const session = await collaborationUtils.joinSession(sessionId);
      if (session) {
        setCurrentSession(session);
        loadComments(sessionId);
        loadDebugSessions(sessionId);
      }
    } catch (error) {
      console.error('Failed to join session:', error);
    }
  };

  const handleLeaveSession = async () => {
    if (currentSession) {
      await realtimeCollaboration.leaveSession(currentSession.id);
      setCurrentSession(null);
      setComments([]);
      setDebugSessions([]);
    }
  };

  const loadComments = (sessionId: string) => {
    // Mock comments for demonstration
    const mockComments: CollaborationComment[] = [
      {
        id: 'comment-1',
        userId: 'user-2',
        file: 'src/components/Button.tsx',
        line: 15,
        column: 10,
        content: 'This button component could benefit from better accessibility features.',
        replies: [
          {
            id: 'reply-1',
            userId: 'user-1',
            file: 'src/components/Button.tsx',
            line: 15,
            column: 10,
            content: 'Good point! I\'ll add ARIA labels and keyboard navigation.',
            replies: [],
            resolved: false,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
        ],
        resolved: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'comment-2',
        userId: 'user-3',
        file: 'src/hooks/useAuth.ts',
        line: 42,
        column: 5,
        content: 'Consider adding error handling for network failures.',
        replies: [],
        resolved: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];
    setComments(mockComments);
  };

  const loadDebugSessions = (sessionId: string) => {
    // Mock debug sessions for demonstration
    const mockDebugSessions: DebugSession[] = [
      {
        id: 'debug-1',
        userId: 'user-2',
        file: 'src/components/Form.tsx',
        breakpoints: [
          {
            id: 'bp-1',
            file: 'src/components/Form.tsx',
            line: 25,
            enabled: true,
            hitCount: 3,
          },
          {
            id: 'bp-2',
            file: 'src/components/Form.tsx',
            line: 45,
            condition: 'value.length > 0',
            enabled: true,
            hitCount: 1,
          },
        ],
        variables: {
          formData: { name: 'John', email: 'john@example.com' },
          isValid: true,
          errors: [],
        },
        callStack: [
          {
            function: 'handleSubmit',
            file: 'src/components/Form.tsx',
            line: 25,
            column: 10,
            variables: { event: 'SubmitEvent' },
          },
        ],
        isActive: true,
        createdAt: new Date().toISOString(),
      },
    ];
    setDebugSessions(mockDebugSessions);
  };

  const handleAddComment = () => {
    if (!newComment.trim() || !selectedFile) return;

    const comment = realtimeCollaboration.addComment(
      currentSession!.id,
      selectedFile,
      selectedLine,
      0,
      newComment
    );
    setComments([...comments, comment]);
    setNewComment('');
  };

  const handleReplyToComment = (commentId: string, reply: string) => {
    const replyComment = realtimeCollaboration.replyToComment(commentId, reply);
    if (replyComment) {
      setComments(comments.map(c => 
        c.id === commentId 
          ? { ...c, replies: [...c.replies, replyComment] }
          : c
      ));
    }
  };

  const handleResolveComment = (commentId: string) => {
    const resolved = realtimeCollaboration.resolveComment(commentId);
    if (resolved) {
      setComments(comments.map(c => 
        c.id === commentId ? { ...c, resolved: true } : c
      ));
    }
  };

  const getUserColor = (userId: string) => {
    const colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6'];
    return colors[userId.charCodeAt(0) % colors.length];
  };

  const getUserName = (userId: string) => {
    const names: Record<string, string> = {
      'user-1': 'John Doe',
      'user-2': 'Jane Smith',
      'user-3': 'Bob Johnson',
    };
    return names[userId] || 'Unknown User';
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Users className="h-8 w-8 text-blue-600" />
            Real-time Collaboration
          </h2>
          <p className="text-muted-foreground">
            Collaborate with your team in real-time
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={isConnected ? 'default' : 'destructive'}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </Badge>
          <Button
            onClick={() => setShowCreateSession(true)}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            New Session
          </Button>
        </div>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.activeSessions}</div>
              <p className="text-xs text-muted-foreground">
                Currently active collaboration sessions
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Events</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.totalEvents}</div>
              <p className="text-xs text-muted-foreground">
                Real-time collaboration events
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Comments</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.totalComments}</div>
              <p className="text-xs text-muted-foreground">
                Code review comments
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Debug Sessions</CardTitle>
              <Bug className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.activeDebugSessions}</div>
              <p className="text-xs text-muted-foreground">
                Active debugging sessions
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <Tabs defaultValue="sessions" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="sessions" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Sessions
          </TabsTrigger>
          <TabsTrigger value="comments" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Comments
          </TabsTrigger>
          <TabsTrigger value="debug" className="flex items-center gap-2">
            <Bug className="h-4 w-4" />
            Debug
          </TabsTrigger>
          <TabsTrigger value="live-coding" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            Live Coding
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sessions" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sessions.map((session) => (
              <Card key={session.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{session.name}</CardTitle>
                    <Badge variant={session.isActive ? 'default' : 'secondary'}>
                      {session.isActive ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <CardDescription>{session.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Participants</span>
                      <span className="text-sm font-bold">
                        {session.participants.length}/{session.settings.maxParticipants}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Created</span>
                      <span className="text-sm">
                        {new Date(session.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {session.participants.slice(0, 3).map((participant) => (
                        <div
                          key={participant.id}
                          className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                          style={{ backgroundColor: participant.color }}
                        >
                          {participant.name.charAt(0)}
                        </div>
                      ))}
                      {session.participants.length > 3 && (
                        <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">
                          +{session.participants.length - 3}
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => handleJoinSession(session.id)}
                        className="flex-1"
                      >
                        Join
                      </Button>
                      <Button size="sm" variant="outline">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="comments" className="space-y-4">
          <div className="space-y-4">
            {comments.map((comment) => (
              <Card key={comment.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white"
                        style={{ backgroundColor: getUserColor(comment.userId) }}
                      >
                        {getUserName(comment.userId).charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium">{getUserName(comment.userId)}</div>
                        <div className="text-sm text-muted-foreground">
                          {comment.file}:{comment.line}:{comment.column}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {comment.resolved ? (
                        <Badge variant="default" className="bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Resolved
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <AlertCircle className="h-3 w-3 mr-1" />
                          Open
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <p className="text-sm">{comment.content}</p>
                    
                    {comment.replies.length > 0 && (
                      <div className="ml-4 space-y-2">
                        {comment.replies.map((reply) => (
                          <div key={reply.id} className="flex items-start gap-2 p-3 bg-muted rounded-lg">
                            <div
                              className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                              style={{ backgroundColor: getUserColor(reply.userId) }}
                            >
                              {getUserName(reply.userId).charAt(0)}
                            </div>
                            <div className="flex-1">
                              <div className="font-medium text-sm">{getUserName(reply.userId)}</div>
                              <p className="text-sm">{reply.content}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          const reply = prompt('Enter your reply:');
                          if (reply) handleReplyToComment(comment.id, reply);
                        }}
                      >
                        <Reply className="h-4 w-4 mr-1" />
                        Reply
                      </Button>
                      {!comment.resolved && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleResolveComment(comment.id)}
                        >
                          <Resolve className="h-4 w-4 mr-1" />
                          Resolve
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="debug" className="space-y-4">
          <div className="space-y-4">
            {debugSessions.map((debugSession) => (
              <Card key={debugSession.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Bug className="h-5 w-5" />
                      <CardTitle className="text-lg">Debug Session</CardTitle>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={debugSession.isActive ? 'default' : 'secondary'}>
                        {debugSession.isActive ? 'Active' : 'Paused'}
                      </Badge>
                      <Button size="sm" variant="outline">
                        {debugSession.isActive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  <CardDescription>
                    Debugging {debugSession.file} by {getUserName(debugSession.userId)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="breakpoints" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="breakpoints">Breakpoints</TabsTrigger>
                      <TabsTrigger value="variables">Variables</TabsTrigger>
                      <TabsTrigger value="callstack">Call Stack</TabsTrigger>
                    </TabsList>

                    <TabsContent value="breakpoints" className="space-y-2">
                      {debugSession.breakpoints.map((breakpoint) => (
                        <div key={breakpoint.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-2">
                            <div className={`w-3 h-3 rounded-full ${breakpoint.enabled ? 'bg-red-500' : 'bg-gray-300'}`} />
                            <span className="text-sm font-mono">
                              {breakpoint.file}:{breakpoint.line}
                            </span>
                            {breakpoint.condition && (
                              <Badge variant="outline" className="text-xs">
                                {breakpoint.condition}
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground">
                              Hit: {breakpoint.hitCount}
                            </span>
                            <Button size="sm" variant="ghost">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </TabsContent>

                    <TabsContent value="variables" className="space-y-2">
                      {Object.entries(debugSession.variables).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between p-3 border rounded-lg">
                          <span className="text-sm font-mono font-medium">{key}</span>
                          <span className="text-sm font-mono">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </span>
                        </div>
                      ))}
                    </TabsContent>

                    <TabsContent value="callstack" className="space-y-2">
                      {debugSession.callStack.map((frame, index) => (
                        <div key={index} className="p-3 border rounded-lg">
                          <div className="font-mono text-sm">
                            {frame.function} ({frame.file}:{frame.line}:{frame.column})
                          </div>
                          {Object.keys(frame.variables).length > 0 && (
                            <div className="mt-2 text-xs text-muted-foreground">
                              Variables: {Object.keys(frame.variables).join(', ')}
                            </div>
                          )}
                        </div>
                      ))}
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="live-coding" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Live Coding Session</CardTitle>
              <CardDescription>
                Real-time collaborative code editing
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Button size="sm" variant="outline">
                    <Video className="h-4 w-4 mr-1" />
                    Start Video
                  </Button>
                  <Button size="sm" variant="outline">
                    <Mic className="h-4 w-4 mr-1" />
                    Mute
                  </Button>
                  <Button size="sm" variant="outline">
                    <Monitor className="h-4 w-4 mr-1" />
                    Share Screen
                  </Button>
                </div>
                
                <div className="bg-muted p-4 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-2">Active Participants:</div>
                  <div className="flex gap-2">
                    {currentSession?.participants.map((participant) => (
                      <div key={participant.id} className="flex items-center gap-2">
                        <div
                          className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                          style={{ backgroundColor: participant.color }}
                        >
                          {participant.name.charAt(0)}
                        </div>
                        <span className="text-sm">{participant.name}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="text-center py-8">
                  <Code className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Live Coding Editor</h3>
                  <p className="text-muted-foreground">
                    The live coding editor will appear here when a session is active.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Session Modal */}
      {showCreateSession && (
        <Card className="fixed inset-4 z-50 overflow-auto">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Create New Session</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowCreateSession(false)}
              >
                ×
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Session Name</label>
                <input
                  type="text"
                  className="w-full mt-1 p-2 border rounded-md"
                  placeholder="Enter session name"
                  defaultValue="New Collaboration Session"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Description</label>
                <textarea
                  className="w-full mt-1 p-2 border rounded-md"
                  placeholder="Enter session description"
                  rows={3}
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleCreateSession}>
                  Create Session
                </Button>
                <Button variant="outline" onClick={() => setShowCreateSession(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}




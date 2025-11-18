import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { Bell, X, Check, AlertCircle, Info, CheckCircle, AlertTriangle } from 'lucide-react';
import { toast } from 'react-hot-toast';

const NotificationCenterContainer = styled.div`
  position: relative;
  display: inline-block;
`;

const BellIcon = styled.div`
  position: relative;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s ease;
  color: ${props => props.theme.colors.text};
  
  &:hover {
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.primary};
  }
`;

const Badge = styled.div`
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: ${props => props.theme.colors.error};
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  border: 2px solid ${props => props.theme.colors.background};
`;

const Dropdown = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  width: 400px;
  max-height: 500px;
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
  margin-top: 8px;
`;

const Header = styled.div`
  padding: 16px;
  border-bottom: 1px solid ${props => props.theme.colors.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: ${props => props.theme.colors.surface};
`;

const Title = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const MarkAllButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.theme.colors.primary};
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: ${props => props.theme.colors.background};
  }
`;

const NotificationList = styled.div`
  max-height: 400px;
  overflow-y: auto;
`;

const NotificationItem = styled.div`
  padding: 12px 16px;
  border-bottom: 1px solid ${props => props.theme.colors.border};
  display: flex;
  align-items: flex-start;
  gap: 12px;
  transition: background-color 0.2s ease;
  cursor: pointer;
  opacity: ${props => props.read ? 0.7 : 1};
  
  &:hover {
    background-color: ${props => props.theme.colors.background};
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const IconContainer = styled.div`
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${props => {
    switch (props.type) {
      case 'error': return props.theme.colors.error + '20';
      case 'success': return props.theme.colors.success + '20';
      case 'warning': return props.theme.colors.warning + '20';
      default: return props.theme.colors.primary + '20';
    }
  }};
  color: ${props => {
    switch (props.type) {
      case 'error': return props.theme.colors.error;
      case 'success': return props.theme.colors.success;
      case 'warning': return props.theme.colors.warning;
      default: return props.theme.colors.primary;
    }
  }};
`;

const Content = styled.div`
  flex: 1;
  min-width: 0;
`;

const NotificationTitle = styled.div`
  font-weight: 600;
  font-size: 14px;
  color: ${props => props.theme.colors.text};
  margin-bottom: 4px;
`;

const NotificationMessage = styled.div`
  font-size: 13px;
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.4;
  margin-bottom: 4px;
`;

const Timestamp = styled.div`
  font-size: 11px;
  color: ${props => props.theme.colors.textSecondary};
`;

const Actions = styled.div`
  display: flex;
  gap: 4px;
  margin-top: 8px;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  color: ${props => props.theme.colors.textSecondary};
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
  }
`;

const EmptyState = styled.div`
  padding: 32px 16px;
  text-align: center;
  color: ${props => props.theme.colors.textSecondary};
`;

const ConnectionStatus = styled.div`
  padding: 8px 16px;
  background-color: ${props => props.connected ? 
    props.theme.colors.success + '20' : 
    props.theme.colors.error + '20'
  };
  color: ${props => props.connected ? 
    props.theme.colors.success : 
    props.theme.colors.error
  };
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const NotificationCenter = ({ userId = 'default_user' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef(null);
  const dropdownRef = useRef(null);

  // Conectar a WebSocket para notificaciones en tiempo real
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`ws://localhost:8000/api/notifications/ws/${userId}`);
        
        ws.onopen = () => {
          setIsConnected(true);
          console.log('Conectado a notificaciones WebSocket');
        };
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          if (data.type === 'notification') {
            // Agregar nueva notificación
            setNotifications(prev => [data.data, ...prev]);
            setUnreadCount(prev => prev + 1);
            
            // Mostrar toast
            toast.success(data.data.title, {
              description: data.data.message,
              duration: 4000,
            });
          } else if (data.type === 'notifications') {
            // Actualizar lista de notificaciones
            setNotifications(data.data);
            setUnreadCount(data.data.filter(n => !n.read).length);
          }
        };
        
        ws.onclose = () => {
          setIsConnected(false);
          console.log('Desconectado de notificaciones WebSocket');
          
          // Reconectar después de 5 segundos
          setTimeout(connectWebSocket, 5000);
        };
        
        ws.onerror = (error) => {
          console.error('Error en WebSocket:', error);
          setIsConnected(false);
        };
        
        wsRef.current = ws;
        
        // Solicitar notificaciones actuales
        ws.send(JSON.stringify({ action: 'get_notifications' }));
        
      } catch (error) {
        console.error('Error conectando WebSocket:', error);
        setIsConnected(false);
      }
    };
    
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId]);

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'error_occurred':
        return <AlertCircle size={16} />;
      case 'search_completed':
        return <CheckCircle size={16} />;
      case 'document_uploaded':
        return <CheckCircle size={16} />;
      case 'system_update':
        return <Info size={16} />;
      case 'recommendation_ready':
        return <CheckCircle size={16} />;
      case 'analytics_update':
        return <Info size={16} />;
      case 'batch_processing_complete':
        return <AlertTriangle size={16} />;
      default:
        return <Info size={16} />;
    }
  };

  const getNotificationType = (type) => {
    switch (type) {
      case 'error_occurred':
        return 'error';
      case 'search_completed':
      case 'document_uploaded':
      case 'recommendation_ready':
        return 'success';
      case 'batch_processing_complete':
        return 'warning';
      default:
        return 'info';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // Menos de 1 minuto
      return 'Hace un momento';
    } else if (diff < 3600000) { // Menos de 1 hora
      const minutes = Math.floor(diff / 60000);
      return `Hace ${minutes} min`;
    } else if (diff < 86400000) { // Menos de 1 día
      const hours = Math.floor(diff / 3600000);
      return `Hace ${hours}h`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      const response = await fetch(`/api/notifications/user/${userId}/read/${notificationId}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        setNotifications(prev => 
          prev.map(n => 
            n.id === notificationId ? { ...n, read: true } : n
          )
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
        
        // Enviar comando por WebSocket
        if (wsRef.current) {
          wsRef.current.send(JSON.stringify({
            action: 'mark_read',
            notification_id: notificationId
          }));
        }
      }
    } catch (error) {
      console.error('Error marcando notificación como leída:', error);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      const response = await fetch(`/api/notifications/user/${userId}/${notificationId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setNotifications(prev => prev.filter(n => n.id !== notificationId));
        setUnreadCount(prev => {
          const notification = notifications.find(n => n.id === notificationId);
          return notification && !notification.read ? Math.max(0, prev - 1) : prev;
        });
      }
    } catch (error) {
      console.error('Error eliminando notificación:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const response = await fetch(`/api/notifications/user/${userId}/read-all`, {
        method: 'POST',
      });
      
      if (response.ok) {
        setNotifications(prev => 
          prev.map(n => ({ ...n, read: true }))
        );
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Error marcando todas como leídas:', error);
    }
  };

  return (
    <NotificationCenterContainer ref={dropdownRef}>
      <BellIcon onClick={() => setIsOpen(!isOpen)}>
        <Bell size={20} />
        {unreadCount > 0 && <Badge>{unreadCount}</Badge>}
      </BellIcon>
      
      {isOpen && (
        <Dropdown>
          <Header>
            <Title>Notificaciones</Title>
            {unreadCount > 0 && (
              <MarkAllButton onClick={markAllAsRead}>
                Marcar todas como leídas
              </MarkAllButton>
            )}
          </Header>
          
          <ConnectionStatus connected={isConnected}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'currentColor' }} />
            {isConnected ? 'Conectado' : 'Desconectado'}
          </ConnectionStatus>
          
          <NotificationList>
            {notifications.length === 0 ? (
              <EmptyState>
                <Bell size={32} style={{ opacity: 0.3, marginBottom: 8 }} />
                <div>No hay notificaciones</div>
              </EmptyState>
            ) : (
              notifications.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  read={notification.read}
                  onClick={() => !notification.read && markAsRead(notification.id)}
                >
                  <IconContainer type={getNotificationType(notification.type)}>
                    {getNotificationIcon(notification.type)}
                  </IconContainer>
                  
                  <Content>
                    <NotificationTitle>{notification.title}</NotificationTitle>
                    <NotificationMessage>{notification.message}</NotificationMessage>
                    <Timestamp>{formatTimestamp(notification.created_at)}</Timestamp>
                    
                    <Actions>
                      {!notification.read && (
                        <ActionButton
                          onClick={(e) => {
                            e.stopPropagation();
                            markAsRead(notification.id);
                          }}
                          title="Marcar como leída"
                        >
                          <Check size={14} />
                        </ActionButton>
                      )}
                      <ActionButton
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNotification(notification.id);
                        }}
                        title="Eliminar"
                      >
                        <X size={14} />
                      </ActionButton>
                    </Actions>
                  </Content>
                </NotificationItem>
              ))
            )}
          </NotificationList>
        </Dropdown>
      )}
    </NotificationCenterContainer>
  );
};

export default NotificationCenter;



























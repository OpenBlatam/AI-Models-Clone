import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Search, 
  Upload, 
  BarChart3, 
  Menu, 
  X, 
  Brain,
  Wifi,
  WifiOff,
  Activity
} from 'lucide-react';
import NotificationCenter from './NotificationCenter';

const HeaderContainer = styled.header`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: ${props => props.theme.colors.surface};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  backdrop-filter: blur(10px);
  box-shadow: ${props => props.theme.shadows.sm};
`;

const HeaderContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 80px;
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  text-decoration: none;
  color: ${props => props.theme.colors.text};
  font-size: 1.5rem;
  font-weight: 700;
  transition: all 0.2s ease;

  &:hover {
    color: ${props => props.theme.colors.primary};
    transform: scale(1.05);
  }
`;

const LogoIcon = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, 
    ${props => props.theme.colors.primary}, 
    ${props => props.theme.colors.secondary});
  border-radius: ${props => props.theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
`;

const Navigation = styled.nav`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.lg};

  @media (max-width: ${props => props.theme.breakpoints.md}) {
    display: ${props => props.isOpen ? 'flex' : 'none'};
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: ${props => props.theme.colors.surface};
    border-bottom: 1px solid ${props => props.theme.colors.border};
    flex-direction: column;
    padding: ${props => props.theme.spacing.lg};
    box-shadow: ${props => props.theme.shadows.lg};
  }
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  text-decoration: none;
  color: ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.textSecondary};
  font-weight: 500;
  border-radius: ${props => props.theme.borderRadius.md};
  transition: all 0.2s ease;
  background: ${props => props.isActive ? props.theme.colors.primary}10 : 'transparent'};

  &:hover {
    color: ${props => props.theme.colors.primary};
    background: ${props => props.theme.colors.primary}10;
    transform: translateY(-1px);
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.isHealthy ? props.theme.colors.success}20 : props.theme.colors.error}20;
  border: 1px solid ${props => props.isHealthy ? props.theme.colors.success}40 : props.theme.colors.error}40;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.isHealthy ? props.theme.colors.success : props.theme.colors.error};
`;

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: ${props => props.theme.colors.text};
  cursor: pointer;
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.md};
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.surfaceDark};
  }

  @media (max-width: ${props => props.theme.breakpoints.md}) {
    display: flex;
    align-items: center;
    justify-content: center;
  }
`;

const Header = ({ apiStatus }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const isHealthy = apiStatus?.status === 'healthy';

  const navigationItems = [
    {
      path: '/',
      label: 'Búsqueda',
      icon: Search
    },
    {
      path: '/upload',
      label: 'Subir',
      icon: Upload
    },
    {
      path: '/stats',
      label: 'Estadísticas',
      icon: BarChart3
    },
    {
      path: '/analytics',
      label: 'Analytics',
      icon: TrendingUp
    }
  ];

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo to="/">
          <LogoIcon>
            <Brain size={24} />
          </LogoIcon>
          AI Search
        </Logo>

        <Navigation isOpen={isMenuOpen}>
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <NavLink
                key={item.path}
                to={item.path}
                isActive={isActive}
                onClick={() => setIsMenuOpen(false)}
              >
                <Icon size={18} />
                {item.label}
              </NavLink>
            );
          })}
        </Navigation>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <NotificationCenter userId="default_user" />
          
          <StatusIndicator isHealthy={isHealthy}>
            {isHealthy ? <Wifi size={16} /> : <WifiOff size={16} />}
            {isHealthy ? 'Conectado' : 'Desconectado'}
          </StatusIndicator>

          <MobileMenuButton onClick={toggleMenu}>
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </MobileMenuButton>
        </div>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header;


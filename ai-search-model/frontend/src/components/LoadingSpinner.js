import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const SpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xxl};
  min-height: ${props => props.fullHeight ? '100vh' : 'auto'};
`;

const Spinner = styled.div`
  width: ${props => {
    switch (props.size) {
      case 'small': return '20px';
      case 'medium': return '40px';
      case 'large': return '60px';
      default: return '40px';
    }
  }};
  height: ${props => {
    switch (props.size) {
      case 'small': return '20px';
      case 'medium': return '40px';
      case 'large': return '60px';
      default: return '40px';
    }
  }};
  border: ${props => {
    switch (props.size) {
      case 'small': return '2px';
      case 'medium': return '3px';
      case 'large': return '4px';
      default: return '3px';
    }
  }} solid ${props => props.theme.colors.border};
  border-top: ${props => {
    switch (props.size) {
      case 'small': return '2px';
      case 'medium': return '3px';
      case 'large': return '4px';
      default: return '3px';
    }
  }} solid ${props => props.theme.colors.primary};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin-bottom: ${props => props.message ? props.theme.spacing.md : 0};
`;

const Message = styled.div`
  font-size: ${props => {
    switch (props.size) {
      case 'small': return '0.875rem';
      case 'medium': return '1rem';
      case 'large': return '1.125rem';
      default: return '1rem';
    }
  }};
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
  animation: ${pulse} 2s ease-in-out infinite;
`;

const LoadingSpinner = ({ 
  size = 'medium', 
  message = '', 
  fullHeight = false,
  className = ''
}) => {
  return (
    <SpinnerContainer fullHeight={fullHeight} className={className}>
      <Spinner size={size} />
      {message && <Message size={size}>{message}</Message>}
    </SpinnerContainer>
  );
};

export default LoadingSpinner;




























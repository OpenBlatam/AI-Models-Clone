import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AdvancedButton, PrimaryButton, SecondaryButton } from '@/components/ui/advanced-button';

// Mock the utils function
jest.mock('@/lib/utils', () => ({
  cn: (...classes: string[]) => classes.filter(Boolean).join(' '),
}));

describe('AdvancedButton', () => {
  const defaultProps = {
    children: 'Test Button',
    onClick: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders with default props', () => {
      render(<AdvancedButton {...defaultProps} />);
      
      const button = screen.getByRole('button', { name: 'Test Button' });
      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('bg-blue-600');
    });

    it('renders with custom variant', () => {
      render(<AdvancedButton {...defaultProps} variant="destructive" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-red-600');
    });

    it('renders with custom size', () => {
      render(<AdvancedButton {...defaultProps} size="lg" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-6 py-3 text-base font-medium');
    });

    it('renders with custom rounded corners', () => {
      render(<AdvancedButton {...defaultProps} rounded="full" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('rounded-full');
    });

    it('renders with custom shadow', () => {
      render(<AdvancedButton {...defaultProps} shadow="xl" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('shadow-xl');
    });

    it('renders with animation', () => {
      render(<AdvancedButton {...defaultProps} animation="pulse" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('animate-pulse');
    });

    it('renders with full width', () => {
      render(<AdvancedButton {...defaultProps} fullWidth />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-full');
    });
  });

  describe('Loading State', () => {
    it('shows loading spinner when loading is true', () => {
      render(<AdvancedButton {...defaultProps} loading />);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('aria-busy', 'true');
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('shows custom loading text', () => {
      render(<AdvancedButton {...defaultProps} loading loadingText="Processing..." />);
      
      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });

    it('hides normal content when loading', () => {
      render(<AdvancedButton {...defaultProps} loading />);
      
      expect(screen.queryByText('Test Button')).not.toBeInTheDocument();
    });
  });

  describe('Disabled State', () => {
    it('is disabled when disabled prop is true', () => {
      render(<AdvancedButton {...defaultProps} disabled />);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });

    it('is disabled when loading is true', () => {
      render(<AdvancedButton {...defaultProps} loading />);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });
  });

  describe('Icons', () => {
    it('renders left icon', () => {
      const leftIcon = <span data-testid="left-icon">←</span>;
      render(<AdvancedButton {...defaultProps} leftIcon={leftIcon} />);
      
      expect(screen.getByTestId('left-icon')).toBeInTheDocument();
    });

    it('renders right icon', () => {
      const rightIcon = <span data-testid="right-icon">→</span>;
      render(<AdvancedButton {...defaultProps} rightIcon={rightIcon} />);
      
      expect(screen.getByTestId('right-icon')).toBeInTheDocument();
    });

    it('hides icons when loading', () => {
      const leftIcon = <span data-testid="left-icon">←</span>;
      render(<AdvancedButton {...defaultProps} leftIcon={leftIcon} loading />);
      
      expect(screen.queryByTestId('left-icon')).not.toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('calls onClick when clicked', () => {
      const onClick = jest.fn();
      render(<AdvancedButton {...defaultProps} onClick={onClick} />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);
      
      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', () => {
      const onClick = jest.fn();
      render(<AdvancedButton {...defaultProps} onClick={onClick} disabled />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);
      
      expect(onClick).not.toHaveBeenCalled();
    });

    it('does not call onClick when loading', () => {
      const onClick = jest.fn();
      render(<AdvancedButton {...defaultProps} onClick={onClick} loading />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);
      
      expect(onClick).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('has correct ARIA attributes when disabled', () => {
      render(<AdvancedButton {...defaultProps} disabled />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });

    it('has correct ARIA attributes when loading', () => {
      render(<AdvancedButton {...defaultProps} loading />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    it('forwards ref correctly', () => {
      const ref = jest.fn();
      render(<AdvancedButton {...defaultProps} ref={ref} />);
      
      expect(ref).toHaveBeenCalled();
    });
  });

  describe('Variant Components', () => {
    it('renders PrimaryButton with correct styles', () => {
      render(<PrimaryButton {...defaultProps} />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-blue-600');
    });

    it('renders SecondaryButton with correct styles', () => {
      render(<SecondaryButton {...defaultProps} />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-gray-600');
    });
  });

  describe('Custom Class Names', () => {
    it('applies custom className', () => {
      render(<AdvancedButton {...defaultProps} className="custom-class" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
    });

    it('merges custom className with default styles', () => {
      render(<AdvancedButton {...defaultProps} className="custom-class" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-blue-600', 'custom-class');
    });
  });

  describe('Edge Cases', () => {
    it('handles empty children gracefully', () => {
      render(<AdvancedButton onClick={jest.fn()} />);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('handles undefined props gracefully', () => {
      render(<AdvancedButton {...defaultProps} variant={undefined} size={undefined} />);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('bg-blue-600'); // Default variant
    });
  });
});

import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/button';

describe('Button Component', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {
      render(<Button>Click me</Button>);
      
      const button = screen.getByRole('button', { name: /click me/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('bg-primary', 'text-primary-foreground');
    });

    it('renders with custom className', () => {
      render(<Button className="custom-class">Custom Button</Button>);
      
      const button = screen.getByRole('button', { name: /custom button/i });
      expect(button).toHaveClass('custom-class');
    });

    it('renders with different variants', () => {
      const { rerender } = render(<Button variant="destructive">Delete</Button>);
      
      let button = screen.getByRole('button', { name: /delete/i });
      expect(button).toHaveClass('bg-destructive');

      rerender(<Button variant="outline">Outline</Button>);
      button = screen.getByRole('button', { name: /outline/i });
      expect(button).toHaveClass('border', 'bg-background');

      rerender(<Button variant="secondary">Secondary</Button>);
      button = screen.getByRole('button', { name: /secondary/i });
      expect(button).toHaveClass('bg-secondary');
    });

    it('renders with different sizes', () => {
      const { rerender } = render(<Button size="sm">Small</Button>);
      
      let button = screen.getByRole('button', { name: /small/i });
      expect(button).toHaveClass('h-9', 'px-3');

      rerender(<Button size="lg">Large</Button>);
      button = screen.getByRole('button', { name: /large/i });
      expect(button).toHaveClass('h-11', 'px-8');

      rerender(<Button size="xl">Extra Large</Button>);
      button = screen.getByRole('button', { name: /extra large/i });
      expect(button).toHaveClass('h-12', 'text-base');
    });

    it('renders with different rounded variants', () => {
      const { rerender } = render(<Button rounded="full">Rounded</Button>);
      
      let button = screen.getByRole('button', { name: /rounded/i });
      expect(button).toHaveClass('rounded-full');

      rerender(<Button rounded="none">No Rounded</Button>);
      button = screen.getByRole('button', { name: /no rounded/i });
      expect(button).toHaveClass('rounded-none');
    });
  });

  describe('Loading State', () => {
    it('shows loading spinner when loading is true', () => {
      render(<Button loading>Loading Button</Button>);
      
      const button = screen.getByRole('button', { name: /loading button/i });
      const spinner = button.querySelector('svg');
      
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('animate-spin');
    });

    it('disables button when loading is true', () => {
      render(<Button loading>Loading Button</Button>);
      
      const button = screen.getByRole('button', { name: /loading button/i });
      expect(button).toBeDisabled();
    });

    it('combines loading and disabled states', () => {
      render(<Button loading disabled>Loading Disabled</Button>);
      
      const button = screen.getByRole('button', { name: /loading disabled/i });
      expect(button).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(<Button aria-label="Custom label">Button</Button>);
      
      const button = screen.getByRole('button', { name: /custom label/i });
      expect(button).toBeInTheDocument();
    });

    it('supports asChild prop for composition', () => {
      render(
        <Button asChild>
          <a href="/test">Link Button</a>
        </Button>
      );
      
      const link = screen.getByRole('link', { name: /link button/i });
      expect(link).toBeInTheDocument();
      expect(link).toHaveAttribute('href', '/test');
    });
  });

  describe('Event Handling', () => {
    it('calls onClick handler when clicked', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Clickable</Button>);
      
      const button = screen.getByRole('button', { name: /clickable/i });
      fireEvent.click(button);
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', () => {
      const handleClick = jest.fn();
      render(<Button disabled onClick={handleClick}>Disabled</Button>);
      
      const button = screen.getByRole('button', { name: /disabled/i });
      fireEvent.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('does not call onClick when loading', () => {
      const handleClick = jest.fn();
      render(<Button loading onClick={handleClick}>Loading</Button>);
      
      const button = screen.getByRole('button', { name: /loading/i });
      fireEvent.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty children gracefully', () => {
      render(<Button />);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('handles null and undefined children', () => {
      const { rerender } = render(<Button>{null}</Button>);
      
      let button = screen.getByRole('button');
      expect(button).toBeInTheDocument();

      rerender(<Button>{undefined}</Button>);
      button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('forwards ref correctly', () => {
      const ref = jest.fn();
      render(<Button ref={ref}>Ref Button</Button>);
      
      expect(ref).toHaveBeenCalledWith(expect.any(HTMLButtonElement));
    });
  });

  describe('Integration', () => {
    it('works with form submission', () => {
      const handleSubmit = jest.fn((e) => e.preventDefault());
      
      render(
        <form onSubmit={handleSubmit}>
          <Button type="submit">Submit</Button>
        </form>
      );
      
      const button = screen.getByRole('button', { name: /submit/i });
      fireEvent.click(button);
      
      expect(handleSubmit).toHaveBeenCalledTimes(1);
    });

    it('works with keyboard navigation', () => {
      render(<Button>Keyboard Button</Button>);
      
      const button = screen.getByRole('button', { name: /keyboard button/i });
      
      // Focus the button
      button.focus();
      expect(button).toHaveFocus();
      
      // Press Enter key
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
      expect(button).toHaveFocus();
    });
  });
});






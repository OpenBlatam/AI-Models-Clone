import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ExamplesContent } from '@/components/examples/examples-content';
import { LocalStorageExample } from '@/components/examples/examples-content';
import { DebounceExample } from '@/components/examples/examples-content';
import { FormValidationExample } from '@/components/examples/examples-content';
import { DataFetchingExample } from '@/components/examples/examples-content';

// Mock the hooks
jest.mock('@/hooks/use-local-storage', () => ({
  useLocalStorage: jest.fn(),
}));

jest.mock('@/hooks/use-debounce', () => ({
  useDebounce: jest.fn(),
}));

jest.mock('@/hooks/use-form-validation', () => ({
  useFormValidation: jest.fn(),
}));

jest.mock('@/hooks/use-data-fetching', () => ({
  useDataFetching: jest.fn(),
}));

jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('ExamplesContent Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all tabs correctly', () => {
    render(<ExamplesContent />);
    
    expect(screen.getByText('Local Storage')).toBeInTheDocument();
    expect(screen.getByText('Debounce')).toBeInTheDocument();
    expect(screen.getByText('Form Validation')).toBeInTheDocument();
    expect(screen.getByText('Data Fetching')).toBeInTheDocument();
  });

  it('shows local storage tab by default', () => {
    render(<ExamplesContent />);
    
    expect(screen.getByText('Local Storage Hook')).toBeInTheDocument();
    expect(screen.queryByText('Debounce Hook')).not.toBeInTheDocument();
  });

  it('switches tabs when clicked', async () => {
    render(<ExamplesContent />);
    
    const debounceTab = screen.getByText('Debounce');
    fireEvent.click(debounceTab);
    
    await waitFor(() => {
      expect(screen.getByText('Debounce Hook')).toBeInTheDocument();
      expect(screen.queryByText('Local Storage Hook')).not.toBeInTheDocument();
    });
  });
});

describe('LocalStorageExample Component', () => {
  const mockUseLocalStorage = require('@/hooks/use-local-storage').useLocalStorage;
  
  beforeEach(() => {
    mockUseLocalStorage.mockReturnValue([
      { name: 'John', email: 'john@example.com', role: 'Admin' },
      jest.fn(),
      jest.fn(),
    ]);
  });

  it('renders user form fields', () => {
    render(<LocalStorageExample />);
    
    expect(screen.getByPlaceholderText('Name')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Role')).toBeInTheDocument();
  });

  it('renders theme toggle and counter', () => {
    mockUseLocalStorage
      .mockReturnValueOnce([{ name: '', email: '', role: '' }, jest.fn(), jest.fn()])
      .mockReturnValueOnce(['light', jest.fn()])
      .mockReturnValueOnce([0, jest.fn()]);
    
    render(<LocalStorageExample />);
    
    expect(screen.getByText('Theme')).toBeInTheDocument();
    expect(screen.getByText('Counter')).toBeInTheDocument();
  });
});

describe('DebounceExample Component', () => {
  const mockUseDebounce = require('@/hooks/use-debounce').useDebounce;
  
  beforeEach(() => {
    mockUseDebounce.mockReturnValue('debounced value');
  });

  it('renders search input', () => {
    render(<DebounceExample />);
    
    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
  });

  it('shows current and debounced values', () => {
    render(<DebounceExample />);
    
    expect(screen.getByText('Current value: (empty)')).toBeInTheDocument();
    expect(screen.getByText('Debounced value: debounced value')).toBeInTheDocument();
  });
});

describe('FormValidationExample Component', () => {
  const mockUseFormValidation = require('@/hooks/use-form-validation').useFormValidation;
  
  const mockFormState = {
    values: { name: '', email: '', role: '' },
    errors: [],
    isValid: false,
    isSubmitting: false,
    touched: new Set(),
    setFieldValue: jest.fn(),
    setFieldTouched: jest.fn(),
    getFieldError: jest.fn(),
    isFieldTouched: jest.fn(),
    hasFieldError: jest.fn(),
    handleSubmit: jest.fn(),
    resetForm: jest.fn(),
  };

  beforeEach(() => {
    mockUseFormValidation.mockReturnValue(mockFormState);
  });

  it('renders form fields', () => {
    render(<FormValidationExample />);
    
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Role')).toBeInTheDocument();
  });

  it('shows form state information', () => {
    render(<FormValidationExample />);
    
    expect(screen.getByText('Form State')).toBeInTheDocument();
    expect(screen.getByText('Field Status:')).toBeInTheDocument();
  });

  it('handles field changes', () => {
    render(<FormValidationExample />);
    
    const nameInput = screen.getByLabelText('Name');
    fireEvent.change(nameInput, { target: { value: 'John' } });
    
    expect(mockFormState.setFieldValue).toHaveBeenCalledWith('name', 'John');
  });

  it('handles field blur', () => {
    render(<FormValidationExample />);
    
    const nameInput = screen.getByLabelText('Name');
    fireEvent.blur(nameInput);
    
    expect(mockFormState.setFieldTouched).toHaveBeenCalledWith('name');
  });
});

describe('DataFetchingExample Component', () => {
  const mockUseDataFetching = require('@/hooks/use-data-fetching').useDataFetching;
  
  const mockDataState = {
    data: null,
    loading: false,
    error: null,
    refetch: jest.fn(),
    clearCache: jest.fn(),
  };

  beforeEach(() => {
    mockUseDataFetching.mockReturnValue(mockDataState);
  });

  it('renders data controls', () => {
    render(<DataFetchingExample />);
    
    expect(screen.getByText('Fetch Data')).toBeInTheDocument();
    expect(screen.getByText('Clear Cache')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockUseDataFetching.mockReturnValue({ ...mockDataState, loading: true });
    
    render(<DataFetchingExample />);
    
    expect(screen.getByText('Loading posts...')).toBeInTheDocument();
  });

  it('shows error state', () => {
    mockUseDataFetching.mockReturnValue({ 
      ...mockDataState, 
      error: { message: 'Failed to fetch' } 
    });
    
    render(<DataFetchingExample />);
    
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch')).toBeInTheDocument();
  });

  it('shows success state with data', () => {
    const mockPosts = [
      { id: 1, title: 'Test Post', body: 'Test body', userId: 1 }
    ];
    
    mockUseDataFetching.mockReturnValue({ 
      ...mockDataState, 
      data: mockPosts 
    });
    
    render(<DataFetchingExample />);
    
    expect(screen.getByText('Posts Data')).toBeInTheDocument();
    expect(screen.getByText('Test Post')).toBeInTheDocument();
  });

  it('calls refetch when fetch button is clicked', () => {
    render(<DataFetchingExample />);
    
    const fetchButton = screen.getByText('Fetch Data');
    fireEvent.click(fetchButton);
    
    expect(mockDataState.refetch).toHaveBeenCalled();
  });

  it('calls clearCache when clear cache button is clicked', () => {
    render(<DataFetchingExample />);
    
    const clearButton = screen.getByText('Clear Cache');
    fireEvent.click(clearButton);
    
    expect(mockDataState.clearCache).toHaveBeenCalled();
  });
});

// Integration tests
describe('Examples Integration', () => {
  it('maintains tab state across component re-renders', () => {
    const { rerender } = render(<ExamplesContent />);
    
    // Switch to debounce tab
    fireEvent.click(screen.getByText('Debounce'));
    
    // Re-render component
    rerender(<ExamplesContent />);
    
    // Should still be on debounce tab
    expect(screen.getByText('Debounce Hook')).toBeInTheDocument();
  });

  it('handles multiple tab switches correctly', async () => {
    render(<ExamplesContent />);
    
    // Switch through all tabs
    const tabs = ['Debounce', 'Form Validation', 'Data Fetching', 'Local Storage'];
    
    for (const tabName of tabs) {
      fireEvent.click(screen.getByText(tabName));
      
      await waitFor(() => {
        expect(screen.getByText(`${tabName} Hook`)).toBeInTheDocument();
      });
    }
  });
});






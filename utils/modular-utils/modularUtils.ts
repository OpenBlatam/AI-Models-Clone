// Modular utility functions using iteration and avoiding code duplication

// Generic factory function for creating similar objects
export const createFactory = <T, P extends Record<string, any>>(
  template: (params: P) => T
) => {
  return (params: P): T => template(params);
};

// Modular configuration builder
export const createConfigBuilder = <T extends Record<string, any>>(defaultConfig: T) => {
  return {
    build: (overrides: Partial<T> = {}): T => ({ ...defaultConfig, ...overrides }),
    extend: (extension: Partial<T>) => createConfigBuilder({ ...defaultConfig, ...extension }),
  };
};

// Modular validation schema builder
export const createValidationSchema = <T extends Record<string, any>>() => {
  const schema: Record<keyof T, any[]> = {} as Record<keyof T, any[]>;
  
  return {
    addRule: <K extends keyof T>(field: K, rule: any) => {
      if (!schema[field]) {
        schema[field] = [];
      }
      schema[field].push(rule);
      return schema;
    },
    addRules: <K extends keyof T>(field: K, rules: any[]) => {
      if (!schema[field]) {
        schema[field] = [];
      }
      schema[field].push(...rules);
      return schema;
    },
    build: () => schema,
  };
};

// Modular event handler factory
export const createEventHandler = <T extends Record<string, any>>() => {
  const handlers: Record<keyof T, ((data: any) => void)[]> = {} as Record<keyof T, ((data: any) => void)[]>;
  
  return {
    on: <K extends keyof T>(event: K, handler: (data: any) => void) => {
      if (!handlers[event]) {
        handlers[event] = [];
      }
      handlers[event].push(handler);
    },
    emit: <K extends keyof T>(event: K, data?: any) => {
      if (handlers[event]) {
        handlers[event].forEach(handler => handler(data));
      }
    },
    off: <K extends keyof T>(event: K, handler?: (data: any) => void) => {
      if (handlers[event]) {
        if (handler) {
          handlers[event] = handlers[event].filter(h => h !== handler);
        } else {
          delete handlers[event];
        }
      }
    },
  };
};

// Modular state manager
export const createStateManager = <T extends Record<string, any>>(initialState: T) => {
  let state = { ...initialState };
  const listeners: ((state: T) => void)[] = [];
  
  return {
    getState: () => ({ ...state }),
    setState: (newState: Partial<T>) => {
      state = { ...state, ...newState };
      listeners.forEach(listener => listener(state));
    },
    subscribe: (listener: (state: T) => void) => {
      listeners.push(listener);
      return () => {
        const index = listeners.indexOf(listener);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      };
    },
  };
};

// Modular API client builder
export const createApiClient = (baseConfig: { baseURL: string; headers?: Record<string, string> }) => {
  const config = { ...baseConfig };
  
  return {
    setHeader: (key: string, value: string) => {
      config.headers = { ...config.headers, [key]: value };
    },
    setHeaders: (headers: Record<string, string>) => {
      config.headers = { ...config.headers, ...headers };
    },
    request: async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
      const url = `${config.baseURL}${endpoint}`;
      const response = await fetch(url, {
        headers: config.headers,
        ...options,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return response.json();
    },
    get: <T>(endpoint: string): Promise<T> => {
      return createApiClient(config).request<T>(endpoint, { method: 'GET' });
    },
    post: <T>(endpoint: string, data: any): Promise<T> => {
      return createApiClient(config).request<T>(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    },
    put: <T>(endpoint: string, data: any): Promise<T> => {
      return createApiClient(config).request<T>(endpoint, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    },
    delete: <T>(endpoint: string): Promise<T> => {
      return createApiClient(config).request<T>(endpoint, { method: 'DELETE' });
    },
  };
};

// Modular form builder
export const createFormBuilder = <T extends Record<string, any>>() => {
  const fields: Record<keyof T, any> = {} as Record<keyof T, any>;
  const validators: Record<keyof T, any[]> = {} as Record<keyof T, any[]>;
  
  return {
    addField: <K extends keyof T>(name: K, config: any) => {
      fields[name] = config;
      return createFormBuilder<T>();
    },
    addValidator: <K extends keyof T>(field: K, validator: any) => {
      if (!validators[field]) {
        validators[field] = [];
      }
      validators[field].push(validator);
      return createFormBuilder<T>();
    },
    build: () => ({
      fields,
      validators,
      validate: (data: Partial<T>) => {
        const errors: Record<keyof T, string[]> = {} as Record<keyof T, string[]>;
        
        Object.keys(validators).forEach(key => {
          const fieldKey = key as keyof T;
          const fieldValidators = validators[fieldKey];
          const value = data[fieldKey];
          
          if (fieldValidators) {
            const fieldErrors = fieldValidators
              .map(validator => validator(value))
              .filter(error => error !== null);
            
            if (fieldErrors.length > 0) {
              errors[fieldKey] = fieldErrors;
            }
          }
        });
        
        return {
          isValid: Object.keys(errors).length === 0,
          errors,
        };
      },
    }),
  };
};

// Modular component factory
export const createComponentFactory = <P extends Record<string, any>>(
  baseComponent: React.ComponentType<P>
) => {
  return {
    withProps: (defaultProps: Partial<P>) => {
      return React.forwardRef<any, Omit<P, keyof typeof defaultProps>>((props, ref) => (
        <baseComponent {...defaultProps} {...props} ref={ref} />
      ));
    },
    withStyle: (style: any) => {
      return React.forwardRef<any, P>((props, ref) => (
        <baseComponent {...props} style={[style, props.style]} ref={ref} />
      ));
    },
    withVariant: <V extends string>(variants: Record<V, any>) => {
      return React.forwardRef<any, P & { variant?: V }>((props, ref) => {
        const { variant, ...restProps } = props;
        const variantStyle = variant ? variants[variant] : {};
        
        return (
          <baseComponent {...restProps} style={[variantStyle, restProps.style]} ref={ref} />
        );
      });
    },
  };
};

// Modular hook factory
export const createHookFactory = <T, P extends any[]>(hook: (...args: P) => T) => {
  return {
    withDefaults: (defaultArgs: Partial<P>) => {
      return (...args: P): T => {
        const mergedArgs = { ...defaultArgs, ...args } as P;
        return hook(...mergedArgs);
      };
    },
    withTransform: <U>(transform: (result: T) => U) => {
      return (...args: P): U => {
        const result = hook(...args);
        return transform(result);
      };
    },
    withMemoization: (dependencies: any[]) => {
      return (...args: P): T => {
        // This would typically use useMemo in a real implementation
        return hook(...args);
      };
    },
  };
};

// Modular utility for creating similar functions
export const createFunctionFamily = <T extends (...args: any[]) => any>(
  baseFunction: T,
  variations: Record<string, Partial<Parameters<T>>>
) => {
  const family: Record<string, T> = {} as Record<string, T>;
  
  Object.entries(variations).forEach(([name, defaultArgs]) => {
    family[name] = ((...args: Parameters<T>) => {
      const mergedArgs = { ...defaultArgs, ...args } as Parameters<T>;
      return baseFunction(...mergedArgs);
    }) as T;
  });
  
  return family;
}; 
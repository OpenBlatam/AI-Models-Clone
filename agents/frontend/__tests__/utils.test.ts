// Utility functions tests

describe('Utility Functions', () => {
  describe('formatDuration', () => {
    it('should format milliseconds to mm:ss', () => {
      const formatDuration = (ms: number): string => {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
      };

      expect(formatDuration(0)).toBe('0:00');
      expect(formatDuration(1000)).toBe('0:01');
      expect(formatDuration(60000)).toBe('1:00');
      expect(formatDuration(125000)).toBe('2:05');
      expect(formatDuration(3661000)).toBe('61:01');
    });
  });

  describe('formatNumber', () => {
    it('should format large numbers', () => {
      const formatNumber = (num: number): string => {
        if (num >= 1000000) {
          return `${(num / 1000000).toFixed(1)}M`;
        }
        if (num >= 1000) {
          return `${(num / 1000).toFixed(1)}K`;
        }
        return num.toString();
      };

      expect(formatNumber(0)).toBe('0');
      expect(formatNumber(500)).toBe('500');
      expect(formatNumber(1500)).toBe('1.5K');
      expect(formatNumber(1000000)).toBe('1.0M');
      expect(formatNumber(2500000)).toBe('2.5M');
    });
  });

  describe('debounce', () => {
    jest.useFakeTimers();

    it('should debounce function calls', () => {
      const mockFn = jest.fn();
      
      const debounce = <T extends (...args: any[]) => any>(
        func: T,
        wait: number
      ): ((...args: Parameters<T>) => void) => {
        let timeout: NodeJS.Timeout;
        return (...args: Parameters<T>) => {
          clearTimeout(timeout);
          timeout = setTimeout(() => func(...args), wait);
        };
      };

      const debouncedFn = debounce(mockFn, 300);

      debouncedFn('call1');
      debouncedFn('call2');
      debouncedFn('call3');

      expect(mockFn).not.toHaveBeenCalled();

      jest.advanceTimersByTime(300);

      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenCalledWith('call3');
    });

    afterEach(() => {
      jest.useRealTimers();
    });
  });
});


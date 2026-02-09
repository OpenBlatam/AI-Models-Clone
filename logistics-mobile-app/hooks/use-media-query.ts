import { useWindowDimensions } from './use-window-dimensions';

interface Breakpoints {
  sm: number;
  md: number;
  lg: number;
  xl: number;
}

const defaultBreakpoints: Breakpoints = {
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
};

export function useMediaQuery(breakpoints: Breakpoints = defaultBreakpoints) {
  const { width } = useWindowDimensions();

  return {
    isSm: width >= breakpoints.sm,
    isMd: width >= breakpoints.md,
    isLg: width >= breakpoints.lg,
    isXl: width >= breakpoints.xl,
    isMobile: width < breakpoints.md,
    isTablet: width >= breakpoints.md && width < breakpoints.lg,
    isDesktop: width >= breakpoints.lg,
    width,
  };
}



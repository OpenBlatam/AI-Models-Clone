'use client';

import dynamic from 'next/dynamic';
import type { ComponentType } from 'react';
import type { Stage, Layer, Image, Group, Rect, Circle, Line, Text } from 'react-konva';

const withNoSSR = (Component: any) => {
  return dynamic(() => Promise.resolve(Component), {
    ssr: false,
  });
};

// Dynamically import react-konva components with no SSR
export const DynamicKonva = dynamic(() => import('react-konva').then((mod) => mod.Stage), {
  ssr: false,
});

export const DynamicLayer = dynamic(() => import('react-konva').then((mod) => mod.Layer), {
  ssr: false,
});

export const DynamicRect = dynamic(() => import('react-konva').then((mod) => mod.Rect), {
  ssr: false,
});

export const DynamicCircle = dynamic(() => import('react-konva').then((mod) => mod.Circle), {
  ssr: false,
});

export const DynamicLine = dynamic(() => import('react-konva').then((mod) => mod.Line), {
  ssr: false,
});

export const DynamicText = dynamic(() => import('react-konva').then((mod) => mod.Text), {
  ssr: false,
});

export const DynamicImage = dynamic(() => import('react-konva').then((mod) => mod.Image), {
  ssr: false,
});

export const DynamicGroup = dynamic(() => import('react-konva').then((mod) => mod.Group), {
  ssr: false,
});

// Generic dynamic import for any other Konva components
export function dynamicKonvaComponent<T extends object>(componentName: string): ComponentType<T> {
  return dynamic<T>(
    () => import('react-konva').then((mod) => {
      const Component = mod[componentName];
      if (!Component) {
        throw new Error(`Component ${componentName} not found in react-konva`);
      }
      return Component;
    }),
    { ssr: false }
  );
} 
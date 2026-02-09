// Math Utilities

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function round(value: number, decimals: number = 2): number {
  const factor = Math.pow(10, decimals);
  return Math.round(value * factor) / factor;
}

export function floor(value: number, decimals: number = 2): number {
  const factor = Math.pow(10, decimals);
  return Math.floor(value * factor) / factor;
}

export function ceil(value: number, decimals: number = 2): number {
  const factor = Math.pow(10, decimals);
  return Math.ceil(value * factor) / factor;
}

export function random(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function randomFloat(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

export function percentage(value: number, total: number): number {
  if (total === 0) return 0;
  return (value / total) * 100;
}

export function percentageOf(percentage: number, total: number): number {
  return (percentage / 100) * total;
}

export function average(numbers: number[]): number {
  if (numbers.length === 0) return 0;
  const sum = numbers.reduce((acc, num) => acc + num, 0);
  return sum / numbers.length;
}

export function sum(numbers: number[]): number {
  return numbers.reduce((acc, num) => acc + num, 0);
}

export function min(numbers: number[]): number {
  return Math.min(...numbers);
}

export function max(numbers: number[]): number {
  return Math.max(...numbers);
}

export function distance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Earth's radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) *
      Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRad(degrees: number): number {
  return degrees * (Math.PI / 180);
}

export function isEven(value: number): boolean {
  return value % 2 === 0;
}

export function isOdd(value: number): boolean {
  return value % 2 !== 0;
}

export function isInteger(value: number): boolean {
  return Number.isInteger(value);
}

export function isFloat(value: number): boolean {
  return !Number.isInteger(value);
}


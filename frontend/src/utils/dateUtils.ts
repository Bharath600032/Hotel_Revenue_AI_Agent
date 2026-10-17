/**
 * Date validation and utility helpers to protect against out-of-bounds dates
 * and partial keystroke inputs (e.g., year '2' when typing '2026').
 */

export const isValidDateString = (dStr: string | null | undefined): boolean => {
  if (!dStr || typeof dStr !== 'string' || dStr.length < 10) return false;
  const parts = dStr.split('-');
  if (parts.length !== 3) return false;
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10);
  const day = parseInt(parts[2], 10);
  if (isNaN(year) || isNaN(month) || isNaN(day)) return false;
  if (year < 2000 || year > 2100) return false;
  if (month < 1 || month > 12) return false;
  if (day < 1 || day > 31) return false;
  return true;
};

export const getTodayDateString = (): string => new Date().toISOString().split('T')[0];

export const getNDaysAgoString = (days: number): string =>
  new Date(Date.now() - days * 86400000).toISOString().split('T')[0];

export const getFutureDateString = (days: number): string =>
  new Date(Date.now() + days * 86400000).toISOString().split('T')[0];

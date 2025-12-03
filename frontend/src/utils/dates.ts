import { format, parseISO, isValid } from 'date-fns';
import { el } from 'date-fns/locale';

/**
 * Format a date string to Greek locale format
 */
export function formatDate(dateString: string | null | undefined, formatStr = 'dd/MM/yyyy'): string {
  if (!dateString) return '-';

  try {
    const date = parseISO(dateString);
    if (!isValid(date)) return '-';
    return format(date, formatStr, { locale: el });
  } catch {
    return '-';
  }
}

/**
 * Format a date with time
 */
export function formatDateTime(dateString: string | null | undefined): string {
  return formatDate(dateString, 'dd/MM/yyyy HH:mm');
}

/**
 * Get month name in Greek
 */
export function getMonthName(month: number): string {
  const months = [
    'Ιανουάριος', 'Φεβρουάριος', 'Μάρτιος', 'Απρίλιος',
    'Μάιος', 'Ιούνιος', 'Ιούλιος', 'Αύγουστος',
    'Σεπτέμβριος', 'Οκτώβριος', 'Νοέμβριος', 'Δεκέμβριος'
  ];
  return months[month - 1] || '';
}

/**
 * Format period (month/year) for display
 */
export function formatPeriod(month: number, year: number): string {
  return `${getMonthName(month)} ${year}`;
}

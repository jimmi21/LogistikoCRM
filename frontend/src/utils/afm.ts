/**
 * Επικυρώνει ελληνικό ΑΦΜ (9 ψηφία, έλεγχος checksum)
 * Validates Greek Tax ID (AFM) - 9 digits with checksum validation
 */
export function validateAfm(afm: string): boolean {
  // Check length and if all digits
  if (afm.length !== 9 || !/^\d{9}$/.test(afm)) {
    return false;
  }

  // Checksum algorithm
  let total = 0;
  for (let i = 0; i < 8; i++) {
    total += parseInt(afm[i], 10) * Math.pow(2, 8 - i);
  }

  const checkDigit = total % 11 % 10;
  return checkDigit === parseInt(afm[8], 10);
}

/**
 * Formats AFM for display (adds spaces for readability)
 */
export function formatAfm(afm: string): string {
  if (afm.length !== 9) return afm;
  return `${afm.slice(0, 3)} ${afm.slice(3, 6)} ${afm.slice(6, 9)}`;
}

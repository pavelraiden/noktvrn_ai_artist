/**
 * Formats a date object or string into a readable format.
 * @param date The date to format
 * @returns Formatted date string (e.g., "May 4, 2025")
 */
export function formatDate(date: Date | string | number): string {
  try {
    return new Date(date).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch (error) {
    console.error("Error formatting date:", error);
    return "Invalid Date";
  }
}

/**
 * Formats a number into a readable format (e.g., with commas).
 * @param num The number to format
 * @returns Formatted number string
 */
export function formatNumber(num: number): string {
  try {
    return num.toLocaleString();
  } catch (error) {
    console.error("Error formatting number:", error);
    return "Invalid Number";
  }
}



/**
 * Formats a number as currency (e.g., $1,234.56).
 * @param amount The number to format
 * @param currency The currency code (default: USD)
 * @returns Formatted currency string
 */
export function formatCurrency(amount: number, currency: string = 'USD'): string {
  try {
    return amount.toLocaleString(undefined, {
      style: 'currency',
      currency: currency,
    });
  } catch (error) {
    console.error("Error formatting currency:", error);
    return "Invalid Amount";
  }
}


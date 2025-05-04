import { formatDate, formatNumber } from './formatters';

console.log('--- Testing formatDate ---');
console.log('Date object:', formatDate(new Date(2025, 4, 4))); // Month is 0-indexed
console.log('Date string:', formatDate('2025-05-04T12:00:00Z'));
console.log('Timestamp number:', formatDate(1746331200000)); // May 4, 2025 12:00:00 GMT
console.log('Invalid date string:', formatDate('not a date'));
console.log('Invalid date input:', formatDate(NaN));

console.log('\n--- Testing formatNumber ---');
console.log('Simple number:', formatNumber(1234));
console.log('Large number:', formatNumber(1234567.89));
console.log('Zero:', formatNumber(0));
console.log('Negative number:', formatNumber(-5000));
// console.log('Invalid number input:', formatNumber(NaN)); // toLocaleString throws on NaN

console.log('\n--- Testing Error Handling ---');
try {
  formatDate(new Date('invalid date string'));
} catch (e) {
  console.log('Caught error for invalid date object (expected):', e);
}
try {
  formatNumber(Number('not a number'));
} catch (e) {
  console.log('Caught error for invalid number (expected):', e);
}


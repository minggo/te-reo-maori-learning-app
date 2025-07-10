// Utility function to shuffle an array
export function shuffleArray(array) {
  return [...array].sort(() => Math.random() - 0.5);
}

// Utility function to validate email format
export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Utility function to format timer display
export function formatTimer(seconds) {
  if (seconds < 0) return '0s';
  return `${seconds}s`;
}

// Utility function to calculate quiz score percentage
export function calculateScorePercentage(correct, total) {
  if (total === 0) return 0;
  return Math.round((correct / total) * 100);
}
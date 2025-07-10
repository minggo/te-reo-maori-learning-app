import { shuffleArray, isValidEmail, formatTimer, calculateScorePercentage } from './utils';

describe('Utility Functions', () => {
  describe('shuffleArray', () => {
    test('returns an array with the same length', () => {
      const originalArray = [1, 2, 3, 4, 5];
      const shuffled = shuffleArray(originalArray);
      
      expect(shuffled).toHaveLength(originalArray.length);
    });

    test('returns an array with the same elements', () => {
      const originalArray = [1, 2, 3, 4, 5];
      const shuffled = shuffleArray(originalArray);
      
      expect(shuffled.sort()).toEqual(originalArray.sort());
    });

    test('does not mutate the original array', () => {
      const originalArray = [1, 2, 3, 4, 5];
      const originalCopy = [...originalArray];
      shuffleArray(originalArray);
      
      expect(originalArray).toEqual(originalCopy);
    });

    test('handles empty array', () => {
      const emptyArray = [];
      const shuffled = shuffleArray(emptyArray);
      
      expect(shuffled).toEqual([]);
    });

    test('handles array with one element', () => {
      const singleArray = ['single'];
      const shuffled = shuffleArray(singleArray);
      
      expect(shuffled).toEqual(['single']);
    });

    test('handles array with duplicate elements', () => {
      const duplicateArray = [1, 1, 2, 2, 3];
      const shuffled = shuffleArray(duplicateArray);
      
      expect(shuffled.sort()).toEqual([1, 1, 2, 2, 3]);
    });
  });

  describe('isValidEmail', () => {
    test('returns true for valid email addresses', () => {
      const validEmails = [
        'test@example.com',
        'user123@gmail.com',
        'first.last@domain.co.nz',
        'user+tag@example.org',
        'a@b.co'
      ];

      validEmails.forEach(email => {
        expect(isValidEmail(email)).toBe(true);
      });
    });

    test('returns false for invalid email addresses', () => {
      const invalidEmails = [
        'notanemail',
        '@example.com',
        'test@',
        'test.example.com',
        'test@.com',
        'test@example',
        '',
        'test space@example.com',
        'test@exam ple.com'
      ];

      invalidEmails.forEach(email => {
        expect(isValidEmail(email)).toBe(false);
      });
    });
  });

  describe('formatTimer', () => {
    test('formats positive seconds correctly', () => {
      expect(formatTimer(30)).toBe('30s');
      expect(formatTimer(5)).toBe('5s');
      expect(formatTimer(120)).toBe('120s');
    });

    test('formats zero seconds correctly', () => {
      expect(formatTimer(0)).toBe('0s');
    });

    test('handles negative seconds by returning 0s', () => {
      expect(formatTimer(-5)).toBe('0s');
      expect(formatTimer(-100)).toBe('0s');
    });
  });

  describe('calculateScorePercentage', () => {
    test('calculates percentage correctly', () => {
      expect(calculateScorePercentage(8, 10)).toBe(80);
      expect(calculateScorePercentage(5, 10)).toBe(50);
      expect(calculateScorePercentage(10, 10)).toBe(100);
      expect(calculateScorePercentage(0, 10)).toBe(0);
    });

    test('rounds to nearest integer', () => {
      expect(calculateScorePercentage(1, 3)).toBe(33); // 33.33... rounded
      expect(calculateScorePercentage(2, 3)).toBe(67); // 66.66... rounded
    });

    test('handles zero total by returning 0', () => {
      expect(calculateScorePercentage(5, 0)).toBe(0);
      expect(calculateScorePercentage(0, 0)).toBe(0);
    });

    test('handles correct answers greater than total', () => {
      expect(calculateScorePercentage(15, 10)).toBe(150);
    });
  });
});
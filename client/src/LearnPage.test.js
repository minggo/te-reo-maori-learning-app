import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LearnPage from './LearnPage';

// Mock fetch API
global.fetch = jest.fn();

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = mockLocalStorage;

const mockVocabularyData = [
  { id: '1', maori: 'kia ora', english: 'hello' },
  { id: '2', maori: 'aroha', english: 'love' },
  { id: '3', maori: 'whakapapa', english: 'genealogy' }
];

const renderWithRouter = (component) => {
  return render(
    <MemoryRouter>
      {component}
    </MemoryRouter>
  );
};

describe('LearnPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fetch.mockClear();
    mockLocalStorage.getItem.mockReturnValue('anonymous');
  });

  test('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderWithRouter(<LearnPage />);
    expect(screen.getByText('Loading vocabulary…')).toBeInTheDocument();
  });

  test('fetches vocabulary data on mount', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockVocabularyData,
    });

    renderWithRouter(<LearnPage />);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/vocabulary/?user_id=anonymous&limit=10');
    });
  });

  test('displays vocabulary words', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockVocabularyData,
    });

    renderWithRouter(<LearnPage />);
    
    await waitFor(() => {
      expect(screen.getByText('kia ora')).toBeInTheDocument();
      expect(screen.getByText(/hello/)).toBeInTheDocument();
      expect(screen.getByText('aroha')).toBeInTheDocument();
      expect(screen.getByText(/love/)).toBeInTheDocument();
    });
  });

  test('handles fetch error', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    renderWithRouter(<LearnPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Error: Network error')).toBeInTheDocument();
    });
  });

  test('handles HTTP error response', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({}),
    });

    renderWithRouter(<LearnPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Error: HTTP 404')).toBeInTheDocument();
    });
  });

  test('refetches words when Next Words button is clicked', async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: async () => mockVocabularyData,
    });

    renderWithRouter(<LearnPage />);
    
    await waitFor(() => {
      expect(screen.getByText('kia ora')).toBeInTheDocument();
    });

    const nextWordsButton = screen.getByText('🔄 Next Words');
    fireEvent.click(nextWordsButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
    });
  });

  test('uses anonymous user_id when no user is logged in', async () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockVocabularyData,
    });

    renderWithRouter(<LearnPage />);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/vocabulary/?user_id=anonymous&limit=10');
    });
  });

  test('renders page title and description', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockVocabularyData,
    });

    renderWithRouter(<LearnPage />);
    
    await waitFor(() => {
      expect(screen.getByText('📚 Māori Vocabulary Learning')).toBeInTheDocument();
      expect(screen.getByText('Here are some Māori words and their English meanings:')).toBeInTheDocument();
    });
  });

  test('renders navigation buttons', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockVocabularyData,
    });

    renderWithRouter(<LearnPage />);
    
    await waitFor(() => {
      expect(screen.getByText('🎯 Start Quiz')).toBeInTheDocument();
      expect(screen.getByText('👤 Profile')).toBeInTheDocument();
      expect(screen.getByText('🌐 Culture')).toBeInTheDocument();
    });
  });

  test('console logs user_id when fetching', async () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    mockLocalStorage.getItem.mockReturnValue('anonymous');
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockVocabularyData,
    });

    renderWithRouter(<LearnPage />);
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Fetching words for user_id', 'anonymous');
    });

    consoleSpy.mockRestore();
  });
});
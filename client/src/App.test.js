import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

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

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const mockQuizData = [
  {
    id: '1',
    maori: 'kia ora',
    answer: 'hello',
    options: ['hello', 'goodbye', 'thank you', 'please']
  },
  {
    id: '2',
    maori: 'aroha',
    answer: 'love',
    options: ['love', 'hate', 'peace', 'war']
  }
];

const renderWithRouter = (component) => {
  return render(
    <MemoryRouter>
      {component}
    </MemoryRouter>
  );
};

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fetch.mockClear();
    mockLocalStorage.getItem.mockReturnValue('{"total":0,"correct":0}');
  });

  test('renders loading state initially', () => {
    fetch.mockResolvedValueOnce({
      json: async () => [],
    });
    
    renderWithRouter(<App />);
    expect(screen.getByText('Loading quiz...')).toBeInTheDocument();
  });

  test('fetches quiz data on mount', async () => {
    fetch.mockResolvedValueOnce({
      json: async () => mockQuizData,
    });

    renderWithRouter(<App />);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/quiz/?user_id=anonymous&limit=10');
    });
  });

  test('displays quiz question and choices', async () => {
    fetch.mockResolvedValueOnce({
      json: async () => mockQuizData,
    });

    renderWithRouter(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('kia ora')).toBeInTheDocument();
      expect(screen.getByText('hello')).toBeInTheDocument();
      expect(screen.getByText('goodbye')).toBeInTheDocument();
    });
  });

  test('handles correct answer selection', async () => {
    fetch.mockResolvedValueOnce({
      json: async () => mockQuizData,
    });

    renderWithRouter(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('kia ora')).toBeInTheDocument();
    });

    const correctButton = screen.getByText('hello');
    fireEvent.click(correctButton);

    await waitFor(() => {
      expect(screen.getByText('✅ Correct!')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  test('handles wrong answer selection', async () => {
    fetch.mockResolvedValueOnce({
      json: async () => mockQuizData,
    });

    renderWithRouter(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('kia ora')).toBeInTheDocument();
    });

    const wrongButton = screen.getByText('goodbye');
    fireEvent.click(wrongButton);

    await waitFor(() => {
      expect(screen.getByText('❌ Wrong! Answer: hello')).toBeInTheDocument();
    });
  });

  test('advances to next question', async () => {
    fetch.mockResolvedValueOnce({
      json: async () => mockQuizData,
    });

    renderWithRouter(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('kia ora')).toBeInTheDocument();
    });

    const correctButton = screen.getByText('hello');
    fireEvent.click(correctButton);

    await waitFor(() => {
      expect(screen.getByText('Next')).toBeInTheDocument();
    });

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText('aroha')).toBeInTheDocument();
    });
  });

  test('updates localStorage with quiz stats', async () => {
    fetch.mockResolvedValueOnce({
      json: async () => mockQuizData,
    });

    renderWithRouter(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('kia ora')).toBeInTheDocument();
    });

    const correctButton = screen.getByText('hello');
    fireEvent.click(correctButton);

    await waitFor(() => {
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'quizStats',
        JSON.stringify({ total: 1, correct: 1 })
      );
    });
  });

  test('displays progress counter', async () => {
    fetch.mockResolvedValueOnce({
      json: async () => mockQuizData,
    });

    renderWithRouter(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('1/2')).toBeInTheDocument();
    });
  });

  test('shows timer countdown', async () => {
    fetch.mockResolvedValueOnce({
      json: async () => mockQuizData,
    });

    renderWithRouter(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Time Left: 20s')).toBeInTheDocument();
    });
  });
});
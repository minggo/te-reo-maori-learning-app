import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from './LoginPage';

// Mock fetch API
global.fetch = jest.fn();

// Mock localStorage
const mockSetItem = jest.fn();
const mockGetItem = jest.fn();
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: mockGetItem,
    setItem: mockSetItem,
    removeItem: jest.fn(),
    clear: jest.fn(),
  },
  writable: true,
});

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const renderWithRouter = (component) => {
  return render(
    <MemoryRouter>
      {component}
    </MemoryRouter>
  );
};

describe('LoginPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fetch.mockClear();
    mockNavigate.mockClear();
  });

  test('renders login form', () => {
    renderWithRouter(<LoginPage />);
    
    expect(screen.getByText('🔐 Username Login')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
  });

  test('renders registration link', () => {
    renderWithRouter(<LoginPage />);
    
    expect(screen.getByText("Don't have an account? Register")).toBeInTheDocument();
  });


  test('handles login failure', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Invalid credentials' }),
    });

    renderWithRouter(<LoginPage />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const loginButton = screen.getByRole('button', { name: 'Login' });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  test('handles network error', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    renderWithRouter(<LoginPage />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const loginButton = screen.getByRole('button', { name: 'Login' });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  test('shows loading state during login', async () => {
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderWithRouter(<LoginPage />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const loginButton = screen.getByRole('button', { name: 'Login' });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Logging in…')).toBeInTheDocument();
      expect(usernameInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
      expect(loginButton).toBeDisabled();
    });
  });

  test('prevents form submission without required fields', () => {
    renderWithRouter(<LoginPage />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    
    expect(usernameInput).toBeRequired();
    expect(passwordInput).toBeRequired();
  });

  test('handles form submission', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: 'test-token' }),
    });

    renderWithRouter(<LoginPage />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Login' });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'testuser', password: 'password123' }),
      });
    });
  });

  test('clears error on new login attempt', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Invalid credentials' }),
    });

    renderWithRouter(<LoginPage />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const loginButton = screen.getByRole('button', { name: 'Login' });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });

    // Mock successful login on second attempt
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: 'test-token' }),
    });

    fireEvent.change(passwordInput, { target: { value: 'correctpassword' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.queryByText('Invalid credentials')).not.toBeInTheDocument();
    });
  });
});
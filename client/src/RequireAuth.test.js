import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import RequireAuth from './RequireAuth';

// Mock localStorage
const mockGetItem = jest.fn();
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: mockGetItem,
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
  },
  writable: true,
});

// Test components
const TestProtectedComponent = () => <div>Protected Content</div>;
const TestLoginComponent = () => <div>Login Page</div>;

const renderWithRouter = (initialEntry = '/protected') => {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/login" element={<TestLoginComponent />} />
        <Route path="/protected" element={<RequireAuth />}>
          <Route index element={<TestProtectedComponent />} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
};

describe('RequireAuth Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders protected content when user is authenticated', () => {
    mockGetItem.mockReturnValue('test-user-id');
    
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<TestLoginComponent />} />
          <Route path="/protected" element={<RequireAuth />}>
            <Route index element={<TestProtectedComponent />} />
          </Route>
        </Routes>
      </MemoryRouter>
    );
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
  });

  test('redirects to login when user is not authenticated', () => {
    mockGetItem.mockReturnValue(null);
    
    renderWithRouter();
    
    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('redirects to login when user_id is empty string', () => {
    mockGetItem.mockReturnValue('');
    
    renderWithRouter();
    
    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('calls localStorage.getItem with correct key', () => {
    mockGetItem.mockReturnValue('test-user-id');
    
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<TestLoginComponent />} />
          <Route path="/protected" element={<RequireAuth />}>
            <Route index element={<TestProtectedComponent />} />
          </Route>
        </Routes>
      </MemoryRouter>
    );
    
    expect(mockGetItem).toHaveBeenCalledWith('user_id');
  });

  test('handles multiple nested routes', () => {
    mockLocalStorage.getItem.mockReturnValue('test-user-id');
    
    const NestedComponent = () => <div>Nested Protected Content</div>;
    
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<TestLoginComponent />} />
          <Route path="/protected" element={<RequireAuth />}>
            <Route index element={<TestProtectedComponent />} />
            <Route path="nested" element={<NestedComponent />} />
          </Route>
        </Routes>
      </MemoryRouter>
    );
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('preserves location state for redirect', () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    
    renderWithRouter('/protected?test=1');
    
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });
});
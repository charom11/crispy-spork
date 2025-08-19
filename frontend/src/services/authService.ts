import axios from 'axios';
import { LoginCredentials, RegisterCredentials, AuthResponse, User, TokenData } from '../types/auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, remove it
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await api.post<TokenData>('/auth/login', credentials);
      
      if (response.data.access_token) {
        // Get user info using the token
        const userResponse = await api.get<User>('/auth/me', {
          headers: { Authorization: `Bearer ${response.data.access_token}` }
        });
        
        return {
          success: true,
          token: response.data.access_token,
          user: userResponse.data,
        };
      }
      
      return { success: false, message: 'Login failed' };
    } catch (error: any) {
      if (error.response?.data?.detail) {
        return { success: false, message: error.response.data.detail };
      }
      return { success: false, message: 'Network error occurred' };
    }
  },

  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    try {
      const response = await api.post<User>('/auth/register', credentials);
      
      if (response.data.id) {
        // Auto-login after successful registration
        const loginResponse = await this.login({
          email: credentials.email,
          password: credentials.password,
        });
        
        return loginResponse;
      }
      
      return { success: false, message: 'Registration failed' };
    } catch (error: any) {
      if (error.response?.data?.detail) {
        return { success: false, message: error.response.data.detail };
      }
      if (error.response?.data?.errors) {
        return { success: false, errors: error.response.data.errors };
      }
      return { success: false, message: 'Network error occurred' };
    }
  },

  async getCurrentUser(token: string): Promise<User | null> {
    try {
      const response = await api.get<User>('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching current user:', error);
      return null;
    }
  },

  async updateUser(userData: Partial<User>): Promise<AuthResponse> {
    try {
      const response = await api.put<User>('/auth/me', userData);
      
      if (response.data.id) {
        return {
          success: true,
          user: response.data,
          message: 'Profile updated successfully',
        };
      }
      
      return { success: false, message: 'Update failed' };
    } catch (error: any) {
      if (error.response?.data?.detail) {
        return { success: false, message: error.response.data.detail };
      }
      return { success: false, message: 'Network error occurred' };
    }
  },

  async logout(): Promise<void> {
    // Clear local storage
    localStorage.removeItem('authToken');
  },
};

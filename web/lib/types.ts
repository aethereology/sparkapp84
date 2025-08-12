// Authentication types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  username: string;
  email?: string;
  full_name?: string;
  disabled?: boolean;
  roles: string[];
}

// API Response types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

// Data Room types
export interface Document {
  name: string;
  url: string;
  key?: string;
}

export interface DataRoomResponse {
  org: string;
  documents: Document[];
}

// Donation types
export interface Donation {
  donation_id: string;
  donor_id: string;
  amount: number;
  designation?: string;
  restricted?: boolean;
  method: string;
  received_at: string;
  receipt_id?: string;
  soft_credit_to?: string;
  designation_breakdown?: string;
}

export interface Donor {
  donor_id: string;
  primary_contact_name: string;
  email?: string;
  phone?: string;
  address?: string;
}

// Receipt types
export interface ReceiptRequest {
  donation_id: string;
}

export interface EmailReceiptResponse {
  sent: boolean;
}

// Health check types
export interface HealthCheckResponse {
  status: string;
  env: string;
  email_provider: string;
  logo_exists: boolean;
  timestamp?: string;
}

// Error types
export interface ApiError {
  error: string;
  status_code?: number;
  details?: any;
}

// Component prop types
export interface DataRoomProps {
  org?: string;
}

// Form types
export interface ContactFormData {
  name: string;
  email: string;
  message: string;
}

// Utility types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// Authentication context types
export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// API client configuration
export interface ApiClientConfig {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}

// HTTP method types
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// SWR configuration
export interface SWRConfig {
  refreshInterval?: number;
  revalidateOnFocus?: boolean;
  revalidateOnReconnect?: boolean;
}
// Backend API URL
// Using direct URL to backend since the backend has CORS properly configured
// If you want to use Next.js proxy instead, set this to empty string ''
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Common fetch options for all API calls
// This helps ensure consistent behavior across all requests
const getDefaultFetchOptions = (): RequestInit => ({
  credentials: 'omit', // Don't send credentials unless needed
  cache: 'no-cache', // Don't cache requests
  mode: 'cors', // Enable CORS
});

// Type definitions for API requests and responses
export interface SignupRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface UserResponse {
  id: number;
  email: string;
  username: string;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail: string;
}

// Helper function to handle API errors
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    try {
      const error: ApiError = await response.json();
      console.error('API error response:', error);
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    } catch (jsonError) {
      console.error('Failed to parse error response:', jsonError);
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  }
  return response.json();
}

// Helper function to make API requests with better error handling
async function apiRequest<T>(
  url: string, 
  options: RequestInit = {}
): Promise<T> {
  try {
    // Merge default options with provided options
    const fetchOptions: RequestInit = {
      ...getDefaultFetchOptions(),
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const fullUrl = url.startsWith('http') ? url : `http://localhost:8000${url}`;
    console.log(`Making ${options.method || 'GET'} request to:`, fullUrl);
    console.log('Request options:', { 
      method: options.method || 'GET',
      hasBody: !!options.body,
      headers: fetchOptions.headers 
    });
    
    const response = await fetch(fullUrl, fetchOptions);
    
    console.log(`Response status: ${response.status}`);
    
    return handleResponse<T>(response);
  } catch (error) {
    console.error('API request failed:', error);
    console.error('Failed URL:', url);
    console.error('Error details:', {
      name: error instanceof Error ? error.name : 'Unknown',
      message: error instanceof Error ? error.message : String(error)
    });
    
    // Check if it's a network error (no response from server)
    if (error instanceof TypeError && (error.message.includes('fetch') || error.message.includes('Failed to fetch'))) {
      throw new Error(
        'Cannot connect to the server. Please make sure:\n' +
        '1. The backend is running (docker-compose up)\n' +
        '2. The frontend dev server is running (pnpm dev)\n' +
        '3. Try accessing http://localhost:8000 directly in your browser'
      );
    }
    
    // Re-throw other errors as-is
    throw error;
  }
}

// Authentication API calls

/**
 * Sign up a new user
 * @param data - User registration data (username, email, password)
 * @returns User information
 */
export async function signup(data: SignupRequest): Promise<UserResponse> {
  return apiRequest<UserResponse>(`${API_BASE_URL}/api/v1/auth/signup`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Log in a user
 * @param data - Login credentials (username, password)
 * @returns Access token and token type
 */
export async function login(data: LoginRequest): Promise<TokenResponse> {
  return apiRequest<TokenResponse>(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Get current user information
 * @param token - Access token
 * @returns User information
 */
export async function getCurrentUser(token: string): Promise<UserResponse> {
  return apiRequest<UserResponse>(`${API_BASE_URL}/api/v1/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
}

/**
 * Check if a username is available
 * @param username - Username to check
 * @returns Whether the username is available
 */
export async function checkUsernameAvailability(username: string): Promise<{ available: boolean; message: string }> {
  return apiRequest<{ available: boolean; message: string }>(
    `${API_BASE_URL}/api/v1/auth/check-username/${username}`
  );
}

// Seoul Events API calls

/**
 * Seoul Event response from the backend
 */
export interface SeoulEventResponse {
  id: number;
  codename: string | null;      // Category like "뮤지컬/오페라", "콘서트"
  gu_name: string | null;        // District like "송파구", "강남구"
  title: string;                 // Event title
  date_text: string | null;      // Date as text (e.g., "2025.05.24(토) ~ 2025.05.26(월)")
  place: string | null;          // Venue/location
  org_name: string | null;       // Organization name
  use_target: string | null;     // Target audience
  use_fee: string | null;        // Fee information
  inquiry: string | null;        // Contact information
  player: string | null;         // Performer information
  program: string | null;        // Program description
  etc_desc: string | null;       // Additional description
  org_link: string | null;       // Organization website
  main_img: string | null;       // Main image URL
  rgst_date: string | null;      // Registration date
  ticket_type: string | null;    // Ticket type (시민/기관)
  start_date: string | null;     // Start date (YYYY-MM-DD)
  end_date: string | null;       // End date (YYYY-MM-DD)
  theme_code: string | null;     // Theme code
  lot: number | null;            // Longitude
  lat: number | null;            // Latitude
  is_free: string | null;        // Free or paid ("무료"/"유료")
  hmpg_addr: string | null;      // Culture portal URL
  pro_time: string | null;       // Event time
}

/**
 * Parameters for fetching Seoul events
 */
export interface SeoulEventFilters {
  skip?: number;
  limit?: number;
  codename?: string;     // Filter by category
  gu_name?: string;      // Filter by district
  search?: string;       // Search query
  date?: string;         // Specific date (YYYY-MM-DD)
  start_date?: string;   // Start date range
  end_date?: string;     // End date range
  is_free?: string;      // Filter by free/paid
}

/**
 * Fetch Seoul events with optional filters
 * @param filters - Optional filters for the events
 * @returns List of Seoul events
 */
export async function getSeoulEvents(filters?: SeoulEventFilters): Promise<SeoulEventResponse[]> {
  // Build query string from filters
  const queryParams = new URLSearchParams();
  
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, String(value));
      }
    });
  }
  
  const queryString = queryParams.toString();
  // Add trailing slash to avoid 307 redirect which can cause CORS issues
  const url = `${API_BASE_URL}/api/v1/seoul-events/${queryString ? `?${queryString}` : ''}`;
  
  return apiRequest<SeoulEventResponse[]>(url);
}

/**
 * Fetch a single Seoul event by ID
 * @param eventId - The event ID
 * @returns Seoul event details
 */
export async function getSeoulEvent(eventId: number): Promise<SeoulEventResponse> {
  return apiRequest<SeoulEventResponse>(`${API_BASE_URL}/api/v1/seoul-events/${eventId}`);
}

/**
 * Get calendar event counts for a specific month
 * @param year - Year
 * @param month - Month (1-12)
 * @returns Object with dates as keys and event counts as values
 */
export async function getCalendarEventCounts(year: number, month: number): Promise<Record<string, number>> {
  return apiRequest<Record<string, number>>(
    `${API_BASE_URL}/api/v1/seoul-events/calendar?year=${year}&month=${month}`
  );
}

/**
 * Like a Seoul event (requires authentication)
 * @param eventId - The event ID to like
 * @param token - Access token
 * @returns Success message
 */
export async function likeSeoulEvent(eventId: number, token: string): Promise<{ message: string; event_id: number }> {
  return apiRequest<{ message: string; event_id: number }>(
    `${API_BASE_URL}/api/v1/seoul-events/${eventId}/like`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
}

/**
 * Unlike a Seoul event (requires authentication)
 * @param eventId - The event ID to unlike
 * @param token - Access token
 * @returns Success message
 */
export async function unlikeSeoulEvent(eventId: number, token: string): Promise<{ message: string; event_id: number }> {
  return apiRequest<{ message: string; event_id: number }>(
    `${API_BASE_URL}/api/v1/seoul-events/${eventId}/like`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
}

/**
 * Check if a Seoul event is liked (requires authentication)
 * @param eventId - The event ID to check
 * @param token - Access token
 * @returns Whether the event is liked
 */
export async function checkSeoulEventLiked(eventId: number, token: string): Promise<{ event_id: number; is_liked: boolean }> {
  return apiRequest<{ event_id: number; is_liked: boolean }>(
    `${API_BASE_URL}/api/v1/seoul-events/${eventId}/is-liked`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
}

/**
 * Get all liked Seoul events for the current user (requires authentication)
 * @param token - Access token
 * @param skip - Number of events to skip (for pagination)
 * @param limit - Maximum number of events to return
 * @returns List of liked Seoul events
 */
export async function getLikedSeoulEvents(token: string, skip: number = 0, limit: number = 100): Promise<SeoulEventResponse[]> {
  return apiRequest<SeoulEventResponse[]>(
    `${API_BASE_URL}/api/v1/seoul-events/liked/all?skip=${skip}&limit=${limit}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
}

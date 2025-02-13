import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

// Add request interceptor to get CSRF token
api.interceptors.request.use(async (config) => {
    // Only get CSRF token for non-GET methods
    if (config.method !== 'get') {
        try {
            const response = await axios.get(`${API_URL}/auth/csrf/`, { withCredentials: true });
            config.headers['X-CSRFToken'] = response.data.csrfToken;
        } catch (error) {
            console.error('Error fetching CSRF token:', error);
        }
    }
    return config;
});

// Book endpoints
export const getBooks = () => api.get('/books/');
export const getAvailableBooks = () => api.get('/books/available/');
export const getMyBooks = () => api.get('/books/my_books/');
export const createBook = (bookData) => api.post('/books/', bookData);
export const updateBook = (bookId, bookData) => api.put(`/books/${bookId}/`, bookData);
export const deleteBook = (bookId) => api.delete(`/books/${bookId}/`);
export const requestRental = (bookId, days) => api.post(`/books/${bookId}/request_rental/`, { days });

// Rental endpoints
export const getRentals = () => api.get('/rentals/');
export const getMyRentals = () => api.get('/rentals/my_rentals/');
export const getRentalRequests = () => api.get('/rentals/rental_requests/');
export const getActiveRentals = () => api.get('/rentals/active/');
export const approveRental = (rentalId) => api.post(`/rentals/${rentalId}/approve_rental/`);
export const rejectRental = (rentalId) => api.post(`/rentals/${rentalId}/reject_rental/`);
export const returnBook = (rentalId) => api.post(`/rentals/${rentalId}/return_book/`);

// Auth endpoints
export const register = (userData) => api.post('/auth/register/', userData);
export const login = (credentials) => api.post('/auth/login/', credentials);
export const logout = () => api.post('/auth/logout/');
export const getCurrentUser = () => api.get('/auth/profile/');
export const updateProfile = (userData) => api.put('/auth/profile/update/', userData);
export const getProfile = () => api.get('/auth/profile/');
export const getNearbyUsers = (radius) => api.get(`/auth/nearby-users/?radius=${radius}`);

export default api; 
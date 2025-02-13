import api from './api';

export const register = async (userData) => {
    const response = await api.post('/auth/register/', userData);
    if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
};

export const login = async (credentials) => {
    const response = await api.post('/auth/login/', credentials);
    if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
};

export const logout = async () => {
    await api.post('/auth/logout/');
    localStorage.removeItem('user');
};

export const getCurrentUser = () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
};

export const updateProfile = async (userData) => {
    const response = await api.put('/auth/profile/update/', userData);
    const user = getCurrentUser();
    if (response.data && user) {
        const updatedUser = { ...user, ...response.data };
        localStorage.setItem('user', JSON.stringify(updatedUser));
    }
    return response.data;
};

export const getProfile = async () => {
    const response = await api.get('/auth/profile/');
    return response.data;
};

export const getNearbyUsers = async (radius) => {
    const response = await api.get(`/auth/nearby-users/?radius=${radius}`);
    return response.data;
}; 
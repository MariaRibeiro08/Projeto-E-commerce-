import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Use seu IP
const API_URL = 'http://192.168.0.135:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('userToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (email, senha) => {
  try {
    const response = await api.post('/api/mobile/login', { email, senha });
    if (response.data.success) {
      await AsyncStorage.setItem('userToken', response.data.token);
      await AsyncStorage.setItem('userData', JSON.stringify(response.data.usuario));
      return { success: true, usuario: response.data.usuario };
    }
    return { success: false, message: response.data.message };
  } catch (error) {
    return { success: false, message: 'Erro de conexão' };
  }
};

export const getProdutos = async (categoriaId = null) => {
  const url = categoriaId 
    ? `/api/mobile/produtos?categoria_id=${categoriaId}`
    : '/api/mobile/produtos';
  const response = await api.get(url);
  return response.data;
};

export const getUserData = async () => {
  const userData = await AsyncStorage.getItem('userData');
  return userData ? JSON.parse(userData) : null;
};

export const logout = async () => {
  await AsyncStorage.removeItem('userToken');
  await AsyncStorage.removeItem('userData');
};

export default api;
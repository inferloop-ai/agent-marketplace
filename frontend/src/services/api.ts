// frontend/src/services/api.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          toast.error('Session expired. Please login again.');
          window.location.href = '/login';
        } else if (error.response?.status >= 500) {
          toast.error('Server error. Please try again later.');
        } else if (error.response?.data?.message) {
          toast.error(error.response.data.message);
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  loadToken() {
    const token = localStorage.getItem('auth_token');
    if (token) {
      this.token = token;
    }
  }

  // Auth endpoints
  async login(username: string, password: string) {
    const response = await this.client.post('/auth/login', {
      username,
      password,
    });
    return response.data;
  }

  async register(userData: any) {
    const response = await this.client.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Workflow endpoints
  async getWorkflows(params?: any) {
    const response = await this.client.get('/workflows', { params });
    return response.data;
  }

  async getWorkflow(id: string) {
    const response = await this.client.get(`/workflows/${id}`);
    return response.data;
  }

  async createWorkflow(data: any) {
    const response = await this.client.post('/workflows', data);
    return response.data;
  }

  async updateWorkflow(id: string, data: any) {
    const response = await this.client.put(`/workflows/${id}`, data);
    return response.data;
  }

  async deleteWorkflow(id: string) {
    await this.client.delete(`/workflows/${id}`);
  }

  // Node endpoints
  async createNode(workflowId: string, nodeData: any) {
    const response = await this.client.post(`/workflows/${workflowId}/nodes`, nodeData);
    return response.data;
  }

  async updateNode(workflowId: string, nodeId: string, data: any) {
    const response = await this.client.put(`/workflows/${workflowId}/nodes/${nodeId}`, data);
    return response.data;
  }

  async deleteNode(workflowId: string, nodeId: string) {
    await this.client.delete(`/workflows/${workflowId}/nodes/${nodeId}`);
  }

  // Execution endpoints
  async executeWorkflow(workflowId: string, inputs?: any) {
    const response = await this.client.post(`/workflows/${workflowId}/execute`, { inputs });
    return response.data;
  }

  async getExecutions(workflowId?: string) {
    const params = workflowId ? { workflow_id: workflowId } : {};
    const response = await this.client.get('/executions', { params });
    return response.data;
  }

  async getExecution(executionId: string) {
    const response = await this.client.get(`/executions/${executionId}`);
    return response.data;
  }
}

export const apiService = new ApiService();


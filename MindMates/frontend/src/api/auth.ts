import request from './request'
import type { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types'

export const authApi = {
  login(data: LoginRequest): Promise<AuthResponse> {
    return request.post('/auth/login', data)
  },

  register(data: RegisterRequest): Promise<AuthResponse> {
    return request.post('/auth/register', data)
  },

  getProfile(): Promise<User> {
    return request.get('/auth/profile')
  },

  updateProfile(data: Partial<User>): Promise<User> {
    return request.put('/auth/profile', data)
  },

  changePassword(oldPassword: string, newPassword: string): Promise<void> {
    return request.post('/auth/change-password', { oldPassword, newPassword })
  }
}

// API 응답 타입
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: {
    code: string
    message: string
    details?: string
  }
  meta?: {
    requestId?: string
    timestamp?: string
    processingTime?: number
  }
}

// API 키 관련 타입
export interface ApiKey {
  id: string
  name: string
  provider: 'anthropic' | 'openai'
  maskedKey?: string
  isActive: boolean
  createdAt: string
  lastUsed?: string
  userId: string
}

export interface AddApiKeyForm {
  name: string
  provider: 'anthropic' | 'openai'
  apiKey: string
}

// 변환 요청 타입
export interface ConvertRequest {
  url: string
  ai_provider: 'anthropic' | 'openai'
  api_key: string
  model?: string
}

export interface ConvertResponse {
  id: string
  originalTitle: string
  originalContent: string
  socialContent: string
  platform: string
  aiProvider: string
  processingTime: number
  timestamp: string
  usage?: {
    input_tokens: number
    output_tokens: number
    total_tokens: number
  }
}

// 사용자 관련 타입
export interface User {
  id: string
  email: string
  name?: string
  image?: string
  createdAt: string
  updatedAt: string
}

// 사용량 통계 타입
export interface UsageStats {
  totalRequests: number
  totalTokens: number
  totalCost: number
  averageProcessingTime: number
  successRate: number
  dailyStats: Array<{
    date: string
    requests: number
    tokens: number
    cost: number
  }>
}

// 뉴스 기사 타입
export interface NewsArticle {
  url: string
  title: string
  content: string
  author?: string
  publishedAt?: string
  source?: string
}

// 소셜 미디어 플랫폼 타입
export type SocialPlatform = 'twitter' | 'threads' | 'linkedin' | 'instagram'

// 에러 타입
export interface AppError {
  code: string
  message: string
  details?: string
  statusCode?: number
}

// 설정 타입
export interface AppSettings {
  defaultAiProvider: 'anthropic' | 'openai'
  defaultModel: string
  maxContentLength: number
  autoSave: boolean
  theme: 'light' | 'dark' | 'system'
}

// 폼 검증 타입
export interface ValidationError {
  field: string
  message: string
}

// 페이지네이션 타입
export interface PaginationMeta {
  page: number
  limit: number
  total: number
  totalPages: number
  hasNext: boolean
  hasPrev: boolean
}

export interface PaginatedResponse<T> {
  success: boolean
  data?: T[]
  error?: {
    code: string
    message: string
    details?: string
  }
  meta: PaginationMeta & {
    requestId?: string
    timestamp?: string
    processingTime?: number
  }
} 
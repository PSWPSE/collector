import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { Anthropic } from '@anthropic-ai/sdk'
import OpenAI from 'openai'
import { prisma } from '@/lib/prisma'
import { encrypt, decrypt, validateApiKeyFormat, maskApiKey } from '@/lib/crypto'
import type { AddApiKeyForm, ApiResponse, ApiKey } from '@/types'

// POST: API 키 추가
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session?.user?.email) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'UNAUTHORIZED',
          message: '로그인이 필요합니다.',
        }
      } as ApiResponse, { status: 401 })
    }

    const body: AddApiKeyForm = await request.json()
    const { name, provider, apiKey } = body

    // 입력 값 검증
    if (!name || !provider || !apiKey) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'INVALID_REQUEST',
          message: '모든 필드가 필요합니다.',
        }
      } as ApiResponse, { status: 400 })
    }

    // API 키 형식 검증
    if (!validateApiKeyFormat(apiKey, provider)) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'INVALID_API_KEY',
          message: `올바르지 않은 ${provider === 'anthropic' ? 'Anthropic' : 'OpenAI'} API 키 형식입니다.`,
        }
      } as ApiResponse, { status: 400 })
    }

    // 사용자 조회
    const user = await prisma.user.findUnique({
      where: { email: session.user.email }
    })

    if (!user) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: '사용자를 찾을 수 없습니다.',
        }
      } as ApiResponse, { status: 404 })
    }

    // API 키 유효성 테스트
    const isValid = await testApiKey(apiKey, provider)
    if (!isValid) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'INVALID_API_KEY',
          message: 'API 키가 유효하지 않습니다. 키를 확인해주세요.',
        }
      } as ApiResponse, { status: 400 })
    }

    // API 키 암호화
    const encryptedKey = encrypt(apiKey)

    // 데이터베이스에 저장
    const savedApiKey = await prisma.apiKey.create({
      data: {
        name,
        provider,
        keyHash: encryptedKey,
        userId: user.id,
      }
    })

    // 응답에서 keyHash 제외
    const { keyHash, ...apiKeyResponse } = savedApiKey

    return NextResponse.json({
      success: true,
      data: {
        ...apiKeyResponse,
        maskedKey: maskApiKey(apiKey)
      }
    } as ApiResponse)

  } catch (error) {
    console.error('API 키 추가 중 오류:', error)
    return NextResponse.json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: '서버 오류가 발생했습니다.',
      }
    } as ApiResponse, { status: 500 })
  }
}

// GET: API 키 목록 조회
export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session?.user?.email) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'UNAUTHORIZED',
          message: '로그인이 필요합니다.',
        }
      } as ApiResponse, { status: 401 })
    }

    // 사용자 조회
    const user = await prisma.user.findUnique({
      where: { email: session.user.email },
      include: {
        apiKeys: {
          orderBy: { createdAt: 'desc' }
        }
      }
    })

    if (!user) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: '사용자를 찾을 수 없습니다.',
        }
      } as ApiResponse, { status: 404 })
    }

    // keyHash 제외하고 응답
    const apiKeys = user.apiKeys.map(({ keyHash, ...apiKey }) => ({
      ...apiKey,
      maskedKey: '****' // 실제 키는 노출하지 않음
    }))

    return NextResponse.json({
      success: true,
      data: apiKeys
    } as ApiResponse<typeof apiKeys>)

  } catch (error) {
    console.error('API 키 목록 조회 중 오류:', error)
    return NextResponse.json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: '서버 오류가 발생했습니다.',
      }
    } as ApiResponse, { status: 500 })
  }
}

// DELETE: API 키 삭제
export async function DELETE(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session?.user?.email) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'UNAUTHORIZED',
          message: '로그인이 필요합니다.',
        }
      } as ApiResponse, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const id = searchParams.get('id')

    if (!id) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'INVALID_REQUEST',
          message: 'API 키 ID가 필요합니다.',
        }
      } as ApiResponse, { status: 400 })
    }

    // 사용자 조회
    const user = await prisma.user.findUnique({
      where: { email: session.user.email }
    })

    if (!user) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: '사용자를 찾을 수 없습니다.',
        }
      } as ApiResponse, { status: 404 })
    }

    // API 키 삭제 (본인의 키만 삭제 가능)
    const deletedApiKey = await prisma.apiKey.delete({
      where: {
        id,
        userId: user.id
      }
    })

    return NextResponse.json({
      success: true,
      data: { message: 'API 키가 삭제되었습니다.' }
    } as ApiResponse)

  } catch (error) {
    console.error('API 키 삭제 중 오류:', error)
    return NextResponse.json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: '서버 오류가 발생했습니다.',
      }
    } as ApiResponse, { status: 500 })
  }
}

/**
 * API 키 유효성 테스트
 */
async function testApiKey(apiKey: string, provider: 'anthropic' | 'openai'): Promise<boolean> {
  try {
    if (provider === 'anthropic') {
      const anthropic = new Anthropic({ apiKey })
      // 간단한 테스트 메시지로 API 키 검증
      await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 10,
        messages: [{ role: 'user', content: 'Hi' }],
      })
      return true
    } else if (provider === 'openai') {
      const openai = new OpenAI({ apiKey })
      // 간단한 테스트 요청으로 API 키 검증
      await openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: 'Hi' }],
        max_tokens: 5,
      })
      return true
    }
    return false
  } catch (error) {
    console.error(`${provider} API 키 테스트 실패:`, error)
    return false
  }
} 
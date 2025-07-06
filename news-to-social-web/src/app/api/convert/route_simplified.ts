/**
 * 간소화된 변환 API 라우트
 * 복잡한 중간 계층 제거, 직접 백엔드 연결
 */

import { NextRequest, NextResponse } from 'next/server';

// 통합 백엔드 URL
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://nongbux-production.up.railway.app';

// 요청 타입 정의
interface ConvertRequest {
  url: string;
  title: string;
  content: string;
  provider?: string;
  user_api_key?: string;
}

// 응답 타입 정의
interface ConvertResponse {
  id: string;
  url: string;
  original_title: string;
  markdown_content: string;
  provider: string;
  processing_time_seconds: number;
  timestamp: string;
  success: boolean;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  error?: string;
}

export async function POST(request: NextRequest) {
  try {
    // 요청 데이터 파싱
    const body: ConvertRequest = await request.json();
    
    // 입력 검증
    if (!body.url || !body.title || !body.content) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'URL, 제목, 내용이 모두 필요합니다.' 
        },
        { status: 400 }
      );
    }

    // 제공자 검증
    const validProviders = ['openai', 'anthropic'];
    if (body.provider && !validProviders.includes(body.provider)) {
      return NextResponse.json(
        { 
          success: false, 
          error: '지원되지 않는 AI 제공자입니다.' 
        },
        { status: 400 }
      );
    }

    console.log(`🔄 Converting with ${body.provider || 'openai'}: ${body.url}`);

    // 통합 백엔드 API 직접 호출
    const backendResponse = await fetch(`${BACKEND_URL}/api/v1/convert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: body.url,
        title: body.title,
        content: body.content,
        provider: body.provider || 'openai',
        user_api_key: body.user_api_key || undefined
      })
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json();
      console.error('❌ Backend error:', errorData);
      
      return NextResponse.json(
        { 
          success: false, 
          error: errorData.error || '변환 중 오류가 발생했습니다.' 
        },
        { status: backendResponse.status }
      );
    }

    const result: ConvertResponse = await backendResponse.json();
    
    // 성공 응답
    if (result.success) {
      console.log(`✅ Conversion completed: ${result.id}`);
      
      return NextResponse.json({
        success: true,
        data: {
          id: result.id,
          originalTitle: result.original_title,
          socialContent: result.markdown_content,
          platform: 'markdown',
          aiProvider: result.provider,
          processingTime: result.processing_time_seconds,
          timestamp: result.timestamp,
          usage: result.token_usage
        }
      });
    } else {
      console.error('❌ Conversion failed:', result.error);
      
      return NextResponse.json(
        { 
          success: false, 
          error: result.error || '변환에 실패했습니다.' 
        },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error('❌ API route error:', error);
    
    return NextResponse.json(
      { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      },
      { status: 500 }
    );
  }
}

// 백엔드 상태 확인 엔드포인트
export async function GET() {
  try {
    const healthResponse = await fetch(`${BACKEND_URL}/api/v1/health`);
    const healthData = await healthResponse.json();
    
    return NextResponse.json({
      status: 'healthy',
      backend: healthData,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Health check failed:', error);
    
    return NextResponse.json(
      { 
        status: 'error',
        error: '백엔드 서버에 연결할 수 없습니다.',
        timestamp: new Date().toISOString()
      },
      { status: 503 }
    );
  }
} 
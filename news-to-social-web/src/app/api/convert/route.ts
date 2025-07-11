/**
 * 간소화된 변환 API 라우트
 * 복잡한 중간 계층 제거, 직접 백엔드 연결
 */

import { NextRequest, NextResponse } from 'next/server';

// 통합 백엔드 URL
const BACKEND_URL = 'https://nongbux-production.up.railway.app';

console.log(`🔗 Unified Backend URL: ${BACKEND_URL}`);

export async function POST(request: NextRequest) {
  try {
    console.log('🔄 Processing conversion request...');
    
    // 요청 데이터 파싱
    const body = await request.json();
    const { url, title, content, provider = 'openai', user_api_key } = body;
    
    // 입력 검증
    if (!url || !title || !content) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'URL, 제목, 내용이 모두 필요합니다.' 
        },
        { status: 400 }
      );
    }

    console.log(`🔄 Converting ${url} with ${provider}`);

    // 통합 백엔드 API 직접 호출
    const backendResponse = await fetch(`${BACKEND_URL}/api/v1/convert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: url,
        title: title,
        content: content,
        provider: provider,
        user_api_key: user_api_key || undefined
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

    const result = await backendResponse.json();
    
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

// 백엔드 상태 확인
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
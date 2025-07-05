import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { apiKey, provider } = await request.json();

    // 입력 검증
    if (!apiKey || typeof apiKey !== 'string') {
      return NextResponse.json(
        { error: 'API 키를 입력해주세요.' },
        { status: 400 }
      );
    }

    if (!provider || !['openai', 'anthropic'].includes(provider)) {
      return NextResponse.json(
        { error: '지원되는 API 제공업체를 선택해주세요.' },
        { status: 400 }
      );
    }

    // API 키 검증
    if (provider === 'openai') {
      // OpenAI API 키 검증
      if (!apiKey.startsWith('sk-')) {
        return NextResponse.json(
          { error: 'OpenAI API 키는 sk-로 시작해야 합니다.' },
          { status: 400 }
        );
      }

      try {
        const { OpenAI } = await import('openai');
        const openai = new OpenAI({ apiKey });
        
        // 간단한 테스트 요청으로 키 유효성 확인
        await openai.models.list();
        
        return NextResponse.json({
          success: true,
          provider: 'openai',
          message: 'OpenAI API 키가 유효합니다.'
        });
      } catch (error: any) {
        console.error('OpenAI API validation error:', error);
        
        if (error.status === 401) {
          return NextResponse.json(
            { error: '유효하지 않은 OpenAI API 키입니다.' },
            { status: 401 }
          );
        }
        
        return NextResponse.json(
          { error: 'OpenAI API 키 검증 중 오류가 발생했습니다.' },
          { status: 500 }
        );
      }
    }

    if (provider === 'anthropic') {
      // Anthropic API 키 검증
      if (!apiKey.startsWith('sk-ant-')) {
        return NextResponse.json(
          { error: 'Anthropic API 키는 sk-ant-로 시작해야 합니다.' },
          { status: 400 }
        );
      }

      try {
        const { Anthropic } = await import('@anthropic-ai/sdk');
        const anthropic = new Anthropic({ apiKey });
        
        // 간단한 테스트 요청으로 키 유효성 확인
        await anthropic.messages.create({
          model: 'claude-3-5-sonnet-20241022',
          max_tokens: 10,
          messages: [
            {
              role: 'user',
              content: 'Test'
            }
          ]
        });
        
        return NextResponse.json({
          success: true,
          provider: 'anthropic',
          message: 'Anthropic API 키가 유효합니다.'
        });
      } catch (error: any) {
        console.error('Anthropic API validation error:', error);
        
        if (error.status === 401) {
          return NextResponse.json(
            { error: '유효하지 않은 Anthropic API 키입니다.' },
            { status: 401 }
          );
        }
        
        return NextResponse.json(
          { error: 'Anthropic API 키 검증 중 오류가 발생했습니다.' },
          { status: 500 }
        );
      }
    }

    return NextResponse.json(
      { error: '지원되지 않는 API 제공업체입니다.' },
      { status: 400 }
    );

  } catch (error) {
    console.error('API key validation error:', error);
    return NextResponse.json(
      { error: '서버 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
} 
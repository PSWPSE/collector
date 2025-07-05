import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import * as fs from 'fs/promises';
import * as path from 'path';

// FastAPI 서버 URL - 127.0.0.1 사용으로 연결 안정성 개선
const FASTAPI_URL = 'http://127.0.0.1:8000';

// FastAPI 서버 연결 테스트
async function testFastApiConnection(): Promise<boolean> {
  try {
    const response = await fetch(`${FASTAPI_URL}/api/v1/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000) // 5초 타임아웃
    });
    return response.ok;
  } catch (error) {
    console.error('FastAPI connection test failed:', error);
    return false;
  }
}

// 사이트 접근 가능성 검증
async function validateSiteAccess(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, {
      method: 'HEAD',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    
    return response.ok;
  } catch (error) {
    console.error('Site access validation error:', error);
    return false;
  }
}

// FastAPI 서버로 변환 요청
async function callFastApiConverter(
  url: string,
  userApiKey: string,
  userApiProvider: 'openai' | 'anthropic'
): Promise<{content: string, taskId: string}> {
  
  console.log(`Calling FastAPI converter for URL: ${url}`);
  console.log(`Provider: ${userApiProvider}`);
  
  // 먼저 FastAPI 서버 연결 테스트
  const isConnected = await testFastApiConnection();
  if (!isConnected) {
    throw new Error('FastAPI 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
  }
  
  try {
    // 1. 변환 요청 시작
    const convertResponse = await fetch(`${FASTAPI_URL}/api/v1/convert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: url,
        platforms: ['twitter'],
        converter_type: userApiProvider,
        api_key: userApiKey,
        api_provider: userApiProvider
      }),
      signal: AbortSignal.timeout(30000) // 30초 타임아웃
    });

    if (!convertResponse.ok) {
      const errorData = await convertResponse.json();
      throw new Error(errorData.detail || `FastAPI 요청 실패: ${convertResponse.status}`);
    }

    const convertData = await convertResponse.json();
    
    if (!convertData.success || !convertData.task_id) {
      throw new Error(convertData.message || '변환 요청에 실패했습니다.');
    }

    console.log(`FastAPI conversion started, task_id: ${convertData.task_id}`);
    
    // 2. 결과 폴링
    const result = await pollForResult(convertData.task_id);
    
    return {
      content: result.converted_content,
      taskId: convertData.task_id
    };
    
  } catch (error) {
    console.error('FastAPI conversion error:', error);
    throw error;
  }
}

// 결과 폴링 함수
async function pollForResult(taskId: string): Promise<any> {
  const maxAttempts = 30; // 최대 30회 시도 (약 60초)
  const pollInterval = 2000; // 2초 간격
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const response = await fetch(`${FASTAPI_URL}/api/v1/conversion/${taskId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('변환 작업을 찾을 수 없습니다.');
        }
        throw new Error(`상태 확인 실패: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'completed') {
        return result;
      } else if (result.status === 'failed') {
        throw new Error(result.error || '변환에 실패했습니다.');
      } else {
        // 아직 진행 중
        console.log(`Conversion in progress: ${result.current_step} (${result.progress}%)`);
        await new Promise(resolve => setTimeout(resolve, pollInterval));
      }
      
    } catch (error) {
      if (attempt === maxAttempts - 1) {
        throw error;
      }
      console.log(`Polling attempt ${attempt + 1} failed, retrying...`);
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }
  }
  
  throw new Error('변환 시간이 초과되었습니다.');
}

// Legacy Python 방식 (폴백용)
async function callPythonConverter(
  url: string,
  userApiKey: string,
  userApiProvider: 'openai' | 'anthropic'
): Promise<string> {
  
  console.log(`Falling back to Python converter for URL: ${url}`);
  
  return new Promise((resolve, reject) => {
    const workingDir = path.join(process.cwd(), '..');
    const processKey = `${url}_${userApiProvider}`;
    
    const runningProcesses = new Set<string>();
    
    if (runningProcesses.has(processKey)) {
      reject(new Error('해당 URL은 이미 처리 중입니다.'));
      return;
    }
    
    runningProcesses.add(processKey);
    
    const env = {
      ...process.env,
      [userApiProvider === 'openai' ? 'OPENAI_API_KEY' : 'ANTHROPIC_API_KEY']: userApiKey,
    };
    
    const python = spawn('bash', [
      '-c',
      `source venv/bin/activate && python news_converter_service.py --type ${userApiProvider} --keep-txt "${url}"`
    ], {
      cwd: workingDir,
      env: env,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let stdout = '';
    let stderr = '';
    let isResolved = false;
    
    const timeout = setTimeout(() => {
      if (!isResolved) {
        console.error('Python process timeout');
        python.kill('SIGKILL');
        runningProcesses.delete(processKey);
        reject(new Error('처리 시간이 초과되었습니다.'));
        isResolved = true;
      }
    }, 20000);
    
    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    python.on('close', async (code) => {
      clearTimeout(timeout);
      runningProcesses.delete(processKey);
      
      if (isResolved) return;
      
      if (code !== 0) {
        reject(new Error(`Python 변환 실패: ${stderr.slice(0, 200)}`));
        isResolved = true;
        return;
      }
      
      try {
        const outputMatch = stdout.match(/최종 결과: (.+\.md)/);
        if (!outputMatch) {
          reject(new Error('변환 결과를 찾을 수 없습니다.'));
          isResolved = true;
          return;
        }
        
        const resultFilePath = path.join(workingDir, outputMatch[1]);
        const markdownContent = await fs.readFile(resultFilePath, 'utf-8');
        
        resolve(markdownContent);
        isResolved = true;
        
      } catch (error) {
        reject(new Error('결과 파일을 읽을 수 없습니다.'));
        isResolved = true;
      }
    });
    
    python.on('error', (error) => {
      clearTimeout(timeout);
      runningProcesses.delete(processKey);
      
      if (isResolved) return;
      
      reject(new Error('Python 프로세스 실행 오류가 발생했습니다.'));
      isResolved = true;
    });
  });
}

export async function POST(request: NextRequest) {
  try {
    const { url, platform, userApiKey, userApiProvider } = await request.json();

    // 입력 검증
    if (!url || typeof url !== 'string') {
      return NextResponse.json(
        { error: '유효한 URL을 제공해주세요.' },
        { status: 400 }
      );
    }

    if (!userApiKey || typeof userApiKey !== 'string') {
      return NextResponse.json(
        { error: 'API 키를 설정해주세요.' },
        { status: 400 }
      );
    }

    if (!userApiProvider || !['openai', 'anthropic'].includes(userApiProvider)) {
      return NextResponse.json(
        { error: '지원되는 AI 제공업체를 선택해주세요.' },
        { status: 400 }
      );
    }

    // URL 유효성 검사
    let parsedUrl: URL;
    try {
      parsedUrl = new URL(url);
      if (!['http:', 'https:'].includes(parsedUrl.protocol)) {
        throw new Error('HTTP 또는 HTTPS URL만 지원됩니다.');
      }
    } catch {
      return NextResponse.json(
        { error: '유효하지 않은 URL 형식입니다.' },
        { status: 400 }
      );
    }

    console.log(`Processing request: ${url} with ${userApiProvider}`);

    let markdownContent: string;
    let source: string;
    
    try {
      // 1. FastAPI 서버 우선 시도
      const result = await callFastApiConverter(url, userApiKey, userApiProvider);
      markdownContent = result.content;
      source = 'fastapi_converter';
      console.log(`FastAPI conversion successful, content length: ${markdownContent?.length}`);
      
    } catch (fastApiError) {
      console.log(`FastAPI conversion failed: ${fastApiError}`);
      console.log('Falling back to Python converter...');
      
      // 2. Python 방식으로 폴백
      try {
        markdownContent = await callPythonConverter(url, userApiKey, userApiProvider);
        source = 'python_converter';
        console.log(`Python conversion successful, content length: ${markdownContent.length}`);
      } catch (pythonError) {
        const fastApiErrorMessage = fastApiError instanceof Error ? fastApiError.message : String(fastApiError);
        const pythonErrorMessage = pythonError instanceof Error ? pythonError.message : String(pythonError);
        
        console.error('Both FastAPI and Python conversion failed:', {
          fastApiError: fastApiErrorMessage,
          pythonError: pythonErrorMessage
        });
        throw new Error(`변환에 실패했습니다: ${fastApiErrorMessage}`);
      }
    }

    // 플랫폼별 최적화
    let optimizedContent = markdownContent;
    
    if (platform === 'twitter') {
      const lines = markdownContent.split('\n');
      const title = lines[0] || '';
      const firstSection = lines.slice(1, 6).join('\n').substring(0, 200);
      optimizedContent = `${title}\n\n${firstSection}...`;
    } else if (platform === 'threads') {
      const lines = markdownContent.split('\n');
      const title = lines[0] || '';
      const mainSections = lines.slice(1, 10).join('\n').substring(0, 450);
      optimizedContent = `${title}\n\n${mainSections}...`;
    }

    return NextResponse.json({
      success: true,
      content: optimizedContent,
      platform: platform || 'full',
      aiProvider: userApiProvider,
      timestamp: new Date().toISOString(),
      source: source
    });

  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '서버 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
} 
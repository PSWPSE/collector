import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import * as fs from 'fs/promises';
import * as path from 'path';

// FastAPI 서버 URL - 127.0.0.1 사용으로 연결 안정성 개선
const FASTAPI_URL = 'http://127.0.0.1:8000';

// FastAPI 서버 연결 테스트 (개선된 버전)
async function testFastApiConnection(): Promise<boolean> {
  const maxRetries = 3;
  const timeout = 10000; // 10초 타임아웃으로 증가
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`Health check 시도 ${attempt}/${maxRetries}...`);
      
      const response = await fetch(`${FASTAPI_URL}/api/v1/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(timeout)
      });
      
      if (response.ok) {
        console.log(`✅ Health check 성공 (${attempt}번째 시도)`);
        return true;
      } else {
        console.log(`⚠️  Health check 응답 오류: ${response.status}`);
      }
    } catch (error) {
      console.log(`❌ Health check 실패 (${attempt}/${maxRetries}):`, error);
      
      // 마지막 시도가 아니면 잠시 대기
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // 2초 대기
      }
    }
  }
  
  return false;
}

// FastAPI 서버 자동 시작 시도
async function tryStartFastApiServer(): Promise<boolean> {
  console.log('🚀 FastAPI 서버 자동 시작 시도...');
  
  try {
    // Python 스크립트로 서버 시작 시도
    const { spawn } = await import('child_process');
    const serverProcess = spawn('python', ['run_server.py', 'start'], {
      cwd: '../newsforge-pro/backend',
      detached: true,
      stdio: 'ignore'
    });
    
    serverProcess.unref(); // 프로세스를 백그라운드로 실행
    
    // 서버 시작 대기 (최대 30초)
    for (let i = 0; i < 30; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (await testFastApiConnection()) {
        console.log('✅ FastAPI 서버 자동 시작 성공!');
        return true;
      }
    }
    
    console.log('❌ FastAPI 서버 자동 시작 타임아웃');
    return false;
    
  } catch (error) {
    console.log('❌ FastAPI 서버 자동 시작 실패:', error);
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

// FastAPI 서버로 변환 요청 (개선된 버전)
async function callFastApiConverter(
  url: string,
  userApiKey: string,
  userApiProvider: 'openai' | 'anthropic'
): Promise<{content: string, taskId: string}> {
  
  console.log(`Calling FastAPI converter for URL: ${url}`);
  console.log(`Provider: ${userApiProvider}`);
  
  // 1단계: FastAPI 서버 연결 테스트
  let isConnected = await testFastApiConnection();
  
  // 2단계: 연결 실패 시 자동 복구 시도
  if (!isConnected) {
    console.log('⚠️  FastAPI 서버 연결 실패, 자동 복구 시도...');
    
    // 서버 자동 시작 시도
    const autoStarted = await tryStartFastApiServer();
    
    if (autoStarted) {
      isConnected = true;
    } else {
      // 혹시 이미 실행 중이지만 아직 준비가 안 된 경우를 위해 한 번 더 시도
      console.log('🔄 마지막 연결 시도...');
      await new Promise(resolve => setTimeout(resolve, 5000)); // 5초 추가 대기
      isConnected = await testFastApiConnection();
    }
  }
  
  if (!isConnected) {
    throw new Error('FastAPI 서버에 연결할 수 없습니다. 서버 자동 시작에 실패했습니다.');
  }
  
  try {
    // 3단계: 변환 요청 시작
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
    
    // 4단계: 결과 폴링
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

// 결과 폴링 함수 (개선된 버전)
async function pollForResult(taskId: string): Promise<any> {
  const maxAttempts = 90; // 최대 90회 시도 (약 90초)
  const pollInterval = 1000; // 1초 간격
  let consecutiveErrors = 0;
  const maxConsecutiveErrors = 5;
  
  console.log(`📊 결과 폴링 시작 (Task ID: ${taskId})`);
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const response = await fetch(`${FASTAPI_URL}/api/v1/conversion/${taskId}`, {
        signal: AbortSignal.timeout(10000) // 10초 타임아웃
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('변환 작업을 찾을 수 없습니다.');
        }
        throw new Error(`상태 확인 실패: ${response.status}`);
      }
      
      const result = await response.json();
      
      // 연속 에러 카운터 리셋
      consecutiveErrors = 0;
      
      if (result.status === 'completed') {
        console.log(`✅ 변환 완료! (총 ${attempt + 1}초 소요)`);
        return result;
      } else if (result.status === 'failed') {
        console.error(`❌ 변환 실패: ${result.error}`);
        throw new Error(result.error || '변환에 실패했습니다.');
      } else {
        // 아직 진행 중
        const progressInfo = result.current_step ? 
          `${result.current_step} (${result.progress || 0}%)` : 
          '진행 중...';
        
        // 5초마다 진행 상황 로그
        if (attempt % 5 === 0 || result.progress) {
          console.log(`⏳ 변환 진행 중: ${progressInfo} (${attempt + 1}초 경과)`);
        }
        
        await new Promise(resolve => setTimeout(resolve, pollInterval));
      }
      
    } catch (error) {
      consecutiveErrors++;
      console.log(`⚠️  폴링 오류 (${consecutiveErrors}/${maxConsecutiveErrors}):`, error);
      
      // 연속으로 너무 많은 에러가 발생하면 중단
      if (consecutiveErrors >= maxConsecutiveErrors) {
        throw new Error(`연속적인 네트워크 오류로 인해 변환을 중단합니다. (${consecutiveErrors}회 연속 실패)`);
      }
      
      // 마지막 시도가 아니면 대기
      if (attempt < maxAttempts - 1) {
        const retryDelay = Math.min(2000 * consecutiveErrors, 10000); // 점진적 대기 (최대 10초)
        console.log(`🔄 ${retryDelay/1000}초 후 재시도...`);
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
  }
  
  throw new Error(`변환 시간이 초과되었습니다. (${maxAttempts}초 초과)`);
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
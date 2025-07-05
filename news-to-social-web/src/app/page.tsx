"use client";

import React, { useState, useCallback } from 'react';

interface ApiKeyInfo {
  key: string;
  provider: 'openai' | 'anthropic';
  validated: boolean;
  maskedKey: string;
}

export default function Home() {
  const [newsUrl, setNewsUrl] = useState('');
  const [generatedContent, setGeneratedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentApiKey, setCurrentApiKey] = useState<ApiKeyInfo | null>(null);
  const [showApiKeyForm, setShowApiKeyForm] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [apiProvider, setApiProvider] = useState<'openai' | 'anthropic'>('openai');

  const handleApiKeyValidated = useCallback((apiKey: string, provider: 'openai' | 'anthropic') => {
    if (apiKey && provider) {
      const maskedKey = apiKey.length <= 10 ? apiKey : apiKey.substring(0, 6) + '...' + apiKey.substring(apiKey.length - 4);
      setCurrentApiKey({
        key: apiKey,
        provider,
        validated: true,
        maskedKey
      });
      localStorage.setItem('userApiKey', apiKey);
      localStorage.setItem('userApiProvider', provider);
      setShowApiKeyForm(false);
    } else {
      setCurrentApiKey(null);
      localStorage.removeItem('userApiKey');
      localStorage.removeItem('userApiProvider');
    }
  }, []);

  const validateApiKey = async () => {
    if (!apiKeyInput.trim()) {
      setError('API 키를 입력해주세요.');
      return;
    }

    try {
      const response = await fetch('/api/validate-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          apiKey: apiKeyInput.trim(),
          provider: apiProvider,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        handleApiKeyValidated(apiKeyInput.trim(), apiProvider);
        setApiKeyInput('');
        setError('');
      } else {
        setError(data.error || '검증에 실패했습니다.');
      }
    } catch (error) {
      setError('네트워크 오류가 발생했습니다.');
    }
  };

  const handleGenerate = async () => {
    if (!newsUrl.trim()) {
      setError('뉴스 URL을 입력해주세요.');
      return;
    }

    if (!currentApiKey || !currentApiKey.validated) {
      setError('먼저 API 키를 설정해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    setGeneratedContent('');

    try {
      // 70초 타임아웃 설정 (API 60초 + 버퍼)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 70000);

      const response = await fetch('/api/convert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: newsUrl,
          platform: 'full',
          userApiKey: currentApiKey.key,
          userApiProvider: currentApiKey.provider,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        
        // 권장 URL이 있는 경우 표시
        if (errorData.suggestions && errorData.suggestions.length > 0) {
          const suggestionText = '\n\n권장 URL:\n' + errorData.suggestions.map((url: string) => `• ${url}`).join('\n');
          throw new Error((errorData.error || '변환 중 오류가 발생했습니다.') + suggestionText);
        }
        
        throw new Error(errorData.error || '변환 중 오류가 발생했습니다.');
      }

      const data = await response.json();
      setGeneratedContent(data.content);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError('요청 시간이 초과되었습니다. 다시 시도해주세요.');
      } else {
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      }
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(generatedContent);
      alert('클립보드에 복사되었습니다!');
    } catch (err) {
      console.error('복사 실패:', err);
    }
  };

  // URL 전체 삭제 기능
  const clearUrl = () => {
    setNewsUrl('');
    setError('');
  };

  // 컴포넌트 마운트 시 로컬 스토리지에서 API 키 로드
  React.useEffect(() => {
    const savedApiKey = localStorage.getItem('userApiKey');
    const savedProvider = localStorage.getItem('userApiProvider') as 'openai' | 'anthropic';
    
    if (savedApiKey && savedProvider) {
      handleApiKeyValidated(savedApiKey, savedProvider);
    }
  }, [handleApiKeyValidated]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2 text-gray-800">
            뉴스 기사 콘텐츠 생성기 📰➡️📝
          </h1>
          <p className="text-gray-600">
            뉴스 기사를 체계적인 콘텐츠로 변환하세요
          </p>
        </div>

        {/* API 키 설정 - 간소화된 버전 */}
        <div className="mb-6 p-4 bg-white rounded-lg shadow-sm border">
          {currentApiKey ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium">
                  {currentApiKey.provider === 'openai' ? 'OpenAI' : 'Anthropic'} 
                </span>
                <span className="text-sm text-gray-500">
                  {currentApiKey.maskedKey}
                </span>
              </div>
              <button
                onClick={() => handleApiKeyValidated('', 'openai')}
                className="px-3 py-1 text-sm text-red-600 hover:text-red-700"
              >
                변경
              </button>
            </div>
          ) : (
            <div>
              {!showApiKeyForm ? (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">API 키가 설정되지 않았습니다</span>
                  <button
                    onClick={() => setShowApiKeyForm(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                  >
                    API 키 설정
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex gap-3">
                    <select
                      value={apiProvider}
                      onChange={(e) => setApiProvider(e.target.value as 'openai' | 'anthropic')}
                      className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic</option>
                    </select>
                    <input
                      type="password"
                      placeholder="API 키 입력"
                      value={apiKeyInput}
                      onChange={(e) => setApiKeyInput(e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                    <button
                      onClick={validateApiKey}
                      className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
                    >
                      확인
                    </button>
                    <button
                      onClick={() => setShowApiKeyForm(false)}
                      className="px-4 py-2 bg-gray-400 text-white rounded-md hover:bg-gray-500 text-sm"
                    >
                      취소
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* 메인 콘텐츠 영역 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 입력 섹션 */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">뉴스 URL 입력</h2>
              <div className="flex items-center gap-2">
                <div className="relative group">
                  <button className="text-gray-400 hover:text-gray-600 text-sm">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>
                  <div className="absolute right-0 top-6 w-64 p-3 bg-gray-800 text-white text-xs rounded-md opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                    <div className="space-y-1">
                      <div>• 뉴스 기사 URL을 입력하면 AI가 콘텐츠로 변환합니다</div>
                      <div>• 대부분의 뉴스 사이트를 지원합니다</div>
                      <div>• 변환 완료까지 최대 60초 소요됩니다</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <div className="relative">
                  <input
                    type="url"
                    placeholder="뉴스 기사 URL을 입력하세요"
                    value={newsUrl}
                    onChange={(e) => setNewsUrl(e.target.value)}
                    className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  {newsUrl && (
                    <button
                      onClick={clearUrl}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>

              <button
                onClick={handleGenerate}
                disabled={loading || !currentApiKey}
                className={`w-full py-3 px-4 rounded-md font-medium text-white transition-colors ${
                  loading || !currentApiKey
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {loading ? '콘텐츠 생성 중...' : '콘텐츠 생성'}
              </button>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
          </div>

          {/* 결과 섹션 */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">생성된 콘텐츠</h2>
              {generatedContent && (
                <button
                  onClick={copyToClipboard}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
                >
                  복사
                </button>
              )}
            </div>
            
            <div className="min-h-96 max-h-96 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">AI가 콘텐츠를 생성하고 있습니다...</p>
                  </div>
                </div>
              ) : generatedContent ? (
                <pre className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">
                  {generatedContent}
                </pre>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-gray-500">생성된 콘텐츠가 여기에 표시됩니다</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
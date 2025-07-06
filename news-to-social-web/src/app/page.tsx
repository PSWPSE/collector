"use client";

import React, { useState, useCallback, useRef } from 'react';
import AdSenseUnit from '@/components/ads/AdSenseUnit';
import MobileAnchorAd from '@/components/ads/MobileAnchorAd';
import { ApiKeyManager } from '@/components/api-key-manager';

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
  const urlInputRef = useRef<HTMLInputElement>(null);

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
    } else {
      setCurrentApiKey(null);
      localStorage.removeItem('userApiKey');
      localStorage.removeItem('userApiProvider');
    }
  }, []);

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

  const clearUrl = () => {
    setNewsUrl('');
    setError('');
  };

  const handleUrlInputClick = () => {
    if (urlInputRef.current && newsUrl.trim()) {
      urlInputRef.current.select();
    }
  };

  React.useEffect(() => {
    const savedApiKey = localStorage.getItem('userApiKey');
    const savedProvider = localStorage.getItem('userApiProvider') as 'openai' | 'anthropic';
    
    if (savedApiKey && savedProvider) {
      handleApiKeyValidated(savedApiKey, savedProvider);
    }
  }, [handleApiKeyValidated]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 상단 애드센스 배너 - Above the fold 최적화 */}
      <section className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <AdSenseUnit 
            slot="top-banner"
            size="leaderboard"
            isPreview={true}
            className="!bg-transparent !border-none !shadow-none"
          />
        </div>
      </section>

      {/* 메인 컨테이너 - 12컬럼 그리드 시스템 통일 */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* 헤더 섹션 - 브랜딩 + API 키 관리 */}
        <header className="mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
                  📰 뉴스 기사 콘텐츠 생성기
                </h1>
                <p className="text-gray-600 text-sm md:text-base">
                  AI 기술로 뉴스 기사를 소셜 미디어 최적화 콘텐츠로 변환하세요
                </p>
              </div>
              <div className="ml-6">
                <ApiKeyManager 
                  onApiKeyValidated={handleApiKeyValidated}
                  currentApiKey={currentApiKey}
                />
              </div>
            </div>
          </div>
        </header>

        {/* 뉴스 URL 입력 바 - 헤더 바로 아래 전체 폭 */}
        <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 mb-8">
          <div className="space-y-4">
            {/* 상단 라벨 */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">뉴스 URL 입력</h2>
                <p className="text-sm text-gray-600">변환하고 싶은 뉴스 기사의 URL을 입력하세요</p>
              </div>
              
              {/* API 키 상태 표시 */}
              <div className="hidden md:flex items-center space-x-2">
                {currentApiKey?.validated ? (
                  <div className="flex items-center space-x-2 text-green-600">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm font-medium">{currentApiKey.provider.toUpperCase()} 연결됨</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2 text-amber-600">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm font-medium">API 키 필요</span>
                  </div>
                )}
              </div>
            </div>

            {/* 입력 영역 */}
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <input
                  ref={urlInputRef}
                  type="url"
                  value={newsUrl}
                  onChange={(e) => setNewsUrl(e.target.value)}
                  onClick={handleUrlInputClick}
                  placeholder="https://news.example.com/article"
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-sm"
                  disabled={loading}
                />
                
                {/* 클리어 버튼 */}
                {newsUrl && (
                  <button
                    onClick={clearUrl}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    disabled={loading}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>

              <button
                onClick={handleGenerate}
                disabled={loading || !currentApiKey}
                className={`px-8 py-3 rounded-lg font-medium text-white transition-all duration-200 whitespace-nowrap ${
                  loading || !currentApiKey
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg'
                }`}
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    콘텐츠 생성 중...
                  </span>
                ) : '🚀 콘텐츠 생성'}
              </button>
            </div>

            {/* 에러 메시지 */}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm text-red-700 whitespace-pre-line">{error}</p>
                </div>
              </div>
            )}

            {/* 사용 팁 - 모바일에서는 숨김 */}
            <div className="hidden lg:flex items-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>Enter키로 빠른 생성</span>
              </div>
              <div className="flex items-center space-x-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>처리 시간: 30-60초</span>
              </div>
            </div>
          </div>
        </section>

        {/* 메인 그리드 레이아웃 - 콘텐츠 중심 */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* 왼쪽 사이드바 - 광고 및 부가 기능 */}
          <aside className="lg:col-span-3 order-2 lg:order-1">
            <div className="sticky top-8 space-y-6">
              {/* 사이드바 상단 광고 */}
              <div className="hidden lg:block">
                <AdSenseUnit 
                  slot="sidebar-top"
                  size="sidebar"
                  isPreview={true}
                />
              </div>

              {/* 사용 가이드 */}
              <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 사용 가이드</h3>
                <div className="space-y-3 text-sm text-gray-600">
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-600 font-medium">1.</span>
                    <p>상단에 뉴스 기사 URL을 입력하세요</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-600 font-medium">2.</span>
                    <p>AI가 자동으로 콘텐츠를 분석합니다</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-600 font-medium">3.</span>
                    <p>소셜 미디어 최적화 콘텐츠로 변환됩니다</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-600 font-medium">4.</span>
                    <p>생성된 콘텐츠를 복사하여 사용하세요</p>
                  </div>
                </div>
                
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-xs text-blue-800">
                    <strong>처리 시간:</strong> 30-60초 소요 • <strong>지원 사이트:</strong> 대부분의 뉴스 웹사이트
                  </p>
                </div>
              </div>

              {/* 사이드바 하단 광고 */}
              <div className="hidden lg:block">
                <AdSenseUnit 
                  slot="sidebar-bottom"
                  size="sidebar"
                  isPreview={true}
                />
              </div>
            </div>
          </aside>

          {/* 메인 콘텐츠 영역 */}
          <main className="lg:col-span-6 order-1 lg:order-2">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200">
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">생성된 콘텐츠</h2>
                  <p className="text-sm text-gray-600 mt-1">AI가 생성한 소셜 미디어 최적화 콘텐츠</p>
                </div>
                {generatedContent && (
                  <button
                    onClick={copyToClipboard}
                    className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all duration-200 font-medium text-sm shadow-md hover:shadow-lg"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    복사
                  </button>
                )}
              </div>
              
              <div className="p-6">
                <div className="min-h-[700px] max-h-[85vh] overflow-y-auto">
                  {loading ? (
                    <div className="flex items-center justify-center h-96">
                      <div className="text-center">
                        <div className="relative">
                          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-2xl">🤖</span>
                          </div>
                        </div>
                        <p className="text-gray-700 font-medium mt-6">AI가 콘텐츠를 생성하고 있습니다</p>
                        <p className="text-gray-500 text-sm mt-2">뉴스 기사를 분석하고 최적화된 콘텐츠로 변환 중...</p>
                        <div className="mt-4 bg-gray-100 rounded-lg p-3">
                          <p className="text-xs text-gray-600">⏱️ 최대 60초 소요 • 잠시만 기다려주세요</p>
                        </div>
                      </div>
                    </div>
                  ) : generatedContent ? (
                    <div className="prose prose-sm max-w-none">
                      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                        <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed font-sans">
                          {generatedContent}
                        </pre>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-96">
                      <div className="text-center">
                        <div className="text-6xl mb-6">📝</div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">콘텐츠 생성을 시작하세요</h3>
                        <p className="text-gray-600 mb-6 max-w-md mx-auto">
                          뉴스 기사 URL을 입력하고 AI가 소셜 미디어에 최적화된 콘텐츠를 생성해드립니다.
                        </p>
                        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                          <p className="text-sm text-blue-800">
                            💡 <strong>팁:</strong> 대부분의 뉴스 사이트를 지원하며, 생성된 콘텐츠는 바로 복사하여 사용할 수 있습니다.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 콘텐츠 내 광고 - 모바일에서 표시 */}
            <div className="lg:hidden mt-8">
              <AdSenseUnit 
                slot="in-content-mobile"
                size="in-content"
                isPreview={true}
              />
            </div>
          </main>

          {/* 오른쪽 사이드바 - 서비스 정보와 추가 광고 */}
          <aside className="lg:col-span-3 order-3">
            <div className="sticky top-8 space-y-6">
              {/* 서비스 정보를 상단으로 이동 */}
              <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🔥 서비스 특징</h3>
                <ul className="space-y-3 text-sm">
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    <span className="text-gray-700">AI 기반 자동 콘텐츠 변환</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    <span className="text-gray-700">OpenAI & Anthropic 지원</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    <span className="text-gray-700">소셜 미디어 최적화</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    <span className="text-gray-700">원클릭 클립보드 복사</span>
                  </li>
                </ul>
              </div>

              {/* 데스크톱 우측 광고를 하단으로 이동 */}
              <div className="hidden lg:block">
                <AdSenseUnit 
                  slot="right-sidebar"
                  size="sidebar"
                  isPreview={true}
                />
              </div>

              {/* 하단 광고 */}
              <div className="hidden lg:block">
                <AdSenseUnit 
                  slot="right-sidebar-bottom"
                  size="sidebar"
                  isPreview={true}
                />
              </div>
            </div>
          </aside>
        </div>

        {/* 하단 광고 섹션 */}
        <section className="mt-12">
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <p className="text-xs text-gray-500 text-center mb-4">Advertisement</p>
            <AdSenseUnit 
              slot="bottom-banner"
              size="leaderboard"
              isPreview={true}
            />
          </div>
        </section>
      </div>

      {/* 모바일 앵커 광고 */}
      <MobileAnchorAd 
        slot="mobile-anchor"
        isPreview={true}
      />
    </div>
  );
}
"use client";

import React, { useRef, KeyboardEvent } from 'react';

interface ApiKeyInfo {
  key: string;
  provider: 'openai' | 'anthropic';
  validated: boolean;
  maskedKey: string;
}

interface UrlInputBarProps {
  newsUrl: string;
  setNewsUrl: (url: string) => void;
  loading: boolean;
  error: string;
  currentApiKey: ApiKeyInfo | null;
  onGenerate: () => void;
  onClear: () => void;
}

export function UrlInputBar({ 
  newsUrl, 
  setNewsUrl, 
  loading, 
  error, 
  currentApiKey, 
  onGenerate, 
  onClear 
}: UrlInputBarProps) {
  const urlInputRef = useRef<HTMLInputElement>(null);

  const handleUrlInputClick = () => {
    if (urlInputRef.current && newsUrl.trim()) {
      urlInputRef.current.select();
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading && currentApiKey?.validated) {
      onGenerate();
    }
  };

  return (
    <section className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* 상단 라벨과 설명 */}
        <div className="mb-4">
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
        </div>

        {/* 메인 입력 영역 */}
        <div className="space-y-4">
          {/* URL 입력 필드 */}
          <div className="flex space-x-4">
            <div className="flex-1 relative">
              <input
                ref={urlInputRef}
                type="url"
                value={newsUrl}
                onChange={(e) => setNewsUrl(e.target.value)}
                onClick={handleUrlInputClick}
                onKeyPress={handleKeyPress}
                placeholder="https://example.com/news-article"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors text-base"
                disabled={loading}
              />
              
              {/* 클리어 버튼 */}
              {newsUrl && (
                <button
                  onClick={onClear}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  disabled={loading}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>

            {/* 생성 버튼 */}
            <button
              onClick={onGenerate}
              disabled={loading || !newsUrl.trim() || !currentApiKey?.validated}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>변환 중...</span>
                </div>
              ) : (
                '콘텐츠 생성'
              )}
            </button>
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div className="flex items-start space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg">
              <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="flex-1">
                <p className="text-red-800 text-sm whitespace-pre-line">{error}</p>
              </div>
            </div>
          )}

          {/* 사용 팁 - 모바일에서는 숨김 */}
          <div className="hidden lg:block">
            <div className="flex items-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>Ctrl + Enter로 빠른 생성</span>
              </div>
              <div className="flex items-center space-x-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>처리 시간: 30-60초</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
} 
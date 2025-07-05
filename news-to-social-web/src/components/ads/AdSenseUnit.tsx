"use client";

interface AdSenseUnitProps {
  slot: string;
  size: 'banner' | 'rectangle' | 'leaderboard' | 'mobile-banner' | 'sidebar' | 'in-content';
  className?: string;
  isPreview?: boolean;
}

const AD_SIZES = {
  banner: { width: 728, height: 90, label: '728x90 배너' },
  rectangle: { width: 300, height: 250, label: '300x250 사각형' },
  leaderboard: { width: 728, height: 90, label: '728x90 리더보드' },
  'mobile-banner': { width: 320, height: 50, label: '320x50 모바일 배너' },
  sidebar: { width: 300, height: 250, label: '300x250 사이드바' },
  'in-content': { width: 336, height: 280, label: '336x280 본문 내' }
};

export default function AdSenseUnit({ slot, size, className = '', isPreview = false }: AdSenseUnitProps) {
  const adSize = AD_SIZES[size];
  
  if (isPreview) {
    // 개발/미리보기 모드에서는 플레이스홀더 표시
    return (
      <div className={`relative overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 border border-gray-300 rounded-lg shadow-sm ${className}`}>
        {/* 광고 레이블 */}
        <div className="absolute top-2 left-2 z-10">
          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-600 text-white shadow-sm">
            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
            광고
          </span>
        </div>

        {/* 광고 크기별 스타일링 */}
        <div 
          className="flex items-center justify-center text-gray-500 relative"
          style={{ 
            width: size === 'leaderboard' || size === 'banner' ? '100%' : `${adSize.width}px`,
            height: `${adSize.height}px`,
            maxWidth: '100%'
          }}
        >
          {/* 배경 패턴 */}
          <div className="absolute inset-0 opacity-20">
            <div className="grid grid-cols-8 gap-1 h-full p-2">
              {Array.from({ length: 32 }).map((_, i) => (
                <div key={i} className="bg-gray-400 rounded-sm opacity-50"></div>
              ))}
            </div>
          </div>

          {/* 광고 정보 */}
          <div className="relative z-10 text-center">
            <div className="text-lg font-semibold text-gray-600 mb-1">📢</div>
            <div className="text-sm font-medium text-gray-700">{adSize.label}</div>
            <div className="text-xs text-gray-500 mt-1">Google AdSense</div>
          </div>
        </div>

        {/* 하단 브랜딩 */}
        <div className="absolute bottom-1 right-2">
          <span className="text-xs text-gray-400 font-medium">Ads by Google</span>
        </div>
      </div>
    );
  }

  // 실제 AdSense 코드 (프로덕션)
  return (
    <div className={`adsense-container ${className}`}>
      <ins
        className="adsbygoogle"
        style={{
          display: 'block',
          width: size === 'leaderboard' || size === 'banner' ? '100%' : `${adSize.width}px`,
          height: `${adSize.height}px`,
        }}
        data-ad-client="ca-pub-xxxxxxxxxxxxxxxx" // 실제 AdSense 퍼블리셔 ID로 교체
        data-ad-slot={slot}
        data-ad-format={size === 'leaderboard' || size === 'banner' ? 'horizontal' : 'rectangle'}
        data-full-width-responsive={size === 'leaderboard' || size === 'banner' ? 'true' : 'false'}
      />
    </div>
  );
} 
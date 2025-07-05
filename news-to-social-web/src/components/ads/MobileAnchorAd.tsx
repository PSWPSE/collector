"use client";

interface MobileAnchorAdProps {
  slot: string;
  isPreview?: boolean;
  className?: string;
}

export default function MobileAnchorAd({ slot, isPreview = false, className = '' }: MobileAnchorAdProps) {
  if (isPreview) {
    return (
      <div className={`fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-2xl block md:hidden z-50 ${className}`}>
        {/* 광고 레이블 */}
        <div className="flex items-center justify-between px-4 py-1 bg-gray-50 border-b border-gray-200">
          <span className="text-xs text-gray-500 font-medium">Advertisement</span>
          <span className="text-xs text-gray-400">Ads by Google</span>
        </div>
        
        {/* 광고 콘텐츠 영역 */}
        <div className="relative overflow-hidden bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-center justify-center h-12 relative">
            {/* 배경 패턴 */}
            <div className="absolute inset-0 opacity-10">
              <div className="flex items-center justify-center h-full">
                {Array.from({ length: 12 }).map((_, i) => (
                  <div key={i} className="w-2 h-2 bg-blue-400 rounded-full mx-1 animate-pulse" style={{ animationDelay: `${i * 0.1}s` }}></div>
                ))}
              </div>
            </div>
            
            {/* 광고 아이콘과 텍스트 */}
            <div className="relative z-10 flex items-center">
              <span className="text-lg mr-2">📱</span>
              <span className="text-sm font-medium text-gray-700">320x50 모바일 앵커 광고</span>
            </div>
          </div>
        </div>

        {/* 닫기 버튼 (실제 앵커 광고는 닫기 기능 제공) */}
        <button className="absolute top-2 right-2 w-6 h-6 bg-gray-200 hover:bg-gray-300 rounded-full flex items-center justify-center transition-colors">
          <svg className="w-3 h-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    );
  }

  // 실제 AdSense 앵커 광고 코드 (프로덕션)
  return (
    <div className={`fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-2xl block md:hidden z-50 ${className}`}>
      <div className="text-center text-xs text-gray-500 py-1 bg-gray-50 border-b border-gray-200">Advertisement</div>
      <ins 
        className="adsbygoogle"
        style={{
          display: 'block',
          width: '100%',
          height: '50px'
        }}
        data-ad-client="ca-pub-xxxxxxxxxxxxxxxx" // 실제 AdSense 퍼블리셔 ID로 교체
        data-ad-slot={slot}
        data-ad-format="banner"
        data-ad-region="anchor"
        data-anchor-shown="true"
      />
    </div>
  );
} 
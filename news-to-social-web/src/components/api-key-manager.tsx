"use client";

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Eye, EyeOff, Check, X, Key, AlertCircle, Settings } from 'lucide-react';

interface ApiKeyInfo {
  key: string;
  provider: 'openai' | 'anthropic';
  validated: boolean;
  maskedKey: string;
}

interface ApiKeyManagerProps {
  onApiKeyValidated: (apiKey: string, provider: 'openai' | 'anthropic') => void;
  currentApiKey?: ApiKeyInfo | null;
}

export function ApiKeyManager({ onApiKeyValidated, currentApiKey }: ApiKeyManagerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<'openai' | 'anthropic'>('openai');
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 컴포넌트 마운트 시 로컬 스토리지에서 API 키 로드
  const onApiKeyValidatedRef = useRef(onApiKeyValidated);
  onApiKeyValidatedRef.current = onApiKeyValidated;

  useEffect(() => {
    const loadSavedApiKey = () => {
      const savedApiKey = localStorage.getItem('userApiKey');
      const savedProvider = localStorage.getItem('userApiProvider') as 'openai' | 'anthropic';
      
      if (savedApiKey && savedProvider) {
        onApiKeyValidatedRef.current(savedApiKey, savedProvider);
      }
    };

    loadSavedApiKey();
  }, []); // 빈 dependency array로 마운트 시에만 실행

  const maskApiKey = (key: string): string => {
    if (key.length <= 10) return key;
    return key.substring(0, 6) + '...' + key.substring(key.length - 4);
  };

  const validateApiKey = async () => {
    if (!apiKey.trim()) {
      setError('API 키를 입력해주세요.');
      return;
    }

    setValidating(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('/api/validate-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          apiKey: apiKey.trim(),
          provider: selectedProvider,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setSuccess(data.message);
        
        // 로컬 스토리지에 저장
        localStorage.setItem('userApiKey', apiKey.trim());
        localStorage.setItem('userApiProvider', selectedProvider);
        
        // 부모 컴포넌트에 알림
        onApiKeyValidated(apiKey.trim(), selectedProvider);
        
        // 폼 초기화
        setApiKey('');
        setIsOpen(false);
      } else {
        setError(data.error || '검증에 실패했습니다.');
      }
    } catch (error) {
      setError('네트워크 오류가 발생했습니다.');
    } finally {
      setValidating(false);
    }
  };

  const removeApiKey = () => {
    localStorage.removeItem('userApiKey');
    localStorage.removeItem('userApiProvider');
    onApiKeyValidated('', 'openai');
    setSuccess('API 키가 제거되었습니다.');
  };

  const getProviderInfo = (provider: 'openai' | 'anthropic') => {
    return provider === 'openai' 
      ? { name: 'OpenAI', prefix: 'sk-', url: 'https://platform.openai.com/api-keys' }
      : { name: 'Anthropic', prefix: 'sk-ant-', url: 'https://console.anthropic.com/settings/keys' };
  };

  return (
    <div className="flex items-center gap-2">
      {currentApiKey && currentApiKey.validated ? (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 rounded-md border border-green-200">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm font-medium text-green-700">
            {getProviderInfo(currentApiKey.provider).name}
          </span>
          <span className="text-xs text-green-600">
            {currentApiKey.maskedKey}
          </span>
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-green-600 hover:text-green-700 hover:bg-green-100">
                <Settings className="h-3 w-3" />
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Key className="h-5 w-5" />
                  API 키 관리
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-4">
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="font-medium text-green-700">
                          {getProviderInfo(currentApiKey.provider).name} API 연결됨
                        </span>
                      </div>
                      <span className="text-sm text-green-600">
                        {currentApiKey.maskedKey}
                      </span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={removeApiKey}
                      className="text-red-600 hover:text-red-700"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-medium">새 API 키로 변경</h3>
                  
                  <Tabs value={selectedProvider} onValueChange={(value) => setSelectedProvider(value as 'openai' | 'anthropic')}>
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="openai">OpenAI</TabsTrigger>
                      <TabsTrigger value="anthropic">Anthropic</TabsTrigger>
                    </TabsList>

                    <TabsContent value="openai" className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <label className="text-sm font-medium">OpenAI API 키</label>
                          <a
                            href="https://platform.openai.com/api-keys"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:underline"
                          >
                            API 키 발급받기
                          </a>
                        </div>
                        <div className="relative">
                          <Input
                            type={showKey ? "text" : "password"}
                            placeholder="sk-..."
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="pr-10"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                            onClick={() => setShowKey(!showKey)}
                          >
                            {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </Button>
                        </div>
                        <p className="text-xs text-gray-500">
                          OpenAI API 키는 sk-로 시작합니다.
                        </p>
                      </div>
                    </TabsContent>

                    <TabsContent value="anthropic" className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <label className="text-sm font-medium">Anthropic API 키</label>
                          <a
                            href="https://console.anthropic.com/settings/keys"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:underline"
                          >
                            API 키 발급받기
                          </a>
                        </div>
                        <div className="relative">
                          <Input
                            type={showKey ? "text" : "password"}
                            placeholder="sk-ant-..."
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="pr-10"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                            onClick={() => setShowKey(!showKey)}
                          >
                            {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </Button>
                        </div>
                        <p className="text-xs text-gray-500">
                          Anthropic API 키는 sk-ant-로 시작합니다.
                        </p>
                      </div>
                    </TabsContent>
                  </Tabs>

                  {error && (
                    <div className="text-red-600 text-sm p-3 bg-red-50 rounded-md">
                      {error}
                    </div>
                  )}

                  {success && (
                    <div className="text-green-600 text-sm p-3 bg-green-50 rounded-md flex items-center gap-2">
                      <Check className="h-4 w-4" />
                      {success}
                    </div>
                  )}

                  <Button
                    onClick={validateApiKey}
                    disabled={validating || !apiKey.trim()}
                    className="w-full"
                  >
                    {validating ? '검증 중...' : 'API 키 검증 및 저장'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      ) : (
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" className="flex items-center gap-2 px-3 py-1.5">
              <Key className="h-4 w-4" />
              <span className="text-sm">API 키 설정</span>
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                API 키 설정
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-blue-800">
                    <p className="font-medium mb-1">API 키가 필요합니다</p>
                    <p>뉴스 콘텐츠를 AI로 변환하려면 OpenAI 또는 Anthropic API 키가 필요합니다.</p>
                  </div>
                </div>
              </div>

              <Tabs value={selectedProvider} onValueChange={(value) => setSelectedProvider(value as 'openai' | 'anthropic')}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="openai">OpenAI</TabsTrigger>
                  <TabsTrigger value="anthropic">Anthropic</TabsTrigger>
                </TabsList>

                <TabsContent value="openai" className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">OpenAI API 키</label>
                      <a
                        href="https://platform.openai.com/api-keys"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:underline"
                      >
                        API 키 발급받기
                      </a>
                    </div>
                    <div className="relative">
                      <Input
                        type={showKey ? "text" : "password"}
                        placeholder="sk-..."
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        className="pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowKey(!showKey)}
                      >
                        {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                    <p className="text-xs text-gray-500">
                      OpenAI API 키는 sk-로 시작합니다.
                    </p>
                  </div>
                </TabsContent>

                <TabsContent value="anthropic" className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Anthropic API 키</label>
                      <a
                        href="https://console.anthropic.com/settings/keys"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:underline"
                      >
                        API 키 발급받기
                      </a>
                    </div>
                    <div className="relative">
                      <Input
                        type={showKey ? "text" : "password"}
                        placeholder="sk-ant-..."
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        className="pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowKey(!showKey)}
                      >
                        {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                    <p className="text-xs text-gray-500">
                      Anthropic API 키는 sk-ant-로 시작합니다.
                    </p>
                  </div>
                </TabsContent>
              </Tabs>

              {error && (
                <div className="text-red-600 text-sm p-3 bg-red-50 rounded-md">
                  {error}
                </div>
              )}

              {success && (
                <div className="text-green-600 text-sm p-3 bg-green-50 rounded-md flex items-center gap-2">
                  <Check className="h-4 w-4" />
                  {success}
                </div>
              )}

              <Button
                onClick={validateApiKey}
                disabled={validating || !apiKey.trim()}
                className="w-full"
              >
                {validating ? '검증 중...' : 'API 키 검증 및 저장'}
              </Button>

              <div className="text-xs text-gray-500 space-y-1">
                <p>• API 키는 브라우저에 안전하게 저장됩니다</p>
                <p>• 서버에 API 키가 저장되지 않습니다</p>
                <p>• 언제든지 API 키를 변경하거나 삭제할 수 있습니다</p>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
} 
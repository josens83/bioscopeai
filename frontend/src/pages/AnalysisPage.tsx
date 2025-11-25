import { useState, useRef, useEffect } from 'react'
import { useAnalysis } from '../hooks/useAnalysis'
import { usePapers } from '../hooks/usePapers'
import ReactMarkdown from 'react-markdown'
import {
  Card,
  CardHeader,
  CardContent,
  Button,
  Textarea,
  Badge,
  Avatar,
  SkeletonChatMessage,
  EmptyAnalyses,
  ChatBubbleIcon,
  DocumentTextIcon,
  ArrowsRightLeftIcon,
  PaperAirplaneIcon,
  SparklesIcon,
  BookOpenIcon,
  CheckIcon,
} from '../components/ui'

type Tab = 'qa' | 'summary' | 'compare'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: any[]
  timestamp: Date
}

export default function AnalysisPage() {
  const { questionMutation, summarizeMutation, compareMutation } = useAnalysis()
  const { papers } = usePapers()
  const [activeTab, setActiveTab] = useState<Tab>('qa')

  // Q&A 상태
  const [question, setQuestion] = useState('')
  const [selectedPaperId, setSelectedPaperId] = useState<number | undefined>()
  const [messages, setMessages] = useState<Message[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 요약 상태
  const [summaryPaperId, setSummaryPaperId] = useState<number | undefined>()
  const [summaryResult, setSummaryResult] = useState<any>(null)

  // 비교 상태
  const [selectedPaperIds, setSelectedPaperIds] = useState<number[]>([])
  const [compareResult, setCompareResult] = useState<any>(null)

  const tabs = [
    { id: 'qa' as Tab, label: '질의응답', icon: ChatBubbleIcon },
    { id: 'summary' as Tab, label: '논문 요약', icon: DocumentTextIcon },
    { id: 'compare' as Tab, label: '논문 비교', icon: ArrowsRightLeftIcon },
  ]

  // 메시지 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleQuestion = async () => {
    if (!question.trim()) return

    const userMessage: Message = {
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setQuestion('')

    try {
      const response = await questionMutation.mutateAsync({
        question: userMessage.content,
        paper_id: selectedPaperId,
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: '죄송합니다. 질문 처리 중 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    }
  }

  const handleSummarize = async () => {
    if (!summaryPaperId) return

    try {
      const response = await summarizeMutation.mutateAsync(summaryPaperId)
      setSummaryResult(response.data)
    } catch (error) {
      console.error('요약 실패:', error)
    }
  }

  const handleCompare = async () => {
    if (selectedPaperIds.length < 2) return

    try {
      const response = await compareMutation.mutateAsync(selectedPaperIds)
      setCompareResult(response.data)
    } catch (error) {
      console.error('비교 실패:', error)
    }
  }

  const togglePaperSelection = (paperId: number) => {
    if (selectedPaperIds.includes(paperId)) {
      setSelectedPaperIds(selectedPaperIds.filter((id) => id !== paperId))
    } else if (selectedPaperIds.length < 10) {
      setSelectedPaperIds([...selectedPaperIds, paperId])
    }
  }

  const selectedPaper = papers?.find((p: any) => p.id === selectedPaperId)

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 페이지 헤더 */}
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
          AI 분석
        </h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">
          AI와 대화하며 논문을 분석하세요
        </p>
      </div>

      {/* 탭 네비게이션 */}
      <div className="border-b border-surface-200 dark:border-surface-700">
        <nav className="flex gap-1 -mb-px">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
                  ${isActive
                    ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                    : 'border-transparent text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
                  }
                `}
              >
                <Icon size={18} />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* 질의응답 (채팅형 인터페이스) */}
      {activeTab === 'qa' && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 사이드바 - 논문 선택 */}
          <div className="lg:col-span-1">
            <Card className="sticky top-6">
              <CardHeader title="분석 대상" />
              <CardContent className="p-3 space-y-2 max-h-[400px] overflow-y-auto">
                <button
                  onClick={() => setSelectedPaperId(undefined)}
                  className={`
                    w-full p-3 rounded-lg text-left transition-colors
                    ${!selectedPaperId
                      ? 'bg-brand-50 dark:bg-brand-900/20 border-2 border-brand-500'
                      : 'bg-surface-50 dark:bg-surface-800 border-2 border-transparent hover:border-surface-300 dark:hover:border-surface-600'
                    }
                  `}
                >
                  <div className="flex items-center gap-2">
                    <SparklesIcon size={16} className="text-brand-500" />
                    <span className="text-sm font-medium text-surface-900 dark:text-surface-100">
                      전체 논문
                    </span>
                  </div>
                  <p className="text-xs text-surface-500 mt-1">
                    모든 논문에서 검색합니다
                  </p>
                </button>

                {papers?.map((paper: any) => (
                  <button
                    key={paper.id}
                    onClick={() => setSelectedPaperId(paper.id)}
                    className={`
                      w-full p-3 rounded-lg text-left transition-colors
                      ${selectedPaperId === paper.id
                        ? 'bg-brand-50 dark:bg-brand-900/20 border-2 border-brand-500'
                        : 'bg-surface-50 dark:bg-surface-800 border-2 border-transparent hover:border-surface-300 dark:hover:border-surface-600'
                      }
                    `}
                  >
                    <div className="flex items-center gap-2">
                      <BookOpenIcon size={16} className="text-surface-400" />
                      <span className="text-sm font-medium text-surface-900 dark:text-surface-100 line-clamp-1">
                        {paper.title}
                      </span>
                    </div>
                  </button>
                ))}

                {(!papers || papers.length === 0) && (
                  <p className="text-sm text-surface-400 text-center py-4">
                    저장된 논문이 없습니다
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* 채팅 영역 */}
          <div className="lg:col-span-3">
            <Card className="flex flex-col h-[600px]">
              {/* 채팅 헤더 */}
              <div className="px-5 py-4 border-b border-surface-200 dark:border-surface-700">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center">
                    <SparklesIcon size={20} className="text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-surface-900 dark:text-surface-100">
                      BioscopeAI
                    </h3>
                    <p className="text-xs text-surface-500">
                      {selectedPaper ? `분석 중: ${selectedPaper.title.slice(0, 30)}...` : '전체 논문 검색 모드'}
                    </p>
                  </div>
                </div>
              </div>

              {/* 메시지 목록 */}
              <div className="flex-1 overflow-y-auto p-5 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <div className="w-16 h-16 rounded-2xl bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center mb-4">
                      <ChatBubbleIcon size={32} className="text-brand-500" />
                    </div>
                    <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100">
                      논문에 대해 질문하세요
                    </h3>
                    <p className="mt-2 text-sm text-surface-500 max-w-sm">
                      AI가 논문 내용을 분석하여 정확한 답변을 제공합니다.
                      궁금한 점을 자유롭게 질문해보세요.
                    </p>
                    <div className="mt-4 flex flex-wrap justify-center gap-2">
                      {[
                        '연구의 주요 발견은?',
                        '사용된 방법론은?',
                        '한계점은 무엇인가?',
                      ].map((suggestion) => (
                        <button
                          key={suggestion}
                          onClick={() => setQuestion(suggestion)}
                          className="px-3 py-1.5 text-sm rounded-full bg-surface-100 dark:bg-surface-800 text-surface-600 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <>
                    {messages.map((message, index) => (
                      <div
                        key={index}
                        className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                      >
                        {message.role === 'assistant' ? (
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center flex-shrink-0">
                            <SparklesIcon size={16} className="text-white" />
                          </div>
                        ) : (
                          <Avatar size="sm" name="User" />
                        )}
                        <div
                          className={`
                            max-w-[80%] rounded-2xl px-4 py-3
                            ${message.role === 'user'
                              ? 'bg-brand-500 text-white rounded-br-md'
                              : 'bg-surface-100 dark:bg-surface-800 text-surface-900 dark:text-surface-100 rounded-bl-md'
                            }
                          `}
                        >
                          {message.role === 'assistant' ? (
                            <div className="prose prose-sm dark:prose-invert max-w-none">
                              <ReactMarkdown>{message.content}</ReactMarkdown>
                            </div>
                          ) : (
                            <p className="text-sm">{message.content}</p>
                          )}

                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-surface-200 dark:border-surface-700">
                              <p className="text-xs font-medium text-surface-500 mb-2">참고 문서</p>
                              <div className="space-y-1">
                                {message.sources.slice(0, 3).map((source: any, idx: number) => (
                                  <p key={idx} className="text-xs text-surface-400 line-clamp-2">
                                    {source.text}
                                  </p>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}

                    {questionMutation.isPending && (
                      <SkeletonChatMessage isAssistant />
                    )}
                  </>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* 입력 영역 */}
              <div className="p-4 border-t border-surface-200 dark:border-surface-700">
                <div className="flex gap-3">
                  <Textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleQuestion()
                      }
                    }}
                    placeholder="논문에 대해 질문하세요... (Shift+Enter로 줄바꿈)"
                    className="resize-none"
                    rows={2}
                  />
                  <Button
                    variant="primary"
                    onClick={handleQuestion}
                    disabled={!question.trim() || questionMutation.isPending}
                    loading={questionMutation.isPending}
                    className="self-end"
                  >
                    <PaperAirplaneIcon size={20} />
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* 논문 요약 */}
      {activeTab === 'summary' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title="요약할 논문 선택"
              subtitle="AI가 논문의 핵심 내용을 요약합니다"
            />
            <CardContent className="space-y-4">
              <div className="space-y-2 max-h-[400px] overflow-y-auto">
                {papers?.map((paper: any) => (
                  <button
                    key={paper.id}
                    onClick={() => setSummaryPaperId(paper.id)}
                    className={`
                      w-full p-4 rounded-xl text-left transition-all
                      ${summaryPaperId === paper.id
                        ? 'bg-brand-50 dark:bg-brand-900/20 border-2 border-brand-500 shadow-sm'
                        : 'bg-surface-50 dark:bg-surface-800 border-2 border-transparent hover:border-surface-300 dark:hover:border-surface-600'
                      }
                    `}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`
                        w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5
                        ${summaryPaperId === paper.id
                          ? 'border-brand-500 bg-brand-500'
                          : 'border-surface-300 dark:border-surface-600'
                        }
                      `}>
                        {summaryPaperId === paper.id && (
                          <CheckIcon size={12} className="text-white" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-surface-900 dark:text-surface-100 line-clamp-2">
                          {paper.title}
                        </p>
                        {paper.authors && (
                          <p className="text-sm text-surface-500 mt-1 line-clamp-1">
                            {paper.authors}
                          </p>
                        )}
                      </div>
                    </div>
                  </button>
                ))}

                {(!papers || papers.length === 0) && (
                  <EmptyAnalyses />
                )}
              </div>

              <Button
                variant="primary"
                size="lg"
                className="w-full"
                onClick={handleSummarize}
                disabled={!summaryPaperId || summarizeMutation.isPending}
                loading={summarizeMutation.isPending}
                leftIcon={<DocumentTextIcon size={20} />}
              >
                요약 생성
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="요약 결과" />
            <CardContent>
              {summarizeMutation.isPending ? (
                <div className="space-y-4">
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-full" />
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-5/6" />
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-4/6" />
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-full" />
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-3/4" />
                </div>
              ) : summaryResult ? (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{summaryResult.summary}</ReactMarkdown>
                </div>
              ) : (
                <div className="text-center py-12">
                  <DocumentTextIcon size={48} className="mx-auto text-surface-300 dark:text-surface-600" />
                  <p className="mt-4 text-surface-500">
                    논문을 선택하고 '요약 생성'을 클릭하세요
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* 논문 비교 */}
      {activeTab === 'compare' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title="비교할 논문 선택"
              subtitle="2~10개의 논문을 선택하여 비교 분석합니다"
              action={
                <Badge variant={selectedPaperIds.length >= 2 ? 'success' : 'secondary'}>
                  {selectedPaperIds.length}/10 선택됨
                </Badge>
              }
            />
            <CardContent className="space-y-4">
              <div className="space-y-2 max-h-[400px] overflow-y-auto">
                {papers?.map((paper: any) => {
                  const isSelected = selectedPaperIds.includes(paper.id)
                  return (
                    <button
                      key={paper.id}
                      onClick={() => togglePaperSelection(paper.id)}
                      className={`
                        w-full p-4 rounded-xl text-left transition-all
                        ${isSelected
                          ? 'bg-brand-50 dark:bg-brand-900/20 border-2 border-brand-500 shadow-sm'
                          : 'bg-surface-50 dark:bg-surface-800 border-2 border-transparent hover:border-surface-300 dark:hover:border-surface-600'
                        }
                      `}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`
                          w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5
                          ${isSelected
                            ? 'border-brand-500 bg-brand-500'
                            : 'border-surface-300 dark:border-surface-600'
                          }
                        `}>
                          {isSelected && (
                            <CheckIcon size={12} className="text-white" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-surface-900 dark:text-surface-100 line-clamp-2">
                            {paper.title}
                          </p>
                          {paper.authors && (
                            <p className="text-sm text-surface-500 mt-1 line-clamp-1">
                              {paper.authors}
                            </p>
                          )}
                        </div>
                      </div>
                    </button>
                  )
                })}

                {(!papers || papers.length === 0) && (
                  <EmptyAnalyses />
                )}
              </div>

              <Button
                variant="primary"
                size="lg"
                className="w-full"
                onClick={handleCompare}
                disabled={selectedPaperIds.length < 2 || compareMutation.isPending}
                loading={compareMutation.isPending}
                leftIcon={<ArrowsRightLeftIcon size={20} />}
              >
                비교 분석
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="비교 결과" />
            <CardContent>
              {compareMutation.isPending ? (
                <div className="space-y-4">
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-full" />
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-5/6" />
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-4/6" />
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-full" />
                  <div className="h-4 bg-surface-200 dark:bg-surface-700 rounded animate-pulse w-3/4" />
                </div>
              ) : compareResult ? (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{compareResult.comparison}</ReactMarkdown>
                </div>
              ) : (
                <div className="text-center py-12">
                  <ArrowsRightLeftIcon size={48} className="mx-auto text-surface-300 dark:text-surface-600" />
                  <p className="mt-4 text-surface-500">
                    최소 2개의 논문을 선택하고 '비교 분석'을 클릭하세요
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

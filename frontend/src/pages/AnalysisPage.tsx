import { useState } from 'react'
import { useAnalysis } from '../hooks/useAnalysis'
import { usePapers } from '../hooks/usePapers'
import ReactMarkdown from 'react-markdown'

export default function AnalysisPage() {
  const { questionMutation, summarizeMutation, compareMutation } = useAnalysis()
  const { papers } = usePapers()
  const [activeTab, setActiveTab] = useState<'qa' | 'summary' | 'compare'>('qa')

  // Q&A 상태
  const [question, setQuestion] = useState('')
  const [selectedPaperId, setSelectedPaperId] = useState<number | undefined>()
  const [qaResult, setQaResult] = useState<any>(null)

  // 요약 상태
  const [summaryPaperId, setSummaryPaperId] = useState<number | undefined>()
  const [summaryResult, setSummaryResult] = useState<any>(null)

  // 비교 상태
  const [selectedPaperIds, setSelectedPaperIds] = useState<number[]>([])
  const [compareResult, setCompareResult] = useState<any>(null)

  const handleQuestion = async () => {
    if (!question.trim()) {
      alert('질문을 입력해주세요')
      return
    }

    try {
      const response = await questionMutation.mutateAsync({
        question,
        paper_id: selectedPaperId,
      })
      setQaResult(response.data)
    } catch (error) {
      console.error('질문 실패:', error)
      alert('질문에 실패했습니다')
    }
  }

  const handleSummarize = async () => {
    if (!summaryPaperId) {
      alert('요약할 논문을 선택해주세요')
      return
    }

    try {
      const response = await summarizeMutation.mutateAsync(summaryPaperId)
      setSummaryResult(response.data)
    } catch (error) {
      console.error('요약 실패:', error)
      alert('요약에 실패했습니다')
    }
  }

  const handleCompare = async () => {
    if (selectedPaperIds.length < 2) {
      alert('최소 2개 이상의 논문을 선택해주세요')
      return
    }

    if (selectedPaperIds.length > 10) {
      alert('최대 10개까지만 비교할 수 있습니다')
      return
    }

    try {
      const response = await compareMutation.mutateAsync(selectedPaperIds)
      setCompareResult(response.data)
    } catch (error) {
      console.error('비교 실패:', error)
      alert('비교 분석에 실패했습니다')
    }
  }

  const togglePaperSelection = (paperId: number) => {
    if (selectedPaperIds.includes(paperId)) {
      setSelectedPaperIds(selectedPaperIds.filter((id) => id !== paperId))
    } else {
      setSelectedPaperIds([...selectedPaperIds, paperId])
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">AI 분석</h1>

      {/* 탭 네비게이션 */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('qa')}
            className={`${
              activeTab === 'qa'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            질의응답
          </button>
          <button
            onClick={() => setActiveTab('summary')}
            className={`${
              activeTab === 'summary'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            논문 요약
          </button>
          <button
            onClick={() => setActiveTab('compare')}
            className={`${
              activeTab === 'compare'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            논문 비교
          </button>
        </nav>
      </div>

      {/* 질의응답 */}
      {activeTab === 'qa' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">논문에 대해 질문하세요</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  논문 선택 (선택사항)
                </label>
                <select
                  value={selectedPaperId || ''}
                  onChange={(e) => setSelectedPaperId(e.target.value ? Number(e.target.value) : undefined)}
                  className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">모든 논문에서 검색</option>
                  {papers?.map((paper: any) => (
                    <option key={paper.id} value={paper.id}>
                      {paper.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  질문
                </label>
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="예: 이 연구의 주요 결과는 무엇인가요?"
                  rows={4}
                  className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <button
                onClick={handleQuestion}
                disabled={questionMutation.isPending}
                className="w-full px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
              >
                {questionMutation.isPending ? '분석 중...' : '질문하기'}
              </button>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">답변</h2>
            {qaResult ? (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{qaResult.answer}</ReactMarkdown>
                {qaResult.sources && qaResult.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h3 className="text-sm font-medium text-gray-700">참고 문서</h3>
                    <ul className="mt-2 space-y-2">
                      {qaResult.sources.map((source: any, index: number) => (
                        <li key={index} className="text-xs text-gray-600">
                          {source.text}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500">질문을 입력하고 '질문하기'를 클릭하세요</p>
            )}
          </div>
        </div>
      )}

      {/* 논문 요약 */}
      {activeTab === 'summary' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">논문 선택</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  요약할 논문
                </label>
                <select
                  value={summaryPaperId || ''}
                  onChange={(e) => setSummaryPaperId(Number(e.target.value))}
                  className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">논문을 선택하세요</option>
                  {papers?.map((paper: any) => (
                    <option key={paper.id} value={paper.id}>
                      {paper.title}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={handleSummarize}
                disabled={summarizeMutation.isPending}
                className="w-full px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
              >
                {summarizeMutation.isPending ? '요약 생성 중...' : '요약 생성'}
              </button>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">요약 결과</h2>
            {summaryResult ? (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{summaryResult.summary}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-gray-500">논문을 선택하고 '요약 생성'을 클릭하세요</p>
            )}
          </div>
        </div>
      )}

      {/* 논문 비교 */}
      {activeTab === 'compare' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              논문 선택 ({selectedPaperIds.length}/10)
            </h2>

            <div className="space-y-2 mb-4 max-h-96 overflow-y-auto">
              {papers?.map((paper: any) => (
                <label
                  key={paper.id}
                  className="flex items-start p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedPaperIds.includes(paper.id)}
                    onChange={() => togglePaperSelection(paper.id)}
                    className="mt-1 mr-3"
                  />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{paper.title}</p>
                    {paper.authors && (
                      <p className="text-xs text-gray-500 mt-1">{paper.authors}</p>
                    )}
                  </div>
                </label>
              ))}
            </div>

            <button
              onClick={handleCompare}
              disabled={compareMutation.isPending || selectedPaperIds.length < 2}
              className="w-full px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              {compareMutation.isPending ? '비교 분석 중...' : '비교 분석'}
            </button>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">비교 결과</h2>
            {compareResult ? (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{compareResult.comparison}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-gray-500">최소 2개의 논문을 선택하고 '비교 분석'을 클릭하세요</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

import { usePapers } from '../hooks/usePapers'
import { useAnalysis } from '../hooks/useAnalysis'
import { useSubscription } from '../hooks/useSubscription'

export default function DashboardPage() {
  const { papers, isLoading: papersLoading } = usePapers()
  const { analyses, isLoading: analysesLoading } = useAnalysis()
  const { mySubscription, subscriptionLoading } = useSubscription()

  const totalPapers = papers?.length || 0
  const totalAnalyses = analyses?.length || 0
  const subscriptionStatus = mySubscription?.plan?.name || 'Free'

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">대시보드</h1>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-500">총 논문 수</p>
                <p className="mt-1 text-3xl font-semibold text-primary-600">
                  {papersLoading ? '...' : totalPapers}
                </p>
              </div>
              <div className="flex-shrink-0">
                <svg className="h-12 w-12 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-500">총 분석 수</p>
                <p className="mt-1 text-3xl font-semibold text-green-600">
                  {analysesLoading ? '...' : totalAnalyses}
                </p>
              </div>
              <div className="flex-shrink-0">
                <svg className="h-12 w-12 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 00 2-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-500">구독 플랜</p>
                <p className="mt-1 text-lg font-semibold text-purple-600">
                  {subscriptionLoading ? '...' : subscriptionStatus}
                </p>
                {mySubscription && (
                  <p className="text-xs text-gray-500 mt-1">
                    상태: {mySubscription.status}
                  </p>
                )}
              </div>
              <div className="flex-shrink-0">
                <svg className="h-12 w-12 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">최근 논문</h2>
          {papersLoading ? (
            <p className="text-gray-500">로딩 중...</p>
          ) : papers && papers.length > 0 ? (
            <ul className="divide-y divide-gray-200">
              {papers.slice(0, 5).map((paper: any) => (
                <li key={paper.id} className="py-3">
                  <p className="text-sm font-medium text-gray-900 truncate">{paper.title}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(paper.created_at).toLocaleDateString('ko-KR')}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">저장된 논문이 없습니다</p>
          )}
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">최근 분석</h2>
          {analysesLoading ? (
            <p className="text-gray-500">로딩 중...</p>
          ) : analyses && analyses.length > 0 ? (
            <ul className="divide-y divide-gray-200">
              {analyses.slice(0, 5).map((analysis: any) => (
                <li key={analysis.id} className="py-3">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {analysis.analysis_type === 'qa' && '질의응답'}
                        {analysis.analysis_type === 'summary' && '논문 요약'}
                        {analysis.analysis_type === 'comparison' && '논문 비교'}
                      </p>
                      {analysis.query && (
                        <p className="text-xs text-gray-500 mt-1 truncate">{analysis.query}</p>
                      )}
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(analysis.created_at).toLocaleDateString('ko-KR')}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">분석 기록이 없습니다</p>
          )}
        </div>
      </div>

      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-2">💡 빠른 시작</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• <strong>논문</strong> 탭에서 PubMed를 검색하거나 PDF를 업로드하세요</li>
          <li>• <strong>분석</strong> 탭에서 AI에게 논문에 대해 질문하세요</li>
          <li>• <strong>구독</strong> 탭에서 더 많은 기능을 사용하세요</li>
        </ul>
      </div>
    </div>
  )
}

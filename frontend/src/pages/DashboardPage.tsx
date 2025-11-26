import { Link } from 'react-router-dom'
import { usePapers } from '../hooks/usePapers'
import { useAnalysis } from '../hooks/useAnalysis'
import { useSubscription } from '../hooks/useSubscription'
import {
  Card,
  CardHeader,
  CardContent,
  StatCard,
  Badge,
  SkeletonStatCard,
  SkeletonListItem,
  EmptyPapers,
  EmptyAnalyses,
  DocumentIcon,
  ChartBarIcon,
  SparklesIcon,
  ArrowRightIcon,
  ClockIcon,
  LightBulbIcon,
  BookOpenIcon,
  BeakerIcon,
} from '../components/ui'

export default function DashboardPage() {
  const { papers, isLoading: papersLoading } = usePapers()
  const { analyses, isLoading: analysesLoading } = useAnalysis()
  const { mySubscription, subscriptionLoading } = useSubscription()

  const totalPapers = papers?.length || 0
  const totalAnalyses = analyses?.length || 0
  const subscriptionPlan = mySubscription?.plan?.name || 'Free'
  const subscriptionStatus = mySubscription?.status || 'active'

  // 분석 타입별 라벨
  const analysisTypeLabels: Record<string, string> = {
    qa: '질의응답',
    summary: '논문 요약',
    comparison: '논문 비교',
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* 페이지 헤더 */}
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
          대시보드
        </h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">
          BioscopeAI와 함께하는 논문 분석 현황을 확인하세요
        </p>
      </div>

      {/* 통계 카드 섹션 */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {papersLoading ? (
          <SkeletonStatCard />
        ) : (
          <StatCard
            title="총 논문 수"
            value={totalPapers}
            icon={<DocumentIcon size={24} />}
          />
        )}

        {analysesLoading ? (
          <SkeletonStatCard />
        ) : (
          <StatCard
            title="총 분석 수"
            value={totalAnalyses}
            icon={<ChartBarIcon size={24} />}
          />
        )}

        {subscriptionLoading ? (
          <SkeletonStatCard />
        ) : (
          <StatCard
            title="구독 플랜"
            value={subscriptionPlan}
            description={`상태: ${subscriptionStatus === 'active' ? '활성' : subscriptionStatus}`}
            icon={<SparklesIcon size={24} />}
          />
        )}
      </div>

      {/* 최근 활동 섹션 */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* 최근 논문 */}
        <Card>
          <CardHeader
            title="최근 논문"
            subtitle="최근 저장한 논문 목록"
            action={
              papers && papers.length > 0 && (
                <Link
                  to="/papers"
                  className="inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400 dark:hover:text-brand-300 transition-colors"
                >
                  전체 보기
                  <ArrowRightIcon size={16} />
                </Link>
              )
            }
          />
          <CardContent className="p-0">
            {papersLoading ? (
              <div className="divide-y divide-surface-100 dark:divide-surface-700">
                {[1, 2, 3, 4, 5].map((i) => (
                  <SkeletonListItem key={i} />
                ))}
              </div>
            ) : papers && papers.length > 0 ? (
              <ul className="divide-y divide-surface-100 dark:divide-surface-700">
                {papers.slice(0, 5).map((paper: any) => (
                  <li
                    key={paper.id}
                    className="px-5 py-4 hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 mt-0.5">
                        <div className="w-8 h-8 rounded-lg bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center">
                          <BookOpenIcon size={16} className="text-brand-600 dark:text-brand-400" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-surface-900 dark:text-surface-100 line-clamp-1">
                          {paper.title}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <ClockIcon size={12} className="text-surface-400" />
                          <span className="text-xs text-surface-500 dark:text-surface-400">
                            {new Date(paper.created_at).toLocaleDateString('ko-KR')}
                          </span>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="py-8">
                <EmptyPapers />
              </div>
            )}
          </CardContent>
        </Card>

        {/* 최근 분석 */}
        <Card>
          <CardHeader
            title="최근 분석"
            subtitle="AI 분석 기록"
            action={
              analyses && analyses.length > 0 && (
                <Link
                  to="/analysis"
                  className="inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400 dark:hover:text-brand-300 transition-colors"
                >
                  전체 보기
                  <ArrowRightIcon size={16} />
                </Link>
              )
            }
          />
          <CardContent className="p-0">
            {analysesLoading ? (
              <div className="divide-y divide-surface-100 dark:divide-surface-700">
                {[1, 2, 3, 4, 5].map((i) => (
                  <SkeletonListItem key={i} />
                ))}
              </div>
            ) : analyses && analyses.length > 0 ? (
              <ul className="divide-y divide-surface-100 dark:divide-surface-700">
                {analyses.slice(0, 5).map((analysis: any) => (
                  <li
                    key={analysis.id}
                    className="px-5 py-4 hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3 min-w-0">
                        <div className="flex-shrink-0 mt-0.5">
                          <div className="w-8 h-8 rounded-lg bg-accent-100 dark:bg-accent-900/30 flex items-center justify-center">
                            <BeakerIcon size={16} className="text-accent-600 dark:text-accent-400" />
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary" size="sm">
                              {analysisTypeLabels[analysis.analysis_type] || analysis.analysis_type}
                            </Badge>
                          </div>
                          {analysis.query && (
                            <p className="text-sm text-surface-600 dark:text-surface-400 mt-1 line-clamp-1">
                              {analysis.query}
                            </p>
                          )}
                        </div>
                      </div>
                      <span className="flex-shrink-0 text-xs text-surface-400">
                        {new Date(analysis.created_at).toLocaleDateString('ko-KR')}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="py-8">
                <EmptyAnalyses />
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 빠른 시작 가이드 */}
      <Card variant="outlined" className="border-brand-200 dark:border-brand-800 bg-brand-50/50 dark:bg-brand-900/10">
        <CardContent>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-xl bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center">
                <LightBulbIcon size={20} className="text-brand-600 dark:text-brand-400" />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100">
                빠른 시작 가이드
              </h3>
              <ul className="mt-3 space-y-2">
                <li className="flex items-center gap-2 text-sm text-surface-600 dark:text-surface-400">
                  <span className="w-5 h-5 rounded-full bg-brand-500 text-white text-xs flex items-center justify-center font-medium">
                    1
                  </span>
                  <span>
                    <Link to="/papers" className="text-brand-600 dark:text-brand-400 font-medium hover:underline">
                      논문
                    </Link>
                    {' '}탭에서 PubMed를 검색하거나 PDF를 업로드하세요
                  </span>
                </li>
                <li className="flex items-center gap-2 text-sm text-surface-600 dark:text-surface-400">
                  <span className="w-5 h-5 rounded-full bg-brand-500 text-white text-xs flex items-center justify-center font-medium">
                    2
                  </span>
                  <span>
                    <Link to="/analysis" className="text-brand-600 dark:text-brand-400 font-medium hover:underline">
                      분석
                    </Link>
                    {' '}탭에서 AI에게 논문에 대해 질문하세요
                  </span>
                </li>
                <li className="flex items-center gap-2 text-sm text-surface-600 dark:text-surface-400">
                  <span className="w-5 h-5 rounded-full bg-brand-500 text-white text-xs flex items-center justify-center font-medium">
                    3
                  </span>
                  <span>
                    <Link to="/subscription" className="text-brand-600 dark:text-brand-400 font-medium hover:underline">
                      구독
                    </Link>
                    {' '}탭에서 더 많은 기능을 이용하세요
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

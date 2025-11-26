import { useState } from 'react'
import { useSubscription } from '../hooks/useSubscription'
import {
  Card,
  CardContent,
  Button,
  SkeletonCard,
  ConfirmModal,
  SparklesIcon,
  CheckIcon,
  XMarkIcon,
  CrownIcon,
  RocketLaunchIcon,
  BuildingOfficeIcon,
  UserIcon,
} from '../components/ui'

const planIcons: Record<string, typeof SparklesIcon> = {
  free: UserIcon,
  basic: SparklesIcon,
  pro: RocketLaunchIcon,
  enterprise: BuildingOfficeIcon,
}

const planColors: Record<string, string> = {
  free: 'from-surface-400 to-surface-500',
  basic: 'from-brand-400 to-brand-600',
  pro: 'from-accent-400 to-accent-600',
  enterprise: 'from-purple-400 to-purple-600',
}

export default function SubscriptionPage() {
  const { plans, plansLoading, mySubscription, subscriptionLoading, createMutation, cancelMutation } = useSubscription()
  const [cancelModalOpen, setCancelModalOpen] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)

  const handleSubscribe = async (tier: string) => {
    setSelectedPlan(tier)
    try {
      await createMutation.mutateAsync(tier)
    } catch (error) {
      console.error('구독 실패:', error)
    } finally {
      setSelectedPlan(null)
    }
  }

  const handleCancel = async () => {
    try {
      await cancelMutation.mutateAsync(true)
      setCancelModalOpen(false)
    } catch (error) {
      console.error('구독 취소 실패:', error)
    }
  }

  const currentTier = mySubscription?.plan?.tier || 'free'

  if (plansLoading || subscriptionLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div>
          <div className="h-8 w-48 bg-surface-200 dark:bg-surface-700 rounded animate-pulse" />
          <div className="h-5 w-64 bg-surface-200 dark:bg-surface-700 rounded animate-pulse mt-2" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* 페이지 헤더 */}
      <div className="text-center max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-surface-900 dark:text-surface-50">
          구독 플랜
        </h1>
        <p className="mt-2 text-lg text-surface-500 dark:text-surface-400">
          연구에 맞는 플랜을 선택하고 AI 논문 분석의 힘을 경험하세요
        </p>
      </div>

      {/* 현재 구독 상태 */}
      {mySubscription && mySubscription.status !== 'canceled' && (
        <Card className="border-brand-200 dark:border-brand-800 bg-brand-50/50 dark:bg-brand-900/10">
          <CardContent className="py-4">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center">
                  <CrownIcon size={20} className="text-brand-600 dark:text-brand-400" />
                </div>
                <div>
                  <p className="font-medium text-surface-900 dark:text-surface-100">
                    현재 플랜: <span className="text-brand-600 dark:text-brand-400">{mySubscription.plan?.name}</span>
                  </p>
                  <p className="text-sm text-surface-500">
                    상태: {mySubscription.status === 'active' ? '활성' : mySubscription.status}
                    {mySubscription.current_period_end && (
                      <> · 다음 결제일: {new Date(mySubscription.current_period_end).toLocaleDateString('ko-KR')}</>
                    )}
                  </p>
                </div>
              </div>
              {mySubscription.plan?.tier !== 'free' && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-error-600 hover:bg-error-50 dark:hover:bg-error-900/20"
                  onClick={() => setCancelModalOpen(true)}
                >
                  구독 취소
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 플랜 카드 그리드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {plans?.map((plan: any) => {
          const Icon = planIcons[plan.tier] || SparklesIcon
          const gradientColor = planColors[plan.tier] || planColors.basic
          const isCurrentPlan = currentTier === plan.tier
          const isPopular = plan.tier === 'pro'

          return (
            <Card
              key={plan.id}
              className={`
                relative overflow-hidden transition-all duration-300
                ${isCurrentPlan ? 'ring-2 ring-brand-500 dark:ring-brand-400' : ''}
                ${isPopular ? 'lg:-translate-y-2' : ''}
                hover:shadow-lg
              `}
            >
              {/* 인기 배지 */}
              {isPopular && (
                <div className="absolute top-0 right-0">
                  <div className="bg-accent-500 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
                    인기
                  </div>
                </div>
              )}

              {/* 현재 플랜 배지 */}
              {isCurrentPlan && (
                <div className="absolute top-0 left-0">
                  <div className="bg-brand-500 text-white text-xs font-bold px-3 py-1 rounded-br-lg">
                    현재 플랜
                  </div>
                </div>
              )}

              <CardContent className="pt-8">
                {/* 플랜 아이콘 */}
                <div className={`
                  w-14 h-14 rounded-2xl bg-gradient-to-br ${gradientColor}
                  flex items-center justify-center mb-4
                `}>
                  <Icon size={28} className="text-white" />
                </div>

                {/* 플랜 이름 */}
                <h3 className="text-xl font-bold text-surface-900 dark:text-surface-100">
                  {plan.name}
                </h3>

                {/* 가격 */}
                <div className="mt-4 mb-6">
                  <span className="text-4xl font-bold text-surface-900 dark:text-surface-100">
                    {plan.price === 0 ? '무료' : `$${plan.price}`}
                  </span>
                  {plan.price > 0 && (
                    <span className="text-surface-500 dark:text-surface-400">/월</span>
                  )}
                </div>

                {/* 기능 목록 */}
                <ul className="space-y-3 mb-6">
                  <PlanFeature
                    included
                    text={`논문 저장 ${plan.max_papers === -1 ? '무제한' : `최대 ${plan.max_papers}개`}`}
                  />
                  <PlanFeature
                    included
                    text={`월 ${plan.max_analyses_per_month === -1 ? '무제한' : plan.max_analyses_per_month}회 분석`}
                  />
                  <PlanFeature
                    included
                    text={`${plan.max_comparison_papers}개 논문 비교`}
                  />
                  <PlanFeature
                    included={plan.tier !== 'free'}
                    text="우선 지원"
                  />
                  <PlanFeature
                    included={plan.tier === 'pro' || plan.tier === 'enterprise'}
                    text="고급 분석 기능"
                  />
                  <PlanFeature
                    included={plan.tier === 'enterprise'}
                    text="전용 API 엔드포인트"
                  />
                </ul>

                {/* 구독 버튼 */}
                <Button
                  variant={isCurrentPlan ? 'secondary' : isPopular ? 'primary' : 'outline'}
                  size="lg"
                  className="w-full"
                  disabled={isCurrentPlan || createMutation.isPending}
                  isLoading={selectedPlan === plan.tier && createMutation.isPending}
                  onClick={() => handleSubscribe(plan.tier)}
                >
                  {isCurrentPlan ? '현재 플랜' : plan.price === 0 ? '무료로 시작' : '구독하기'}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* FAQ 섹션 */}
      <div className="mt-16">
        <h2 className="text-2xl font-bold text-center text-surface-900 dark:text-surface-100 mb-8">
          자주 묻는 질문
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <FaqItem
            question="플랜을 업그레이드하면 어떻게 되나요?"
            answer="업그레이드 시 즉시 새로운 플랜의 기능을 사용할 수 있습니다. 기존 결제 기간의 남은 금액은 비례 계산되어 다음 결제에 반영됩니다."
          />
          <FaqItem
            question="구독을 취소하면 데이터는 어떻게 되나요?"
            answer="구독 취소 후에도 저장된 논문과 분석 결과는 유지됩니다. 다만 무료 플랜의 제한이 적용됩니다."
          />
          <FaqItem
            question="결제 방법은 무엇인가요?"
            answer="Visa, Mastercard, American Express 등 주요 신용카드와 체크카드를 지원합니다."
          />
          <FaqItem
            question="환불 정책은 어떻게 되나요?"
            answer="첫 결제 후 7일 이내에 환불을 요청하시면 전액 환불해 드립니다."
          />
        </div>
      </div>

      {/* 구독 취소 확인 모달 */}
      <ConfirmModal
        isOpen={cancelModalOpen}
        onClose={() => setCancelModalOpen(false)}
        onConfirm={handleCancel}
        title="구독 취소"
        message="정말 구독을 취소하시겠습니까? 현재 결제 기간이 끝나면 무료 플랜으로 전환됩니다."
        confirmLabel="구독 취소"
        variant="danger"
        isLoading={cancelMutation.isPending}
      />
    </div>
  )
}

// 플랜 기능 아이템 컴포넌트
function PlanFeature({ included, text }: { included: boolean; text: string }) {
  return (
    <li className="flex items-center gap-2">
      {included ? (
        <CheckIcon size={18} className="text-brand-500 flex-shrink-0" />
      ) : (
        <XMarkIcon size={18} className="text-surface-300 dark:text-surface-600 flex-shrink-0" />
      )}
      <span className={included ? 'text-surface-700 dark:text-surface-300' : 'text-surface-400 dark:text-surface-500'}>
        {text}
      </span>
    </li>
  )
}

// FAQ 아이템 컴포넌트
function FaqItem({ question, answer }: { question: string; answer: string }) {
  return (
    <Card variant="ghost" className="bg-surface-50 dark:bg-surface-800/50">
      <CardContent>
        <h3 className="font-semibold text-surface-900 dark:text-surface-100 mb-2">
          {question}
        </h3>
        <p className="text-sm text-surface-600 dark:text-surface-400">
          {answer}
        </p>
      </CardContent>
    </Card>
  )
}

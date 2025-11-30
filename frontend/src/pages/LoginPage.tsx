import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'
import {
  Input,
  PasswordInput,
  Button,
  Card,
  CardContent,
  InlineError,
  BeakerIcon,
  SparklesIcon,
  ShieldCheckIcon,
  ChartBarIcon,
} from '../components/ui'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await authAPI.login({ email, password })
      const { access_token, refresh_token } = response.data

      setAuth(
        { id: 1, email, username: email.split('@')[0] },
        access_token,
        refresh_token
      )

      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || '로그인에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const features = [
    {
      icon: BeakerIcon,
      title: 'AI 기반 논문 분석',
      description: 'GPT-4를 활용한 심층 논문 분석',
    },
    {
      icon: ChartBarIcon,
      title: '논문 비교 분석',
      description: '여러 논문을 한눈에 비교',
    },
    {
      icon: SparklesIcon,
      title: 'RAG 기술',
      description: '정확한 정보 검색 및 요약',
    },
    {
      icon: ShieldCheckIcon,
      title: '보안 우선',
      description: '안전한 데이터 관리',
    },
  ]

  return (
    <div className="min-h-screen flex bg-surface-50 dark:bg-surface-950">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 xl:w-[55%] bg-gradient-to-br from-brand-600 via-brand-500 to-accent-500 p-12 flex-col justify-between relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-white rounded-full blur-3xl" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
              <BeakerIcon size={24} className="text-white" />
            </div>
            <span className="text-2xl font-bold text-white">BioscopeAI</span>
          </div>
        </div>

        <div className="relative z-10 space-y-8">
          <div>
            <h1 className="text-4xl xl:text-5xl font-bold text-white leading-tight">
              생물의학 논문 분석의
              <br />
              <span className="text-brand-200">새로운 패러다임</span>
            </h1>
            <p className="mt-4 text-lg text-white/80 max-w-md">
              AI 기반 논문 분석 플랫폼으로 연구 효율을 극대화하세요.
              PubMed 검색부터 AI 분석까지 한 곳에서.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {features.map((feature, index) => (
              <div
                key={index}
                className="p-4 rounded-xl bg-white/10 backdrop-blur border border-white/20"
              >
                <feature.icon size={24} className="text-white mb-2" />
                <h3 className="font-semibold text-white">{feature.title}</h3>
                <p className="text-sm text-white/70 mt-1">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-sm text-white/60">
            &copy; 2024 BioscopeAI. All rights reserved.
          </p>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 xl:w-[45%] flex items-center justify-center p-6 sm:p-12">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center">
            <div className="inline-flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-brand-500 flex items-center justify-center">
                <BeakerIcon size={24} className="text-white" />
              </div>
              <span className="text-2xl font-bold text-surface-900 dark:text-surface-50">
                BioscopeAI
              </span>
            </div>
            <p className="mt-2 text-surface-500 dark:text-surface-400">
              생물의학 논문 분석 플랫폼
            </p>
          </div>

          {/* Welcome Text */}
          <div className="text-center lg:text-left">
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              다시 오신 것을 환영합니다
            </h2>
            <p className="mt-2 text-surface-500 dark:text-surface-400">
              계정에 로그인하여 논문 분석을 시작하세요
            </p>
          </div>

          {/* Login Form */}
          <Card className="border-0 shadow-xl dark:bg-surface-900">
            <CardContent className="p-6">
              <form onSubmit={handleSubmit} className="space-y-5">
                <Input
                  label="이메일"
                  type="email"
                  placeholder="example@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />

                <PasswordInput
                  label="비밀번호"
                  placeholder="비밀번호를 입력하세요"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />

                {error && <InlineError message={error} />}

                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      className="w-4 h-4 rounded border-surface-300 text-brand-500 focus:ring-brand-500"
                    />
                    <span className="text-surface-600 dark:text-surface-400">
                      로그인 상태 유지
                    </span>
                  </label>
                  <button
                    type="button"
                    className="text-brand-600 dark:text-brand-400 hover:underline"
                  >
                    비밀번호 찾기
                  </button>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  isLoading={loading}
                  fullWidth
                >
                  로그인
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Sign Up Link */}
          <p className="text-center text-surface-600 dark:text-surface-400">
            계정이 없으신가요?{' '}
            <Link
              to="/register"
              className="text-brand-600 dark:text-brand-400 font-medium hover:underline"
            >
              회원가입
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

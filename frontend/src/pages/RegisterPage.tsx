import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../services/api'
import {
  Input,
  PasswordInput,
  Button,
  Card,
  CardContent,
  InlineError,
  BeakerIcon,
  CheckCircleIcon,
} from '../components/ui'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await authAPI.register(formData)
      navigate('/login')
    } catch (err: any) {
      setError(err.response?.data?.detail || '회원가입에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  // 비밀번호 강도 체크
  const passwordStrength = {
    hasMinLength: formData.password.length >= 8,
    hasUppercase: /[A-Z]/.test(formData.password),
    hasNumber: /[0-9]/.test(formData.password),
  }

  const benefits = [
    'AI 기반 논문 분석 무제한 이용',
    'PubMed 통합 검색',
    '논문 비교 분석',
    '개인 라이브러리 관리',
  ]

  return (
    <div className="min-h-screen flex bg-surface-50 dark:bg-surface-950">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 xl:w-[55%] bg-gradient-to-br from-accent-600 via-brand-500 to-brand-600 p-12 flex-col justify-between relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 right-20 w-72 h-72 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-32 left-20 w-96 h-96 bg-white rounded-full blur-3xl" />
        </div>

        <div className="relative z-10">
          <Link to="/login" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
              <BeakerIcon size={24} className="text-white" />
            </div>
            <span className="text-2xl font-bold text-white">BioscopeAI</span>
          </Link>
        </div>

        <div className="relative z-10 space-y-8">
          <div>
            <h1 className="text-4xl xl:text-5xl font-bold text-white leading-tight">
              연구의 새로운 시작,
              <br />
              <span className="text-accent-200">지금 시작하세요</span>
            </h1>
            <p className="mt-4 text-lg text-white/80 max-w-md">
              무료로 가입하고 AI 기반 논문 분석의 힘을 경험하세요.
              연구 효율성을 한 단계 높여드립니다.
            </p>
          </div>

          {/* Benefits */}
          <div className="space-y-3">
            <p className="text-sm font-medium text-white/60 uppercase tracking-wider">
              가입 혜택
            </p>
            {benefits.map((benefit, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center">
                  <CheckCircleIcon size={14} className="text-white" />
                </div>
                <span className="text-white">{benefit}</span>
              </div>
            ))}
          </div>

          {/* Testimonial */}
          <div className="p-6 rounded-2xl bg-white/10 backdrop-blur border border-white/20">
            <p className="text-white/90 italic">
              "BioscopeAI 덕분에 문헌 리뷰 시간이 절반으로 줄었습니다.
              연구자에게 꼭 필요한 도구입니다."
            </p>
            <div className="mt-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20" />
              <div>
                <p className="font-medium text-white">김연구</p>
                <p className="text-sm text-white/60">서울대학교 의과대학</p>
              </div>
            </div>
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-sm text-white/60">
            &copy; 2024 BioscopeAI. All rights reserved.
          </p>
        </div>
      </div>

      {/* Right Panel - Register Form */}
      <div className="w-full lg:w-1/2 xl:w-[45%] flex items-center justify-center p-6 sm:p-12">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center">
            <Link to="/login" className="inline-flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-brand-500 flex items-center justify-center">
                <BeakerIcon size={24} className="text-white" />
              </div>
              <span className="text-2xl font-bold text-surface-900 dark:text-surface-50">
                BioscopeAI
              </span>
            </Link>
          </div>

          {/* Welcome Text */}
          <div className="text-center lg:text-left">
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              계정 만들기
            </h2>
            <p className="mt-2 text-surface-500 dark:text-surface-400">
              무료로 가입하고 AI 논문 분석을 시작하세요
            </p>
          </div>

          {/* Register Form */}
          <Card className="border-0 shadow-xl dark:bg-surface-900">
            <CardContent className="p-6">
              <form onSubmit={handleSubmit} className="space-y-5">
                <Input
                  label="이메일"
                  type="email"
                  placeholder="example@email.com"
                  value={formData.email}
                  onChange={(e) => updateField('email', e.target.value)}
                  required
                  autoComplete="email"
                />

                <Input
                  label="사용자명"
                  type="text"
                  placeholder="사용자명을 입력하세요"
                  value={formData.username}
                  onChange={(e) => updateField('username', e.target.value)}
                  required
                  autoComplete="username"
                  hint="영문, 숫자, 언더스코어(_)만 사용 가능"
                />

                <Input
                  label="이름"
                  type="text"
                  placeholder="이름 (선택사항)"
                  value={formData.full_name}
                  onChange={(e) => updateField('full_name', e.target.value)}
                  autoComplete="name"
                />

                <div>
                  <PasswordInput
                    label="비밀번호"
                    placeholder="비밀번호를 입력하세요"
                    value={formData.password}
                    onChange={(e) => updateField('password', e.target.value)}
                    required
                    autoComplete="new-password"
                  />

                  {/* Password Strength Indicator */}
                  {formData.password && (
                    <div className="mt-3 space-y-2">
                      <div className="flex gap-1">
                        {[...Array(3)].map((_, i) => {
                          const filledCount = Object.values(passwordStrength).filter(Boolean).length
                          return (
                            <div
                              key={i}
                              className={`h-1 flex-1 rounded-full transition-colors ${
                                i < filledCount
                                  ? filledCount === 3
                                    ? 'bg-success-500'
                                    : filledCount === 2
                                    ? 'bg-warning-500'
                                    : 'bg-error-500'
                                  : 'bg-surface-200 dark:bg-surface-700'
                              }`}
                            />
                          )
                        })}
                      </div>
                      <ul className="text-xs space-y-1">
                        <li
                          className={
                            passwordStrength.hasMinLength
                              ? 'text-success-600 dark:text-success-400'
                              : 'text-surface-400'
                          }
                        >
                          {passwordStrength.hasMinLength ? '✓' : '○'} 최소 8자 이상
                        </li>
                        <li
                          className={
                            passwordStrength.hasUppercase
                              ? 'text-success-600 dark:text-success-400'
                              : 'text-surface-400'
                          }
                        >
                          {passwordStrength.hasUppercase ? '✓' : '○'} 대문자 포함
                        </li>
                        <li
                          className={
                            passwordStrength.hasNumber
                              ? 'text-success-600 dark:text-success-400'
                              : 'text-surface-400'
                          }
                        >
                          {passwordStrength.hasNumber ? '✓' : '○'} 숫자 포함
                        </li>
                      </ul>
                    </div>
                  )}
                </div>

                {error && <InlineError message={error} />}

                {/* Terms Agreement */}
                <label className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    required
                    className="mt-1 w-4 h-4 rounded border-surface-300 text-brand-500 focus:ring-brand-500"
                  />
                  <span className="text-sm text-surface-600 dark:text-surface-400">
                    <Link to="/terms" className="text-brand-600 dark:text-brand-400 hover:underline">
                      이용약관
                    </Link>
                    {' '}및{' '}
                    <Link to="/privacy" className="text-brand-600 dark:text-brand-400 hover:underline">
                      개인정보처리방침
                    </Link>
                    에 동의합니다
                  </span>
                </label>

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  isLoading={loading}
                  fullWidth
                >
                  가입하기
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Login Link */}
          <p className="text-center text-surface-600 dark:text-surface-400">
            이미 계정이 있으신가요?{' '}
            <Link
              to="/login"
              className="text-brand-600 dark:text-brand-400 font-medium hover:underline"
            >
              로그인
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

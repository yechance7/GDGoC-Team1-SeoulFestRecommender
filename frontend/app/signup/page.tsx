"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import Image from "next/image"

export default function SignupPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  })
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setError("")
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    // Validation
    if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) {
      setError("모든 필드를 입력해주세요.")
      return
    }

    if (!formData.email.includes("@")) {
      setError("유효한 이메일을 입력해주세요.")
      return
    }

    if (formData.password.length < 6) {
      setError("비밀번호는 최소 6자 이상이어야 합니다.")
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError("비밀번호가 일치하지 않습니다.")
      return
    }

    // Simulate account creation
    setSuccess(true)
    setTimeout(() => {
      router.push("/")
    }, 2000)
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
        <div className="bg-slate-800 rounded-lg p-8 w-full max-w-md border border-slate-700 text-center">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-white mb-2">계정이 생성되었습니다!</h2>
          <p className="text-slate-300">메인 페이지로 이동합니다...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-lg p-8 w-full max-w-md border border-slate-700">
        <div className="flex justify-center mb-6">
          <Link href="/">
            <Image 
              src="/logo.png" 
              alt="Logo" 
              width={120} 
              height={40}
              className="object-contain cursor-pointer"
            />
          </Link>
        </div>

        <h2 className="text-2xl font-bold text-white mb-2 text-center">계정 만들기</h2>
        <p className="text-slate-400 text-sm mb-6 text-center">FindFest에 가입하고 행사를 찜해보세요!</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">사용자 이름</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-slate-700 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="홍길동"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">이메일</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-slate-700 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">비밀번호</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-slate-700 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">비밀번호 확인</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-slate-700 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            className="w-full py-2 bg-purple-500 text-white font-semibold rounded-lg hover:bg-purple-600 transition-colors"
          >
            계정 만들기
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-slate-400 text-sm">
            이미 계정이 있으신가요?{" "}
            <Link href="/" className="text-purple-400 hover:text-purple-300 font-medium transition-colors">
              로그인
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}


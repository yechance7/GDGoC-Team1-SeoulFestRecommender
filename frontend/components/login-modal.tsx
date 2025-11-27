"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"

interface LoginModalProps {
  onLogin: (username: string) => void
  onClose: () => void
}

export default function LoginModal({ onLogin, onClose }: LoginModalProps) {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!email || !password) {
      setError("모든 필드를 입력해주세요.")
      return
    }

    if (!email.includes("@")) {
      setError("유효한 이메일을 입력해주세요.")
      return
    }

    if (password.length < 6) {
      setError("비밀번호는 최소 6자 이상이어야 합니다.")
      return
    }

    const username = email.split("@")[0]
    onLogin(username)
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-8 w-full max-w-md border border-slate-700">
        <h2 className="text-2xl font-bold text-white mb-6">FindFest에 로그인하세요</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">이메일</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">비밀번호</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="••••••••"
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            type="submit"
            className="w-full py-2 bg-purple-500 text-white font-semibold rounded-lg hover:bg-purple-600 transition-colors"
          >
            로그인
          </button>
        </form>

        <button
          onClick={onClose}
          className="mt-4 w-full py-2 text-slate-300 border border-slate-600 rounded-lg hover:bg-slate-700 transition-colors"
        >
          취소
        </button>

        <div className="mt-6 text-center">
          <p className="text-slate-400 text-sm mb-3">계정이 없으신가요?</p>
          <button
            onClick={() => {
              onClose()
              router.push('/signup')
            }}
            className="text-purple-400 hover:text-purple-300 font-medium text-sm transition-colors"
          >
            계정 만들기
          </button>
        </div>

        <p className="text-slate-400 text-xs mt-4 text-center">이메일과 비밀번호를 입력해주세요 (최소 6자 이상)</p>
      </div>
    </div>
  )
}

"use client"

import Image from 'next/image'
import Link from 'next/link'

interface HeaderProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  isLoggedIn: boolean
  username?: string
  onLogin: () => void
  onLogout: () => void
  onNavigateLiked?: () => void
}

export default function Header({
  searchQuery,
  onSearchChange,
  isLoggedIn,
  username,
  onLogin,
  onLogout,
  onNavigateLiked,
}: HeaderProps) {
  return (
    <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center gap-10">
          <Link href="/" className="cursor-pointer"> 
            <Image 
              src="/logo.png" 
              alt="Logo" 
              width={150} 
              height={50}
              className="object-contain"
            />
          </Link>

          <div className="w-110">
            <input
              type="text"
              placeholder="Search events..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div className="flex items-center gap-4 ml-auto">
            {isLoggedIn ? (
              <>
                <button onClick={onNavigateLiked} className="text-slate-300 hover:text-purple-400 font-medium text-sm">
                  ❤️ 내가 찜한 행사들
                </button>
                <span className="text-slate-400 text-sm">{username}님, 환영합니다!</span>
                <button
                  onClick={onLogout}
                  className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors text-sm"
                >
                  로그아웃
                </button>
              </>
            ) : (
              <button
                onClick={onLogin}
                className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors text-sm"
              >
                로그인
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

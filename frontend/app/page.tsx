"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Header from "@/components/header"
import EventCalendar from "@/components/event-calendar"
import EventList from "@/components/event-list"
import ChatBot from "@/components/chat-bot"
import LoginModal from "@/components/login-modal"
import { eventsData, categories } from "@/lib/events-data"

export default function Home() {
  const router = useRouter()
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [showChat, setShowChat] = useState(false)
  const [showLoginModal, setShowLoginModal] = useState(false)

  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState("")
  const [likedEvents, setLikedEvents] = useState<string[]>([])

  useEffect(() => {
    const savedUsername = localStorage.getItem("username")
    const savedLikes = localStorage.getItem("likedEvents")

    if (savedUsername) {
      setUsername(savedUsername)
      setIsLoggedIn(true)
    }

    if (savedLikes) {
      setLikedEvents(JSON.parse(savedLikes))
    }
  }, [])

  useEffect(() => {
    if (isLoggedIn) {
      localStorage.setItem("likedEvents", JSON.stringify(likedEvents))
    }
  }, [likedEvents, isLoggedIn])

  const handleLogin = (newUsername: string) => {
    setUsername(newUsername)
    setIsLoggedIn(true)
    setShowLoginModal(false)
    localStorage.setItem("username", newUsername)
  }

  const handleLogout = () => {
    setUsername("")
    setIsLoggedIn(false)
    setLikedEvents([])
    localStorage.removeItem("username")
    localStorage.removeItem("likedEvents")
  }

  const handleToggleLike = (eventId: string) => {
    setLikedEvents((prev) => (prev.includes(eventId) ? prev.filter((id) => id !== eventId) : [...prev, eventId]))
  }

  const handleNavigateLiked = () => {
    router.push("/liked")
  }

  const filteredEvents = eventsData.filter((event) => {
    const matchesCategory = !selectedCategory || event.category === selectedCategory
    const matchesSearch =
      event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesDate = !selectedDate || new Date(event.date).toDateString() === selectedDate.toDateString()

    return matchesCategory && matchesSearch && matchesDate
  })

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Header
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        isLoggedIn={isLoggedIn}
        username={username}
        onLogin={() => setShowLoginModal(true)}
        onLogout={handleLogout}
        onNavigateLiked={handleNavigateLiked}
      />

      {showLoginModal && <LoginModal onLogin={handleLogin} onClose={() => setShowLoginModal(false)} />}

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar with Calendar and Filters */}
          <div className="lg:col-span-1 space-y-6">
            <EventCalendar events={eventsData} selectedDate={selectedDate} onSelectDate={setSelectedDate} />

            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4">카테고리</h3>
              <div className="space-y-2">
                <button
                  onClick={() => setSelectedCategory(null)}
                  className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                    selectedCategory === null ? "bg-purple-500 text-white" : "text-slate-300 hover:bg-slate-700"
                  }`}
                >
                  모든 행사
                </button>
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`w-full text-left px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                      selectedCategory === category.id
                        ? "bg-purple-500 text-white"
                        : "text-slate-300 hover:bg-slate-700"
                    }`}
                  >
                    <span className="text-xl">{category.icon}</span>
                    {category.name}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {selectedDate && (
              <div className="flex items-center gap-2 text-slate-300">
                <button onClick={() => setSelectedDate(null)} className="text-purple-500 hover:text-purple-400">
                  ✕
                </button>
                <p>{selectedDate.getFullYear()}년 {selectedDate.getMonth() + 1}월 {selectedDate.getDate()}일 행사들</p>
              </div>
            )}

            <EventList
              events={filteredEvents}
              likedEvents={likedEvents}
              onToggleLike={isLoggedIn ? handleToggleLike : undefined}
              isLoggedIn={isLoggedIn}
            />
          </div>
        </div>
      </div>

      <button
        onClick={() => setShowChat(!showChat)}
        className="fixed bottom-6 right-6 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2 z-40 shadow-lg"
        style={{ backgroundColor: "#8B5CF6", minWidth: "240px" }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#7C3AED")}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#8B5CF6")}
      >
        <span>💬</span>
        챗봇과 대화하기
      </button>

      {showChat && (
        <div className="fixed bottom-24 right-6 w-96 shadow-2xl z-50">
          <ChatBot events={eventsData} onClose={() => setShowChat(false)} />
        </div>
      )}
    </main>
  )
}

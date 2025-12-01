"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Header from "@/components/header"
import EventCalendar from "@/components/event-calendar"
import EventList from "@/components/event-list"
import ChatBot from "@/components/chat-bot"
import LoginModal from "@/components/login-modal"
import { categories, convertSeoulEventsToEvents, type Event } from "@/lib/events-data"
import { getSeoulEvents, getLikedSeoulEvents, likeSeoulEvent, unlikeSeoulEvent } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"

export default function Home() {
  const router = useRouter()
  const { user, token, logout } = useAuth()
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [showChat, setShowChat] = useState(false)
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [likedEvents, setLikedEvents] = useState<string[]>([])
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch Seoul events from backend on component mount
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Fetch events from backend with a reasonable limit
        const seoulEvents = await getSeoulEvents({ limit: 500 })
        
        // Convert backend data to frontend format
        const convertedEvents = convertSeoulEventsToEvents(seoulEvents)
        
        setEvents(convertedEvents)
        console.log(`Successfully loaded ${convertedEvents.length} events from backend`)
      } catch (err) {
        console.error("Failed to fetch events:", err)
        setError(err instanceof Error ? err.message : "Failed to load events")
      } finally {
        setLoading(false)
      }
    }

    fetchEvents()
  }, [])

  // Check if login parameter is present in URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.get('login') === 'true') {
      setShowLoginModal(true)
    }
  }, [])

  // Load liked events from backend when user logs in
  useEffect(() => {
    if (user && token) {
      fetchLikedEvents()
    } else {
      setLikedEvents([])
    }
  }, [user, token])

  const fetchLikedEvents = async () => {
    if (!token) return

    try {
      const seoulEvents = await getLikedSeoulEvents(token)
      // Store just the IDs as strings to match the existing format
      const likedIds = seoulEvents.map(e => String(e.id))
      setLikedEvents(likedIds)
    } catch (err) {
      console.error("Failed to fetch liked events:", err)
      // Don't show error to user on main page, just log it
    }
  }

  const handleLogin = () => {
    setShowLoginModal(false)
  }

  const handleLogout = () => {
    logout()
    setLikedEvents([])
  }

  const handleToggleLike = async (eventId: string) => {
    if (!token) return

    try {
      const numericEventId = Number(eventId)
      
      if (likedEvents.includes(eventId)) {
        // Unlike the event
        await unlikeSeoulEvent(numericEventId, token)
        setLikedEvents((prev) => prev.filter((id) => id !== eventId))
      } else {
        // Like the event
        await likeSeoulEvent(numericEventId, token)
        setLikedEvents((prev) => [...prev, eventId])
      }
    } catch (err) {
      console.error("Failed to toggle like:", err)
      // Optionally show error to user
      alert("찜하기 상태를 변경하는데 실패했습니다. 다시 시도해주세요.")
    }
  }

  const handleNavigateLiked = () => {
    router.push("/liked")
  }

  const filteredEvents = events.filter((event) => {
    const matchesCategory = !selectedCategory || event.category === selectedCategory
    const matchesSearch =
      event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (event.location && event.location.toLowerCase().includes(searchQuery.toLowerCase()))
    
    // Check if the selected date falls within the event's date range
    let matchesDate = true
    if (selectedDate) {
      if (event.startDate && event.endDate) {
        const start = new Date(event.startDate + 'T00:00:00')
        const end = new Date(event.endDate + 'T00:00:00')
        const selected = new Date(selectedDate.toDateString())
        matchesDate = selected >= start && selected <= end
      } else {
        const eventDate = new Date(event.date + 'T00:00:00')
        matchesDate = eventDate.toDateString() === selectedDate.toDateString()
      }
    }

    return matchesCategory && matchesSearch && matchesDate
  })

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Header
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        isLoggedIn={!!user}
        username={user?.username}
        onLogin={() => setShowLoginModal(true)}
        onLogout={handleLogout}
        onNavigateLiked={handleNavigateLiked}
      />

      {showLoginModal && <LoginModal onLogin={handleLogin} onClose={() => setShowLoginModal(false)} />}

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Show loading state */}
        {loading && (
          <div className="text-center py-12 text-slate-300">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mb-4"></div>
            <p className="text-lg">서울 행사 정보를 불러오는 중...</p>
          </div>
        )}

        {/* Show error state */}
        {error && (
          <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 text-center text-red-300">
            <p className="text-lg font-semibold mb-2">행사 정보를 불러올 수 없습니다</p>
            <p className="text-sm">{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-4 px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
            >
              다시 시도
            </button>
          </div>
        )}

        {/* Show content when loaded */}
        {!loading && !error && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Sidebar with Calendar and Filters */}
            <div className="lg:col-span-1 space-y-6">
              <EventCalendar events={events} selectedDate={selectedDate} onSelectDate={setSelectedDate} />

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
              {/* Display total events count */}
              <div className="text-slate-300 text-sm">
                총 <span className="text-purple-400 font-semibold">{events.length}</span>개의 행사
                {selectedCategory && ` · ${selectedCategory} 필터 적용`}
                {searchQuery && ` · "${searchQuery}" 검색 결과`}
              </div>

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
                onToggleLike={user ? handleToggleLike : undefined}
                isLoggedIn={!!user}
              />
            </div>
          </div>
        )}
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
          <ChatBot events={events} onClose={() => setShowChat(false)} />
        </div>
      )}
    </main>
  )
}

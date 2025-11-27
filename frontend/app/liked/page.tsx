"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Header from "@/components/header"
import EventList from "@/components/event-list"
import LoginModal from "@/components/login-modal"
import { eventsData } from "@/lib/events-data"

export default function LikedPage() {
  const router = useRouter()
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState("")
  const [likedEvents, setLikedEvents] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [showLoginModal, setShowLoginModal] = useState(false)

  useEffect(() => {
    const savedUsername = localStorage.getItem("username")
    const savedLikes = localStorage.getItem("likedEvents")

    if (savedUsername) {
      setUsername(savedUsername)
      setIsLoggedIn(true)
    } else {
      router.push("/")
    }

    if (savedLikes) {
      setLikedEvents(JSON.parse(savedLikes))
    }
  }, [router])

  const handleLogout = () => {
    setUsername("")
    setIsLoggedIn(false)
    setLikedEvents([])
    localStorage.removeItem("username")
    localStorage.removeItem("likedEvents")
    router.push("/")
  }

  const handleToggleLike = (eventId: string) => {
    setLikedEvents((prev) => {
      const updated = prev.includes(eventId) ? prev.filter((id) => id !== eventId) : [...prev, eventId]
      localStorage.setItem("likedEvents", JSON.stringify(updated))
      return updated
    })
  }

  const handleNavigateLiked = () => {
    // Already on liked page, do nothing
  }

  const likedEventsList = eventsData
    .filter((event) => likedEvents.includes(event.id))
    .filter(
      (event) =>
        event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        event.description.toLowerCase().includes(searchQuery.toLowerCase()),
    )

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

      {showLoginModal && (
        <LoginModal
          onLogin={(newUsername) => {
            setUsername(newUsername)
            setIsLoggedIn(true)
            setShowLoginModal(false)
          }}
          onClose={() => setShowLoginModal(false)}
        />
      )}

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">내가 찜한 행사들</h2>
          <p className="text-slate-400">
            {likedEventsList.length} event{likedEventsList.length !== 1 ? "s" : ""} saved
          </p>
        </div>

        <EventList
          events={likedEventsList}
          likedEvents={likedEvents}
          onToggleLike={handleToggleLike}
          isLoggedIn={isLoggedIn}
        />
      </div>
    </main>
  )
}

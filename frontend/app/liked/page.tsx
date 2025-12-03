"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Header from "@/components/header"
import EventList from "@/components/event-list"
import LoginModal from "@/components/login-modal"
import { useAuth } from "@/contexts/auth-context"
import { getLikedSeoulEvents, likeSeoulEvent, unlikeSeoulEvent } from "@/lib/api"
import { Event, convertSeoulEventsToEvents } from "@/lib/events-data"

export default function LikedPage() {
  const router = useRouter()
  const { user, token, logout } = useAuth()
  const [likedEvents, setLikedEvents] = useState<Event[]>([])
  const [likedEventIds, setLikedEventIds] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState("")
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Redirect to home if not logged in
  useEffect(() => {
    if (!user) {
      router.push("/")
    }
  }, [user, router])

  const fetchLikedEvents = async () => {
    if (!token) return

    try {
      setIsLoading(true)
      setError(null)
      const seoulEvents = await getLikedSeoulEvents(token)
      // Convert Seoul events to frontend Event format
      const events = convertSeoulEventsToEvents(seoulEvents)
      setLikedEvents(events)
      // Create a set of liked event IDs for quick lookup
      setLikedEventIds(new Set(events.map(e => e.id)))
    } catch (err) {
      console.error("Failed to fetch liked events:", err)
      setError(err instanceof Error ? err.message : "Failed to load liked events")
    } finally {
      setIsLoading(false)
    }
  }

  // Load liked events from backend
  useEffect(() => {
    if (user && token) {
      fetchLikedEvents()
    }
  }, [user, token])

  const handleLogout = () => {
    logout()
    setLikedEvents([])
    setLikedEventIds(new Set())
    router.push("/")
  }

  const handleToggleLike = async (eventId: string) => {
    if (!token) return

    try {
      const numericEventId = Number(eventId)
      
      if (likedEventIds.has(eventId)) {
        // Unlike the event
        await unlikeSeoulEvent(numericEventId, token)
        // Remove from local state
        setLikedEvents(prev => prev.filter(e => e.id !== eventId))
        setLikedEventIds(prev => {
          const newSet = new Set(prev)
          newSet.delete(eventId)
          return newSet
        })
      } else {
        // Like the event (shouldn't happen on this page, but handle it anyway)
        await likeSeoulEvent(numericEventId, token)
        // Refresh the list
        await fetchLikedEvents()
      }
    } catch (err) {
      console.error("Failed to toggle like:", err)
      setError(err instanceof Error ? err.message : "Failed to update like status")
    }
  }

  const handleNavigateLiked = () => {
    // Already on liked page, do nothing
  }

  // Filter liked events based on search query
  const filteredLikedEvents = likedEvents.filter(
    (event) =>
      event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.location.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <main className="min-h-screen bg-linear-to-br from-slate-950 via-slate-900 to-slate-950">
      <Header
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        isLoggedIn={!!user}
        username={user?.username}
        onLogin={() => setShowLoginModal(true)}
        onLogout={handleLogout}
        onNavigateLiked={handleNavigateLiked}
      />

      {showLoginModal && (
        <LoginModal
          onLogin={() => setShowLoginModal(false)}
          onClose={() => setShowLoginModal(false)}
        />
      )}

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">내가 찜한 행사들</h2>
          <p className="text-slate-400">
            {filteredLikedEvents.length} event{filteredLikedEvents.length !== 1 ? "s" : ""} saved
          </p>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <p className="text-slate-400">Loading your liked events...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-400 mb-4">{error}</p>
            <button
              onClick={fetchLikedEvents}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white"
            >
              Try Again
            </button>
          </div>
        ) : filteredLikedEvents.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-400">
              {searchQuery ? "No liked events match your search." : "You haven't liked any events yet."}
            </p>
          </div>
        ) : (
          <EventList
            events={filteredLikedEvents}
            likedEvents={Array.from(likedEventIds)}
            onToggleLike={handleToggleLike}
            isLoggedIn={!!user}
          />
        )}
      </div>
    </main>
  )
}

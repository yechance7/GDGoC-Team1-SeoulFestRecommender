"use client"

import type { Event } from "@/lib/events-data"
import { categoryEmojis } from "@/lib/events-data"

interface EventListProps {
  events: Event[]
  likedEvents?: string[]
  onToggleLike?: (eventId: string) => void
  isLoggedIn?: boolean
}

export default function EventList({ events, likedEvents = [], onToggleLike, isLoggedIn = false }: EventListProps) {
  const handleEventClick = (event: Event) => {
    // Try to open the event's homepage link
    // Priority: org_link (organization website) or hmpg_addr (culture portal)
    const url = event.orgLink || event.hmpgAddr
    
    if (url) {
      window.open(url, '_blank', 'noopener,noreferrer')
    } else {
      // If no link available, show a message
      alert('이 행사의 홈페이지 정보가 없습니다.')
    }
  }

  return (
    <div className="space-y-4">
      {events.length === 0 ? (
        <div className="text-center py-12 text-slate-400">
          <p className="text-lg">행사를 찾을 수 없어요.</p>
          <p className="text-sm mt-1">검색어나 필터를 변경해보세요.</p>
        </div>
      ) : (
        events.map((event) => {
          const isLiked = likedEvents.includes(event.id)
          const emoji = categoryEmojis[event.category] || "📌"
          const hasLink = !!(event.orgLink || event.hmpgAddr)
          
          return (
            <div
              key={event.id}
              onClick={() => handleEventClick(event)}
              className={`bg-slate-800 rounded-lg overflow-hidden border border-slate-700 hover:border-purple-500 transition-all ${
                hasLink ? 'cursor-pointer hover:shadow-lg hover:shadow-purple-500/20' : 'cursor-default'
              }`}
            >
              <div className="flex items-start gap-4">
                {/* Event Image (if available) */}
                {event.image && (
                  <div className="w-48 h-48 flex-shrink-0">
                    <img
                      src={event.image}
                      alt={event.title}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Hide image if it fails to load
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                  </div>
                )}

                {/* Event Details */}
                <div className="flex-1 p-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">{emoji}</span>
                        <span className="inline-block px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-xs font-semibold">
                          {event.category}
                        </span>
                      </div>
                      <h3 className="text-xl font-bold text-white mb-2">{event.title}</h3>
                      <p className="text-slate-300 mb-4">{event.description}</p>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex items-center gap-2 text-slate-400">
                          <span>📅</span>
                          {new Date(event.date).toLocaleDateString("ko-KR", {
                            month: "long",
                            day: "numeric",
                            weekday: "long",
                          })}
                        </div>
                        <div className="flex items-center gap-2 text-slate-400">
                          <span>⏰</span>
                          {event.time}
                        </div>
                        <div className="flex items-center gap-2 text-slate-400">
                          <span>📍</span>
                          {event.location}
                        </div>
                        {event.price && (
                          <div className="flex items-center gap-2 text-slate-400">
                            <span>💰</span>
                            {event.price}
                          </div>
                        )}
                      </div>
                      
                      {/* Link indicator */}
                      {hasLink && (
                        <div className="mt-4 flex items-center gap-2 text-xs text-purple-400">
                          <span>🔗</span>
                          <span>클릭하여 홈페이지 방문</span>
                        </div>
                      )}
                    </div>

                    {isLoggedIn && onToggleLike && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation() // Prevent event card click
                          onToggleLike(event.id)
                        }}
                        className="mt-2 text-2xl hover:scale-110 transition-transform flex-shrink-0"
                        title={isLiked ? "찜 취소" : "찜하기"}
                      >
                        {isLiked ? "❤️" : "🤍"}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })
      )}
    </div>
  )
}

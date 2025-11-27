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
  return (
    <div className="space-y-4">
      {events.length === 0 ? (
        <div className="text-center py-12 text-slate-400">
          <p className="text-lg">행사를 찾을 수 없어요.</p>
          <p className="text-sm mt-1">검색어를 입력해보세요.</p>
        </div>
      ) : (
        events.map((event) => {
          const isLiked = likedEvents.includes(event.id)
          return (
            <div
              key={event.id}
              className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-purple-500 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{categoryEmojis[event.category]}</span>
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
                </div>

                {isLoggedIn && onToggleLike && (
                  <button
                    onClick={() => onToggleLike(event.id)}
                    className="mt-2 text-2xl hover:scale-110 transition-transform"
                  >
                    {isLiked ? "❤️" : "🤍"}
                  </button>
                )}
              </div>
            </div>
          )
        })
      )}
    </div>
  )
}

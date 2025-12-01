"use client"

import { useMemo, useState } from "react"
import type { Event } from "@/lib/events-data"

interface EventCalendarProps {
  events: Event[]
  selectedDate: Date | null
  onSelectDate: (date: Date) => void
}

export default function EventCalendar({ events, selectedDate, onSelectDate }: EventCalendarProps) {
  // Start with December 2024 where most events are
  const [currentMonth, setCurrentMonth] = useState(new Date(2024, 11, 1)) // Month is 0-indexed, so 11 = December

  // Count events per date to show multiple event markers
  const eventCountsByDate = useMemo(() => {
    const countMap = new Map<string, number>()
    
    events.forEach((event) => {
      // If event has start and end dates, count for all dates in between
      if (event.startDate && event.endDate) {
        const start = new Date(event.startDate + 'T00:00:00')
        const end = new Date(event.endDate + 'T00:00:00')
        
        // Add to count for each date from start to end
        const current = new Date(start)
        while (current <= end) {
          const dateString = current.toDateString()
          countMap.set(dateString, (countMap.get(dateString) || 0) + 1)
          current.setDate(current.getDate() + 1)
        }
      } else if (event.date) {
        // Fall back to single date
        const dateString = new Date(event.date + 'T00:00:00').toDateString()
        countMap.set(dateString, (countMap.get(dateString) || 0) + 1)
      }
    })
    
    return countMap
  }, [events])

  const daysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
  }

  const firstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay()
  }

  const days = Array.from({ length: daysInMonth(currentMonth) }, (_, i) => i + 1)
  const emptyDays = Array.from({ length: firstDayOfMonth(currentMonth) }, () => null)

  const handlePrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))
  }

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">행사 캘린더</h2>
        <div className="flex gap-2">
          <button onClick={handlePrevMonth} className="text-slate-400 hover:text-white">
            ←
          </button>
          <span className="text-sm text-slate-300 min-w-32 text-center">
            {currentMonth.toLocaleDateString("ko-KR", { month: "long", year: "numeric" })}
          </span>
          <button onClick={handleNextMonth} className="text-slate-400 hover:text-white">
            →
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1 mb-2">
        {["일", "월", "화", "수", "목", "금", "토"].map((day) => (
          <div key={day} className="text-center text-xs text-slate-400 py-2">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {emptyDays.map((_, i) => (
          <div key={`empty-${i}`} className="aspect-square" />
        ))}
        {days.map((day) => {
          const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day)
          const dateString = date.toDateString()
          const eventCount = eventCountsByDate.get(dateString) || 0
          const hasEvent = eventCount > 0
          const isSelected = selectedDate?.toDateString() === dateString

          // Show up to 3 dots for events (if more than 3, still show 3 dots)
          const dotsToShow = Math.min(eventCount, 3)

          return (
            <button
              key={day}
              onClick={() => onSelectDate(date)}
              className={`aspect-square text-sm rounded-lg transition-colors font-medium relative ${
                isSelected ? "text-white" : hasEvent ? "text-white" : "text-slate-300"
              }`}
              style={{
                backgroundColor: isSelected ? "#8B5CF6" : hasEvent ? "#7C3AED" : "transparent",
              }}
              onMouseEnter={(e) => {
                if (!isSelected && !hasEvent) {
                  e.currentTarget.style.backgroundColor = "#8B5CF6"
                }
              }}
              onMouseLeave={(e) => {
                if (!isSelected && !hasEvent) {
                  e.currentTarget.style.backgroundColor = "transparent"
                }
              }}
            >
              <div className="flex flex-col items-center justify-center h-full gap-0.5">
                <span className="mb-0.5">{day}</span>
                {hasEvent && (
                  <div className="flex gap-0.5">
                    {Array.from({ length: dotsToShow }).map((_, i) => (
                      <div
                        key={i}
                        className="w-1 h-1 rounded-full bg-white opacity-90"
                      />
                    ))}
                  </div>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}

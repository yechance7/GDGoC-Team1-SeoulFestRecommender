"use client"

import { useMemo, useState } from "react"
import type { Event } from "@/lib/events-data"

interface EventCalendarProps {
  events: Event[]
  selectedDate: Date | null
  onSelectDate: (date: Date) => void
}

export default function EventCalendar({ events, selectedDate, onSelectDate }: EventCalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date())

  const eventDates = useMemo(() => {
    return events.map((e) => new Date(e.date).toDateString())
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
          const hasEvent = eventDates.includes(dateString)
          const isSelected = selectedDate?.toDateString() === dateString

          return (
            <button
              key={day}
              onClick={() => onSelectDate(date)}
              className={`aspect-square text-sm rounded-lg transition-colors font-medium ${
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
              {day}
            </button>
          )
        })}
      </div>
    </div>
  )
}

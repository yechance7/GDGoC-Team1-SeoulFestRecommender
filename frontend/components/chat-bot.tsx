"use client"

import { useState, useRef, useEffect } from "react"
import type { Event } from "@/lib/events-data"

interface ChatMessage {
  id: string
  text: string
  sender: "user" | "bot"
  timestamp: Date
}

interface ChatBotProps {
  events: Event[]
  onClose?: () => void
}

//check for Festivals queries
export default function ChatBot({ events, onClose }: ChatBotProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      text: "안녕하세요! 저는 서울에서 열리는 행사들을 찾는 것을 도와드릴 수 있어요. 관심 있는 행사, 이번 주의 행사 등을 물어보세요!",
      sender: "bot",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const generateBotResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase()

    if (lowerMessage.includes("festival")) {
      const festivals = events.filter((e) => e.category === "festival")
      if (festivals.length > 0) {
        return `${festivals.length} 행사를 찾았어요! 요즘 핫한 행사들은 ${festivals.map((e) => e.title).join(", ")} 정도에요!`
      }
      return "현재 열리는 행사가 없어요."
    }

    if (lowerMessage.includes("concert")) {
      const concerts = events.filter((e) => e.category === "concert")
      if (concerts.length > 0) {
        return `${concerts.length} 공연을 찾았어요! 요즘 핫한 공연들은 ${concerts.map((e) => e.title).join(", ")} 정도에요!`
      }
      return "현재 열리는 공연이 없어요."
    }

    if (lowerMessage.includes("exhibition") || lowerMessage.includes("exhibit")) {
      const exhibitions = events.filter((e) => e.category === "exhibition")
      if (exhibitions.length > 0) {
        return `${exhibitions.length} 전시회를 찾았어요! 요즘 핫한 전시회들은 ${exhibitions.map((e) => e.title).join(", ")} 정도에요!`
      }
      return "현재 열리는 전시회가 없어요."
    }

    // Check for date queries
    if (lowerMessage.includes("today") || lowerMessage.includes("tonight")) {
      const today = new Date().toDateString()
      const todayEvents = events.filter((e) => new Date(e.date).toDateString() === today)
      if (todayEvents.length > 0) {
        return `오늘의 행사들: ${todayEvents.map((e) => e.title).join(", ")}`
      }
      return "오늘의 행사는 없습니다."
    }

    if (lowerMessage.includes("this week")) {
      const thisWeek = events.filter((e) => {
        const eventDate = new Date(e.date)
        const now = new Date()
        const diff = (eventDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
        return diff >= 0 && diff <= 7
      })
      if (thisWeek.length > 0) {
        return `이번 주의 행사들: ${thisWeek.map((e) => e.title).join(", ")}`
      }
      return "이번 주의 행사는 없습니다."
    }

    // Check for location queries
    if (lowerMessage.includes("gangnam") || lowerMessage.includes("myeongdong") || lowerMessage.includes("hongdae")) {
      const locationQuery = lowerMessage.includes("gangnam")
        ? "Gangnam"
        : lowerMessage.includes("myeongdong")
          ? "Myeongdong"
          : "Hongdae"
      const locationEvents = events.filter((e) => e.location.includes(locationQuery))
      if (locationEvents.length > 0) {
        return `${locationQuery} 지역의 행사들: ${locationEvents.map((e) => e.title).join(", ")}`
      }
      return `${locationQuery} 지역의 행사는 없습니다.`
    }

    // General response
    const randomResponses = [
      "행사를 찾는 것을 도와드릴 수 있어요! 행사의 카테고리, 날짜, 지역 등을 물어보세요!",
      "관심 있는 행사의 카테고리, 날짜, 지역 등을 물어보세요!",
      "오늘의 행사, 이번 주의 행사, 특정 지역의 행사 등을 물어보세요!",
      "핫한 행사를 추천해드릴 수 있어요! 무엇을 도와드릴까요?",
    ]
    return randomResponses[Math.floor(Math.random() * randomResponses.length)]
  }

  const handleSend = async () => {
    if (!input.trim()) return

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: input,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate bot thinking time
    setTimeout(() => {
      const botResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: generateBotResponse(input),
        sender: "bot",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botResponse])
      setIsLoading(false)
    }, 500)
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden flex flex-col h-96">
      <div className="bg-slate-700 px-6 py-4 border-b border-slate-600 flex justify-between items-center">
        <h3 className="text-white font-semibold">행사 챗봇</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors text-lg leading-none"
            aria-label="Close chat"
          >
            ✕
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.sender === "user" ? "bg-purple-500 text-white" : "bg-slate-700 text-slate-100"
              }`}
            >
              <p className="text-sm">{msg.text}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 px-4 py-2 rounded-lg">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-slate-600 p-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about events..."
          className="flex-1 px-4 py-2 bg-slate-700 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
        />
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="px-4 py-2 bg-purple-500 hover:bg-purple-600 disabled:opacity-50 text-white rounded-lg font-semibold transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  )
}

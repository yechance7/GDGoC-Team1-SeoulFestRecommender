"use client"

import { useState, useRef, useEffect, type ChangeEvent, type KeyboardEvent } from "react"
import { chatWithBot } from "@/lib/api" // 💡 Add chatWithBot
import { useAuth } from "@/contexts/auth-context" // 💡 Import useAuth to get username

interface ChatMessage {
  id: string
  text: string
  sender: "user" | "bot"
  timestamp: Date
}

interface ChatBotProps {
  onClose?: () => void
}

// Update the ChatBot component signature
export default function ChatBot({ onClose }: ChatBotProps) {
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
  const { user } = useAuth()
  const username = user?.username || "guest_user" // Use real username or a default

// Scroll logic
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  const handleSend = async () => {
    if (!input.trim()) return
    if (isLoading) return // Prevent multiple sends

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: input,
      sender: "user",
      timestamp: new Date(),
    }

    // Use the current input value before clearing
    const messageToSend = input
    
    setMessages((prev: ChatMessage[]) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // 2. Call the new backend API function
    try {
      const apiResponse = await chatWithBot({
        username: username, // Pass the real or default username
        message: messageToSend,
      })
      
      const botReply: string = apiResponse.reply
    
      // 3. Add bot message
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: botReply,
        sender: "bot",
        timestamp: new Date(),
      }
      setMessages((prev: ChatMessage[]) => [...prev, botMessage])

    } catch (error) {
      console.error("Chatbot API Error:", error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: "죄송합니다. 챗봇과의 통신에 문제가 발생했습니다.",
        sender: "bot",
        timestamp: new Date(),
      }
      setMessages((prev: ChatMessage[]) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden flex flex-col h-150">
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
        {messages.map((msg: ChatMessage) => {
          // Replace literal "\n" in text with actual newline characters for display
          const formattedText = msg.text.replace(/\\n/g, "\n")

          return (
            <div key={msg.id} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-xs px-4 py-2 rounded-lg ${
                  msg.sender === "user" ? "bg-purple-500 text-white" : "bg-slate-700 text-slate-100"
                }`}
              >
                <p className="text-sm whitespace-pre-line">{formattedText}</p>
              </div>
            </div>
          )
        })}
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
          onChange={(e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
          onKeyPress={(e: KeyboardEvent<HTMLInputElement>) => e.key === "Enter" && handleSend()}
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
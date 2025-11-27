export interface Event {
  id: string
  title: string
  description: string
  date: string
  time: string
  location: string
  category: string
  price?: string
  image?: string
}

export interface Category {
  id: string
  name: string
  icon: string
}

export const categories: Category[] = [
  { id: "festival", name: "페스티벌", icon: "🎉" },
  { id: "concert", name: "콘서트", icon: "🎵" },
  { id: "exhibition", name: "전시회", icon: "🎨" },
]

export const categoryEmojis: Record<string, string> = {
  페스티벌: "🎉",
  콘서트: "🎵",
  전시회: "🎨",
}

export const eventsData: Event[] = [
  {
    id: "1",
    title: "서울 페스티벌",
    description: "서울 페스티벌은 어찌고저찌고 행사입니다.",
    date: "2025-11-28",
    time: "18:00 - 22:00",
    location: "청계천, 종로구",
    category: "페스티벌",
    price: "무료",
  },
]

import type { SeoulEventResponse } from './api'

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
  // Additional fields from Seoul Event API
  startDate?: string
  endDate?: string
  dateText?: string
  orgName?: string
  guName?: string
  useTarget?: string
  inquiry?: string
  player?: string
  program?: string
  orgLink?: string
  hmpgAddr?: string
  lat?: number
  lot?: number
}

export interface Category {
  id: string
  name: string
  icon: string
}

// Categories based on the backend's codename field
// These are common Seoul event categories
export const categories: Category[] = [
  { id: "뮤지컬/오페라", name: "뮤지컬/오페라", icon: "🎭" },
  { id: "콘서트", name: "콘서트", icon: "🎵" },
  { id: "전시회", name: "전시회", icon: "🎨" },
  { id: "클래식", name: "클래식", icon: "🎻" },
  { id: "무용", name: "무용", icon: "💃" },
  { id: "페스티벌", name: "페스티벌", icon: "🎉" },
  { id: "기타", name: "기타", icon: "📌" },
]

export const categoryEmojis: Record<string, string> = {
  "뮤지컬/오페라": "🎭",
  "콘서트": "🎵",
  "전시회": "🎨",
  "클래식": "🎻",
  "무용": "💃",
  "페스티벌": "🎉",
  "기타": "📌",
}

/**
 * Convert Seoul Event API response to frontend Event format
 * This function transforms the backend data structure into the format used by the frontend components
 */
export function convertSeoulEventToEvent(seoulEvent: SeoulEventResponse): Event {
  // Use program description, or fall back to etc_desc, or use a default message
  const description = seoulEvent.program || seoulEvent.etc_desc || "행사에 대한 자세한 정보를 확인해보세요.";
  
  // Format location: combine place and gu_name
  const location = [seoulEvent.place, seoulEvent.gu_name].filter(Boolean).join(", ") || "장소 미정";
  
  // Use start_date as the main date, or fall back to date_text
  const date = seoulEvent.start_date || new Date().toISOString().split('T')[0];
  
  // Use pro_time or extract from date_text, or use a default
  const time = seoulEvent.pro_time || "시간 미정";
  
  // Determine category - use codename or default to "기타"
  // Map '전시/미술' to '전시회' to consolidate exhibition categories
  let category = seoulEvent.codename || "기타";
  if (category === "전시/미술") {
    category = "전시회";
  }
  
  // Price info from use_fee or is_free
  const price = seoulEvent.is_free || seoulEvent.use_fee || "가격 정보 없음";
  
  return {
    id: String(seoulEvent.id),
    title: seoulEvent.title,
    description: description.length > 200 ? description.substring(0, 200) + "..." : description,
    date: date,
    time: time,
    location: location,
    category: category,
    price: price,
    image: seoulEvent.main_img || undefined,
    // Additional fields for detailed view
    startDate: seoulEvent.start_date || undefined,
    endDate: seoulEvent.end_date || undefined,
    dateText: seoulEvent.date_text || undefined,
    orgName: seoulEvent.org_name || undefined,
    guName: seoulEvent.gu_name || undefined,
    useTarget: seoulEvent.use_target || undefined,
    inquiry: seoulEvent.inquiry || undefined,
    player: seoulEvent.player || undefined,
    program: seoulEvent.program || undefined,
    orgLink: seoulEvent.org_link || undefined,
    hmpgAddr: seoulEvent.hmpg_addr || undefined,
    lat: seoulEvent.lat || undefined,
    lot: seoulEvent.lot || undefined,
  };
}

/**
 * Convert multiple Seoul Events to Event array
 */
export function convertSeoulEventsToEvents(seoulEvents: SeoulEventResponse[]): Event[] {
  return seoulEvents.map(convertSeoulEventToEvent);
}

// Sample data for initial development (can be removed once API is connected)
export const eventsData: Event[] = [
  {
    id: "1",
    title: "서울 페스티벌",
    description: "서울 페스티벌은 어찌고저찌고 행사입니다.",
    date: "2025-11-28",
    time: "18:00 - 22:00",
    location: "청계천, 종로구",
    category: "축제-전통공연",
    price: "무료",
  },
]

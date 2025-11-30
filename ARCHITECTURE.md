# 🏗️ Seoul Events Architecture - How Everything Works Together

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Seoul Open Data API                          │
│              (Seoul city's official event data)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Fetches events every 6 hours
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    WORKER (Python)                               │
│          app/worker/collect_event_worker.py                      │
│                                                                   │
│  - Automatically runs every 6 hours                              │
│  - Fetches new Seoul events                                      │
│  - Cleans and processes data                                     │
│  - Saves to database                                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Stores events
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                         │
│                    Table: seoul_events                           │
│                                                                   │
│  Stores event information:                                       │
│  - id, title, codename (category)                                │
│  - start_date, end_date, place                                   │
│  - description, image, price, etc.                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Provides data
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND API (FastAPI)                          │
│                   app/api/seoul_event.py                         │
│                                                                   │
│  Endpoints:                                                      │
│  GET /api/v1/seoul-events                                        │
│    - Returns list of events                                      │
│    - Supports filtering:                                         │
│      • codename (category)                                       │
│      • gu_name (district)                                        │
│      • search (keyword)                                          │
│      • date, start_date, end_date                                │
│      • is_free (free/paid)                                       │
│                                                                   │
│  GET /api/v1/seoul-events/{id}                                   │
│    - Returns single event details                                │
│                                                                   │
│  POST /api/v1/seoul-events/{id}/like                             │
│    - Like an event (requires login)                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ API calls
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND (Next.js)                             │
│                   Port: 3000                                     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  lib/api.ts - API Client                                │    │
│  │  - getSeoulEvents(filters)                              │    │
│  │  - likeSeoulEvent(id)                                   │    │
│  │  - etc.                                                 │    │
│  └─────────────────────┬───────────────────────────────────┘    │
│                        │                                         │
│                        ↓                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  lib/events-data.ts - Data Conversion                   │    │
│  │  - Converts backend format to frontend format           │    │
│  │  - Categories and emoji mappings                        │    │
│  └─────────────────────┬───────────────────────────────────┘    │
│                        │                                         │
│                        ↓                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  app/page.tsx - Main Page                               │    │
│  │  - Fetches events on load                               │    │
│  │  - Manages filters (category, search, date)             │    │
│  │  - Shows loading/error states                           │    │
│  └─────────────────────┬───────────────────────────────────┘    │
│                        │                                         │
│                        ↓                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  components/event-list.tsx - Display Events             │    │
│  │  - Renders event cards                                  │    │
│  │  - Shows images, details, like buttons                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
                    👤 USER'S BROWSER
                    Sees beautiful events website!
```

## 🔄 Data Flow Example: Viewing Events

When a user visits the website:

```
1. User opens browser → http://localhost:3000

2. Frontend (page.tsx) loads → Calls getSeoulEvents()

3. API call → GET /api/v1/seoul-events?limit=500

4. Next.js proxy → Forwards to http://localhost:8000/api/v1/seoul-events

5. Backend API → Queries PostgreSQL database

6. Database → Returns event records

7. Backend → Converts to JSON and sends response

8. Frontend → Receives SeoulEventResponse[] array

9. Data conversion → convertSeoulEventsToEvents() 
   Transforms backend format to frontend Event format

10. React renders → EventList component displays events

11. User sees → Beautiful event cards with categories!
```

## 🎯 Filtering Example: Category Selection

When user clicks "콘서트" category:

```
1. User clicks → "콘서트" button

2. React state → setSelectedCategory("콘서트")

3. JavaScript filter → 
   events.filter(event => event.category === "콘서트")

4. Re-render → Only concerts show in the list

5. User sees → Only 콘서트 events!
```

## 🔍 Search Example

When user types in search box:

```
1. User types → "서울" in search box

2. React state → setSearchQuery("서울")

3. JavaScript filter →
   events.filter(event => 
     event.title.includes("서울") ||
     event.description.includes("서울") ||
     event.location.includes("서울")
   )

4. Re-render → Only matching events show

5. User sees → Events related to "서울"!
```

## 🗂️ Category System

### Backend (Database)
Events are stored with `codename` field:
```
codename = "뮤지컬/오페라"
codename = "콘서트"
codename = "전시회"
codename = "클래식"
codename = "무용"
codename = "페스티벌"
```

### Frontend (Display)
Categories are defined in `events-data.ts`:
```typescript
categories = [
  { id: "뮤지컬/오페라", name: "뮤지컬/오페라", icon: "🎭" },
  { id: "콘서트", name: "콘서트", icon: "🎵" },
  { id: "전시회", name: "전시회", icon: "🖼️" },
  ...
]
```

### Mapping
When converting:
```typescript
event.category = seoulEvent.codename
// "콘서트" → "콘서트" 🎵
// "뮤지컬/오페라" → "뮤지컬/오페라" 🎭
```

## 🏃 Services Running

### Docker Containers (docker-compose.yml)

1. **postgres_db** (Port 5432)
   - PostgreSQL database
   - Stores all event data
   - Persistent storage

2. **fastapi_backend** (Port 8000)
   - FastAPI application
   - REST API endpoints
   - Connects frontend to database

3. **seoul_event_worker**
   - Background worker
   - Fetches data every 6 hours
   - Updates database automatically

### Frontend Process

4. **Next.js dev server** (Port 3000)
   - React application
   - Serves web pages
   - Proxies API calls to backend

## 📁 Key Files

### Backend
```
backend/
├── app/
│   ├── main.py                  # FastAPI app setup
│   ├── api/
│   │   └── seoul_event.py       # Event API endpoints
│   ├── entity/
│   │   └── seoul_event_entity.py # Database model
│   ├── models/
│   │   └── seoul_event.py       # API request/response models
│   ├── repository/
│   │   └── seoul_event_repo.py  # Database queries
│   └── worker/
│       └── collect_event_worker.py # Data collection
```

### Frontend
```
frontend/
├── lib/
│   ├── api.ts                   # Backend API client
│   └── events-data.ts           # Data types & conversion
├── app/
│   └── page.tsx                 # Main page
└── components/
    └── event-list.tsx           # Event display
```

## 🔐 Authentication Flow (For Likes)

```
1. User logs in → Receives JWT token

2. Token stored → localStorage

3. User likes event → 
   POST /api/v1/seoul-events/{id}/like
   Header: Authorization: Bearer {token}

4. Backend verifies → Token valid?

5. If valid → Save like to database

6. Response → Success!

7. Frontend updates → Heart icon turns red ❤️
```

## 🎨 UI Components Hierarchy

```
app/page.tsx (Main Page)
├── Header (search, login)
├── LoginModal (if not logged in)
└── Content
    ├── Sidebar
    │   ├── EventCalendar
    │   └── Category Filter
    │       ├── "모든 행사" button
    │       └── Category buttons (뮤지컬/오페라, 콘서트, etc.)
    └── Main Content
        ├── Event count & filters display
        └── EventList
            └── Event cards (repeated)
                ├── Image (if available)
                ├── Category badge
                ├── Title
                ├── Description
                ├── Details (date, time, location, price)
                └── Like button (if logged in)
```

## 🚀 Performance Optimizations

1. **Single API Call**
   - Fetch all events once (up to 500)
   - Filter on client side (fast!)
   - No reload needed for filtering

2. **Next.js Proxy**
   - Avoids CORS issues
   - Same-origin requests
   - Better security

3. **React State Management**
   - Efficient re-renders
   - Only updates what changes
   - Smooth user experience

4. **Lazy Image Loading**
   - Images load as needed
   - Fallback for broken images
   - Doesn't block page load

## 📈 Future Scalability

When you have more events:

1. **Pagination**
   - Load events in chunks
   - Use skip/limit parameters
   - Infinite scroll

2. **Server-Side Filtering**
   - Filter in backend
   - Reduce data transfer
   - Faster for large datasets

3. **Caching**
   - Cache frequent queries
   - Redis for faster access
   - Reduce database load

4. **Search Optimization**
   - Full-text search in PostgreSQL
   - Elasticsearch for advanced search
   - Better performance

## 🎓 For Beginners: Simple Explanation

Think of it like a restaurant:

- **Database (PostgreSQL)**: The kitchen where food (data) is stored
- **Backend (FastAPI)**: The waiter who takes orders and brings food
- **Frontend (Next.js)**: The menu and dining area where customers see and order
- **Worker**: The chef who goes shopping and restocks the kitchen
- **User**: You! The customer who enjoys the meal (website)

When you click a category, it's like telling the waiter "I only want Italian food" - the waiter quickly sorts through the menu and shows you only Italian dishes!

---

This architecture allows your Seoul events website to show real data, filter by themes, search, and provide a great user experience! 🎉


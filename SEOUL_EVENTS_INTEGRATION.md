# Seoul Events Backend-Frontend Integration Guide

This document explains how the Seoul events database from the backend has been integrated with the frontend to display events on the website according to their themes.

## 🎯 What Was Done

### 1. **Backend API Connection** (`frontend/lib/api.ts`)

Added comprehensive API functions to interact with the Seoul events backend:

- `getSeoulEvents(filters?)` - Fetch all Seoul events with optional filters
- `getSeoulEvent(eventId)` - Fetch a single event by ID
- `getCalendarEventCounts(year, month)` - Get event counts for calendar view
- `likeSeoulEvent(eventId, token)` - Like an event (requires authentication)
- `unlikeSeoulEvent(eventId, token)` - Unlike an event
- `checkSeoulEventLiked(eventId, token)` - Check if an event is liked

**Key Features:**
- Supports filtering by category (`codename`), district (`gu_name`), search query, dates, and free/paid status
- Proper TypeScript types for all API requests and responses
- Error handling for network issues

### 2. **Data Type Definitions** (`frontend/lib/events-data.ts`)

Updated the event types and categories to match the backend structure:

**New Categories Based on Backend Data:**
- 뮤지컬/오페라 🎭
- 콘서트 🎵
- 전시/미술 🎨
- 클래식 🎻
- 무용 💃
- 국악 🥁
- 연극 🎪
- 영화 🎬
- 축제-전통공연 🎉
- 기타 📌

**Data Conversion Functions:**
- `convertSeoulEventToEvent()` - Converts backend API response to frontend Event format
- `convertSeoulEventsToEvents()` - Converts array of backend events

This ensures that backend data (with fields like `codename`, `gu_name`, `start_date`, etc.) is properly transformed into the format expected by frontend components.

### 3. **Main Page Updates** (`frontend/app/page.tsx`)

The main page now:

1. **Fetches real data** from the backend on page load
2. **Shows loading state** with a spinner while data is being fetched
3. **Displays error messages** if the backend is unavailable
4. **Filters events** by category (theme), search query, and selected date
5. **Shows event count** and active filters
6. **Supports all categories** from the backend's `codename` field

**Key Changes:**
- Added `events` state to store fetched data
- Added `loading` and `error` states for better UX
- `useEffect` hook to fetch data on component mount
- Updated filtering logic to work with real data
- All components now use real data instead of mock data

### 4. **Enhanced Event Display** (`frontend/components/event-list.tsx`)

Improved the event list component to:

- **Display event images** (if available from backend's `main_img` field)
- **Handle missing images** gracefully (hide if failed to load)
- **Show proper category emojis** for all backend categories
- **Better layout** with image on the side and details on the right

### 5. **Image Support** (`frontend/next.config.ts`)

Added configuration to allow loading images from external sources:

```typescript
images: {
  remotePatterns: [
    { protocol: 'https', hostname: '**' },
    { protocol: 'http', hostname: '**' },
  ],
}
```

This allows the frontend to display event images from Seoul event data sources.

## 🚀 How to Use

### Starting the Application

1. **Start the backend** (database + API):
   ```bash
   docker-compose up
   ```
   This will start:
   - PostgreSQL database
   - FastAPI backend (port 8000)
   - Seoul event worker (collects data from Seoul Open API)

2. **Start the frontend** (in a separate terminal):
   ```bash
   cd frontend
   pnpm dev
   ```
   This will start the Next.js frontend on port 3000

3. **Visit the website**:
   - Open http://localhost:3000 in your browser
   - You should see all Seoul events loaded from the backend

### How the Data Flow Works

```
Seoul Open API
      ↓
   Worker (collects data periodically)
      ↓
PostgreSQL Database
      ↓
FastAPI Backend (/api/v1/seoul-events)
      ↓
Next.js Frontend (displays events)
      ↓
   Browser
```

### Filtering Events

The frontend now supports filtering by:

1. **Category/Theme**: Click any category button in the sidebar
   - The categories match the backend's `codename` field
   - Examples: 뮤지컬/오페라, 콘서트, 전시/미술, etc.

2. **Search**: Type in the search bar to filter by:
   - Event title
   - Event description
   - Location

3. **Date**: Click on a date in the calendar to see events on that specific day

4. **Combined Filters**: You can use multiple filters at once

## 📊 Backend API Details

### Main Endpoint

**GET** `/api/v1/seoul-events`

**Query Parameters:**
- `skip` (default: 0) - Pagination offset
- `limit` (default: 100, max: 500) - Number of events to fetch
- `codename` - Filter by category (e.g., "콘서트", "뮤지컬/오페라")
- `gu_name` - Filter by district (e.g., "송파구", "강남구")
- `search` - Search in title, place, and organization name
- `date` - Filter events happening on a specific date (YYYY-MM-DD)
- `start_date` - Filter events starting from this date
- `end_date` - Filter events ending before this date
- `is_free` - Filter by free/paid ("무료"/"유료")

**Example:**
```
GET /api/v1/seoul-events?codename=콘서트&limit=50
```

### Backend Data Structure

Each Seoul event has these fields:
- `id` - Unique event ID
- `title` - Event title
- `codename` - Category/theme (used for filtering)
- `gu_name` - District name
- `place` - Venue location
- `start_date` / `end_date` - Event dates
- `program` - Event description
- `main_img` - Event image URL
- `is_free` - Free or paid event
- `use_fee` - Price information
- `pro_time` - Event time
- And many more fields...

## 🔧 Technical Implementation

### Type Safety

All API calls are fully typed with TypeScript:

```typescript
interface SeoulEventResponse {
  id: number;
  codename: string | null;
  title: string;
  // ... all backend fields
}

interface Event {
  id: string;
  title: string;
  category: string;  // Converted from codename
  // ... frontend fields
}
```

### Error Handling

The application handles various error scenarios:

1. **Backend not running**: Shows error message with retry button
2. **Network issues**: Displays helpful error messages
3. **Missing images**: Hides broken images gracefully
4. **No events found**: Shows friendly "no results" message

### Performance

- Events are fetched once on page load (can fetch up to 500 events)
- Filtering happens on the client side (fast)
- Direct connection to backend with CORS enabled
- Images are lazy loaded by the browser

## 🎨 Category Mapping

The backend uses `codename` field for event categories. Here's how they map to the frontend:

| Backend codename | Frontend Display | Emoji |
|-----------------|------------------|-------|
| 뮤지컬/오페라 | 뮤지컬/오페라 | 🎭 |
| 콘서트 | 콘서트 | 🎵 |
| 전시/미술 | 전시/미술 | 🎨 |
| 클래식 | 클래식 | 🎻 |
| 무용 | 무용 | 💃 |
| 국악 | 국악 | 🥁 |
| 연극 | 연극 | 🎪 |
| 영화 | 영화 | 🎬 |
| 축제-전통공연 | 축제-전통공연 | 🎉 |
| (any other) | 기타 | 📌 |

## 🐛 Troubleshooting

### "Cannot connect to the server" Error

**Problem**: Frontend can't reach the backend

**Solution**:
1. Make sure Docker containers are running: `docker-compose up`
2. Check if backend is accessible: http://localhost:8000
3. Check backend logs: `docker logs fastapi_backend`
4. Restart backend if needed: `docker-compose restart backend`

### No Events Displayed

**Problem**: Events list is empty

**Solution**:
1. Wait for the worker to collect events (runs every 6 hours)
2. Manually trigger data collection:
   ```bash
   curl -X POST http://localhost:8000/sync-seoul-events
   ```
3. Check worker logs: `docker logs seoul_event_worker`

### Images Not Loading

**Problem**: Event images show broken or don't load

**Solution**:
- This is normal - some backend image URLs might be invalid or expired
- The frontend handles this gracefully by hiding broken images
- Images are optional and don't affect the core functionality

### CORS Errors

**Problem**: Browser shows CORS errors in console

**Solution**:
1. Restart the backend: `docker-compose restart backend`
2. Verify CORS settings in `backend/app/main.py`
3. Make sure you're accessing from `http://localhost:3000`

## 📝 Summary

**What Changed:**
- ✅ Added API client for Seoul events backend
- ✅ Created data conversion functions
- ✅ Updated main page to fetch real data
- ✅ Added loading and error states
- ✅ Enhanced event display with images
- ✅ Updated categories to match backend
- ✅ Configured image loading from external sources
- ✅ Made event cards clickable to visit homepages

**Result:**
The frontend now displays real Seoul events from the database, filtered by their themes (categories), with full search and date filtering capabilities!

## 🎉 Features

Users can now:
1. See all Seoul events from the database
2. Filter events by theme/category
3. Search events by title, description, or location
4. Filter events by date using the calendar
5. See event images (when available)
6. See detailed event information
7. Click on events to visit their homepage
8. Like/unlike events (when logged in)

All data is live from the backend database, which is automatically updated by the worker service! 🚀


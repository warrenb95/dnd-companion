# Player Availability Selection Flow

## Overview

Players click time slot buttons to indicate when they're available. HTMX handles the interactivity without page reloads.

## Key Components

### Models (campaigns/models/sessions.py)

- **SessionSchedule**: Stores the date range, time slots configuration, and shareable token
- **PlayerAvailability**: Stores each player's selections in `availability_data` JSON field: `{date: [time_slots]}`

### Templates

**player_availability.html** (campaigns/templates/sessions/player_availability.html:264)

- Main page that loops through dates and includes `_day_card.html` for each date
- Contains player info form (name, email, character name)
- Auto-saves player info on blur using HTMX

**\_day_card.html** (campaigns/templates/sessions/components/\_day_card.html)

- Displays one day with its time slot buttons
- Each button has HTMX attributes for toggling

**\_time_slot_button.html** (campaigns/templates/sessions/components/\_time_slot_button.html)

- Single button component returned after toggle
- Shows selected/unselected state via CSS class

### HTMX Flow

**Time Slot Toggle** (campaigns/htmx_views.py:434-487)

1. Player clicks time slot button
2. HTMX POSTs to `toggle_time_slot` with:
   - `date`: Date string (YYYY-MM-DD)
   - `time_slot`: Time label (e.g., "19:00 - 22:00")
   - `email`: Player's email
   - `player_name`: Player's name
3. View logic:
   - Gets/creates `PlayerAvailability` by email
   - Retrieves existing selections for that date from JSON
   - Toggles the time slot (add if not present, remove if present)
   - Saves updated availability
4. Returns updated button HTML with toggled selected state
5. HTMX swaps button with `outerHTML` - replaces entire button

### URL Routes (campaigns/urls.py:439-443)

```python
path("schedule/<uuid:token>/toggle-slot/", toggle_time_slot, name="toggle_time_slot")
path("schedule/<uuid:token>/save-info/", save_player_info, name="save_player_info")
```

## Data Storage

Player selections stored in `PlayerAvailability.availability_data` as:

```json
{
  "2025-11-15": ["19:00 - 22:00", "20:00 - 23:00"],
  "2025-11-16": ["12:00 - 15:00"]
}
```

## Key Features

- No login required (uses shareable token)
- Real-time toggle feedback via HTMX
- Auto-saves player info on field blur
- Multiple time slots can be selected per day
- Visual feedback with CSS classes (`selected`)

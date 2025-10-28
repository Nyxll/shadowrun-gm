# UI Reference - Web Interface

This document describes the web-based user interface for the Shadowrun GM system.

## Overview

The web UI (`www/`) provides:
- Real-time chat interface with Grok AI GM
- Character selection and management
- Character sheet viewer with detailed stats
- WebSocket-based streaming responses
- Theme customization (Tron, Matrix, Cyberpunk, Classic)
- Error handling with trace IDs for debugging

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     index.html                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Chat Area   │  │  Character   │  │   Character  │ │
│  │              │  │  Selection   │  │    Sheet     │ │
│  │  (Messages)  │  │              │  │    Modal     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
           │                    │                  │
           ▼                    ▼                  ▼
    ┌─────────────┐    ┌──────────────────┐  ┌──────────────────┐
    │   app.js    │    │ character-sheet- │  │ error-handler.js │
    │             │    │   renderer.js    │  │                  │
    │ (WebSocket) │    │                  │  │  (Trace IDs)     │
    └─────────────┘    └──────────────────┘  └──────────────────┘
           │
           ▼
    ┌─────────────────────────────────┐
    │   game-server.py (WebSocket)    │
    └─────────────────────────────────┘
```

## File Structure

```
www/
├── index.html                    # Main HTML structure
├── app.js                        # WebSocket client & UI logic
├── character-sheet-renderer.js   # Character sheet rendering
├── error-handler.js              # Error handling with trace IDs
├── character-sheet.css           # Character sheet styles
└── themes.css                    # Theme definitions
```

## Key Components

### 1. Main Interface (index.html)

**Layout Sections:**
- **Header** - Title, session ID, connection status, theme selector
- **Sidebar** - Character selection and management
- **Chat Area** - Message history and input
- **Status Bar** - Current operation status
- **Modal** - Character sheet viewer

**Key Elements:**
```html
<div id="messages">              <!-- Chat messages -->
<input id="message-input">       <!-- User input -->
<select id="character-select">   <!-- Character dropdown -->
<div id="character-list">        <!-- Active characters -->
<div id="character-sheet-modal"> <!-- Sheet viewer -->
```

### 2. WebSocket Client (app.js)

**Connection Management:**
```javascript
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/game/${sessionId}`;
ws = new WebSocket(wsUrl);
```

**Message Handling:**
- `system` - System notifications
- `narrative` - Streamed GM responses
- `processing` - Status updates
- `tool_execution` - Tool call notifications
- `tool_result` - Tool execution results
- `complete` - Response completion
- `error` - Error messages
- `session_info` - Session state updates

**Key Functions:**

**sendMessage()**
```javascript
function sendMessage() {
    const message = messageInput.value.trim();
    currentTraceId = errorHandler.generateTraceId();
    
    ws.send(JSON.stringify({
        trace_id: currentTraceId,
        type: 'chat',
        message: message
    }));
}
```

**addCharacter()**
```javascript
function addCharacter() {
    const characterName = characterSelect.value;
    
    ws.send(JSON.stringify({
        type: 'add_character',
        character: characterName
    }));
}
```

**viewCharacterSheet()**
```javascript
async function viewCharacterSheet(characterName) {
    const traceId = errorHandler.generateTraceId();
    
    const response = await fetch(
        `/api/character/${encodeURIComponent(characterName)}`,
        { headers: { 'X-Trace-ID': traceId } }
    );
    
    const character = await response.json();
    displayCharacterSheet(character);
}
```

### 3. Character Sheet Renderer (character-sheet-renderer.js)

**CharacterSheetRenderer Class**

Renders complete character sheets with:
- Basic info (name, archetype, metatype)
- Attributes (base and augmented)
- Derived stats (initiative, combat pool, essence)
- Skills (active, knowledge, language)
- Cyberware with essence costs
- Bioware with body index costs
- Weapons with stats
- Armor and equipment
- Vehicles and cyberdecks
- Contacts, edges, flaws
- Spirits and spells

**Key Methods:**

**render(character)**
```javascript
render(character) {
    return `
        ${this.renderHeader(character)}
        ${this.renderAttributes(character)}
        ${this.renderSkills(character)}
        ${this.renderCyberware(character)}
        ${this.renderGear(character)}
        ...
    `;
}
```

**Collapsible Sections:**
```javascript
<div class="section-header" onclick="toggleSection(this)">
    <span class="section-toggle">▼</span>
    <h3>Section Title</h3>
</div>
<div class="section-content">
    <!-- Content -->
</div>
```

### 4. Error Handler (error-handler.js)

**ErrorHandler Class**

Provides structured error handling with trace IDs:

**generateTraceId()**
```javascript
generateTraceId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
```

**handleServerError(errorData, traceId)**
```javascript
handleServerError(errorData, traceId) {
    if (errorData.error) {
        return {
            code: errorData.error.code,
            type: errorData.error.type,
            message: errorData.error.message,
            traceId: errorData.error.trace_id || traceId,
            details: errorData.error.details
        };
    }
    // Fallback for non-standard errors
}
```

**handleFetchError(error, endpoint, traceId)**
```javascript
handleFetchError(error, endpoint, traceId) {
    console.error(`[Trace: ${traceId}] Fetch error at ${endpoint}:`, error);
    
    return {
        code: 9001,
        type: 'FETCH_ERROR',
        message: error.message,
        traceId: traceId,
        endpoint: endpoint
    };
}
```

**Usage Example:**
```javascript
try {
    const response = await fetch('/api/character/Platinum', {
        headers: { 'X-Trace-ID': traceId }
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        const error = errorHandler.handleServerError(errorData, traceId);
        throw new Error(error.message);
    }
} catch (error) {
    const err = errorHandler.handleFetchError(error, endpoint, traceId);
    console.error(`Error [${err.traceId}]:`, err.message);
}
```

## Theme System

### Available Themes

**1. Tron (Default)**
- Cyan/blue neon aesthetic
- Dark background with glowing accents
- Inspired by Tron Legacy

**2. Matrix**
- Green terminal aesthetic
- Black background with green text
- Classic hacker/cyberpunk look

**3. Cyberpunk**
- Pink/purple neon aesthetic
- Dark background with vibrant accents
- Cyberpunk 2077 inspired

**4. Classic**
- Traditional RPG aesthetic
- Parchment-style background
- Brown/tan color scheme

### Theme Implementation

**HTML:**
```html
<div class="theme-selector">
    <button id="theme-toggle">🎨 Theme</button>
    <div id="theme-dropdown" class="theme-dropdown">
        <div class="theme-option" data-theme="tron">Tron</div>
        <div class="theme-option" data-theme="matrix">Matrix</div>
        <div class="theme-option" data-theme="cyberpunk">Cyberpunk</div>
        <div class="theme-option" data-theme="classic">Classic</div>
    </div>
</div>
```

**JavaScript:**
```javascript
const savedTheme = localStorage.getItem('shadowrun-theme') || 'tron';
document.body.setAttribute('data-theme', savedTheme);

themeOptions.forEach(option => {
    option.addEventListener('click', () => {
        const theme = option.getAttribute('data-theme');
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('shadowrun-theme', theme);
    });
});
```

**CSS:**
```css
[data-theme="tron"] {
    --primary-color: #00ffff;
    --secondary-color: #0080ff;
    --background-color: #0a0e27;
    --text-color: #e0e0e0;
}

[data-theme="matrix"] {
    --primary-color: #00ff00;
    --secondary-color: #008000;
    --background-color: #000000;
    --text-color: #00ff00;
}
```

## User Workflows

### 1. Starting a Game Session

```
1. Page loads → WebSocket connects
2. Characters preload from database
3. User selects character from dropdown
4. Click "Add Character" → Character added to session
5. Repeat for additional characters
6. Start chatting with GM
```

### 2. Viewing Character Sheet

```
1. Click character name in active list
   OR
2. Select from dropdown → Click "View Sheet"
   ↓
3. Fetch character data with trace ID
4. Render character sheet in modal
5. View stats, cyberware, gear, etc.
6. Click outside or close button to dismiss
```

### 3. Chatting with GM

```
1. Type message in input field
2. Press Enter or click Send
3. Message appears in chat
4. Status shows "GM is thinking..."
5. GM response streams in real-time
6. Tool executions shown (if any)
7. Final response completes
8. Status returns to "Ready"
```

### 4. Handling Errors

```
1. Error occurs (network, server, etc.)
2. Trace ID generated/extracted
3. Error logged to console with trace ID
4. User-friendly message shown in chat
5. Trace ID included for debugging
6. User can report issue with trace ID
```

## Message Types

### User Messages
```html
<div class="message user">
    I want to shoot the ganger
</div>
```

### GM Responses (Narrative)
```html
<div class="message assistant">
    You take aim with your Ares Predator...
</div>
```

### System Messages
```html
<div class="message system">
    Connected to game server
</div>
```

### Tool Results
```html
<div class="message tool">
    [calculate_ranged_attack] { "final_tn": 4, ... }
</div>
```

## Character Sheet Sections

### Header
- Character name and street name
- Archetype and metatype
- Physical description

### Attributes
- Base and augmented values
- Color-coded (augmented = green)
- Essence and Magic ratings

### Derived Stats
- Initiative
- Combat Pool
- Body Index (if applicable)
- Karma Pool

### Skills
- Active skills (combat, technical, etc.)
- Knowledge skills
- Language skills
- Specializations shown

### Augmentations
- **Cyberware** - With essence costs and effects
- **Bioware** - With body index costs and effects
- Parent-child relationships preserved
- Effects listed (attribute bonuses, vision, etc.)

### Gear
- **Weapons** - With stats (damage, conceal, etc.)
- **Armor** - With ratings and modifications
- **Equipment** - General gear and quantities

### Vehicles & Decks
- Vehicles with stats
- Cyberdecks with MPCP, programs, etc.

### Social
- Contacts with connection/loyalty
- Edges and flaws
- Background notes

### Magic
- **Totem Information** - Totem name with favored/opposed categories
- **Spells** - Grouped by category (Combat, Health, Manipulation, etc.)
  - Spell type (mana/physical)
  - Target type and duration
  - Drain modifiers
  - Descriptions
- **Foci** - Magical foci with bonuses
  - Force ratings
  - Spell category or specific spell
  - Bonus dice and TN modifiers
  - Bonding status
- **Bound Spirits** - With services and special abilities

## Styling

### CSS Variables

Each theme defines:
```css
--primary-color        /* Main accent color */
--secondary-color      /* Secondary accent */
--background-color     /* Main background */
--text-color          /* Primary text */
--border-color        /* Borders and dividers */
--hover-color         /* Hover states */
--input-bg            /* Input backgrounds */
--message-bg          /* Message backgrounds */
```

### Responsive Design

**Breakpoints:**
- Desktop: > 768px (sidebar + chat)
- Mobile: ≤ 768px (stacked layout)

**Mobile Optimizations:**
- Collapsible sidebar
- Full-width chat
- Touch-friendly buttons
- Simplified character sheets

## Performance Considerations

### Message History Limit

Client-side message limit (optional):
```javascript
const MAX_MESSAGES = 100;
if (messagesDiv.children.length > MAX_MESSAGES) {
    messagesDiv.removeChild(messagesDiv.firstChild);
}
```

### Streaming Optimization

Messages stream character-by-character for real-time feel:
```javascript
case 'narrative':
    if (!currentMessageDiv) {
        currentMessageDiv = createMessage('assistant', '');
    }
    currentMessageDiv.textContent += data.content;
    scrollToBottom();
    break;
```

### Character Data Caching

Characters loaded once on page load:
```javascript
async function preloadCharacters() {
    await loadAvailableCharacters();
    // Cached in availableCharacters array
}
```

## Accessibility

### Keyboard Navigation
- Enter key sends messages
- Tab navigation through controls
- Escape closes modals

### Screen Reader Support
- Semantic HTML structure
- ARIA labels on interactive elements
- Status announcements

### Color Contrast
- All themes meet WCAG AA standards
- High contrast text on backgrounds
- Clear visual hierarchy

## Browser Compatibility

**Supported Browsers:**
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

**Required Features:**
- WebSocket support
- ES6+ JavaScript
- CSS Grid and Flexbox
- LocalStorage

## Development

### Local Testing

```bash
# Start game server
python game-server.py

# Open in browser
http://localhost:8001
```

### Debug Mode

Enable console logging:
```javascript
const DEBUG = true;

if (DEBUG) {
    console.log('[Trace:', traceId, '] Message:', data);
}
```

### Testing WebSocket

```javascript
// Manual WebSocket test
const ws = new WebSocket('ws://localhost:8001/game/test');

ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);

ws.send(JSON.stringify({
    type: 'chat',
    message: 'Test message'
}));
```

## Future Enhancements

### Planned Features

1. **Dice Roller UI** - Visual dice rolling interface
2. **Combat Tracker** - Initiative and turn management
3. **Map Integration** - Tactical map display
4. **Voice Chat** - WebR

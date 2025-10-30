// WebSocket connection
let ws = null;
let sessionId = 'session_' + Date.now();
let currentTraceId = null;

// DOM elements
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const sessionIdSpan = document.getElementById('session-id');
const connectionStatus = document.getElementById('connection-status');
const characterList = document.getElementById('character-list');
const characterSelect = document.getElementById('character-select');
const addCharacterButton = document.getElementById('add-character-button');
const viewSheetButton = document.getElementById('view-sheet-button');
const createScenarioButton = document.getElementById('create-scenario-button');
const statusDisplay = document.getElementById('status-display');
const characterSheetModal = document.getElementById('character-sheet-modal');
const modalCloseButton = document.getElementById('modal-close-button');
const characterSheetContent = document.getElementById('character-sheet-content');
const toolCallLog = document.getElementById('tool-call-log');
const clearLogButton = document.getElementById('clear-log-button');

// Current message being streamed
let currentMessageDiv = null;
let characters = [];
let availableCharacters = [];
let scenarioStarted = false;

// Tool call tracking
let toolCalls = [];
let requestStartTime = null;

// Connect to WebSocket
function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/game/${sessionId}`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        connectionStatus.textContent = 'Connected';
        connectionStatus.style.color = '#00ff00';
        messageInput.disabled = false;
        sendButton.disabled = false;
        sessionIdSpan.textContent = sessionId;
        addMessage('system', 'Connected to game server. Select your characters and start playing!');
    };
    
    ws.onclose = () => {
        connectionStatus.textContent = 'Disconnected';
        connectionStatus.style.color = '#ff0000';
        messageInput.disabled = true;
        sendButton.disabled = true;
        addMessage('system', 'Disconnected from server. Refresh to reconnect.');
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addMessage('system', 'Connection error occurred');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
}

// Handle incoming messages
function handleMessage(data) {
    switch (data.type) {
        case 'system':
            addMessage('system', data.content);
            break;
        
        case 'narrative':
            // Stream narrative content
            if (!currentMessageDiv) {
                currentMessageDiv = createMessage('assistant', '');
            }
            currentMessageDiv.textContent += data.content;
            scrollToBottom();
            break;
        
        case 'processing':
            setStatus(data.content);
            break;
        
        case 'telemetry':
            // Handle telemetry events
            logTelemetryEvent(data.event, data.data, data.timestamp);
            break;
        
        case 'tool_execution':
            setStatus(`Executing tools: ${data.tools.join(', ')}`);
            break;
        
        case 'tool_call':
            // Tool call tracking (already handled by telemetry)
            const index = logToolCall(data.tool, data.arguments || {}, Date.now());
            if (!window.pendingToolCalls) window.pendingToolCalls = {};
            window.pendingToolCalls[data.tool] = index;
            break;
        
        case 'tool_result':
            addMessage('tool', `[${data.tool}] ${JSON.stringify(data.result, null, 2)}`);
            if (window.pendingToolCalls && window.pendingToolCalls[data.tool] !== undefined) {
                completeToolCall(window.pendingToolCalls[data.tool], data.result, true);
                delete window.pendingToolCalls[data.tool];
            }
            break;
        
        case 'complete':
            currentMessageDiv = null;
            setStatus('Ready');
            break;
        
        case 'error':
            addMessage('system', `ERROR: ${data.content}`);
            currentMessageDiv = null;
            setStatus('Error occurred');
            break;
        
        case 'session_info':
            characters = data.characters;
            updateCharacterList();
            break;
    }
}

// Add message to chat
function addMessage(type, content) {
    const messageDiv = createMessage(type, content);
    scrollToBottom();
}

// Create message element
function createMessage(type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = content;
    messagesDiv.appendChild(messageDiv);
    return messageDiv;
}

// Scroll to bottom of messages
function scrollToBottom() {
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Set status display
function setStatus(text) {
    statusDisplay.textContent = text;
}

// Send message
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !ws || ws.readyState !== WebSocket.OPEN) {
        return;
    }
    
    // Generate trace ID for this request
    currentTraceId = errorHandler.generateTraceId();
    
    // Add user message to chat
    addMessage('user', message);
    
    // Send to server with trace ID
    ws.send(JSON.stringify({
        trace_id: currentTraceId,
        type: 'chat',
        message: message
    }));
    
    console.log(`[Trace: ${currentTraceId}] Sent message:`, message);
    
    // Clear input
    messageInput.value = '';
    setStatus('GM is thinking...');
}

// Add character
function addCharacter() {
    const characterName = characterSelect.value;
    if (!characterName || !ws || ws.readyState !== WebSocket.OPEN) {
        return;
    }
    
    // Get the street name for display
    const char = availableCharacters.find(c => c.name === characterName);
    const displayName = char ? (char.street_name || char.name) : characterName;
    
    // Check if already added
    if (characters.includes(characterName)) {
        addMessage('system', `${displayName} is already in the session`);
        return;
    }
    
    // Disable button and show loading state
    addCharacterButton.disabled = true;
    const originalText = addCharacterButton.textContent;
    addCharacterButton.textContent = 'Adding Character...';
    setStatus(`Adding ${displayName} to session...`);
    
    // Send to server (server will validate)
    ws.send(JSON.stringify({
        type: 'add_character',
        character: characterName
    }));
    
    // Reset dropdown
    characterSelect.value = '';
    
    // Re-enable button after a short delay (server will send session_info which triggers updateCharacterList)
    setTimeout(() => {
        addCharacterButton.disabled = false;
        addCharacterButton.textContent = originalText;
        setStatus('Ready');
    }, 1000);
}

// Remove character
function removeCharacter(characterName) {
    if (scenarioStarted) {
        addMessage('system', 'Cannot remove characters after scenario has started');
        return;
    }
    
    // Remove from local list
    characters = characters.filter(c => c !== characterName);
    updateCharacterList();
    
    // Send to server
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'remove_character',
            character: characterName
        }));
    }
    
    addMessage('system', `Removed ${characterName} from session`);
}

// View character sheet - accepts either character name or character object
async function viewCharacterSheet(characterNameOrObject) {
    const traceId = errorHandler.generateTraceId();
    
    try {
        let character;
        let characterName;
        
        // Check if we received a character object or just a name
        if (typeof characterNameOrObject === 'object' && characterNameOrObject !== null) {
            // We already have the character data
            character = characterNameOrObject;
            characterName = character.name || character.street_name || 'Unknown';
            console.log(`[Trace: ${traceId}] Using pre-loaded character data for: ${characterName}`);
        } else {
            // We need to fetch the character data
            characterName = characterNameOrObject;
            setStatus(`Loading character sheet for ${characterName}...`);
            console.log(`[Trace: ${traceId}] Loading character sheet for: ${characterName}`);
            
            const response = await fetch(`/api/character/${encodeURIComponent(characterName)}`, {
                headers: {
                    'X-Trace-ID': traceId
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const error = errorHandler.handleServerError(errorData, traceId);
                throw new Error(error.message);
            }
            
            const responseData = await response.json();
            console.log(`[Trace: ${traceId}] Character loaded successfully`);
            // Extract the actual character data from the response
            character = responseData.data || responseData;
        }
        
        displayCharacterSheet(character);
        setStatus('Ready');
    } catch (error) {
        const err = errorHandler.handleFetchError(error, `/api/character/${characterNameOrObject}`, traceId);
        addMessage('system', `❌ Failed to load character sheet: ${err.message} [Trace: ${traceId}]`);
        setStatus('Error');
    }
}

// Display character sheet in modal
function displayCharacterSheet(character) {
    // Use the new renderer
    const renderer = new CharacterSheetRenderer();
    const html = renderer.render(character);
    
    characterSheetContent.innerHTML = html;
    characterSheetModal.classList.add('active');
    
    // Add click handlers for collapsible sections
    setupSectionToggles();
}

// Setup collapsible section toggles
function setupSectionToggles() {
    const sectionHeaders = document.querySelectorAll('.section-header');
    sectionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;
            const toggle = header.querySelector('.section-toggle');
            
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                toggle.textContent = '▼';
            } else {
                content.classList.add('collapsed');
                toggle.textContent = '▶';
            }
        });
    });
}

// Close character sheet modal
function closeCharacterSheet() {
    characterSheetModal.classList.remove('active');
}

// Update character list display
function updateCharacterList() {
    characterList.innerHTML = '';
    characters.forEach(char => {
        const li = document.createElement('li');
        
        // Get street name for display
        const charData = availableCharacters.find(c => c.name === char);
        const displayName = charData ? (charData.street_name || charData.name) : char;
        
        // Character name (clickable) - show street name
        const nameSpan = document.createElement('span');
        nameSpan.className = 'character-name';
        nameSpan.textContent = displayName;
        nameSpan.onclick = () => viewCharacterSheet(char);
        li.appendChild(nameSpan);
        
        // Remove button (only if scenario hasn't started)
        if (!scenarioStarted) {
            const removeBtn = document.createElement('button');
            removeBtn.className = 'character-remove';
            removeBtn.textContent = '✕';
            removeBtn.onclick = (e) => {
                e.stopPropagation();
                removeCharacter(char);
            };
            li.appendChild(removeBtn);
        }
        
        characterList.appendChild(li);
    });
}

// Load available characters from database
async function loadAvailableCharacters() {
    const traceId = errorHandler.generateTraceId();
    setStatus('Loading characters...');
    
    try {
        console.log(`[Trace: ${traceId}] Loading available characters`);
        
        const response = await fetch('/api/characters', {
            headers: {
                'X-Trace-ID': traceId
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const error = errorHandler.handleServerError(errorData, traceId);
            throw new Error(error.message);
        }
        
        const data = await response.json();
        availableCharacters = data.characters;
        
        console.log(`[Trace: ${traceId}] Loaded ${availableCharacters.length} characters`);
        
        // Populate dropdown
        characterSelect.innerHTML = '<option value="">Select a character...</option>';
        availableCharacters.forEach(char => {
            const option = document.createElement('option');
            // Use street_name as the display name (what everyone uses)
            const displayName = char.street_name || char.name;
            option.value = char.name;  // Keep using real name as value for API calls
            // Show archetype instead of character_type (which may be null)
            const subtitle = char.archetype || char.character_type || 'Character';
            option.textContent = `${displayName} (${subtitle})`;
            characterSelect.appendChild(option);
        });
        
        addMessage('system', `✓ Loaded ${availableCharacters.length} characters from database`);
        setStatus('Loaded');
        
        // Enable scenario creation button
        createScenarioButton.disabled = false;
        
        // Dispatch custom event to signal characters are loaded
        window.dispatchEvent(new CustomEvent('charactersLoaded', { 
            detail: { characters: availableCharacters } 
        }));
        
        return availableCharacters;
    } catch (error) {
        const err = errorHandler.handleFetchError(error, '/api/characters', traceId);
        addMessage('system', `✗ Failed to load characters: ${err.message} [Trace: ${traceId}]`);
        setStatus('Error loading characters');
        
        // Show error in dropdown
        characterSelect.innerHTML = '<option value="">Error loading characters</option>';
        throw error;
    }
}

// View sheet button handler
function viewSheetFromDropdown() {
    const characterName = characterSelect.value;
    if (!characterName) {
        addMessage('system', 'Please select a character first');
        return;
    }
    viewCharacterSheet(characterName);
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

addCharacterButton.addEventListener('click', addCharacter);

viewSheetButton.addEventListener('click', viewSheetFromDropdown);

createScenarioButton.addEventListener('click', () => {
    scenarioStarted = true;
    updateCharacterList(); // Remove the remove buttons
    addMessage('system', '🎲 Scenario creation feature coming soon!');
    addMessage('system', 'This will use Grok AI to generate a custom Shadowrun scenario based on your characters.');
});

modalCloseButton.addEventListener('click', closeCharacterSheet);

// Close modal when clicking outside
characterSheetModal.addEventListener('click', (e) => {
    if (e.target === characterSheetModal) {
        closeCharacterSheet();
    }
});

// Theme Management
const themeToggle = document.getElementById('theme-toggle');
const themeDropdown = document.getElementById('theme-dropdown');
const themeOptions = document.querySelectorAll('.theme-option');

// Load saved theme or default to tron
const savedTheme = localStorage.getItem('shadowrun-theme') || 'tron';
document.body.setAttribute('data-theme', savedTheme);
updateActiveTheme(savedTheme);

// Toggle theme dropdown
themeToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    themeDropdown.classList.toggle('active');
});

// Close dropdown when clicking outside
document.addEventListener('click', () => {
    themeDropdown.classList.remove('active');
});

// Theme selection
themeOptions.forEach(option => {
    option.addEventListener('click', (e) => {
        e.stopPropagation();
        const theme = option.getAttribute('data-theme');
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('shadowrun-theme', theme);
        updateActiveTheme(theme);
        themeDropdown.classList.remove('active');
    });
});

function updateActiveTheme(theme) {
    themeOptions.forEach(opt => {
        if (opt.getAttribute('data-theme') === theme) {
            opt.classList.add('active');
        } else {
            opt.classList.remove('active');
        }
    });
}

// Preload characters on page load
async function preloadCharacters() {
    try {
        await loadAvailableCharacters();
        console.log('Characters preloaded successfully');
    } catch (error) {
        console.error('Failed to preload characters:', error);
    }
}

// Telemetry Event Logging
let telemetryEvents = [];
let telemetryFilter = 'all'; // all, errors, warnings, info
let telemetrySearch = '';
let telemetryAutoScroll = true;

// Complete event color mapping
const EVENT_COLORS = {
    // WebSocket Events
    'websocket_connected': '#00ff00',
    'websocket_disconnected': '#ff0000',
    'message_received': '#00ffff',
    'message_sent': '#00ffff',
    
    // Grok AI Events
    'grok_api_call_start': '#9d4edd',
    'grok_streaming_start': '#9d4edd',
    'grok_tool_request': '#ffaa00',
    'grok_api_error': '#ff0000',
    
    // MCP Operation Events
    'mcp_operation_start': '#ffaa00',
    'mcp_operation_complete': '#00ff88',
    
    // Database Events
    'database_query': '#4cc9f0',
    
    // API Events
    'api_request': '#7209b7',
    'api_response': '#7209b7',
    
    // UI Events
    'ui_interaction': '#f72585',
    'character_added': '#00ff88',
    'character_removed': '#ff6b6b',
    
    // System Events
    'request_complete': '#00ff88',
    'error_occurred': '#ff0000',
    
    // Legacy events
    'tool_execution_start': '#ffaa00',
    'tool_execution_complete': '#00ff88'
};

// Event level mapping
function getEventLevel(event, data) {
    if (event.includes('error') || event === 'error_occurred') return 'ERROR';
    if (event.includes('warning')) return 'WARNING';
    if (event.includes('complete') || event.includes('success')) return 'INFO';
    return 'DEBUG';
}

// Event component mapping
function getEventComponent(event) {
    if (event.startsWith('websocket_')) return 'WebSocket';
    if (event.startsWith('grok_')) return 'Grok AI';
    if (event.startsWith('mcp_')) return 'MCP';
    if (event.startsWith('database_')) return 'Database';
    if (event.startsWith('api_')) return 'API';
    if (event.startsWith('ui_')) return 'UI';
    if (event.startsWith('tool_')) return 'Tools';
    return 'System';
}

function logTelemetryEvent(event, data, timestamp) {
    const entry = {
        event: event,
        data: data,
        timestamp: timestamp || new Date().toISOString(),
        displayTime: new Date().toLocaleTimeString(),
        level: getEventLevel(event, data),
        component: getEventComponent(event)
    };
    
    telemetryEvents.push(entry);
    
    // Keep last 500 events to prevent memory issues
    if (telemetryEvents.length > 500) {
        telemetryEvents = telemetryEvents.slice(-500);
    }
    
    updateToolCallLog(); // Update the display
    
    // Also log to console for debugging
    console.log(`[Telemetry] ${event}:`, data);
}

// Tool Call Logging Functions
function logToolCall(toolName, args, startTime) {
    const entry = {
        tool: toolName,
        args: args,
        startTime: startTime,
        endTime: null,
        duration: null,
        status: 'pending'
    };
    toolCalls.push(entry);
    updateToolCallLog();
    return toolCalls.length - 1; // Return index for updating later
}

function completeToolCall(index, result, success = true) {
    if (index >= 0 && index < toolCalls.length) {
        toolCalls[index].endTime = Date.now();
        toolCalls[index].duration = toolCalls[index].endTime - toolCalls[index].startTime;
        toolCalls[index].status = success ? 'success' : 'error';
        toolCalls[index].result = result;
        updateToolCallLog();
    }
}

function updateToolCallLog() {
    if (telemetryEvents.length === 0 && toolCalls.length === 0) {
        toolCallLog.innerHTML = '<div style="color: var(--neon-orange); font-style: italic;">Waiting for activity...</div>';
        return;
    }
    
    // Filter events
    let filteredEvents = telemetryEvents;
    
    // Apply level filter
    if (telemetryFilter !== 'all') {
        filteredEvents = filteredEvents.filter(e => {
            if (telemetryFilter === 'errors') return e.level === 'ERROR';
            if (telemetryFilter === 'warnings') return e.level === 'WARNING';
            if (telemetryFilter === 'info') return e.level === 'INFO';
            return true;
        });
    }
    
    // Apply search filter
    if (telemetrySearch) {
        const searchLower = telemetrySearch.toLowerCase();
        filteredEvents = filteredEvents.filter(e => {
            const eventStr = JSON.stringify(e).toLowerCase();
            return eventStr.includes(searchLower);
        });
    }
    
    let html = '';
    
    // Display telemetry events
    filteredEvents.forEach((event, index) => {
        const color = EVENT_COLORS[event.event] || '#00ffff';
        const eventName = event.event ? String(event.event).replace(/_/g, ' ').toUpperCase() : 'UNKNOWN EVENT';
        
        // Format data for display
        let dataDisplay = '';
        if (event.data) {
            const importantKeys = ['operation', 'duration_ms', 'success', 'tool', 'tools_requested', 'total_duration_ms', 
                                   'error', 'error_type', 'action', 'component', 'character', 'query_type', 'table'];
            const filtered = {};
            importantKeys.forEach(key => {
                if (event.data[key] !== undefined) {
                    filtered[key] = event.data[key];
                }
            });
            
            if (Object.keys(filtered).length > 0) {
                dataDisplay = JSON.stringify(filtered, null, 2);
            }
        }
        
        // Level badge
        const levelColors = {
            'ERROR': '#ff0000',
            'WARNING': '#ffaa00',
            'INFO': '#00ff88',
            'DEBUG': '#888888'
        };
        const levelColor = levelColors[event.level] || '#888888';
        
        html += `
            <div class="telemetry-entry" data-level="${event.level}" data-event="${event.event}" 
                 style="margin-bottom: 0.5rem; padding: 0.5rem; background: var(--panel-bg); border-left: 3px solid ${color};"
                 onclick="showEventDetails(${index})">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="color: ${color}; font-weight: bold; font-size: 0.75rem;">
                        ${event.displayTime} - ${eventName}
                    </div>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <span style="background: ${levelColor}; color: #000; padding: 0.1rem 0.3rem; border-radius: 3px; font-size: 0.6rem; font-weight: bold;">
                            ${event.level}
                        </span>
                        <span style="color: #888; font-size: 0.6rem;">[${event.component}]</span>
                    </div>
                </div>
                ${dataDisplay ? `
                <div style="color: #888; font-size: 0.7rem; margin-top: 0.25rem; max-height: 60px; overflow-y: auto; font-family: monospace;">
                    ${dataDisplay}
                </div>
                ` : ''}
            </div>
        `;
    });
    
    if (filteredEvents.length === 0) {
        html = '<div style="color: var(--neon-orange); font-style: italic;">No events match the current filter</div>';
    }
    
    toolCallLog.innerHTML = html;
    
    // Auto-scroll if enabled
    if (telemetryAutoScroll) {
        toolCallLog.scrollTop = toolCallLog.scrollHeight;
    }
}

function clearToolCallLog() {
    toolCalls = [];
    telemetryEvents = [];
    updateToolCallLog();
}

// Filter telemetry events
function filterTelemetryEvents(filter) {
    telemetryFilter = filter;
    updateToolCallLog();
    
    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-filter="${filter}"]`)?.classList.add('active');
}

// Search telemetry events
function searchTelemetryEvents(query) {
    telemetrySearch = query;
    updateToolCallLog();
}

// Toggle auto-scroll
function toggleAutoScroll() {
    telemetryAutoScroll = !telemetryAutoScroll;
    const checkbox = document.getElementById('autoscroll-checkbox');
    if (checkbox) {
        checkbox.checked = telemetryAutoScroll;
    }
}

// Export telemetry logs
function exportTelemetryLogs() {
    const data = {
        exported_at: new Date().toISOString(),
        session_id: sessionId,
        event_count: telemetryEvents.length,
        events: telemetryEvents
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `shadowrun-telemetry-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    addMessage('system', `✓ Exported ${telemetryEvents.length} telemetry events`);
}

// Show event details in modal
function showEventDetails(index) {
    const event = telemetryEvents[index];
    if (!event) return;
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 10000;';
    
    const content = document.createElement('div');
    content.style.cssText = 'background: var(--panel-bg); border: 2px solid var(--neon-cyan); padding: 2rem; max-width: 800px; max-height: 80vh; overflow-y: auto; border-radius: 8px;';
    
    const color = EVENT_COLORS[event.event] || '#00ffff';
    
    content.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="color: ${color}; margin: 0;">${event.event.replace(/_/g, ' ').toUpperCase()}</h3>
            <button onclick="this.closest('.modal').remove()" style="background: #ff0000; color: #fff; border: none; padding: 0.5rem 1rem; cursor: pointer; border-radius: 4px;">Close</button>
        </div>
        <div style="margin-bottom: 1rem;">
            <p style="margin: 0.5rem 0;"><strong>Time:</strong> ${event.timestamp}</p>
            <p style="margin: 0.5rem 0;"><strong>Level:</strong> <span style="color: ${event.level === 'ERROR' ? '#ff0000' : event.level === 'WARNING' ? '#ffaa00' : '#00ff88'}">${event.level}</span></p>
            <p style="margin: 0.5rem 0;"><strong>Component:</strong> ${event.component}</p>
        </div>
        <div style="background: #000; padding: 1rem; border-radius: 4px; overflow-x: auto;">
            <pre style="margin: 0; color: #00ff88; font-size: 0.9rem;">${JSON.stringify(event.data, null, 2)}</pre>
        </div>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Wire up clear button
clearLogButton.addEventListener('click', clearToolCallLog);

// Connect on load
connect();
preloadCharacters();

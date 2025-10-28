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
    
    // Check if already added
    if (characters.includes(characterName)) {
        addMessage('system', `${characterName} is already in the session`);
        return;
    }
    
    // Disable button and show loading state
    addCharacterButton.disabled = true;
    const originalText = addCharacterButton.textContent;
    addCharacterButton.textContent = 'Adding Character...';
    setStatus(`Adding ${characterName} to session...`);
    
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

// View character sheet
async function viewCharacterSheet(characterName) {
    const traceId = errorHandler.generateTraceId();
    
    try {
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
        
        const character = await response.json();
        console.log(`[Trace: ${traceId}] Character loaded successfully`);
        displayCharacterSheet(character);
        setStatus('Ready');
    } catch (error) {
        const err = errorHandler.handleFetchError(error, `/api/character/${characterName}`, traceId);
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
        
        // Character name (clickable)
        const nameSpan = document.createElement('span');
        nameSpan.className = 'character-name';
        nameSpan.textContent = char;
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
            // Use the display name (street_name or name) as the value
            option.value = char.name;  // This is the street_name from the API
            // Show archetype instead of character_type (which may be null)
            const subtitle = char.archetype || char.character_type || 'Character';
            option.textContent = `${char.name} (${subtitle})`;
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

function logTelemetryEvent(event, data, timestamp) {
    const entry = {
        event: event,
        data: data,
        timestamp: timestamp || new Date().toISOString(),
        displayTime: new Date().toLocaleTimeString()
    };
    
    telemetryEvents.push(entry);
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
    
    let html = '';
    
    // Display telemetry events
    telemetryEvents.forEach((event, index) => {
        const eventColors = {
            'message_received': 'var(--neon-cyan)',
            'grok_api_call_start': 'var(--neon-purple)',
            'grok_streaming_start': 'var(--neon-purple)',
            'grok_tool_request': 'var(--neon-orange)',
            'tool_execution_start': 'var(--neon-yellow)',
            'tool_execution_complete': 'var(--neon-green)',
            'request_complete': 'var(--neon-green)'
        };
        
        const color = eventColors[event.event] || 'var(--neon-cyan)';
        const eventName = event.event ? String(event.event).replace(/_/g, ' ').toUpperCase() : 'UNKNOWN EVENT';
        
        // Format data for display
        let dataDisplay = '';
        if (event.data) {
            const importantKeys = ['latency_ms', 'duration_ms', 'tool', 'tools_requested', 'total_duration_ms', 'grok_calls', 'tool_calls'];
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
        
        html += `
            <div style="
                margin-bottom: 0.5rem;
                padding: 0.5rem;
                background: var(--panel-bg);
                border-left: 3px solid ${color};
            ">
                <div style="color: ${color}; font-weight: bold; font-size: 0.75rem;">
                    ${event.displayTime} - ${eventName}
                </div>
                ${dataDisplay ? `
                <div style="color: #888; font-size: 0.7rem; margin-top: 0.25rem; max-height: 60px; overflow-y: auto;">
                    ${dataDisplay}
                </div>
                ` : ''}
            </div>
        `;
    });
    
    toolCallLog.innerHTML = html;
    toolCallLog.scrollTop = toolCallLog.scrollHeight;
}

function clearToolCallLog() {
    toolCalls = [];
    telemetryEvents = [];
    updateToolCallLog();
}

// Wire up clear button
clearLogButton.addEventListener('click', clearToolCallLog);

// Connect on load
connect();
preloadCharacters();

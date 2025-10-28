/**
 * Shadowrun GM - Error Handler with Distributed Tracing
 * Provides structured error handling, logging, and trace ID management
 */

class ErrorHandler {
    constructor() {
        this.errors = [];
        this.maxErrors = 50;
        this.errorCodes = this.initializeErrorCodes();
        this.loadErrorsFromStorage();
    }

    /**
     * Initialize error code definitions
     */
    initializeErrorCodes() {
        return {
            // Connection errors (1xxx)
            1001: { type: 'WEBSOCKET_CONNECTION_FAILED', severity: 'error' },
            1002: { type: 'WEBSOCKET_DISCONNECTED', severity: 'warning' },
            1003: { type: 'WEBSOCKET_TIMEOUT', severity: 'error' },
            1004: { type: 'WEBSOCKET_ERROR', severity: 'error' },

            // API errors (2xxx)
            2001: { type: 'CHARACTER_NOT_FOUND', severity: 'error' },
            2002: { type: 'CHARACTER_LOAD_FAILED', severity: 'error' },
            2003: { type: 'DATABASE_ERROR', severity: 'error' },
            2004: { type: 'INVALID_REQUEST', severity: 'error' },
            2005: { type: 'API_TIMEOUT', severity: 'error' },
            2006: { type: 'API_ERROR', severity: 'error' },

            // Tool errors (3xxx)
            3001: { type: 'TOOL_EXECUTION_FAILED', severity: 'error' },
            3002: { type: 'TOOL_TIMEOUT', severity: 'error' },
            3003: { type: 'INVALID_TOOL_PARAMS', severity: 'error' },
            3004: { type: 'TOOL_NOT_FOUND', severity: 'error' },

            // AI errors (4xxx)
            4001: { type: 'GROK_API_ERROR', severity: 'error' },
            4002: { type: 'GROK_RATE_LIMIT', severity: 'warning' },
            4003: { type: 'GROK_TIMEOUT', severity: 'error' },
            4004: { type: 'GROK_INVALID_RESPONSE', severity: 'error' },

            // Validation errors (5xxx)
            5001: { type: 'INVALID_CHARACTER_NAME', severity: 'warning' },
            5002: { type: 'SESSION_EXPIRED', severity: 'warning' },
            5003: { type: 'MISSING_REQUIRED_FIELD', severity: 'error' },
            5004: { type: 'INVALID_INPUT', severity: 'warning' },

            // Generic errors (9xxx)
            9000: { type: 'UNKNOWN_ERROR', severity: 'error' },
            9001: { type: 'INTERNAL_ERROR', severity: 'error' }
        };
    }

    /**
     * Generate a unique trace ID (UUID v4)
     */
    generateTraceId() {
        return crypto.randomUUID();
    }

    /**
     * Create a structured error object
     */
    createError(code, message, context = {}, traceId = null, source = 'ui') {
        const errorDef = this.errorCodes[code] || this.errorCodes[9000];
        
        const error = {
            trace_id: traceId || this.generateTraceId(),
            code: code,
            type: errorDef.type,
            message: message,
            timestamp: new Date().toISOString(),
            context: context,
            severity: errorDef.severity,
            source: source,
            stack: new Error().stack
        };

        this.logError(error);
        return error;
    }

    /**
     * Log error to console and storage
     */
    logError(error) {
        // Add to error list
        this.errors.unshift(error);
        
        // Trim to max size
        if (this.errors.length > this.maxErrors) {
            this.errors = this.errors.slice(0, this.maxErrors);
        }

        // Save to localStorage
        this.saveErrorsToStorage();

        // Log to console with appropriate level
        const consoleMethod = error.severity === 'warning' ? 'warn' : 'error';
        console[consoleMethod](`[SR-GM ${error.code}] [Trace: ${error.trace_id}]`, {
            type: error.type,
            message: error.message,
            context: error.context,
            timestamp: error.timestamp,
            source: error.source
        });
    }

    /**
     * Handle error from server response
     */
    handleServerError(errorData, traceId = null) {
        const code = errorData.code || 9001;
        const message = errorData.message || errorData.error || 'Unknown server error';
        const context = errorData.context || {};
        const source = errorData.source || 'server';

        return this.createError(code, message, context, traceId, source);
    }

    /**
     * Handle WebSocket error
     */
    handleWebSocketError(event, traceId = null) {
        return this.createError(
            1004,
            'WebSocket error occurred',
            { event: event.type },
            traceId,
            'websocket'
        );
    }

    /**
     * Handle fetch/API error
     */
    handleFetchError(error, url, traceId = null) {
        let code = 2006;
        let message = error.message;
        let context = { url: url };

        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            code = 1001;
            message = 'Network connection failed';
        } else if (error.message.includes('timeout')) {
            code = 2005;
            message = 'API request timed out';
        }

        return this.createError(code, message, context, traceId, 'api');
    }

    /**
     * Get all errors
     */
    getErrors() {
        return this.errors;
    }

    /**
     * Get errors by severity
     */
    getErrorsBySeverity(severity) {
        return this.errors.filter(e => e.severity === severity);
    }

    /**
     * Get errors by trace ID
     */
    getErrorsByTraceId(traceId) {
        return this.errors.filter(e => e.trace_id === traceId);
    }

    /**
     * Clear all errors
     */
    clearErrors() {
        this.errors = [];
        this.saveErrorsToStorage();
    }

    /**
     * Export errors as JSON
     */
    exportErrors() {
        const data = {
            exported_at: new Date().toISOString(),
            error_count: this.errors.length,
            errors: this.errors
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `shadowrun-gm-errors-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Save errors to localStorage
     */
    saveErrorsToStorage() {
        try {
            localStorage.setItem('shadowrun-gm-errors', JSON.stringify(this.errors));
        } catch (e) {
            console.warn('Failed to save errors to localStorage:', e);
        }
    }

    /**
     * Load errors from localStorage
     */
    loadErrorsFromStorage() {
        try {
            const stored = localStorage.getItem('shadowrun-gm-errors');
            if (stored) {
                this.errors = JSON.parse(stored);
            }
        } catch (e) {
            console.warn('Failed to load errors from localStorage:', e);
            this.errors = [];
        }
    }

    /**
     * Format error for display
     */
    formatErrorForDisplay(error) {
        const severityIcon = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        };

        const icon = severityIcon[error.severity] || '❌';
        const time = new Date(error.timestamp).toLocaleTimeString();

        return {
            icon: icon,
            title: `${icon} ${error.type} (${error.code})`,
            message: error.message,
            time: time,
            traceId: error.trace_id,
            context: error.context,
            severity: error.severity,
            source: error.source
        };
    }
}

// Create global error handler instance
window.errorHandler = new ErrorHandler();

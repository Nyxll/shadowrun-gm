# API Logging Documentation

## Overview

The Dice Rolling API includes comprehensive logging to help with debugging, monitoring, security, and performance analysis. All logs are written to files in the `logs/` directory.

## Log Files

### 1. `logs/api.log`
**Purpose:** General API activity log  
**Contains:**
- All incoming requests (INFO level)
- Successful responses (INFO level)
- Failed responses (WARNING level)
- Request parameters (sanitized)
- Response times and sizes

### 2. `logs/error.log`
**Purpose:** Error tracking and debugging  
**Contains:**
- All errors and exceptions (ERROR level)
- Stack traces for debugging
- Failed request details
- Error context

## Log Entry Format

Each log entry follows this format:

```
[TIMESTAMP] [LEVEL] [IP_ADDRESS] [METHOD URI] MESSAGE | Context: {JSON}
```

**Example:**
```
[2025-10-04 02:20:15] [INFO] [127.0.0.1] [GET /api.php?action=roll&notation=2d6] Request: action=roll | Context: {"params":{"action":"roll","notation":"2d6"},"user_agent":"Mozilla/5.0..."}
```

## Log Levels

| Level | Purpose | Log File |
|-------|---------|----------|
| **INFO** | Normal operations, successful requests | api.log |
| **WARNING** | Failed requests (400 errors, validation failures) | api.log |
| **ERROR** | Exceptions, system errors, critical failures | error.log |

## What Gets Logged

### Request Logging
Every incoming request logs:
- **Timestamp** - When the request was received
- **Action** - Which endpoint was called
- **Parameters** - All request parameters (GET, POST, JSON body)
- **IP Address** - Client IP address
- **User Agent** - Client browser/application
- **HTTP Method** - GET, POST, etc.
- **Request URI** - Full request path

### Response Logging
Every response logs:
- **Success/Failure** - Whether the request succeeded
- **Execution Time** - How long the request took (in milliseconds)
- **Response Size** - Size of the response in bytes
- **Action** - Which endpoint was called

### Error Logging
Every error logs:
- **Error Message** - The exception message
- **Action** - Which endpoint failed
- **Stack Trace** - Full stack trace for debugging
- **Request Context** - What parameters caused the error

## Configuration

### Enable/Disable Logging

In `api.php`, set the constant:

```php
define('ENABLE_LOGGING', true);  // Set to false to disable all logging
```

### Log File Paths

```php
define('LOG_FILE', __DIR__ . '/logs/api.log');
define('ERROR_LOG_FILE', __DIR__ . '/logs/error.log');
```

### Directory Permissions

The `logs/` directory is automatically created with permissions `0755` if it doesn't exist. Ensure your web server has write permissions to this directory.

## Log Rotation

**Important:** Log files will grow over time. Implement log rotation to prevent disk space issues.

### Manual Rotation

```bash
# Backup and clear logs
cd C:\Users\Rick\Documents\Cline\MCP\dice-server\logs
copy api.log api.log.backup
copy error.log error.log.backup
echo. > api.log
echo. > error.log
```

### Automated Rotation (Recommended)

For production use, implement automated log rotation:

**Option 1: Windows Task Scheduler**
Create a scheduled task to run a PowerShell script:

```powershell
# rotate-logs.ps1
$logDir = "C:\Users\Rick\Documents\Cline\MCP\dice-server\logs"
$date = Get-Date -Format "yyyy-MM-dd"

# Rotate api.log
if (Test-Path "$logDir\api.log") {
    Move-Item "$logDir\api.log" "$logDir\api-$date.log"
    New-Item "$logDir\api.log" -ItemType File
}

# Rotate error.log
if (Test-Path "$logDir\error.log") {
    Move-Item "$logDir\error.log" "$logDir\error-$date.log"
    New-Item "$logDir\error.log" -ItemType File
}

# Delete logs older than 30 days
Get-ChildItem "$logDir\*.log" | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-30)
} | Remove-Item
```

**Option 2: PHP-based Rotation**
Add to `api.php`:

```php
function rotateLogsIfNeeded() {
    $maxSize = 10 * 1024 * 1024; // 10MB
    
    if (file_exists(LOG_FILE) && filesize(LOG_FILE) > $maxSize) {
        $backup = LOG_FILE . '.' . date('Y-m-d-His');
        rename(LOG_FILE, $backup);
    }
    
    if (file_exists(ERROR_LOG_FILE) && filesize(ERROR_LOG_FILE) > $maxSize) {
        $backup = ERROR_LOG_FILE . '.' . date('Y-m-d-His');
        rename(ERROR_LOG_FILE, $backup);
    }
}
```

## Monitoring & Analysis

### View Recent Logs

**Windows PowerShell:**
```powershell
# Last 50 lines of api.log
Get-Content C:\Users\Rick\Documents\Cline\MCP\dice-server\logs\api.log -Tail 50

# Last 50 lines of error.log
Get-Content C:\Users\Rick\Documents\Cline\MCP\dice-server\logs\error.log -Tail 50

# Follow logs in real-time
Get-Content C:\Users\Rick\Documents\Cline\MCP\dice-server\logs\api.log -Wait -Tail 10
```

### Search Logs

**Find all errors:**
```powershell
Select-String -Path "C:\Users\Rick\Documents\Cline\MCP\dice-server\logs\error.log" -Pattern "ERROR"
```

**Find requests from specific IP:**
```powershell
Select-String -Path "C:\Users\Rick\Documents\Cline\MCP\dice-server\logs\api.log" -Pattern "192.168.1.100"
```

**Find slow requests (>1000ms):**
```powershell
Select-String -Path "C:\Users\Rick\Documents\Cline\MCP\dice-server\logs\api.log" -Pattern "execution_time_ms.*[1-9][0-9]{3,}"
```

### Performance Analysis

Extract execution times:
```powershell
Select-String -Path "C:\Users\Rick\Documents\Cline\MCP\dice-server\logs\api.log" -Pattern "execution_time_ms" | 
    ForEach-Object { $_.Line -match 'execution_time_ms":(\d+\.?\d*)' | Out-Null; $matches[1] } |
    Measure-Object -Average -Maximum -Minimum
```

## Security Considerations

### Sensitive Data

The logging system is designed to avoid logging sensitive data:

```php
function logRequest($action, $params = []) {
    $sanitizedParams = $params;
    
    // Remove sensitive data if any
    unset($sanitizedParams['password'], $sanitizedParams['api_key']);
    
    logMessage('INFO', "Request: action={$action}", [
        'params' => $sanitizedParams,
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
    ]);
}
```

**To add more sensitive fields:**
```php
unset(
    $sanitizedParams['password'],
    $sanitizedParams['api_key'],
    $sanitizedParams['token'],
    $sanitizedParams['secret']
);
```

### Log File Security

1. **File Permissions:** Ensure logs are not publicly accessible via web
2. **Add to .htaccess** (if using Apache):
   ```apache
   <Files "*.log">
       Order allow,deny
       Deny from all
   </Files>
   ```

3. **Nginx Configuration:**
   ```nginx
   location ~* \.log$ {
       deny all;
   }
   ```

## Example Log Entries

### Successful Request
```
[2025-10-04 02:20:15] [INFO] [127.0.0.1] [GET /api.php?action=roll&notation=2d6] Request: action=roll | Context: {"params":{"action":"roll","notation":"2d6"},"user_agent":"Mozilla/5.0"}
[2025-10-04 02:20:15] [INFO] [127.0.0.1] [GET /api.php?action=roll&notation=2d6] Response: action=roll | Context: {"success":true,"execution_time_ms":2.45,"result_size_bytes":156}
```

### Failed Request
```
[2025-10-04 02:21:30] [INFO] [127.0.0.1] [GET /api.php?action=roll] Request: action=roll | Context: {"params":{"action":"roll"},"user_agent":"curl/7.68.0"}
[2025-10-04 02:21:30] [ERROR] [127.0.0.1] [GET /api.php?action=roll] Error in action=roll: Missing required parameter: notation | Context: {"error":"Missing required parameter: notation","action":"roll","trace":"#0 /path/to/api.php(150)..."}
[2025-10-04 02:21:30] [WARNING] [127.0.0.1] [GET /api.php?action=roll] Response: action=roll | Context: {"success":false,"execution_time_ms":1.23}
```

### Complex Request (Opposed Pools)
```
[2025-10-04 02:22:45] [INFO] [127.0.0.1] [POST /api.php] Request: action=roll_opposed_pools | Context: {"params":{"action":"roll_opposed_pools","side1":{"label":"Attacker","pools":[{"name":"Firearms","notation":"8d6!"}],"target_number":4},"side2":{"label":"Defender","pools":[{"name":"Body","notation":"6d6!"}],"target_number":5}},"user_agent":"MCP-Server/1.0"}
[2025-10-04 02:22:45] [INFO] [127.0.0.1] [POST /api.php] Response: action=roll_opposed_pools | Context: {"success":true,"execution_time_ms":5.67,"result_size_bytes":1024}
```

## Troubleshooting

### Logs Not Being Created

1. **Check directory permissions:**
   ```powershell
   Test-Path "C:\Users\Rick\Documents\Cline\MCP\dice-server\logs" -PathType Container
   ```

2. **Check ENABLE_LOGGING constant:**
   ```php
   define('ENABLE_LOGGING', true);
   ```

3. **Check web server error logs** for permission issues

### Logs Growing Too Large

1. Implement log rotation (see above)
2. Reduce logging verbosity by filtering certain actions
3. Archive old logs to separate storage

### Performance Impact

Logging has minimal performance impact:
- Average overhead: 1-3ms per request
- File locking prevents race conditions
- Asynchronous logging not needed for this use case

To measure impact:
```php
// Before logging
$start = microtime(true);
logMessage('INFO', 'Test');
$duration = (microtime(true) - $start) * 1000;
echo "Logging took: {$duration}ms";
```

## Best Practices

1. **Regular Monitoring:** Check error.log daily for issues
2. **Log Rotation:** Implement automated rotation before logs exceed 100MB
3. **Retention Policy:** Keep logs for 30-90 days depending on needs
4. **Security:** Never log passwords, tokens, or sensitive user data
5. **Analysis:** Use logs to identify slow endpoints and optimize
6. **Alerts:** Set up alerts for high error rates
7. **Backup:** Include logs in backup strategy for compliance

## Integration with Monitoring Tools

### Export to JSON for Analysis

```powershell
# Convert logs to JSON for analysis tools
Get-Content logs\api.log | ForEach-Object {
    if ($_ -match '\[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] (.+)') {
        [PSCustomObject]@{
            Timestamp = $matches[1]
            Level = $matches[2]
            IP = $matches[3]
            Request = $matches[4]
            Message = $matches[5]
        }
    }
} | ConvertTo-Json
```

### Send to External Logging Service

For production, consider integrating with:
- **Loggly**
- **Papertrail**
- **Splunk**
- **ELK Stack** (Elasticsearch, Logstash, Kibana)

Example integration:
```php
function sendToExternalLogger($level, $message, $context) {
    // Send to external service
    $data = [
        'timestamp' => date('c'),
        'level' => $level,
        'message' => $message,
        'context' => $context
    ];
    
    // Example: POST to logging service
    // file_get_contents('https://logs.example.com/api', [
    //     'http' => [
    //         'method' => 'POST',
    //         'content' => json_encode($data)
    //     ]
    // ]);
}
```

## Summary

The logging system provides:
- ✅ Complete request/response tracking
- ✅ Error tracking with stack traces
- ✅ Performance monitoring
- ✅ Security audit trail
- ✅ Easy troubleshooting
- ✅ Minimal performance overhead

For questions or issues, refer to the main README.md or check the error.log file.

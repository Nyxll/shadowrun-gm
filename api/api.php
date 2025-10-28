<?php
/**
 * Dice Rolling Web Service API
 * 
 * Endpoints:
 * - GET /api.php?action=roll&notation=2d6
 * - GET /api.php?action=roll_multiple&notations[]=2d6&notations[]=1d20+5
 * - GET /api.php?action=roll_advantage&notation=1d20
 * - GET /api.php?action=roll_disadvantage&notation=1d20
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

require_once __DIR__ . '/DiceRoller.php';
require_once __DIR__ . '/CombatModifiers.php';

// ============================================================================
// LOGGING CONFIGURATION
// ============================================================================

// Log file path - ensure this directory is writable
define('LOG_FILE', __DIR__ . '/logs/api.log');
define('ERROR_LOG_FILE', __DIR__ . '/logs/error.log');
define('ENABLE_LOGGING', true); // Set to false to disable logging

// Create logs directory if it doesn't exist
if (ENABLE_LOGGING && !file_exists(__DIR__ . '/logs')) {
    mkdir(__DIR__ . '/logs', 0755, true);
}

/**
 * Log a message to the API log file
 * 
 * @param string $level Log level (INFO, WARNING, ERROR)
 * @param string $message Log message
 * @param array $context Additional context data
 */
function logMessage($level, $message, $context = []) {
    if (!ENABLE_LOGGING) {
        return;
    }
    
    $timestamp = date('Y-m-d H:i:s');
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $method = $_SERVER['REQUEST_METHOD'] ?? 'unknown';
    $uri = $_SERVER['REQUEST_URI'] ?? 'unknown';
    
    $logEntry = sprintf(
        "[%s] [%s] [%s] [%s %s] %s",
        $timestamp,
        $level,
        $ip,
        $method,
        $uri,
        $message
    );
    
    if (!empty($context)) {
        $logEntry .= ' | Context: ' . json_encode($context);
    }
    
    $logEntry .= PHP_EOL;
    
    // Write to appropriate log file
    $logFile = ($level === 'ERROR') ? ERROR_LOG_FILE : LOG_FILE;
    file_put_contents($logFile, $logEntry, FILE_APPEND | LOCK_EX);
}

/**
 * Log request details
 */
function logRequest($action, $params = []) {
    $sanitizedParams = $params;
    
    // Remove sensitive data if any (for future use)
    // unset($sanitizedParams['password'], $sanitizedParams['api_key']);
    
    logMessage('INFO', "Request: action={$action}", [
        'params' => $sanitizedParams,
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
    ]);
}

/**
 * Log response details
 */
function logResponse($action, $success, $executionTime, $resultSize = null) {
    $context = [
        'success' => $success,
        'execution_time_ms' => round($executionTime * 1000, 2)
    ];
    
    if ($resultSize !== null) {
        $context['result_size_bytes'] = $resultSize;
    }
    
    $level = $success ? 'INFO' : 'WARNING';
    logMessage($level, "Response: action={$action}", $context);
}

/**
 * Log errors
 */
function logError($action, $error, $trace = null) {
    $context = [
        'error' => $error,
        'action' => $action
    ];
    
    if ($trace) {
        $context['trace'] = $trace;
    }
    
    logMessage('ERROR', "Error in action={$action}: {$error}", $context);
}

// Start timing the request
$requestStartTime = microtime(true);

// Parse JSON body if present
$jsonData = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST' && 
    isset($_SERVER['CONTENT_TYPE']) && 
    strpos($_SERVER['CONTENT_TYPE'], 'application/json') !== false) {
    $input = file_get_contents('php://input');
    $jsonData = json_decode($input, true);
}

try {
    $action = $_GET['action'] ?? ($jsonData['action'] ?? $_POST['action'] ?? 'roll');
    
    // Log the incoming request
    logRequest($action, array_merge($_GET, $_POST, $jsonData ?? []));
    
    switch ($action) {
        case 'roll':
            $notation = $_GET['notation'] ?? $_POST['notation'] ?? null;
            
            if (!$notation) {
                throw new InvalidArgumentException('Missing required parameter: notation');
            }
            
            $result = DiceRoller::roll($notation);
            $response = json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            
            // Log successful response
            $executionTime = microtime(true) - $requestStartTime;
            logResponse($action, true, $executionTime, strlen($response));
            
            echo $response;
            break;
            
        case 'roll_multiple':
            $notations = $_GET['notations'] ?? $_POST['notations'] ?? null;
            
            if (!$notations || !is_array($notations)) {
                throw new InvalidArgumentException('Missing required parameter: notations (array)');
            }
            
            $result = DiceRoller::rollMultiple($notations);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'roll_advantage':
            $notation = $_GET['notation'] ?? $_POST['notation'] ?? null;
            
            if (!$notation) {
                throw new InvalidArgumentException('Missing required parameter: notation');
            }
            
            $result = DiceRoller::rollWithAdvantage($notation);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'roll_disadvantage':
            $notation = $_GET['notation'] ?? $_POST['notation'] ?? null;
            
            if (!$notation) {
                throw new InvalidArgumentException('Missing required parameter: notation');
            }
            
            $result = DiceRoller::rollWithDisadvantage($notation);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'roll_target_number':
        case 'roll_tn':
            $notation = $_GET['notation'] ?? $_POST['notation'] ?? null;
            $tn = $_GET['tn'] ?? $_POST['tn'] ?? $_GET['target_number'] ?? $_POST['target_number'] ?? null;
            
            if (!$notation) {
                throw new InvalidArgumentException('Missing required parameter: notation');
            }
            
            if (!$tn) {
                throw new InvalidArgumentException('Missing required parameter: tn (target number)');
            }
            
            $result = DiceRoller::rollWithTargetNumber($notation, (int)$tn);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'roll_opposed':
            $notation1 = $_GET['notation1'] ?? $_POST['notation1'] ?? null;
            $tn1 = $_GET['tn1'] ?? $_POST['tn1'] ?? null;
            $notation2 = $_GET['notation2'] ?? $_POST['notation2'] ?? null;
            $tn2 = $_GET['tn2'] ?? $_POST['tn2'] ?? null;
            
            if (!$notation1 || !$tn1 || !$notation2 || !$tn2) {
                throw new InvalidArgumentException('Missing required parameters: notation1, tn1, notation2, tn2');
            }
            
            $result = DiceRoller::rollOpposed($notation1, (int)$tn1, $notation2, (int)$tn2);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'roll_initiative':
            $notation = $_GET['notation'] ?? $_POST['notation'] ?? null;
            
            if (!$notation) {
                throw new InvalidArgumentException('Missing required parameter: notation');
            }
            
            $result = DiceRoller::rollInitiative($notation);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'track_initiative':
            // Get characters from POST body (JSON) or GET parameters
            $characters = null;
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                $characters = $data['characters'] ?? $_POST['characters'] ?? null;
            } else {
                $characters = $_GET['characters'] ?? null;
            }
            
            if (!$characters || !is_array($characters)) {
                throw new InvalidArgumentException('Missing required parameter: characters (array with name and notation)');
            }
            
            $result = DiceRoller::trackInitiative($characters);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'roll_with_pools':
            // Get pools from POST body (JSON) or GET parameters
            $pools = null;
            $tn = null;
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                $pools = $data['pools'] ?? $_POST['pools'] ?? null;
                $tn = $data['target_number'] ?? $_POST['target_number'] ?? null;
            } else {
                $pools = $_GET['pools'] ?? null;
                $tn = $_GET['target_number'] ?? null;
            }
            
            if (!$pools || !is_array($pools)) {
                throw new InvalidArgumentException('Missing required parameter: pools (array with name and notation)');
            }
            
            if ($tn === null) {
                throw new InvalidArgumentException('Missing required parameter: target_number');
            }
            
            $result = DiceRoller::rollWithPools($pools, (int)$tn);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'roll_opposed_pools':
            // Get data from POST body (JSON) or parameters
            $side1Pools = null;
            $side1TN = null;
            $side2Pools = null;
            $side2TN = null;
            $side1Label = 'Side 1';
            $side2Label = 'Side 2';
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                
                $side1 = $data['side1'] ?? null;
                $side2 = $data['side2'] ?? null;
                
                if ($side1) {
                    $side1Pools = $side1['pools'] ?? null;
                    $side1TN = $side1['target_number'] ?? null;
                    $side1Label = $side1['label'] ?? 'Side 1';
                }
                
                if ($side2) {
                    $side2Pools = $side2['pools'] ?? null;
                    $side2TN = $side2['target_number'] ?? null;
                    $side2Label = $side2['label'] ?? 'Side 2';
                }
            } else {
                $side1Pools = $_GET['side1_pools'] ?? null;
                $side1TN = $_GET['side1_tn'] ?? null;
                $side2Pools = $_GET['side2_pools'] ?? null;
                $side2TN = $_GET['side2_tn'] ?? null;
                $side1Label = $_GET['side1_label'] ?? 'Side 1';
                $side2Label = $_GET['side2_label'] ?? 'Side 2';
            }
            
            if (!$side1Pools || !is_array($side1Pools) || $side1TN === null) {
                throw new InvalidArgumentException('Missing required parameters for side1: pools and target_number');
            }
            
            if (!$side2Pools || !is_array($side2Pools) || $side2TN === null) {
                throw new InvalidArgumentException('Missing required parameters for side2: pools and target_number');
            }
            
            $result = DiceRoller::rollOpposedWithPools(
                $side1Pools, (int)$side1TN,
                $side2Pools, (int)$side2TN,
                $side1Label, $side2Label
            );
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'reroll_failures':
            $failedDice = null;
            $tn = null;
            $sides = 6;
            $exploding = true;
            $iteration = 1;
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                $failedDice = $data['failed_dice'] ?? $_POST['failed_dice'] ?? null;
                $tn = $data['target_number'] ?? $_POST['target_number'] ?? null;
                $sides = $data['sides'] ?? $_POST['sides'] ?? 6;
                $exploding = $data['exploding'] ?? $_POST['exploding'] ?? true;
                $iteration = $data['reroll_iteration'] ?? $_POST['reroll_iteration'] ?? 1;
            } else {
                $failedDice = $_GET['failed_dice'] ?? null;
                $tn = $_GET['target_number'] ?? null;
                $sides = $_GET['sides'] ?? 6;
                $exploding = $_GET['exploding'] ?? true;
                $iteration = $_GET['reroll_iteration'] ?? 1;
            }
            
            if (!$failedDice || !is_array($failedDice)) {
                throw new InvalidArgumentException('Missing required parameter: failed_dice (array)');
            }
            if ($tn === null) {
                throw new InvalidArgumentException('Missing required parameter: target_number');
            }
            
            $result = DiceRoller::rerollFailures(
                $failedDice,
                (int)$tn,
                (int)$sides,
                (bool)$exploding,
                (int)$iteration
            );
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'avoid_disaster':
            $rollResult = null;
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                $rollResult = $data['roll_result'] ?? $_POST['roll_result'] ?? null;
            } else {
                $rollResult = $_GET['roll_result'] ?? null;
            }
            
            if (!$rollResult || !is_array($rollResult)) {
                throw new InvalidArgumentException('Missing required parameter: roll_result (array with all_ones=true)');
            }
            
            $result = DiceRoller::avoidDisaster($rollResult);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'buy_karma_dice':
            $count = null;
            $tn = null;
            $sides = 6;
            $exploding = true;
            $maxAllowed = null;
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                $count = $data['karma_dice_count'] ?? $_POST['karma_dice_count'] ?? null;
                $tn = $data['target_number'] ?? $_POST['target_number'] ?? null;
                $sides = $data['sides'] ?? $_POST['sides'] ?? 6;
                $exploding = $data['exploding'] ?? $_POST['exploding'] ?? true;
                $maxAllowed = $data['max_allowed'] ?? $_POST['max_allowed'] ?? null;
            } else {
                $count = $_GET['karma_dice_count'] ?? null;
                $tn = $_GET['target_number'] ?? null;
                $sides = $_GET['sides'] ?? 6;
                $exploding = $_GET['exploding'] ?? true;
                $maxAllowed = $_GET['max_allowed'] ?? null;
            }
            
            if ($count === null) {
                throw new InvalidArgumentException('Missing required parameter: karma_dice_count');
            }
            if ($tn === null) {
                throw new InvalidArgumentException('Missing required parameter: target_number');
            }
            
            $result = DiceRoller::buyKarmaDice(
                (int)$count,
                (int)$tn,
                (int)$sides,
                (bool)$exploding,
                $maxAllowed !== null ? (int)$maxAllowed : null
            );
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'buy_successes':
            $currentSuccesses = null;
            $successesToBuy = null;
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                $currentSuccesses = $data['current_successes'] ?? $_POST['current_successes'] ?? null;
                $successesToBuy = $data['successes_to_buy'] ?? $_POST['successes_to_buy'] ?? null;
            } else {
                $currentSuccesses = $_GET['current_successes'] ?? null;
                $successesToBuy = $_GET['successes_to_buy'] ?? null;
            }
            
            if ($currentSuccesses === null) {
                throw new InvalidArgumentException('Missing required parameter: current_successes');
            }
            if ($successesToBuy === null) {
                throw new InvalidArgumentException('Missing required parameter: successes_to_buy');
            }
            
            $result = DiceRoller::buySuccesses(
                (int)$currentSuccesses,
                (int)$successesToBuy
            );
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'calculate_ranged_tn':
            // Get parameters from POST body (JSON) or GET/POST parameters
            $params = null;
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                $params = $data ?? $_POST;
            } else {
                $params = $_GET;
            }
            
            $result = CombatModifiers::calculateRangedTN($params);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'calculate_melee_tn':
            // Get parameters from POST body (JSON) or GET/POST parameters
            $params = null;
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                $params = $data ?? $_POST;
            } else {
                $params = $_GET;
            }
            
            $result = CombatModifiers::calculateMeleeTN($params);
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'determine_range':
            $distance = $_GET['distance'] ?? $_POST['distance'] ?? null;
            $weaponType = $_GET['weapon_type'] ?? $_POST['weapon_type'] ?? null;
            
            if ($distance === null) {
                throw new InvalidArgumentException('Missing required parameter: distance');
            }
            if (!$weaponType) {
                throw new InvalidArgumentException('Missing required parameter: weapon_type');
            }
            
            $result = CombatModifiers::determineRange((int)$distance, $weaponType);
            echo json_encode([
                'success' => true,
                'data' => [
                    'distance' => (int)$distance,
                    'weapon_type' => $weaponType,
                    'range' => $result
                ]
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'list_light_levels':
            $result = CombatModifiers::getLightLevels();
            echo json_encode([
                'success' => true,
                'data' => $result
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'explain_combat_modifiers':
            $combatType = $_GET['combat_type'] ?? $_POST['combat_type'] ?? 'ranged';
            
            $result = CombatModifiers::explainModifiers($combatType);
            echo json_encode([
                'success' => true,
                'data' => [
                    'combat_type' => $combatType,
                    'modifiers' => $result
                ]
            ], JSON_PRETTY_PRINT);
            break;
            
        case 'help':
            echo json_encode([
                'success' => true,
                'endpoints' => [
                    [
                        'action' => 'roll',
                        'description' => 'Roll dice with standard notation (supports exploding dice with !)',
                        'parameters' => [
                            'notation' => 'Dice notation (e.g., "2d6", "1d20+5", "4d6!" for exploding)'
                        ],
                        'example' => '?action=roll&notation=2d6 or ?action=roll&notation=4d6!'
                    ],
                    [
                        'action' => 'roll_multiple',
                        'description' => 'Roll multiple different dice',
                        'parameters' => [
                            'notations[]' => 'Array of dice notations'
                        ],
                        'example' => '?action=roll_multiple&notations[]=2d6&notations[]=1d20+5'
                    ],
                    [
                        'action' => 'roll_advantage',
                        'description' => 'Roll with advantage (roll twice, take higher)',
                        'parameters' => [
                            'notation' => 'Dice notation'
                        ],
                        'example' => '?action=roll_advantage&notation=1d20'
                    ],
                    [
                        'action' => 'roll_disadvantage',
                        'description' => 'Roll with disadvantage (roll twice, take lower)',
                        'parameters' => [
                            'notation' => 'Dice notation'
                        ],
                        'example' => '?action=roll_disadvantage&notation=1d20'
                    ],
                    [
                        'action' => 'roll_target_number (or roll_tn)',
                        'description' => 'Roll dice and count successes against a target number (Shadowrun-style)',
                        'parameters' => [
                            'notation' => 'Dice notation (e.g., "6d6" or "6d6!" for exploding)',
                            'tn' => 'Target number for success (e.g., 5)'
                        ],
                        'example' => '?action=roll_tn&notation=6d6!&tn=5'
                    ],
                    [
                        'action' => 'roll_opposed',
                        'description' => 'Opposed roll between two sets of dice',
                        'parameters' => [
                            'notation1' => 'First roller\'s dice notation',
                            'tn1' => 'First roller\'s target number',
                            'notation2' => 'Opponent\'s dice notation',
                            'tn2' => 'Opponent\'s target number'
                        ],
                        'example' => '?action=roll_opposed&notation1=6d6!&tn1=5&notation2=4d6!&tn2=4'
                    ],
                    [
                        'action' => 'roll_initiative',
                        'description' => 'Roll initiative (Shadowrun-style - never exploding)',
                        'parameters' => [
                            'notation' => 'Initiative dice notation (e.g., "2d6+10")'
                        ],
                        'example' => '?action=roll_initiative&notation=2d6+10'
                    ],
                    [
                        'action' => 'track_initiative',
                        'description' => 'Track initiative for multiple characters with phase breakdown',
                        'parameters' => [
                            'characters' => 'Array of characters with "name" and "notation" keys (POST JSON recommended)'
                        ],
                        'example' => 'POST with JSON body: {"characters":[{"name":"Samurai","notation":"2d6+10"},{"name":"Mage","notation":"3d6+8"}]}'
                    ],
                    [
                        'action' => 'roll_with_pools',
                        'description' => 'Roll with dice pools (Shadowrun-style). Track skill dice, combat pool, karma pool, etc. separately',
                        'parameters' => [
                            'pools' => 'Array of pools with "name" and "notation" keys',
                            'target_number' => 'Target number for all pools'
                        ],
                        'example' => 'POST: {"pools":[{"name":"Firearms","notation":"6d6!"},{"name":"Combat Pool","notation":"4d6!"}],"target_number":5}'
                    ],
                    [
                        'action' => 'roll_opposed_pools',
                        'description' => 'Opposed roll with dice pools. General-purpose for any opposed test (combat, stealth, social, etc.)',
                        'parameters' => [
                            'side1' => 'Object with pools, target_number, and optional label',
                            'side2' => 'Object with pools, target_number, and optional label'
                        ],
                        'example' => 'POST: {"side1":{"label":"Attacker","pools":[{"name":"Firearms","notation":"6d6!"}],"target_number":5},"side2":{"label":"Defender","pools":[{"name":"Body","notation":"5d6"}],"target_number":4}}'
                    ],
                    [
                        'action' => 'calculate_ranged_tn',
                        'description' => 'Calculate ranged combat target number with all modifiers (SR2)',
                        'parameters' => [
                            'weapon' => 'Weapon properties (smartlink, recoilComp, gyroStabilization)',
                            'range' => 'Range category (short, medium, long, extreme)',
                            'attacker' => 'Attacker properties (hasSmartlink, movement, woundLevel, vision)',
                            'defender' => 'Defender properties (conscious, prone, movement, inMeleeCombat)',
                            'situation' => 'Situational modifiers (recoil, dualWielding, calledShot, lightLevel, conditions)'
                        ],
                        'example' => 'POST: {"weapon":{"smartlink":true},"range":"short","attacker":{"hasSmartlink":true},"defender":{"prone":true},"situation":{}}'
                    ],
                    [
                        'action' => 'calculate_melee_tn',
                        'description' => 'Calculate melee combat target number with all modifiers (SR2)',
                        'parameters' => [
                            'attacker' => 'Attacker properties (prone, woundLevel, naturalReach)',
                            'defender' => 'Defender properties (conscious, prone, naturalReach)',
                            'attackerWeapon' => 'Attacker weapon (reach)',
                            'defenderWeapon' => 'Defender weapon (reach)',
                            'situation' => 'Situational modifiers (lightLevel, conditions, modifier)'
                        ],
                        'example' => 'POST: {"attacker":{},"defender":{},"attackerWeapon":{"reach":1},"defenderWeapon":{"reach":0},"situation":{}}'
                    ],
                    [
                        'action' => 'determine_range',
                        'description' => 'Determine range category based on distance and weapon type',
                        'parameters' => [
                            'distance' => 'Distance to target in meters',
                            'weapon_type' => 'Weapon type (e.g., "heavy pistol", "assault rifle")'
                        ],
                        'example' => '?action=determine_range&distance=25&weapon_type=heavy pistol'
                    ],
                    [
                        'action' => 'list_light_levels',
                        'description' => 'List all available light levels and their effects',
                        'parameters' => [],
                        'example' => '?action=list_light_levels'
                    ],
                    [
                        'action' => 'explain_combat_modifiers',
                        'description' => 'Get detailed explanation of all combat modifiers',
                        'parameters' => [
                            'combat_type' => 'Type of combat (ranged or melee)'
                        ],
                        'example' => '?action=explain_combat_modifiers&combat_type=ranged'
                    ]
                ]
            ], JSON_PRETTY_PRINT);
            break;
            
        default:
            throw new InvalidArgumentException("Unknown action: {$action}. Use action=help for available endpoints.");
    }
    
} catch (Exception $e) {
    // Log the error
    $action = $_GET['action'] ?? ($jsonData['action'] ?? $_POST['action'] ?? 'unknown');
    logError($action, $e->getMessage(), $e->getTraceAsString());
    
    // Log failed response
    $executionTime = microtime(true) - $requestStartTime;
    logResponse($action, false, $executionTime);
    
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ], JSON_PRETTY_PRINT);
}

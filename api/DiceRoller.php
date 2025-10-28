<?php

class DiceRoller
{
    /**
     * Roll a single die with optional exploding
     * 
     * @param int $sides Number of sides on the die
     * @param bool $explode Whether the die should explode on max value
     * @return int The roll result
     */
    private static function rollSingleDie(int $sides, bool $explode = false): int
    {
        $roll = random_int(1, $sides);
        
        // If exploding and rolled max, add another roll
        if ($explode && $roll === $sides) {
            $roll += self::rollSingleDie($sides, true);
        }
        
        return $roll;
    }
    
    /**
     * Roll dice with the specified notation (e.g., "2d6", "1d20+5", "3d8-2", "4d6!")
     * 
     * @param string $notation Dice notation (e.g., "2d6", "1d20+5", "4d6!" for exploding)
     * @return array Result with individual rolls, total, and details
     */
    public static function roll(string $notation): array
    {
        // Parse dice notation: XdY+Z or XdY-Z or XdY or XdY! (exploding)
        $pattern = '/^(\d+)d(\d+)(!)?([+-]\d+)?$/i';
        
        if (!preg_match($pattern, $notation, $matches)) {
            throw new InvalidArgumentException("Invalid dice notation: {$notation}. Use format like '2d6', '1d20+5', or '4d6!' for exploding");
        }
        
        $count = (int)$matches[1];
        $sides = (int)$matches[2];
        $explode = isset($matches[3]) && $matches[3] === '!';
        $modifier = isset($matches[4]) ? (int)$matches[4] : 0;
        
        // Validate inputs
        if ($count < 1 || $count > 100) {
            throw new InvalidArgumentException("Number of dice must be between 1 and 100");
        }
        
        if ($sides < 2 || $sides > 1000) {
            throw new InvalidArgumentException("Number of sides must be between 2 and 1000");
        }
        
        // Roll the dice
        $rolls = [];
        $sum = 0;
        
        for ($i = 0; $i < $count; $i++) {
            $roll = self::rollSingleDie($sides, $explode);
            $rolls[] = $roll;
            $sum += $roll;
        }
        
        // Sort rolls in descending order for easier reading
        rsort($rolls);
        
        $total = $sum + $modifier;
        
        return [
            'notation' => $notation,
            'rolls' => $rolls,
            'sum' => $sum,
            'modifier' => $modifier,
            'total' => $total,
            'exploding' => $explode,
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Roll multiple different dice notations
     * 
     * @param array $notations Array of dice notations
     * @return array Array of results
     */
    public static function rollMultiple(array $notations): array
    {
        $results = [];
        
        foreach ($notations as $notation) {
            try {
                $results[] = self::roll($notation);
            } catch (Exception $e) {
                $results[] = [
                    'notation' => $notation,
                    'error' => $e->getMessage()
                ];
            }
        }
        
        return $results;
    }
    
    /**
     * Roll with advantage (roll twice, take higher)
     * 
     * @param string $notation Dice notation
     * @return array Result with both rolls and the higher value
     */
    public static function rollWithAdvantage(string $notation): array
    {
        $roll1 = self::roll($notation);
        $roll2 = self::roll($notation);
        
        return [
            'notation' => $notation,
            'roll1' => $roll1,
            'roll2' => $roll2,
            'result' => $roll1['total'] >= $roll2['total'] ? $roll1 : $roll2,
            'advantage' => true,
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Roll with disadvantage (roll twice, take lower)
     * 
     * @param string $notation Dice notation
     * @return array Result with both rolls and the lower value
     */
    public static function rollWithDisadvantage(string $notation): array
    {
        $roll1 = self::roll($notation);
        $roll2 = self::roll($notation);
        
        return [
            'notation' => $notation,
            'roll1' => $roll1,
            'roll2' => $roll2,
            'result' => $roll1['total'] <= $roll2['total'] ? $roll1 : $roll2,
            'disadvantage' => true,
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Roll dice with a target number (Shadowrun-style success counting)
     * 
     * @param string $notation Dice notation (e.g., "6d6" or "6d6!")
     * @param int $targetNumber The target number for successes
     * @return array Result with successes counted
     */
    public static function rollWithTargetNumber(string $notation, int $targetNumber): array
    {
        $result = self::roll($notation);
        
        // Count successes and track failures
        $successes = 0;
        $failures = [];
        $allOnes = true;
        
        foreach ($result['rolls'] as $roll) {
            if ($roll >= $targetNumber) {
                $successes++;
            } else {
                $failures[] = $roll;
            }
            
            if ($roll !== 1) {
                $allOnes = false;
            }
        }
        
        return [
            'notation' => $notation,
            'target_number' => $targetNumber,
            'rolls' => $result['rolls'],
            'successes' => $successes,
            'failures' => $failures,
            'failure_count' => count($failures),
            'all_ones' => $allOnes,
            'exploding' => $result['exploding'],
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Opposed roll (two sets of dice rolled against each other)
     * 
     * @param string $notation1 First roller's dice notation
     * @param int $tn1 First roller's target number
     * @param string $notation2 Opponent's dice notation
     * @param int $tn2 Opponent's target number
     * @return array Result with net successes
     */
    public static function rollOpposed(string $notation1, int $tn1, string $notation2, int $tn2): array
    {
        $roll1 = self::rollWithTargetNumber($notation1, $tn1);
        $roll2 = self::rollWithTargetNumber($notation2, $tn2);
        
        $netSuccesses = $roll1['successes'] - $roll2['successes'];
        
        return [
            'roller' => [
                'notation' => $notation1,
                'target_number' => $tn1,
                'rolls' => $roll1['rolls'],
                'successes' => $roll1['successes']
            ],
            'opponent' => [
                'notation' => $notation2,
                'target_number' => $tn2,
                'rolls' => $roll2['rolls'],
                'successes' => $roll2['successes']
            ],
            'net_successes' => $netSuccesses,
            'winner' => $netSuccesses > 0 ? 'roller' : ($netSuccesses < 0 ? 'opponent' : 'tie'),
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Roll initiative (Shadowrun-style - never exploding)
     * 
     * @param string $notation Dice notation (e.g., "2d6+10")
     * @return array Result with initiative score and phases
     */
    public static function rollInitiative(string $notation): array
    {
        // Parse dice notation, removing any ! if present (initiative never explodes)
        $notation = str_replace('!', '', $notation);
        $pattern = '/^(\d+)d(\d+)([+-]\d+)?$/i';
        
        if (!preg_match($pattern, $notation, $matches)) {
            throw new InvalidArgumentException("Invalid initiative notation: {$notation}. Use format like '2d6+10'");
        }
        
        $count = (int)$matches[1];
        $sides = (int)$matches[2];
        $modifier = isset($matches[3]) ? (int)$matches[3] : 0;
        
        // Validate inputs
        if ($count < 1 || $count > 100) {
            throw new InvalidArgumentException("Number of dice must be between 1 and 100");
        }
        
        if ($sides < 2 || $sides > 1000) {
            throw new InvalidArgumentException("Number of sides must be between 2 and 1000");
        }
        
        // Roll the dice (never exploding for initiative)
        $rolls = [];
        $sum = 0;
        
        for ($i = 0; $i < $count; $i++) {
            $roll = random_int(1, $sides);
            $rolls[] = $roll;
            $sum += $roll;
        }
        
        // Sort rolls in descending order
        rsort($rolls);
        
        $initiative = $sum + $modifier;
        
        // Calculate phases (every 10 points)
        $phases = [];
        $currentPhase = $initiative;
        while ($currentPhase > 0) {
            $phases[] = $currentPhase;
            $currentPhase -= 10;
        }
        
        return [
            'notation' => $notation,
            'rolls' => $rolls,
            'modifier' => $modifier,
            'initiative' => $initiative,
            'phases' => $phases,
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Roll with dice pools (Shadowrun-style)
     * Allows tracking multiple pools separately (skill, combat pool, karma pool, etc.)
     * 
     * @param array $pools Array of pools, each with 'name' and 'notation' keys
     * @param int $targetNumber The target number for all pools
     * @return array Results with individual pool breakdowns and totals
     */
    public static function rollWithPools(array $pools, int $targetNumber): array
    {
        if (empty($pools)) {
            throw new InvalidArgumentException("At least one pool must be provided");
        }
        
        $poolResults = [];
        $totalSuccesses = 0;
        $totalFailures = 0;
        $allFailures = [];
        $summaryParts = [];
        
        foreach ($pools as $pool) {
            if (!isset($pool['name']) || !isset($pool['notation'])) {
                throw new InvalidArgumentException("Each pool must have 'name' and 'notation' keys");
            }
            
            // Roll this pool
            $result = self::rollWithTargetNumber($pool['notation'], $targetNumber);
            
            $poolResult = [
                'name' => $pool['name'],
                'notation' => $pool['notation'],
                'rolls' => $result['rolls'],
                'successes' => $result['successes'],
                'failures' => $result['failures'],
                'failure_count' => $result['failure_count'],
                'exploding' => $result['exploding']
            ];
            
            $poolResults[] = $poolResult;
            $totalSuccesses += $result['successes'];
            $totalFailures += $result['failure_count'];
            $allFailures = array_merge($allFailures, $result['failures']);
            $summaryParts[] = "{$pool['name']}: {$result['successes']}";
        }
        
        $summaryParts[] = "Total: {$totalSuccesses}";
        
        return [
            'target_number' => $targetNumber,
            'pools' => $poolResults,
            'total_successes' => $totalSuccesses,
            'total_failures' => $totalFailures,
            'all_failures' => $allFailures,
            'summary' => implode(', ', $summaryParts),
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Opposed roll with dice pools (Shadowrun-style)
     * General-purpose opposed test - no hardcoded logic for specific test types
     * 
     * @param array $side1Pools Array of pools for side 1
     * @param int $side1TN Target number for side 1
     * @param array $side2Pools Array of pools for side 2
     * @param int $side2TN Target number for side 2
     * @param string $side1Label Label for side 1 (e.g., "Attacker", "Sneaker")
     * @param string $side2Label Label for side 2 (e.g., "Defender", "Watcher")
     * @return array Complete results for both sides with net successes
     */
    public static function rollOpposedWithPools(
        array $side1Pools,
        int $side1TN,
        array $side2Pools,
        int $side2TN,
        string $side1Label = 'Side 1',
        string $side2Label = 'Side 2'
    ): array
    {
        $side1Result = self::rollWithPools($side1Pools, $side1TN);
        $side2Result = self::rollWithPools($side2Pools, $side2TN);
        
        $netSuccesses = $side1Result['total_successes'] - $side2Result['total_successes'];
        
        $winner = 'tie';
        if ($netSuccesses > 0) {
            $winner = $side1Label;
        } elseif ($netSuccesses < 0) {
            $winner = $side2Label;
        }
        
        return [
            'test_type' => 'opposed_pools',
            'side1' => [
                'label' => $side1Label,
                'target_number' => $side1TN,
                'pools' => $side1Result['pools'],
                'total_successes' => $side1Result['total_successes'],
                'summary' => $side1Result['summary']
            ],
            'side2' => [
                'label' => $side2Label,
                'target_number' => $side2TN,
                'pools' => $side2Result['pools'],
                'total_successes' => $side2Result['total_successes'],
                'summary' => $side2Result['summary']
            ],
            'net_successes' => $netSuccesses,
            'winner' => $winner,
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Re-roll failed dice using Karma Pool (Shadowrun-style)
     * Cost escalates: 1st re-roll = 1 Karma, 2nd = 2 Karma, 3rd = 3 Karma, etc.
     * 
     * @param array $failedDice Array of failed die values to re-roll
     * @param int $targetNumber The target number for successes
     * @param int $sides Number of sides on the die (default 6)
     * @param bool $exploding Whether dice explode on max value
     * @param int $rerollIteration Which re-roll attempt (1st, 2nd, 3rd, etc.)
     * @return array Re-roll results with new successes and failures
     */
    public static function rerollFailures(
        array $failedDice,
        int $targetNumber,
        int $sides = 6,
        bool $exploding = true,
        int $rerollIteration = 1
    ): array
    {
        if (empty($failedDice)) {
            throw new InvalidArgumentException("No failed dice to re-roll");
        }
        
        if ($rerollIteration < 1) {
            throw new InvalidArgumentException("Re-roll iteration must be at least 1");
        }
        
        $karmaCost = $rerollIteration;
        $rerolledValues = [];
        $newSuccesses = 0;
        $newFailures = [];
        
        // Re-roll each failed die
        foreach ($failedDice as $failedValue) {
            $newRoll = self::rollSingleDie($sides, $exploding);
            $rerolledValues[] = $newRoll;
            
            if ($newRoll >= $targetNumber) {
                $newSuccesses++;
            } else {
                $newFailures[] = $newRoll;
            }
        }
        
        // Sort for readability
        rsort($rerolledValues);
        rsort($newFailures);
        
        return [
            'reroll_iteration' => $rerollIteration,
            'karma_cost' => $karmaCost,
            'next_reroll_cost' => $rerollIteration + 1,
            'failed_dice_count' => count($failedDice),
            'rerolled_values' => $rerolledValues,
            'new_successes' => $newSuccesses,
            'new_failures' => $newFailures,
            'new_failure_count' => count($newFailures),
            'summary' => "Re-rolled " . count($failedDice) . " failures for {$karmaCost} Karma. Got {$newSuccesses} new success" . ($newSuccesses !== 1 ? 'es' : '') . ". " . count($newFailures) . " failure" . (count($newFailures) !== 1 ? 's' : '') . " remain.",
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Avoid disaster when all dice come up 1 (Rule of One)
     * Costs 1 Karma to convert critical failure to simple failure
     * No re-roll is allowed after using this
     * 
     * @param array $rollResult The original roll result with all_ones = true
     * @return array Result of avoiding the disaster
     */
    public static function avoidDisaster(array $rollResult): array
    {
        if (!isset($rollResult['all_ones']) || !$rollResult['all_ones']) {
            throw new InvalidArgumentException("Can only avoid disaster when all dice are 1s");
        }
        
        return [
            'disaster_avoided' => true,
            'karma_cost' => 1,
            'original_result' => 'All 1s - Critical Failure',
            'new_result' => 'Simple Failure',
            'note' => 'Cannot re-roll after avoiding disaster',
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Buy additional dice using Karma Pool
     * 1 Karma per die, up to a maximum (usually skill/attribute level)
     * 
     * @param int $karmaDiceCount Number of Karma dice to buy
     * @param int $targetNumber The target number for successes
     * @param int $sides Number of sides on the die (default 6)
     * @param bool $exploding Whether dice explode on max value
     * @param int|null $maxAllowed Optional cap on Karma dice (usually skill level)
     * @return array Results of the Karma dice roll
     */
    public static function buyKarmaDice(
        int $karmaDiceCount,
        int $targetNumber,
        int $sides = 6,
        bool $exploding = true,
        ?int $maxAllowed = null
    ): array
    {
        if ($karmaDiceCount < 1) {
            throw new InvalidArgumentException("Must buy at least 1 Karma die");
        }
        
        if ($maxAllowed !== null && $karmaDiceCount > $maxAllowed) {
            throw new InvalidArgumentException("Cannot buy more than {$maxAllowed} Karma dice (skill/attribute cap)");
        }
        
        $rolls = [];
        $successes = 0;
        $failures = [];
        
        for ($i = 0; $i < $karmaDiceCount; $i++) {
            $roll = self::rollSingleDie($sides, $exploding);
            $rolls[] = $roll;
            
            if ($roll >= $targetNumber) {
                $successes++;
            } else {
                $failures[] = $roll;
            }
        }
        
        rsort($rolls);
        rsort($failures);
        
        return [
            'karma_dice_bought' => $karmaDiceCount,
            'karma_cost' => $karmaDiceCount,
            'target_number' => $targetNumber,
            'rolls' => $rolls,
            'successes' => $successes,
            'failures' => $failures,
            'failure_count' => count($failures),
            'note' => 'Add these results to your main roll',
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Buy raw successes using Karma Pool
     * Requires at least 1 natural success in the original roll
     * This Karma is PERMANENTLY spent and does not refresh
     * 
     * @param int $currentSuccesses Number of successes already achieved
     * @param int $successesToBuy Number of successes to purchase
     * @return array Result of buying successes
     */
    public static function buySuccesses(
        int $currentSuccesses,
        int $successesToBuy
    ): array
    {
        if ($currentSuccesses < 1) {
            throw new InvalidArgumentException("Must have at least 1 natural success to buy additional successes");
        }
        
        if ($successesToBuy < 1) {
            throw new InvalidArgumentException("Must buy at least 1 success");
        }
        
        $karmaCost = $successesToBuy;
        $newTotal = $currentSuccesses + $successesToBuy;
        
        return [
            'successes_bought' => $successesToBuy,
            'karma_cost' => $karmaCost,
            'permanent_karma_spent' => true,
            'original_successes' => $currentSuccesses,
            'new_total_successes' => $newTotal,
            'warning' => 'This Karma is permanently spent and does not refresh with the next encounter',
            'timestamp' => date('c')
        ];
    }
    
    /**
     * Track initiative for multiple characters (Shadowrun-style)
     * 
     * @param array $characters Array of characters with 'name' and 'notation' keys
     * @return array Complete initiative tracking with phase breakdown
     */
    public static function trackInitiative(array $characters): array
    {
        $results = [];
        
        // Roll initiative for each character
        foreach ($characters as $character) {
            if (!isset($character['name']) || !isset($character['notation'])) {
                throw new InvalidArgumentException("Each character must have 'name' and 'notation' keys");
            }
            
            $roll = self::rollInitiative($character['notation']);
            $results[] = [
                'name' => $character['name'],
                'notation' => $character['notation'],
                'rolls' => $roll['rolls'],
                'modifier' => $roll['modifier'],
                'initiative' => $roll['initiative'],
                'phases' => $roll['phases']
            ];
        }
        
        // Sort by initiative (descending), then by modifier (descending) for tie-breaking
        usort($results, function($a, $b) {
            if ($a['initiative'] === $b['initiative']) {
                return $b['modifier'] - $a['modifier'];
            }
            return $b['initiative'] - $a['initiative'];
        });
        
        // Build phase-by-phase breakdown
        $phaseMap = [];
        foreach ($results as $character) {
            foreach ($character['phases'] as $phase) {
                if (!isset($phaseMap[$phase])) {
                    $phaseMap[$phase] = [];
                }
                $phaseMap[$phase][] = $character;
            }
        }
        
        // Sort phases in descending order
        krsort($phaseMap);
        
        // Build phase order array
        $phaseOrder = [];
        foreach ($phaseMap as $phase => $actors) {
            // Sort actors within phase by initiative, then modifier
            usort($actors, function($a, $b) {
                if ($a['initiative'] === $b['initiative']) {
                    return $b['modifier'] - $a['modifier'];
                }
                return $b['initiative'] - $a['initiative'];
            });
            
            $phaseOrder[] = [
                'phase' => $phase,
                'actors' => array_map(function($actor) {
                    return $actor['name'];
                }, $actors)
            ];
        }
        
        // Build turn summary
        $turnSummary = [];
        foreach ($phaseOrder as $phaseData) {
            $phase = $phaseData['phase'];
            $actorNames = $phaseData['actors'];
            
            // Check for ties in this phase
            $tieNote = '';
            if (count($actorNames) > 1) {
                // Find the actors in this phase from results
                $phaseActors = array_filter($results, function($char) use ($actorNames) {
                    return in_array($char['name'], $actorNames);
                });
                
                // Check if any have the same initiative
                $initiatives = array_map(function($char) {
                    return $char['initiative'];
                }, $phaseActors);
                
                if (count($initiatives) !== count(array_unique($initiatives))) {
                    $tieNote = ' (ties broken by higher modifier)';
                }
            }
            
            $turnSummary[] = "Phase {$phase}: " . implode(', ', $actorNames) . $tieNote;
        }
        
        return [
            'characters' => $results,
            'phase_order' => $phaseOrder,
            'turn_summary' => implode("\n", $turnSummary),
            'timestamp' => date('c')
        ];
    }
}

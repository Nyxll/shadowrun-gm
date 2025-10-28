<?php
/**
 * Combat Modifier System for Shadowrun 2nd Edition
 * Based on AwakeMUD architecture with SR2-specific adjustments
 */

class CombatModifiers {
    // Modifier type constants
    const RECOIL = 0;
    const MOVEMENT_ATTACKER = 1;
    const DUAL_WIELDING = 2;
    const SMARTLINK = 3;
    const RANGE = 4;
    const VISIBILITY = 5;
    const POSITION_TARGET = 6;
    const GYRO = 7;
    const DEFENDER_MOVING = 8;
    const FRIENDS_IN_MELEE = 9;
    const CALLED_SHOT = 10;
    const WOUNDS = 11;
    const REACH = 12;
    const POSITION_ATTACKER = 13;
    const SURPRISE = 14;
    const SITUATIONAL = 15;
    
    // Human-readable names
    private static $MODIFIER_NAMES = [
        'Recoil',
        'Attacker Movement',
        'Dual Wielding',
        'Smartlink',
        'Range',
        'Visibility',
        'Target Position',
        'Gyro Stabilization',
        'Defender Moving',
        'Friends in Melee',
        'Called Shot',
        'Wounds',
        'Reach',
        'Attacker Position',
        'Surprise',
        'Situational'
    ];
    
    // SR2-specific constants
    const PRONE_SHORT_RANGE = -2;  // SR2 uses -2, SR3 uses -1
    const PRONE_LONG_RANGE = 1;
    const EX_AMMO_BONUS = 2;       // SR2 uses +2, SR3 uses +1
    const UNCONSCIOUS_TARGET = -6;
    const SMARTLINK_BONUS = -2;
    const DUAL_WIELD_PENALTY = 2;
    const CALLED_SHOT_PENALTY = 4;
    const FRIENDS_IN_MELEE_PENALTY = 2;
    const WALKING_PENALTY = 1;
    const RUNNING_PENALTY = 4;
    const DEFENDER_RUNNING_PENALTY = 2;
    
    // Light level modifiers (SR2 4-tier system)
    private static $LIGHT_LEVELS = [
        'NORMAL' => ['modifier' => 0, 'name' => 'Normal Light'],
        'PARTIAL' => ['modifier' => 1, 'name' => 'Partial Light'],
        'DIM' => ['modifier' => 2, 'name' => 'Dim Light'],
        'DARK' => ['modifier' => 4, 'name' => 'Total Darkness']
    ];
    
    // Range categories
    const RANGE_SHORT = 'short';
    const RANGE_MEDIUM = 'medium';
    const RANGE_LONG = 'long';
    const RANGE_EXTREME = 'extreme';
    
    // Base target numbers by range
    private static $BASE_TN_BY_RANGE = [
        'short' => 4,
        'medium' => 5,
        'long' => 6,
        'extreme' => 9
    ];
    
    // Weapon range tables (in meters) - SR2 ranges
    private static $WEAPON_RANGES = [
        'hold-out pistol' => ['short' => 15, 'medium' => 30, 'long' => 45, 'extreme' => 60],
        'light pistol' => ['short' => 15, 'medium' => 30, 'long' => 45, 'extreme' => 60],
        'heavy pistol' => ['short' => 20, 'medium' => 30, 'long' => 40, 'extreme' => 60],
        'smg' => ['short' => 40, 'medium' => 80, 'long' => 120, 'extreme' => 160],
        'shotgun' => ['short' => 20, 'medium' => 40, 'long' => 60, 'extreme' => 80],
        'sporting rifle' => ['short' => 60, 'medium' => 120, 'long' => 180, 'extreme' => 240],
        'sniper rifle' => ['short' => 80, 'medium' => 160, 'long' => 240, 'extreme' => 320],
        'assault rifle' => ['short' => 40, 'medium' => 80, 'long' => 120, 'extreme' => 160],
        'lmg' => ['short' => 40, 'medium' => 80, 'long' => 120, 'extreme' => 160]
    ];
    
    private $modifiers = [];
    private $explanations = [];
    
    public function __construct() {
        $this->modifiers = array_fill(0, 16, 0);
        $this->explanations = array_fill(0, 16, null);
    }
    
    /**
     * Apply a modifier with optional explanation
     */
    public function apply($modifierType, $value, $explanation = null) {
        if ($modifierType < 0 || $modifierType >= count($this->modifiers)) {
            throw new Exception("Invalid modifier type: $modifierType");
        }
        
        $this->modifiers[$modifierType] = $value;
        if ($explanation !== null) {
            $this->explanations[$modifierType] = $explanation;
        }
    }
    
    /**
     * Get total of all modifiers
     */
    public function getTotal() {
        return array_sum($this->modifiers);
    }
    
    /**
     * Get breakdown of all non-zero modifiers
     */
    public function getBreakdown() {
        $breakdown = [];
        foreach ($this->modifiers as $idx => $value) {
            if ($value !== 0) {
                $breakdown[] = [
                    'type' => self::$MODIFIER_NAMES[$idx],
                    'value' => $value,
                    'explanation' => $this->explanations[$idx]
                ];
            }
        }
        return $breakdown;
    }
    
    /**
     * Get human-readable summary
     */
    public function getSummary() {
        $breakdown = $this->getBreakdown();
        if (empty($breakdown)) {
            return 'No modifiers';
        }
        
        $lines = [];
        foreach ($breakdown as $m) {
            $sign = $m['value'] > 0 ? '+' : '';
            $exp = $m['explanation'] ? " ({$m['explanation']})" : '';
            $lines[] = "{$m['type']}: {$sign}{$m['value']}{$exp}";
        }
        
        return implode("\n", $lines);
    }
    
    /**
     * Reset all modifiers
     */
    public function reset() {
        $this->modifiers = array_fill(0, 16, 0);
        $this->explanations = array_fill(0, 16, null);
    }
    
    /**
     * Calculate ranged combat target number
     */
    public static function calculateRangedTN($params) {
        $weapon = $params['weapon'] ?? [];
        $range = $params['range'] ?? null;
        $attacker = $params['attacker'] ?? [];
        $defender = $params['defender'] ?? [];
        $situation = $params['situation'] ?? [];
        
        $mods = new self();
        
        // 1. Base TN from range
        $baseTN = self::$BASE_TN_BY_RANGE[$range] ?? 4;
        
        // 2. Dual wielding vs smartlink (mutually exclusive)
        if (!empty($situation['dualWielding'])) {
            $mods->apply(
                self::DUAL_WIELDING,
                self::DUAL_WIELD_PENALTY,
                'Using two weapons'
            );
        } elseif (!empty($weapon['smartlink']) && !empty($attacker['hasSmartlink'])) {
            $mods->apply(
                self::SMARTLINK,
                self::SMARTLINK_BONUS,
                'Smartlink system'
            );
        }
        
        // 3. Recoil (with optional Strength-based compensation)
        if (isset($situation['recoil']) && $situation['recoil'] > 0) {
            $totalRecoilComp = $weapon['recoilComp'] ?? 0;
            
            // Optional rule: Strength provides recoil compensation
            // Strength / 3 (round down) provides additional recoil comp
            if (!empty($situation['useStrengthRecoil']) && isset($attacker['strength'])) {
                $strengthComp = floor($attacker['strength'] / 3);
                $totalRecoilComp += $strengthComp;
                
                if ($strengthComp > 0) {
                    $mods->apply(
                        self::SITUATIONAL,
                        0,  // This is informational, actual reduction happens below
                        "Strength-based recoil comp: +{$strengthComp} (Str {$attacker['strength']})"
                    );
                }
            }
            
            $recoilMod = max(0, $situation['recoil'] - $totalRecoilComp);
            if ($recoilMod > 0) {
                $mods->apply(
                    self::RECOIL,
                    $recoilMod,
                    "Uncompensated recoil: $recoilMod (after {$totalRecoilComp} comp)"
                );
            }
        }
        
        // 4. Gyro stabilization
        if (!empty($weapon['gyroStabilization']) && $weapon['gyroStabilization'] > 0) {
            $gyroReduction = min(
                $weapon['gyroStabilization'],
                $mods->modifiers[self::MOVEMENT_ATTACKER] + $mods->modifiers[self::RECOIL]
            );
            if ($gyroReduction > 0) {
                $mods->apply(
                    self::GYRO,
                    -$gyroReduction,
                    "Gyro stabilization (Rating {$weapon['gyroStabilization']})"
                );
            }
        }
        
        // 5. Attacker movement
        if (isset($attacker['movement'])) {
            if ($attacker['movement'] === 'walking') {
                $mods->apply(
                    self::MOVEMENT_ATTACKER,
                    self::WALKING_PENALTY,
                    'Walking while shooting'
                );
            } elseif ($attacker['movement'] === 'running') {
                $mods->apply(
                    self::MOVEMENT_ATTACKER,
                    self::RUNNING_PENALTY,
                    'Running while shooting'
                );
            }
        }
        
        // 6. Target position (SR2-specific values)
        if (isset($defender['conscious']) && $defender['conscious'] === false) {
            $mods->apply(
                self::POSITION_TARGET,
                self::UNCONSCIOUS_TARGET,
                'Target unconscious'
            );
        } elseif (!empty($defender['prone'])) {
            $proneMod = $range === self::RANGE_SHORT
                ? self::PRONE_SHORT_RANGE  // SR2: -2
                : self::PRONE_LONG_RANGE;
            $mods->apply(
                self::POSITION_TARGET,
                $proneMod,
                "Target prone at $range range"
            );
        }
        
        // 7. Defender movement
        if (isset($defender['movement']) && $defender['movement'] === 'running') {
            $mods->apply(
                self::DEFENDER_MOVING,
                self::DEFENDER_RUNNING_PENALTY,
                'Target running'
            );
        }
        
        // 8. Friends in melee
        if (!empty($defender['inMeleeCombat']) && $range === self::RANGE_SHORT) {
            $mods->apply(
                self::FRIENDS_IN_MELEE,
                self::FRIENDS_IN_MELEE_PENALTY,
                'Target engaged in melee'
            );
        }
        
        // 9. Called shot
        if (!empty($situation['calledShot'])) {
            $mods->apply(
                self::CALLED_SHOT,
                self::CALLED_SHOT_PENALTY,
                'Called shot'
            );
        }
        
        // 10. Visibility
        if (isset($situation['lightLevel'])) {
            $lightMod = self::calculateVisibilityModifier(
                $situation['lightLevel'],
                $attacker['vision'] ?? [],
                $situation['conditions'] ?? []
            );
            if ($lightMod !== 0) {
                $mods->apply(
                    self::VISIBILITY,
                    $lightMod,
                    "Light level: {$situation['lightLevel']}"
                );
            }
        }
        
        // 11. Wound modifiers
        if (isset($attacker['woundLevel'])) {
            $woundMod = self::getWoundModifier($attacker['woundLevel']);
            if ($woundMod > 0) {
                $mods->apply(
                    self::WOUNDS,
                    $woundMod,
                    "{$attacker['woundLevel']} wounds"
                );
            }
        }
        
        // 12. Situational modifiers (GM discretion)
        if (isset($situation['modifier'])) {
            $mods->apply(
                self::SITUATIONAL,
                $situation['modifier'],
                $situation['modifierReason'] ?? 'GM ruling'
            );
        }
        
        $finalTN = max(2, $baseTN + $mods->getTotal());
        
        return [
            'baseTN' => $baseTN,
            'modifiers' => $mods->getBreakdown(),
            'totalModifier' => $mods->getTotal(),
            'finalTN' => $finalTN,
            'summary' => $mods->getSummary()
        ];
    }
    
    /**
     * Calculate melee combat target number
     */
    public static function calculateMeleeTN($params) {
        $attacker = $params['attacker'] ?? [];
        $defender = $params['defender'] ?? [];
        $attackerWeapon = $params['attackerWeapon'] ?? [];
        $defenderWeapon = $params['defenderWeapon'] ?? [];
        $situation = $params['situation'] ?? [];
        
        $mods = new self();
        
        // Base TN for melee is always 4
        $baseTN = 4;
        
        // 1. Reach modifiers
        $attackerReach = ($attackerWeapon['reach'] ?? 0) + ($attacker['naturalReach'] ?? 0);
        $defenderReach = ($defenderWeapon['reach'] ?? 0) + ($defender['naturalReach'] ?? 0);
        $reachDiff = $attackerReach - $defenderReach;
        
        if ($reachDiff !== 0) {
            $mods->apply(
                self::REACH,
                -$reachDiff,  // Negative because higher reach is better
                'Reach ' . ($reachDiff > 0 ? 'advantage' : 'disadvantage') . ': ' . abs($reachDiff)
            );
        }
        
        // 2. Attacker position
        if (!empty($attacker['prone'])) {
            $mods->apply(
                self::POSITION_ATTACKER,
                2,
                'Attacker prone'
            );
        }
        
        // 3. Defender position
        if (isset($defender['conscious']) && $defender['conscious'] === false) {
            $mods->apply(
                self::POSITION_TARGET,
                self::UNCONSCIOUS_TARGET,
                'Defender unconscious'
            );
        } elseif (!empty($defender['prone'])) {
            $mods->apply(
                self::POSITION_TARGET,
                -2,
                'Defender prone'
            );
        }
        
        // 4. Visibility
        if (isset($situation['lightLevel'])) {
            $lightMod = self::calculateVisibilityModifier(
                $situation['lightLevel'],
                $attacker['vision'] ?? [],
                $situation['conditions'] ?? []
            );
            if ($lightMod !== 0) {
                $mods->apply(
                    self::VISIBILITY,
                    $lightMod,
                    "Light level: {$situation['lightLevel']}"
                );
            }
        }
        
        // 5. Wound modifiers
        if (isset($attacker['woundLevel'])) {
            $woundMod = self::getWoundModifier($attacker['woundLevel']);
            if ($woundMod > 0) {
                $mods->apply(
                    self::WOUNDS,
                    $woundMod,
                    "{$attacker['woundLevel']} wounds"
                );
            }
        }
        
        // 6. Situational modifiers
        if (isset($situation['modifier'])) {
            $mods->apply(
                self::SITUATIONAL,
                $situation['modifier'],
                $situation['modifierReason'] ?? 'GM ruling'
            );
        }
        
        $finalTN = max(2, $baseTN + $mods->getTotal());
        
        return [
            'baseTN' => $baseTN,
            'modifiers' => $mods->getBreakdown(),
            'totalModifier' => $mods->getTotal(),
            'finalTN' => $finalTN,
            'summary' => $mods->getSummary()
        ];
    }
    
    /**
     * Calculate visibility modifier based on light level and vision enhancements
     */
    public static function calculateVisibilityModifier($lightLevel, $vision = [], $conditions = []) {
        // Get base modifier from light level
        $lightData = self::$LIGHT_LEVELS[strtoupper($lightLevel)] ?? self::$LIGHT_LEVELS['NORMAL'];
        $modifier = $lightData['modifier'];
        
        // Vision enhancements
        if (!empty($vision['thermographic'])) {
            // Thermographic ignores most light penalties
            $modifier = min($modifier, 1);
        } elseif (!empty($vision['lowLight'])) {
            // Low-light reduces penalties
            $modifier = floor($modifier / 2);
        }
        
        if (!empty($vision['ultrasound'])) {
            // Ultrasound ignores light completely
            $modifier = 0;
        }
        
        // Environmental conditions
        if (isset($conditions['smoke'])) {
            $modifier += $conditions['smoke'] === 'heavy' ? 4 : 2;
        }
        
        if (isset($conditions['fog'])) {
            $modifier += $conditions['fog'] === 'heavy' ? 4 : 2;
        }
        
        return $modifier;
    }
    
    /**
     * Get wound modifier based on wound level
     */
    public static function getWoundModifier($woundLevel) {
        $modifiers = [
            'light' => 1,
            'moderate' => 2,
            'serious' => 3,
            'deadly' => 99  // Unconscious/near death
        ];
        
        return $modifiers[strtolower($woundLevel)] ?? 0;
    }
    
    /**
     * Determine range category based on distance and weapon type
     */
    public static function determineRange($distance, $weaponType) {
        $weaponRanges = self::$WEAPON_RANGES[strtolower($weaponType)] ?? self::$WEAPON_RANGES['heavy pistol'];
        
        if ($distance <= $weaponRanges['short']) return self::RANGE_SHORT;
        if ($distance <= $weaponRanges['medium']) return self::RANGE_MEDIUM;
        if ($distance <= $weaponRanges['long']) return self::RANGE_LONG;
        if ($distance <= $weaponRanges['extreme']) return self::RANGE_EXTREME;
        
        return null; // Out of range
    }
    
    /**
     * Get all light levels with descriptions
     */
    public static function getLightLevels() {
        return self::$LIGHT_LEVELS;
    }
    
    /**
     * Explain all combat modifiers for a given combat type
     */
    public static function explainModifiers($combatType = 'ranged') {
        $modifiers = [];
        
        if ($combatType === 'ranged') {
            $modifiers = [
                'Recoil' => 'Uncompensated recoil from previous shots (+1 per shot)',
                'Attacker Movement' => 'Walking +1, Running +4',
                'Dual Wielding' => 'Using two weapons +2',
                'Smartlink' => 'Smartlink system -2',
                'Target Position' => 'Prone at short range -2 (SR2), prone at long range +1, unconscious -6',
                'Defender Moving' => 'Target running +2',
                'Friends in Melee' => 'Target engaged in melee at short range +2',
                'Called Shot' => 'Aiming for specific location +4',
                'Visibility' => 'Light level penalties (partial +1, dim +2, dark +4)',
                'Wounds' => 'Light +1, Moderate +2, Serious +3',
                'Gyro Stabilization' => 'Reduces movement and recoil penalties',
                'Situational' => 'GM discretion for special circumstances'
            ];
        } else {
            $modifiers = [
                'Reach' => 'Reach advantage/disadvantage (±1 per point difference)',
                'Attacker Position' => 'Attacker prone +2',
                'Target Position' => 'Defender prone -2, unconscious -6',
                'Visibility' => 'Light level penalties (partial +1, dim +2, dark +4)',
                'Wounds' => 'Light +1, Moderate +2, Serious +3',
                'Situational' => 'GM discretion for special circumstances'
            ];
        }
        
        return $modifiers;
    }
}

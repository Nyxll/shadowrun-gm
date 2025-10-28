#!/usr/bin/env python3
"""
Combat Modifier System for Shadowrun 2nd Edition
Based on AwakeMUD architecture with SR2-specific adjustments
"""

from typing import Dict, List, Optional, Any
from enum import IntEnum


class ModifierType(IntEnum):
    """Combat modifier types"""
    RECOIL = 0
    MOVEMENT_ATTACKER = 1
    DUAL_WIELDING = 2
    SMARTLINK = 3
    RANGE = 4
    VISIBILITY = 5
    POSITION_TARGET = 6
    GYRO = 7
    DEFENDER_MOVING = 8
    FRIENDS_IN_MELEE = 9
    CALLED_SHOT = 10
    WOUNDS = 11
    REACH = 12
    POSITION_ATTACKER = 13
    SURPRISE = 14
    SITUATIONAL = 15


class CombatModifiers:
    """Shadowrun 2nd Edition combat modifier calculator"""
    
    # Human-readable names
    MODIFIER_NAMES = [
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
    ]
    
    # SR2-specific constants
    PRONE_SHORT_RANGE = -2  # SR2 uses -2, SR3 uses -1
    PRONE_LONG_RANGE = 1
    EX_AMMO_BONUS = 2  # SR2 uses +2, SR3 uses +1
    UNCONSCIOUS_TARGET = -6
    SMARTLINK_BONUS = -2
    DUAL_WIELD_PENALTY = 2
    CALLED_SHOT_PENALTY = 4
    FRIENDS_IN_MELEE_PENALTY = 2
    WALKING_PENALTY = 1
    RUNNING_PENALTY = 4
    DEFENDER_RUNNING_PENALTY = 2
    
    # Light level modifiers (SR2 4-tier system)
    LIGHT_LEVELS = {
        'NORMAL': {'modifier': 0, 'name': 'Normal Light'},
        'PARTIAL': {'modifier': 1, 'name': 'Partial Light'},
        'DIM': {'modifier': 2, 'name': 'Dim Light'},
        'DARK': {'modifier': 4, 'name': 'Total Darkness'}
    }
    
    # Range categories
    RANGE_SHORT = 'short'
    RANGE_MEDIUM = 'medium'
    RANGE_LONG = 'long'
    RANGE_EXTREME = 'extreme'
    
    # Base target numbers by range
    BASE_TN_BY_RANGE = {
        'short': 4,
        'medium': 5,
        'long': 6,
        'extreme': 9
    }
    
    # Weapon range tables (in meters) - SR2 ranges
    WEAPON_RANGES = {
        'hold-out pistol': {'short': 15, 'medium': 30, 'long': 45, 'extreme': 60},
        'light pistol': {'short': 15, 'medium': 30, 'long': 45, 'extreme': 60},
        'heavy pistol': {'short': 20, 'medium': 30, 'long': 40, 'extreme': 60},
        'smg': {'short': 40, 'medium': 80, 'long': 120, 'extreme': 160},
        'shotgun': {'short': 20, 'medium': 40, 'long': 60, 'extreme': 80},
        'sporting rifle': {'short': 60, 'medium': 120, 'long': 180, 'extreme': 240},
        'sniper rifle': {'short': 80, 'medium': 160, 'long': 240, 'extreme': 320},
        'assault rifle': {'short': 40, 'medium': 80, 'long': 120, 'extreme': 160},
        'lmg': {'short': 40, 'medium': 80, 'long': 120, 'extreme': 160}
    }
    
    def __init__(self):
        """Initialize modifier tracker"""
        self.modifiers = [0] * 16
        self.explanations = [None] * 16
    
    def apply(self, modifier_type: ModifierType, value: int, explanation: Optional[str] = None):
        """Apply a modifier with optional explanation"""
        idx = int(modifier_type)
        if idx < 0 or idx >= len(self.modifiers):
            raise ValueError(f"Invalid modifier type: {modifier_type}")
        
        self.modifiers[idx] = value
        if explanation is not None:
            self.explanations[idx] = explanation
    
    def get_total(self) -> int:
        """Get total of all modifiers"""
        return sum(self.modifiers)
    
    def get_breakdown(self) -> List[Dict[str, Any]]:
        """Get breakdown of all non-zero modifiers"""
        breakdown = []
        for idx, value in enumerate(self.modifiers):
            if value != 0:
                breakdown.append({
                    'type': self.MODIFIER_NAMES[idx],
                    'value': value,
                    'explanation': self.explanations[idx]
                })
        return breakdown
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        breakdown = self.get_breakdown()
        if not breakdown:
            return 'No modifiers'
        
        lines = []
        for m in breakdown:
            sign = '+' if m['value'] > 0 else ''
            exp = f" ({m['explanation']})" if m['explanation'] else ''
            lines.append(f"{m['type']}: {sign}{m['value']}{exp}")
        
        return '\n'.join(lines)
    
    def reset(self):
        """Reset all modifiers"""
        self.modifiers = [0] * 16
        self.explanations = [None] * 16
    
    @classmethod
    def calculate_ranged_tn(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate ranged combat target number
        
        Args:
            params: Dictionary with weapon, range, attacker, defender, situation
        
        Returns:
            Dictionary with baseTN, modifiers, totalModifier, finalTN, summary
        """
        weapon = params.get('weapon', {})
        range_cat = params.get('range')
        attacker = params.get('attacker', {})
        defender = params.get('defender', {})
        situation = params.get('situation', {})
        
        mods = cls()
        
        # 1. Base TN from range
        base_tn = cls.BASE_TN_BY_RANGE.get(range_cat, 4)
        
        # 2. Dual wielding vs smartlink (mutually exclusive)
        if situation.get('dualWielding'):
            mods.apply(
                ModifierType.DUAL_WIELDING,
                cls.DUAL_WIELD_PENALTY,
                'Using two weapons'
            )
        elif weapon.get('smartlink') and attacker.get('hasSmartlink'):
            mods.apply(
                ModifierType.SMARTLINK,
                cls.SMARTLINK_BONUS,
                'Smartlink system'
            )
        
        # 3. Recoil (with optional Strength-based compensation)
        recoil = situation.get('recoil', 0)
        if recoil > 0:
            total_recoil_comp = weapon.get('recoilComp', 0)
            
            # Optional rule: Strength provides recoil compensation
            if situation.get('useStrengthRecoil') and 'strength' in attacker:
                strength_comp = attacker['strength'] // 3
                total_recoil_comp += strength_comp
                
                if strength_comp > 0:
                    mods.apply(
                        ModifierType.SITUATIONAL,
                        0,  # Informational only
                        f"Strength-based recoil comp: +{strength_comp} (Str {attacker['strength']})"
                    )
            
            recoil_mod = max(0, recoil - total_recoil_comp)
            if recoil_mod > 0:
                mods.apply(
                    ModifierType.RECOIL,
                    recoil_mod,
                    f"Uncompensated recoil: {recoil_mod} (after {total_recoil_comp} comp)"
                )
        
        # 4. Gyro stabilization
        gyro_rating = weapon.get('gyroStabilization', 0)
        if gyro_rating > 0:
            gyro_reduction = min(
                gyro_rating,
                mods.modifiers[ModifierType.MOVEMENT_ATTACKER] + mods.modifiers[ModifierType.RECOIL]
            )
            if gyro_reduction > 0:
                mods.apply(
                    ModifierType.GYRO,
                    -gyro_reduction,
                    f"Gyro stabilization (Rating {gyro_rating})"
                )
        
        # 5. Attacker movement
        movement = attacker.get('movement')
        if movement == 'walking':
            mods.apply(
                ModifierType.MOVEMENT_ATTACKER,
                cls.WALKING_PENALTY,
                'Walking while shooting'
            )
        elif movement == 'running':
            mods.apply(
                ModifierType.MOVEMENT_ATTACKER,
                cls.RUNNING_PENALTY,
                'Running while shooting'
            )
        
        # 6. Target position (SR2-specific values)
        if defender.get('conscious') is False:
            mods.apply(
                ModifierType.POSITION_TARGET,
                cls.UNCONSCIOUS_TARGET,
                'Target unconscious'
            )
        elif defender.get('prone'):
            prone_mod = cls.PRONE_SHORT_RANGE if range_cat == cls.RANGE_SHORT else cls.PRONE_LONG_RANGE
            mods.apply(
                ModifierType.POSITION_TARGET,
                prone_mod,
                f"Target prone at {range_cat} range"
            )
        
        # 7. Defender movement
        if defender.get('movement') == 'running':
            mods.apply(
                ModifierType.DEFENDER_MOVING,
                cls.DEFENDER_RUNNING_PENALTY,
                'Target running'
            )
        
        # 8. Friends in melee
        if defender.get('inMeleeCombat') and range_cat == cls.RANGE_SHORT:
            mods.apply(
                ModifierType.FRIENDS_IN_MELEE,
                cls.FRIENDS_IN_MELEE_PENALTY,
                'Target engaged in melee'
            )
        
        # 9. Called shot
        if situation.get('calledShot'):
            mods.apply(
                ModifierType.CALLED_SHOT,
                cls.CALLED_SHOT_PENALTY,
                'Called shot'
            )
        
        # 10. Visibility
        if 'lightLevel' in situation:
            light_mod = cls.calculate_visibility_modifier(
                situation['lightLevel'],
                attacker.get('vision', {}),
                situation.get('conditions', {})
            )
            if light_mod != 0:
                mods.apply(
                    ModifierType.VISIBILITY,
                    light_mod,
                    f"Light level: {situation['lightLevel']}"
                )
        
        # 11. Wound modifiers
        if 'woundLevel' in attacker:
            wound_mod = cls.get_wound_modifier(attacker['woundLevel'])
            if wound_mod > 0:
                mods.apply(
                    ModifierType.WOUNDS,
                    wound_mod,
                    f"{attacker['woundLevel']} wounds"
                )
        
        # 12. Situational modifiers (GM discretion)
        if 'modifier' in situation:
            mods.apply(
                ModifierType.SITUATIONAL,
                situation['modifier'],
                situation.get('modifierReason', 'GM ruling')
            )
        
        final_tn = max(2, base_tn + mods.get_total())
        
        return {
            'baseTN': base_tn,
            'modifiers': mods.get_breakdown(),
            'totalModifier': mods.get_total(),
            'finalTN': final_tn,
            'summary': mods.get_summary()
        }
    
    @classmethod
    def calculate_melee_tn(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate melee combat target number
        
        Args:
            params: Dictionary with attacker, defender, weapons, situation
        
        Returns:
            Dictionary with baseTN, modifiers, totalModifier, finalTN, summary
        """
        attacker = params.get('attacker', {})
        defender = params.get('defender', {})
        attacker_weapon = params.get('attackerWeapon', {})
        defender_weapon = params.get('defenderWeapon', {})
        situation = params.get('situation', {})
        
        mods = cls()
        
        # Base TN for melee is always 4
        base_tn = 4
        
        # 1. Reach modifiers
        attacker_reach = attacker_weapon.get('reach', 0) + attacker.get('naturalReach', 0)
        defender_reach = defender_weapon.get('reach', 0) + defender.get('naturalReach', 0)
        reach_diff = attacker_reach - defender_reach
        
        if reach_diff != 0:
            mods.apply(
                ModifierType.REACH,
                -reach_diff,  # Negative because higher reach is better
                f"Reach {'advantage' if reach_diff > 0 else 'disadvantage'}: {abs(reach_diff)}"
            )
        
        # 2. Attacker position
        if attacker.get('prone'):
            mods.apply(
                ModifierType.POSITION_ATTACKER,
                2,
                'Attacker prone'
            )
        
        # 3. Defender position
        if defender.get('conscious') is False:
            mods.apply(
                ModifierType.POSITION_TARGET,
                cls.UNCONSCIOUS_TARGET,
                'Defender unconscious'
            )
        elif defender.get('prone'):
            mods.apply(
                ModifierType.POSITION_TARGET,
                -2,
                'Defender prone'
            )
        
        # 4. Visibility
        if 'lightLevel' in situation:
            light_mod = cls.calculate_visibility_modifier(
                situation['lightLevel'],
                attacker.get('vision', {}),
                situation.get('conditions', {})
            )
            if light_mod != 0:
                mods.apply(
                    ModifierType.VISIBILITY,
                    light_mod,
                    f"Light level: {situation['lightLevel']}"
                )
        
        # 5. Wound modifiers
        if 'woundLevel' in attacker:
            wound_mod = cls.get_wound_modifier(attacker['woundLevel'])
            if wound_mod > 0:
                mods.apply(
                    ModifierType.WOUNDS,
                    wound_mod,
                    f"{attacker['woundLevel']} wounds"
                )
        
        # 6. Situational modifiers
        if 'modifier' in situation:
            mods.apply(
                ModifierType.SITUATIONAL,
                situation['modifier'],
                situation.get('modifierReason', 'GM ruling')
            )
        
        final_tn = max(2, base_tn + mods.get_total())
        
        return {
            'baseTN': base_tn,
            'modifiers': mods.get_breakdown(),
            'totalModifier': mods.get_total(),
            'finalTN': final_tn,
            'summary': mods.get_summary()
        }
    
    @staticmethod
    def calculate_visibility_modifier(
        light_level: str,
        vision: Dict[str, Any] = None,
        conditions: Dict[str, Any] = None
    ) -> int:
        """
        Calculate visibility modifier based on light level and vision enhancements
        
        Args:
            light_level: Light level (NORMAL, PARTIAL, DIM, DARK)
            vision: Vision enhancements dict with keys:
                - thermographic: bool or 'natural'/'cybernetic'
                - lowLight: bool or 'natural'/'cybernetic'
                - ultrasound: bool
            conditions: Environmental conditions (smoke, fog)
        
        Returns:
            Total visibility modifier
        """
        if vision is None:
            vision = {}
        if conditions is None:
            conditions = {}
        
        # Get base modifier from light level
        light_data = CombatModifiers.LIGHT_LEVELS.get(
            light_level.upper(),
            CombatModifiers.LIGHT_LEVELS['NORMAL']
        )
        modifier = light_data['modifier']
        
        # Vision enhancements - natural is better than cybernetic
        thermo = vision.get('thermographic')
        if thermo:
            if thermo == 'natural' or thermo is True:
                # Natural thermographic: complete darkness becomes +0 or +1
                modifier = 0 if modifier >= 4 else min(modifier, 1)
            elif thermo == 'cybernetic':
                # Cybernetic thermographic: complete darkness becomes +2
                modifier = 2 if modifier >= 4 else min(modifier, 2)
        elif vision.get('lowLight'):
            low_light = vision.get('lowLight')
            if low_light == 'natural' or low_light is True:
                # Natural low-light: halve penalty, minimum 0
                modifier = max(0, modifier // 2)
            elif low_light == 'cybernetic':
                # Cybernetic low-light: halve penalty, minimum 1
                modifier = max(1, modifier // 2) if modifier > 0 else 0
        
        if vision.get('ultrasound'):
            # Ultrasound ignores light completely
            modifier = 0
        
        # Environmental conditions
        if conditions.get('smoke'):
            modifier += 4 if conditions['smoke'] == 'heavy' else 2
        
        if conditions.get('fog'):
            modifier += 4 if conditions['fog'] == 'heavy' else 2
        
        return modifier
    
    @staticmethod
    def get_wound_modifier(wound_level: str) -> int:
        """
        Get wound modifier based on wound level
        
        Args:
            wound_level: Wound level (light, moderate, serious, deadly)
        
        Returns:
            Wound modifier value
        """
        modifiers = {
            'light': 1,
            'moderate': 2,
            'serious': 3,
            'deadly': 99  # Unconscious/near death
        }
        
        return modifiers.get(wound_level.lower(), 0)
    
    @staticmethod
    def determine_range(distance: int, weapon_type: str, magnification: int = 0) -> Optional[str]:
        """
        Determine range category based on distance and weapon type
        
        Args:
            distance: Distance to target in meters
            weapon_type: Type of weapon
            magnification: Optical magnification rating (reduces range category)
        
        Returns:
            Range category (short, medium, long, extreme) or None if out of range
        """
        weapon_ranges = CombatModifiers.WEAPON_RANGES.get(
            weapon_type.lower(),
            CombatModifiers.WEAPON_RANGES['heavy pistol']
        )
        
        # Determine base range category
        if distance <= weapon_ranges['short']:
            base_range = CombatModifiers.RANGE_SHORT
        elif distance <= weapon_ranges['medium']:
            base_range = CombatModifiers.RANGE_MEDIUM
        elif distance <= weapon_ranges['long']:
            base_range = CombatModifiers.RANGE_LONG
        elif distance <= weapon_ranges['extreme']:
            base_range = CombatModifiers.RANGE_EXTREME
        else:
            return None  # Out of range
        
        # Apply magnification (shifts range category toward SHORT)
        # Mag 1: extreme->long, long->medium, medium->short
        # Mag 2: extreme->medium, long->short, medium->short
        # Mag 3: extreme->short, long->short, medium->short
        if magnification > 0:
            range_order = [
                CombatModifiers.RANGE_SHORT,
                CombatModifiers.RANGE_MEDIUM,
                CombatModifiers.RANGE_LONG,
                CombatModifiers.RANGE_EXTREME
            ]
            
            try:
                current_idx = range_order.index(base_range)
                # Shift toward SHORT (index 0) by magnification levels
                new_idx = max(0, current_idx - magnification)
                return range_order[new_idx]
            except ValueError:
                return base_range
        
        return base_range
    
    @staticmethod
    def get_light_levels() -> Dict[str, Dict[str, Any]]:
        """Get all light levels with descriptions"""
        return CombatModifiers.LIGHT_LEVELS
    
    @staticmethod
    def explain_modifiers(combat_type: str = 'ranged') -> Dict[str, str]:
        """
        Explain all combat modifiers for a given combat type
        
        Args:
            combat_type: Type of combat (ranged or melee)
        
        Returns:
            Dictionary of modifier explanations
        """
        if combat_type == 'ranged':
            return {
                'Recoil': 'Uncompensated recoil from previous shots (+1 per shot)',
                'Attacker Movement': 'Walking +1, Running +4',
                'Dual Wielding': 'Using two weapons +2',
                'Smartlink': 'Smartlink system -2',
                'Target Position': 'Prone at short range -2 (SR2), prone at long range +1, unconscious -6',
                'Defender Moving': 'Target running +2',
                'Friends in Melee': 'Target engaged in melee at short range +2',
                'Called Shot': 'Aiming for specific location +4',
                'Visibility': 'Light level penalties (partial +1, dim +2, dark +4)',
                'Wounds': 'Light +1, Moderate +2, Serious +3',
                'Gyro Stabilization': 'Reduces movement and recoil penalties',
                'Situational': 'GM discretion for special circumstances'
            }
        else:
            return {
                'Reach': 'Reach advantage/disadvantage (±1 per point difference)',
                'Attacker Position': 'Attacker prone +2',
                'Target Position': 'Defender prone -2, unconscious -6',
                'Visibility': 'Light level penalties (partial +1, dim +2, dark +4)',
                'Wounds': 'Light +1, Moderate +2, Serious +3',
                'Situational': 'GM discretion for special circumstances'
            }

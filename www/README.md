# Shadowrun 2nd Edition PHP API

Complete API documentation for dice rolling and combat modifier calculations.

**Base URL:** `https://shadowrun2.com/dice/api.php`

---

## Table of Contents

1. [Dice Rolling API](#dice-rolling-api)
2. [Combat Modifier API](#combat-modifier-api)
3. [SR2-Specific Rules](#sr2-specific-rules)
4. [Integration Examples](#integration-examples)
5. [Error Handling](#error-handling)

---

## Dice Rolling API

### Basic Roll

Roll dice with standard notation (supports exploding dice with `!`).

**Endpoint:** `?action=roll`

**Parameters:**
- `notation` (required): Dice notation (e.g., "2d6", "1d20+5", "4d6!" for exploding)

**Example:**
```bash
curl "https://shadowrun2.com/dice/api.php?action=roll&notation=2d6"
```

---

### Roll with Target Number (Shadowrun-style)

Roll dice and count successes against a target number.

**Endpoint:** `?action=roll_target_number` or `?action=roll_tn`

**Parameters:**
- `notation` (required): Dice notation (e.g., "6d6!" for exploding)
- `tn` (required): Target number for success

**Example:**
```bash
curl "https://shadowrun2.com/dice/api.php?action=roll_tn&notation=6d6!&tn=5"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "notation": "6d6!",
    "rolls": [4, 6, 8, 3, 5, 2],
    "total": 28,
    "successes": 3,
    "target_number": 5,
    "result": "3 successes"
  }
}
```

---

### Opposed Roll

Opposed roll between two sets of dice.

**Endpoint:** `?action=roll_opposed`

**Parameters:**
- `notation1`, `tn1`: First roller's dice and target number
- `notation2`, `tn2`: Opponent's dice and target number

**Example:**
```bash
curl "https://shadowrun2.com/dice/api.php?action=roll_opposed&notation1=6d6!&tn1=5&notation2=4d6!&tn2=4"
```

---

### Roll with Dice Pools

Roll with multiple dice pools (skill, combat pool, karma pool, etc.).

**Endpoint:** `?action=roll_with_pools`

**Method:** POST (JSON recommended)

**Parameters:**
```json
{
  "action": "roll_with_pools",
  "pools": [
    {"name": "Firearms", "notation": "6d6!"},
    {"name": "Combat Pool", "notation": "4d6!"}
  ],
  "target_number": 5
}
```

---

### Opposed Roll with Pools

General-purpose opposed test with dice pools.

**Endpoint:** `?action=roll_opposed_pools`

**Method:** POST (JSON recommended)

**Parameters:**
```json
{
  "action": "roll_opposed_pools",
  "side1": {
    "label": "Attacker",
    "pools": [{"name": "Firearms", "notation": "6d6!"}],
    "target_number": 5
  },
  "side2": {
    "label": "Defender",
    "pools": [{"name": "Body", "notation": "5d6"}],
    "target_number": 4
  }
}
```

---

### Initiative Tracking

Track initiative for multiple characters with phase breakdown.

**Endpoint:** `?action=track_initiative`

**Method:** POST (JSON recommended)

**Parameters:**
```json
{
  "action": "track_initiative",
  "characters": [
    {"name": "Samurai", "notation": "2d6+10"},
    {"name": "Mage", "notation": "3d6+8"}
  ]
}
```

---

### Karma Pool Actions

#### Buy Karma Dice

**Endpoint:** `?action=buy_karma_dice`

**Parameters:**
- `karma_dice_count`: Number of karma dice to buy
- `target_number`: Target number
- `max_allowed`: Optional maximum allowed

#### Buy Successes

**Endpoint:** `?action=buy_successes`

**Parameters:**
- `current_successes`: Current number of successes
- `successes_to_buy`: Number of successes to purchase

#### Avoid Disaster (Reroll all 1s)

**Endpoint:** `?action=avoid_disaster`

**Parameters:**
- `roll_result`: The roll result object with `all_ones=true`

---

## Combat Modifier API

### Calculate Ranged Combat TN

Calculate the target number for a ranged combat attack with all applicable modifiers.

**Endpoint:** `?action=calculate_ranged_tn`

**Method:** POST (recommended)

**Parameters:**

```json
{
  "weapon": {
    "name": "Ares Predator",           // Optional: weapon name
    "type": "heavy pistol",            // Optional: weapon type
    "smartlink": true,                 // Optional: has smartlink (default: false)
    "recoilComp": 2,                   // Optional: recoil compensation (default: 0)
    "gyroStabilization": 0             // Optional: gyro rating (default: 0)
  },
  "range": "short",                    // Required: short|medium|long|extreme
  "attacker": {
    "hasSmartlink": true,              // Optional: has smartlink cyberware
    "strength": 6,                     // Optional: for strength-based recoil comp
    "movement": "walking",             // Optional: walking|running
    "woundLevel": "light",             // Optional: light|moderate|serious|deadly
    "vision": {
      "lowLight": true,                // Optional: has low-light vision
      "thermographic": false,          // Optional: has thermographic vision
      "ultrasound": false              // Optional: has ultrasound
    }
  },
  "defender": {
    "conscious": true,                 // Optional: is target conscious (default: true)
    "prone": false,                    // Optional: is target prone
    "movement": "running",             // Optional: target movement
    "inMeleeCombat": false             // Optional: target in melee combat
  },
  "situation": {
    "recoil": 3,                       // Optional: cumulative recoil
    "useStrengthRecoil": true,         // Optional: use Strength/3 for recoil comp (house rule)
    "dualWielding": false,             // Optional: using two weapons
    "calledShot": false,               // Optional: called shot
    "lightLevel": "normal",            // Optional: normal|partial|dim|dark
    "conditions": {
      "smoke": "heavy",                // Optional: smoke (heavy or light)
      "fog": "light"                   // Optional: fog (heavy or light)
    },
    "modifier": 0,                     // Optional: GM discretion modifier
    "modifierReason": "Custom reason"  // Optional: reason for modifier
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "baseTN": 4,
    "modifiers": [
      {
        "type": "Smartlink",
        "value": -2,
        "explanation": "Smartlink system"
      },
      {
        "type": "Target Position",
        "value": -2,
        "explanation": "Target prone at short range"
      }
    ],
    "totalModifier": -4,
    "finalTN": 2,
    "summary": "Smartlink: -2 (Smartlink system)\nTarget Position: -2 (Target prone at short range)"
  }
}
```

---

### Calculate Melee Combat TN

Calculate the target number for a melee combat attack.

**Endpoint:** `?action=calculate_melee_tn`

**Method:** POST (recommended)

**Parameters:**

```json
{
  "attacker": {
    "prone": false,                    // Optional: attacker prone
    "woundLevel": "light",             // Optional: wound level
    "naturalReach": 0                  // Optional: natural reach (trolls = 1)
  },
  "defender": {
    "conscious": true,                 // Optional: defender conscious
    "prone": false,                    // Optional: defender prone
    "naturalReach": 0                  // Optional: natural reach
  },
  "attackerWeapon": {
    "reach": 1                         // Optional: weapon reach (default: 0)
  },
  "defenderWeapon": {
    "reach": 0                         // Optional: weapon reach
  },
  "situation": {
    "lightLevel": "normal",            // Optional: light level
    "conditions": {},                  // Optional: environmental conditions
    "modifier": 0,                     // Optional: GM modifier
    "modifierReason": ""               // Optional: reason
  }
}
```

---

### Determine Range Category

Determine the range category based on distance and weapon type.

**Endpoint:** `?action=determine_range`

**Parameters:**
- `distance` (required): Distance to target in meters
- `weapon_type` (required): Weapon type (e.g., "heavy pistol", "assault rifle")

**Supported Weapon Types:**
- `hold-out pistol`, `light pistol`, `heavy pistol`
- `smg`, `shotgun`, `assault rifle`, `lmg`
- `sporting rifle`, `sniper rifle`

**Example:**
```bash
curl "https://shadowrun2.com/dice/api.php?action=determine_range&distance=25&weapon_type=heavy%20pistol"
```

---

### List Light Levels

Get all available light levels and their modifier values.

**Endpoint:** `?action=list_light_levels`

**Response:**
```json
{
  "success": true,
  "data": {
    "NORMAL": {"modifier": 0, "name": "Normal Light"},
    "PARTIAL": {"modifier": 1, "name": "Partial Light"},
    "DIM": {"modifier": 2, "name": "Dim Light"},
    "DARK": {"modifier": 4, "name": "Total Darkness"}
  }
}
```

---

### Explain Combat Modifiers

Get detailed explanations of all combat modifiers.

**Endpoint:** `?action=explain_combat_modifiers`

**Parameters:**
- `combat_type` (optional): `ranged` or `melee` (default: `ranged`)

---

## SR2-Specific Rules

### Key Differences from SR3

1. **Prone Targets at Short Range:** -2 TN (SR3 uses -1)
2. **EX Ammo Bonus:** +2 TN (SR3 uses +1)
3. **Light Level System:** 4-tier system (Normal/Partial/Dim/Dark)
4. **Unconscious Targets:** -6 TN

### Range Categories by Weapon Type

| Weapon Type | Short | Medium | Long | Extreme |
|-------------|-------|--------|------|---------|
| Hold-out/Light Pistol | 15m | 30m | 45m | 60m |
| Heavy Pistol | 20m | 30m | 40m | 60m |
| SMG | 40m | 80m | 120m | 160m |
| Shotgun | 20m | 40m | 60m | 80m |
| Sporting Rifle | 60m | 120m | 180m | 240m |
| Sniper Rifle | 80m | 160m | 240m | 320m |
| Assault Rifle | 40m | 80m | 120m | 160m |
| LMG | 40m | 80m | 120m | 160m |

### Base Target Numbers

- **Short Range:** TN 4
- **Medium Range:** TN 5
- **Long Range:** TN 6
- **Extreme Range:** TN 9
- **Melee Combat:** TN 4 (always)

### Vision Enhancements

- **Low-Light Vision:** Reduces light penalties by half (round down)
- **Thermographic Vision:** Reduces light penalties to maximum of +1
- **Ultrasound:** Ignores all light penalties completely

### Optional House Rules

#### Strength-Based Recoil Compensation

When `useStrengthRecoil` is set to `true`, the attacker's Strength attribute provides additional recoil compensation:

- **Formula:** Strength ÷ 3 (round down) = additional recoil compensation
- **Example:** Strength 6 = +2 recoil comp, Strength 9 = +3 recoil comp
- **Stacks with:** Weapon recoil compensation and gyro stabilization

**Example:**
```json
{
  "action": "calculate_ranged_tn",
  "weapon": {"recoilComp": 2},
  "range": "short",
  "attacker": {"strength": 6},
  "situation": {
    "recoil": 5,
    "useStrengthRecoil": true
  }
}
```

Result: Weapon comp (2) + Strength comp (2) = 4 total, so 5 - 4 = 1 TN penalty

---

## Integration Examples

### Node.js (axios)

```javascript
const axios = require('axios');

async function calculateRangedTN() {
  const response = await axios.post('https://shadowrun2.com/dice/api.php', {
    action: 'calculate_ranged_tn',
    weapon: { smartlink: true },
    range: 'short',
    attacker: { hasSmartlink: true },
    defender: { prone: true },
    situation: {}
  });
  
  console.log(response.data.data.finalTN); // 2
}
```

### Python (requests)

```python
import requests

response = requests.post('https://shadowrun2.com/dice/api.php', json={
    'action': 'calculate_ranged_tn',
    'weapon': {'smartlink': True},
    'range': 'short',
    'attacker': {'hasSmartlink': True},
    'defender': {'prone': True},
    'situation': {}
})

data = response.json()
print(data['data']['finalTN'])  # 2
```

### JavaScript (fetch)

```javascript
const response = await fetch('https://shadowrun2.com/dice/api.php', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'calculate_ranged_tn',
    weapon: { smartlink: true },
    range: 'short',
    attacker: { hasSmartlink: true },
    defender: { prone: true },
    situation: {}
  })
});

const data = await response.json();
console.log(data.data.finalTN); // 2
```

### cURL

```bash
curl -X POST https://shadowrun2.com/dice/api.php \
  -H "Content-Type: application/json" \
  -d '{
    "action": "calculate_ranged_tn",
    "weapon": {"smartlink": true},
    "range": "short",
    "attacker": {"hasSmartlink": true},
    "defender": {"prone": true},
    "situation": {}
  }'
```

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

Common errors:
- Missing required parameters
- Invalid range category
- Invalid weapon type
- Invalid light level
- Invalid dice notation

---

## Rate Limiting

Currently no rate limiting is enforced, but please be respectful:
- Maximum 100 requests per minute recommended
- Use connection pooling for multiple requests
- Cache results when appropriate

---

## Getting Help

For a complete list of all available endpoints:

```bash
curl "https://shadowrun2.com/dice/api.php?action=help"
```

This returns a JSON response with all available actions and their parameters.

---

## Support

- **GitHub:** [shadowrun-gm repository](https://github.com/Nyxll/shadowrun-gm)
- **Issues:** Report bugs or request features via GitHub Issues
- **API Status:** Use `?action=help` to verify API availability

---

## Files

- `api.php` - Main API endpoint handler
- `DiceRoller.php` - Dice rolling engine
- `CombatModifiers.php` - Combat modifier calculations
- `README.md` - This documentation

---

## License

Part of the Shadowrun GM Assistant project. See main repository for license details.

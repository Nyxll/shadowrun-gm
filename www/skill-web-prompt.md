# Shadowrun Skill Web Defaulting Calculator

## Purpose

This prompt guides the calculation of target number modifiers when a character defaults on a skill using the Shadowrun Skill Web system.

## Instructions for AI

Please calculate the target number modifier for defaulting on the Shadowrun Skill Web. I will provide a starting skill/attribute and an ending skill. Your response should include the following:

1. **The complete, step-by-step path** from the starting node to the ending node
2. **The total number of dots (circles)** on that path
3. **The final target number modifier**

## Important Rules

- Each dot on the path adds a **+2 modifier** to the target number
- The **shortest path** should always be used
- Use the `skill-web.json` file as the definitive map of the skill web
- Nodes prefixed with `dot_` represent connection points (dots/circles) in the web
- Actual skills and attributes are named nodes (e.g., "Firearms", "QUICKNESS", "Athletics")

## Example Calculation

**From: QUICKNESS → To: Firearms**

Path: QUICKNESS → dot_p4 → dot_p5 → Firearms
- Dots traversed: dot_p4, dot_p5 (2 dots)
- Modifier: 2 dots × +2 = **+4 to target number**

## Graph Structure

The skill web is stored in `skill-web.json` as a directed graph where:
- Each node has a list of connections
- Each connection has a destination and a cost (in dots)
- Cost of 0 means direct connection (no dots between)
- Cost of 2 means one dot between nodes

## Usage

When a character attempts to use a skill they don't have, they can default from:
1. A related skill (follow the skill web)
2. The linked attribute (if the skill connects to an attribute)

The AI should use the skill web graph data to find the shortest path and calculate the total modifier.

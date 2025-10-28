#!/usr/bin/env python3
"""Test cyberdeck data in API response"""
import requests
import json

# Test Manticore's character sheet
response = requests.get('http://localhost:8001/api/character/Manticore')

if response.status_code == 200:
    data = response.json()
    
    print("=== MANTICORE CYBERDECKS ===\n")
    
    cyberdecks = data.get('cyberdecks', [])
    
    if cyberdecks:
        for deck in cyberdecks:
            print(f"Deck: {deck.get('deck_name')}")
            print(f"  MPCP: {deck.get('mpcp')}")
            print(f"  Hardening: {deck.get('hardening')}")
            print(f"  Memory: {deck.get('memory')} MP")
            print(f"  Storage: {deck.get('storage')} MP" if deck.get('storage') else "")
            print(f"  I/O Speed: {deck.get('io_speed')}" if deck.get('io_speed') else "")
            print(f"  Response Increase: +{deck.get('response_increase')}" if deck.get('response_increase') else "")
            
            persona = deck.get('persona_programs', {})
            if persona:
                print(f"  Persona Programs:")
                for prog, rating in persona.items():
                    print(f"    {prog.title()}: {rating}")
            
            utilities = deck.get('utilities', {})
            if utilities:
                print(f"  Utilities:")
                for util, data in utilities.items():
                    print(f"    {util}: {data}")
            
            ai = deck.get('ai_companions', [])
            if ai:
                print(f"  AI Companions: {', '.join(ai)}")
            
            print()
    else:
        print("No cyberdecks found!")
        print("\nFull response keys:", list(data.keys()))
else:
    print(f"Error: {response.status_code}")
    print(response.text)

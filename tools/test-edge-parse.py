#!/usr/bin/env python3
import re

def parse_markdown_section(content, section_name):
    """Extract a section from markdown content"""
    pattern = rf'##\s+{re.escape(section_name)}(?:\s*\([^)]*\))?\s*\n(.*)(?=\n##|\Z)'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def parse_edges_flaws(content):
    """Parse Edges and Flaws section"""
    edges = []
    flaws = []
    
    section = parse_markdown_section(content, "Edges and Flaws")
    
    # Parse Edges - stop at next ### subsection, --- separator, or end
    edges_match = re.search(r'###\s+Edges(.*?)(?=\n###|\n---|\Z)', section, re.DOTALL | re.IGNORECASE)
    if edges_match:
        print(f"EDGES SECTION FOUND: {edges_match.group(1)[:100]}")
        for line in edges_match.group(1).split('\n'):
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(.+)', line)
            if match:
                name = match.group(1).strip()
                desc = match.group(2).strip()
                print(f"  MATCHED: {name} -> {desc}")
                edges.append({'name': name, 'description': desc})
    else:
        print("NO EDGES SECTION FOUND")
    
    # Parse Flaws - stop at next ### subsection, --- separator, or end
    flaws_match = re.search(r'###\s+Flaws(.*?)(?=\n###|\n---|\Z)', section, re.DOTALL | re.IGNORECASE)
    if flaws_match:
        print(f"FLAWS SECTION FOUND: {flaws_match.group(1)[:100]}")
        for line in flaws_match.group(1).split('\n'):
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(.+)', line)
            if match:
                name = match.group(1).strip()
                desc = match.group(2).strip()
                print(f"  MATCHED: {name} -> {desc}")
                flaws.append({'name': name, 'description': desc})
    else:
        print("NO FLAWS SECTION FOUND")
    
    return edges, flaws

# Test with Axel
content = open('characters/Axel.md', encoding='utf-8').read()
edges, flaws = parse_edges_flaws(content)
print(f"\nRESULT: {len(edges)} edges, {len(flaws)} flaws")

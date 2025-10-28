import re

with open('data-load-final-1.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# Test different patterns
pattern1 = r"'\[\]'::jsonb"
pattern2 = r"'\[\]'::jsonb,\s*'\{\}'::jsonb"

matches1 = re.findall(pattern1, content)
matches2 = re.findall(pattern2, content)

print(f"Pattern 1 matches: {len(matches1)}")
print(f"Pattern 2 matches: {len(matches2)}")

# Show first metatype INSERT
metatype_match = re.search(r'INSERT INTO metatypes.*?;', content, re.DOTALL)
if metatype_match:
    print("\nFirst metatype INSERT:")
    print(metatype_match.group(0)[:500])

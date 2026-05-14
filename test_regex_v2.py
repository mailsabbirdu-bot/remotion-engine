import re

content = """
**Narrator:** It took a SpaceX rocket to get them there, but it took the vision of a nation to stay there.
[Scene: Rocket launch]
[Narrator: Another block here.]
**বর্ণনাকারী:** এটি একটি পরীক্ষা।
Scene 2: End.
"""

# Even more robust pattern for varied formats
pattern = r"(?im)^[\[\* ]*(Narrator|বর্ণনাকারী)[\:\*\] ]+\s*(.*?)(?=\s*\]?\n\s*(?:\[|\*\*|Narrator|বর্ণনাকারী|Scene|দৃশ্য|Music|সঙ্গীত|={5,})|\Z)"

def get_original_block(match, content):
    # Find where the block actually ends (including closing bracket if any)
    start = match.start()
    end = match.end()
    # Check if there's a trailing bracket right after the text
    if end < len(content) and content[end] == ']':
         end += 1
    return content[start:end]

matches = list(re.finditer(pattern, content, re.DOTALL))
print(f"Found {len(matches)} matches.")
for i, m in enumerate(matches):
    print(f"Match {i+1}: Label='{m.group(1)}', Text='{m.group(2).strip()}'")
    print(f"Full Block: '{get_original_block(m, content).strip()}'")

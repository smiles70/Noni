import sys

# Read v3 content from stdin
content = sys.stdin.read()

with open(r'C:\Users\travel\CascadeProjects\Noni\.windsurf\workflows\the-process.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done. File written.")

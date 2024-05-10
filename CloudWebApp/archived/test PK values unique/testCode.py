#Code adapted from ChatGPT

import json

# Load the JSON file
with open("C:/Users/harol/OneDrive/Desktop/RMIT/S3-03 Cloud Computing/Ass 1/CCass1projectDirectory/musicSubApp/a1.json", 'r') as f:
    data = json.load(f)

# Create a set to store unique song titles
unique_titles = set()

# List to store duplicate titles
duplicate_titles = []

# Iterate over the song entries
for song in data['songs']:
    title = song['title']
    if title in unique_titles:
        duplicate_titles.append(title)
    else:
        unique_titles.add(title)

# Check if there are any duplicate titles
if duplicate_titles:
    print("Duplicate titles found:")
    for title in duplicate_titles:
        print(title)
else:
    print("No duplicate titles found.")

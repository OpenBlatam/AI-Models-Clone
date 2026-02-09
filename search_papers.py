import json
import sys

keyword = "Prompt Engineering"

try:
    # Set stdout to utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    with open('agents/backend/onyx/server/features/gamma_app/data/training_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i, paper in enumerate(data):
            if keyword.lower() in paper['title'].lower() or keyword.lower() in paper['content'].lower()[:500]:
                print(f"Index: {i} | Title: {paper['title']}")
except Exception as e:
    print(f"Error: {e}")

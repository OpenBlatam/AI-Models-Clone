import json

try:
    with open('agents/backend/onyx/server/features/gamma_app/data/training_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i, paper in enumerate(data):
            print(f"{i}: {paper.get('title', 'No Title')}")
except Exception as e:
    print(f"Error: {e}")

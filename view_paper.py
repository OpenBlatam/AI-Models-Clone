import json
import sys

target_index = 15

try:
    # Set stdout to utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    with open('agents/backend/onyx/server/features/gamma_app/data/training_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        if 0 <= target_index < len(data):
            print(f"TITLE: {data[target_index]['title']}")
            print("-" * 50)
            print(data[target_index]['content'][:3000])
        else:
            print("Index out of range")
except Exception as e:
    print(f"Error: {e}")

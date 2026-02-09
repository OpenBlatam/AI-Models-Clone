import shutil
import os

source_dir = "c:/blatam-academy/agents/backend/onyx/server/features/stake_casino_ai"
output_filename = "c:/blatam-academy/stake_casino_ai_v2"

print(f"Zipping {source_dir} to {output_filename}.zip...")
try:
    shutil.make_archive(output_filename, 'zip', source_dir)
    print(f"Successfully created {output_filename}.zip")
except Exception as e:
    print(f"Failed to create zip: {e}")

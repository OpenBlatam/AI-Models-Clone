import shutil
import os

def create_package():
    source_dir = r"c:\blatam-academy\agents\backend\onyx\server\features\marketing_intelligence_ai"
    output_filename = r"c:\blatam-academy\marketing_intelligence_ai_v2"
    
    print(f"Zipping {source_dir} to {output_filename}.zip...")
    try:
        shutil.make_archive(output_filename, 'zip', source_dir)
        print("Package created successfully.")
    except Exception as e:
        print(f"Failed to create package: {e}")

if __name__ == "__main__":
    create_package()

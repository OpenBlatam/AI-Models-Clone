import zipfile
import os

zip_path = r"c:\blatam-academy\agents\backend\onyx\server\features\lovable\lovable_feature_complete.zip"
extract_to = r"c:\blatam-academy\agents\backend\onyx\server\features\lovable"

print(f"Extracting {zip_path} to {extract_to}...")

try:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")
except Exception as e:
    print(f"Error extracting zip: {e}")

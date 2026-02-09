import os
import zipfile

base_dir = r"c:\blatam-academy\agents\backend\onyx\server\features\lovable"
zip_path = os.path.join(base_dir, "lovable_feature_complete.zip")

print(f"--- Listing directory: {base_dir} ---")
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".zip"): continue
        print(os.path.join(root, f))
    # Don't recurse too deep if many files, but lovable seems empty-ish
    # if "node_modules" in dirs: dirs.remove("node_modules")

print(f"\n--- Inspecting Zip: {zip_path} ---")
if os.path.exists(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Print first 20 files to get an idea of structure
            namelist = z.namelist()
            print(f"Total files in zip: {len(namelist)}")
            print("First 50 files:")
            for n in namelist[:50]:
                print(n)
            
            # Check for PDFs or "papers"
            print("\n--- Searching for 'papers' or '.pdf' in zip ---")
            for n in namelist:
                if "papers" in n.lower() or n.endswith(".pdf"):
                    print(n)
    except Exception as e:
        print(f"Error reading zip: {e}")
else:
    print("Zip file not found.")

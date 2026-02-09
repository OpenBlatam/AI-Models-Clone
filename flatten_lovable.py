import shutil
import os

base_dir = r"c:\blatam-academy\agents\backend\onyx\server\features\lovable"
nested_dir = os.path.join(base_dir, "lovable")

if os.path.exists(nested_dir):
    print(f"Moving contents of {nested_dir} to {base_dir}...")
    for item in os.listdir(nested_dir):
        src = os.path.join(nested_dir, item)
        dst = os.path.join(base_dir, item)
        
        if os.path.exists(dst):
            if os.path.isdir(dst):
                # If dir exists, we might need to merge. 
                # For simplicity in this script, let's use a recursive copy-tree style or just move and overwrite/merge
                # shutil.move fails if dst dir exists.
                # So we use copytree with dirs_exist_ok=True (Python 3.8+) or manual walk
                print(f"Merging directory {src} -> {dst}")
                # shutil.copytree(src, dst, dirs_exist_ok=True) # Check python version availability
                # Let's use a manual walk to be safe and verbose
                for root, dirs, files in os.walk(src):
                    rel_path = os.path.relpath(root, src)
                    target_root = os.path.join(dst, rel_path)
                    os.makedirs(target_root, exist_ok=True)
                    for f in files:
                        shutil.copy2(os.path.join(root, f), os.path.join(target_root, f))
                # Now remove the source dir
                shutil.rmtree(src)
            else:
                # Target is a file, overwrite
                print(f"Overwriting file {dst}")
                os.remove(dst)
                shutil.move(src, dst)
        else:
            # Target doesn't exist, just move
            print(f"Moving {src} -> {dst}")
            shutil.move(src, dst)
            
    # Clean up empty nested dir
    try:
        os.rmdir(nested_dir)
        print("Removed empty nested directory.")
    except Exception as e:
        print(f"Could not remove nested dir (might not be empty): {e}")

else:
    print(f"Nested directory {nested_dir} not found.")

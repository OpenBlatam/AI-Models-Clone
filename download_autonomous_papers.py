import subprocess
import os
import sys

# List of papers to download (Original Batch)
papers_legacy = [
    "Safely Interruptible Agents Orseau Armstrong",
    "Dynamic Safe Interruptibility for Decentralized Multi-Agent Reinforcement Learning",
    "Enough is Enough: Towards Autonomous Uncertainty-driven Stopping Criteria",
    "Selectively Quitting Improves LLM Agent Safety",
    "Morae: Proactively Pausing UI Agents for User Choices"
]

# List of papers to download (2025-2026 Batch)
papers_2025 = [
    "Learning to Yield and Request Control YRC",
    "Safe-ROS: An Architecture for Autonomous Robots",
    "Toward Safe and Responsible AI Agents",
    "AI-in-the-Loop Natarajan",
    "Variable Autonomy for Mobile Manipulators Contreras"
]

# Base Output directory
base_output_dir = os.path.join("agents", "backend", "onyx", "server", "features", "github_autonomous_agent", "papers")
os.makedirs(base_output_dir, exist_ok=True)

def download_batch(paper_list, subfolder=None):
    target_dir = os.path.join(base_output_dir, subfolder) if subfolder else base_output_dir
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"Downloading papers to {target_dir}...")

    for paper in paper_list:
        print(f"Processing: {paper}")
        try:
            # Using python -m PyPaperBot to ensure we use the installed module
            cmd = [
                sys.executable, "-m", "PyPaperBot",
                f"--query={paper}",
                f"--dwn-dir={target_dir}",
                "--min-year=2015",
                "--scholar-results=1"
            ]
            subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"Failed to download {paper}: {e}")

# Download Legacy
# download_batch(papers_legacy) # Already downloaded

# Download 2025 Batch
download_batch(papers_2025, subfolder="2025")

print("Download process completed.")

import os
import requests
import time

PAPERS = {
    "2503.23350": "A_Survey_of_WebAgents.pdf",
    "2507.21206": "Agentic_Web.pdf",
    "2507.10644": "From_Semantic_Web_to_Agentic_AI.pdf",
    "2410.16464": "Beyond_Browsing_API_Based_Web_Agents.pdf",
    "2510.10666": "BrowserAgent.pdf",
    "2307.13854": "WebArena.pdf",
    "2507.21504": "Evaluation_and_Benchmarking_of_LLM_Agents.pdf",
    "2412.14161": "TheAgentCompany.pdf",
    "2503.04957": "SafeArena.pdf",
    "2510.10073": "SecureWebArena.pdf"
}

OUTPUT_DIR = r"c:\blatam-academy\agents\backend\onyx\server\features\lovable\data\papers"

def download_file(url, filepath):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {filepath}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    for arxiv_id, filename in PAPERS.items():
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"File already exists: {filename}")
            continue
            
        print(f"Downloading {filename} from {url}...")
        if download_file(url, filepath):
            time.sleep(1) # Be nice to arXiv
        else:
            print(f"Skipping {filename}")

if __name__ == "__main__":
    main()

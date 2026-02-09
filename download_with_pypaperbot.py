from PyPaperBot.Crossref import getPapersInfoFromDOIs
from PyPaperBot.Downloader import downloadPapers
import os

# Read DOIs
doi_file = r'agents/backend/onyx/server/features/dermatology_ai/dois.txt'
if not os.path.exists(doi_file):
    print(f"DOI file not found: {doi_file}")
    exit(1)

with open(doi_file, 'r') as f:
    dois = [line.strip() for line in f if line.strip()]

print(f"Found {len(dois)} DOIs")

# Get Paper Info
try:
    print("Attempting with list of strings...")
    try:
        papers = getPapersInfoFromDOIs(dois, restrict=0)
        print(f"Success with list! Retrieved {len(papers)} papers")
    except Exception as e:
        print(f"Failed with list: {e}")
        
        print("Attempting with single string (comma separated)...")
        try:
            papers = getPapersInfoFromDOIs(",".join(dois), restrict=0)
            print(f"Success with string! Retrieved {len(papers)} papers")
        except Exception as e:
            print(f"Failed with string: {e}")
            
            print("Attempting loop with single items...")
            papers = []
            for doi in dois:
                try:
                    p = getPapersInfoFromDOIs(doi, restrict=0)
                    if p:
                        # Check if p is a list or single object
                        if isinstance(p, list):
                            papers.extend(p)
                        else:
                            papers.append(p)
                        print(f"Found info for {doi}")
                    else:
                        print(f"No info found for {doi}")
                except Exception as e:
                    print(f"Failed for {doi}: {e}")
            print(f"Loop retrieved {len(papers)} papers")

    # Download
    output_dir = r"data/papers/dermatology"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if papers:
        downloadPapers(papers, dwnl_dir=output_dir, num_limit=len(papers))
    else:
        print("No papers to download.")
except Exception as e:
    print(f"Global Error: {e}")

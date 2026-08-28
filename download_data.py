import gdown
import os
import zipfile
from pathlib import Path

def main():
    url = "https://drive.google.com/drive/folders/1yOAc9DaJ86oLReaSKdnATR3dHiCQyhwn?usp=sharing"
    
    print("Attempting to download folder from Google Drive...")
    print("Note: Google Drive frequently blocks automated folder downloads. If this fails, please download the folder manually.")
    
    output_dir = "data_downloaded"
    
    try:
        gdown.download_folder(url, quiet=False, use_cookies=False, output=output_dir)
        print(f"Download attempted. Check the '{output_dir}' directory.")
        print("Please move the contents into 'data/artists' and 'data/briefs' accordingly.")
    except Exception as e:
        print(f"Failed to download automatically: {e}")
        print("\n--- MANUAL INSTRUCTIONS ---")
        print("1. Go to: " + url)
        print("2. Click 'Download all' in the top right corner.")
        print("3. Extract the ZIP file.")
        print("4. Place the artist folders in: D:\\Sekeron_Project\\data\\artists\\")
        print("5. Place the brief files in: D:\\Sekeron_Project\\data\\briefs\\")

if __name__ == "__main__":
    main()

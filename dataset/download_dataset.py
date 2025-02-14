import shutil
import argparse
import kagglehub

def download_megaGymDataset(download_dir):
    '''
    Download megaGymDataset dataset from Kaggle and move it to the specified download directory.
    '''
    path = kagglehub.dataset_download("niharika41298/gym-exercise-data")

    print("Path to dataset files:", path)

    shutil.move(path, download_dir)
    print("Dataset downloaded successfully!")

def main():
    '''
    Main function to download datasets.
    '''
    parser = argparse.ArgumentParser(description="Datasets Downloader Tool.")
    
    parser.add_argument('--megaGymDataset', action='store_true', help="Download megaGymDataset dataset")
    parser.add_argument('--download_dir', required=False, type=str, default=".", help="Directory to download datasets")
    
    args = parser.parse_args()

    if args.megaGymDataset:
        download_path = f"{args.download_dir}/megaGymDataset"
        print(f"Downloading megaGymDataset dataset to [{download_path}]...")
        download_megaGymDataset(download_path)

if __name__ == '__main__':
    main()

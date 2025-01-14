import boto3
import os
import concurrent.futures
from botocore.config import Config
from botocore.exceptions import ClientError
import time

class GameAssetManager:
    def __init__(self):
        # Configure boto3 with retries and timeouts
        config = Config(
            retries = dict(
                max_attempts = 3,
                mode = 'adaptive'
            ),
            connect_timeout = 5,
            read_timeout = 10
        )
        self.s3 = boto3.client('s3', config=config)
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'game-assets')
        self.cache_dir = 'local_assets'
        self.ensure_cache_dir()
        
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def is_available(self):
        """Check if S3 connection is available"""
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            return True
        except Exception:
            return False

    def list_assets(self):
        """List all assets in the S3 bucket"""
        if not self.is_available():
            print("S3 is not available")
            return []

        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            print(f"Error listing assets: {e}")
            return []

    def is_asset_cached(self, filename):
        """Check if asset exists in local cache"""
        cache_path = os.path.join(self.cache_dir, filename)
        return os.path.exists(cache_path)

    def get_cached_path(self, filename):
        """Get the local path for a cached asset"""
        return os.path.join(self.cache_dir, filename)

    def download_asset(self, filename, force_download=False):
        """Download a game asset from S3 with caching"""
        cache_path = os.path.join(self.cache_dir, filename)
        
        # Return cached version if it exists and force_download is False
        if not force_download and self.is_asset_cached(filename):
            return cache_path

        if not self.is_available():
            print("S3 is not available")
            return None

        try:
            # Ensure the directory structure exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            # Download the file
            self.s3.download_file(self.bucket_name, filename, cache_path)
            return cache_path
        except Exception as e:
            print(f"Error downloading {filename}: {str(e)}")
            return None

    def download_assets_parallel(self, filenames, max_workers=4):
        """Download multiple assets in parallel"""
        def download_single(filename):
            return self.download_asset(filename)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_filename = {executor.submit(download_single, filename): filename 
                                for filename in filenames}
            
            results = {}
            for future in concurrent.futures.as_completed(future_to_filename):
                filename = future_to_filename[future]
                try:
                    results[filename] = future.result()
                except Exception as e:
                    print(f"Error downloading {filename}: {str(e)}")
                    results[filename] = None
                    
            return results

    def create_asset_cache(self, cache_dir='local_assets'):
        """Create a local cache of all game assets"""
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
        
        # Get list of all assets
        assets = self.list_assets()
        if not assets:
            return False
            
        # Download all assets in parallel
        results = self.download_assets_parallel(assets)
        
        # Check if all downloads were successful
        return all(path is not None for path in results.values())
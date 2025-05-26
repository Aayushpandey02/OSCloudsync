from dotenv import load_dotenv
import os
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

# Load environment variables from .env
load_dotenv()

SUPABASE_URL = "https://bsypgbmogjznwrdypgts.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzeXBnYm1vZ2p6bndyZHlwZ3RzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyNzc5NDMsImV4cCI6MjA2Mzg1Mzk0M30.sBrIRtujn-qzgDVK-KtfIZ4da0CUF7upupD0khy5UcE"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing SUPABASE_URL or SUPABASE_KEY. Did you forget to create or configure the .env file?")

# Initialize Supabase client
options = ClientOptions(auto_refresh_token=True)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options)

def list_files_in_bucket(bucket: str, folder_path: str = ""):
    """List all files in a bucket/folder to see the actual file paths"""
    try:
        result = supabase.storage.from_(bucket).list(folder_path)
        print(f"📂 Files in bucket '{bucket}' (folder: '{folder_path}'):")
        for file in result:
            print(f"  - {file['name']}")
        return result
    except Exception as e:
        print(f"❌ Failed to list files: {e}")
        return None

def upload_file_to_supabase(bucket: str, file_path: str, dest_path: str):
    try:
        with open(file_path, "rb") as f:
            result = supabase.storage.from_(bucket).upload(dest_path, f)
        print(f"✅ Uploaded to Supabase: {dest_path}")
        return result
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None

def delete_file_from_supabase(bucket: str, file_path: str):
    """Enhanced delete function with comprehensive debugging"""
    try:
        print(f"\n🔍 === DEBUGGING FILE DELETION ===")
        print(f"🔍 Bucket: {bucket}")
        print(f"🔍 File path: '{file_path}'")
        
        # Step 1: Check if file exists by listing bucket contents
        print(f"\n📋 Step 1: Listing all files in bucket...")
        try:
            all_files = supabase.storage.from_(bucket).list()
            print(f"Found {len(all_files)} items in root:")
            for item in all_files:
                print(f"  📄 {item['name']} (type: {item.get('metadata', {}).get('mimetype', 'folder')})")
        except Exception as list_error:
            print(f"❌ Cannot list bucket contents: {list_error}")
            return None
        
        # Step 2: Try to get the file URL to verify existence
        print(f"\n🔗 Step 2: Checking if file exists by getting URL...")
        try:
            file_url = supabase.storage.from_(bucket).get_public_url(file_path)
            print(f"✅ File URL generated: {file_url}")
        except Exception as url_error:
            print(f"⚠️ Cannot generate URL: {url_error}")
        
        # Step 3: Attempt deletion with detailed error handling
        print(f"\n🗑️ Step 3: Attempting deletion...")
        try:
            # Try the deletion
            result = supabase.storage.from_(bucket).remove([file_path])
            print(f"Raw deletion result: {result}")
            
            # Parse the result
            if isinstance(result, list) and len(result) > 0:
                deletion_info = result[0]
                if 'error' in deletion_info and deletion_info['error']:
                    print(f"❌ Deletion failed with error: {deletion_info['error']}")
                    return None
                else:
                    print(f"✅ File deleted successfully!")
                    return result
            else:
                print(f"⚠️ Unexpected result format: {result}")
                return None
                
        except Exception as delete_error:
            print(f"❌ Exception during deletion: {delete_error}")
            print(f"❌ Error type: {type(delete_error)}")
            return None
            
    except Exception as e:
        print(f"❌ Overall deletion process failed: {e}")
        return None

def verify_file_exists(bucket: str, file_path: str):
    """Check if a file exists in Supabase storage"""
    try:
        # Method 1: Try to get file info
        try:
            info = supabase.storage.from_(bucket).list(os.path.dirname(file_path) or "")
            filename = os.path.basename(file_path)
            file_exists = any(item['name'] == filename for item in info)
            print(f"📋 File exists check: {file_exists}")
            return file_exists
        except Exception as e:
            print(f"⚠️ Could not verify file existence: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error in file verification: {e}")
        return False

def search_file_in_bucket(bucket: str, filename: str):
    """Recursively search for a file in the bucket"""
    def search_folder(folder_path=""):
        try:
            items = supabase.storage.from_(bucket).list(folder_path)
            found_files = []
            
            for item in items:
                item_path = f"{folder_path}/{item['name']}" if folder_path else item['name']
                
                if item['name'] == filename:
                    found_files.append(item_path)
                    print(f"🎯 Found file at: {item_path}")
                
                # If it's a folder, search recursively
                if item.get('metadata', {}).get('mimetype') is None:  # Likely a folder
                    found_files.extend(search_folder(item_path))
            
            return found_files
        except Exception as e:
            print(f"❌ Error searching folder '{folder_path}': {e}")
            return []
    
    print(f"🔍 Searching for '{filename}' in bucket '{bucket}'...")
    found = search_folder()
    if found:
        print(f"✅ Found {len(found)} instance(s) of '{filename}':")
        for path in found:
            print(f"  📍 {path}")
    else:
        print(f"❌ File '{filename}' not found in bucket")
    return found

def get_file_url(bucket: str, file_path: str):
    """Get the public URL of a file to verify it exists"""
    try:
        url = supabase.storage.from_(bucket).get_public_url(file_path)
        print(f"🔗 File URL: {url}")
        return url
    except Exception as e:
        print(f"❌ Failed to get URL: {e}")
        return None

# Example usage with comprehensive debugging:
if __name__ == "__main__":
    bucket_name = "your-bucket-name"  # Replace with your actual bucket name
    file_to_delete = "path/to/your/file.txt"  # Replace with actual path
    
    print("=" * 50)
    print("🚀 SUPABASE FILE DELETION DEBUGGING")
    print("=" * 50)
    
    # Step 1: List all files in the bucket
    print("\n📋 STEP 1: LISTING ALL FILES")
    list_files_in_bucket(bucket_name)
    
    # Step 2: Search for the specific file
    filename = os.path.basename(file_to_delete)
    print(f"\n🔍 STEP 2: SEARCHING FOR FILE '{filename}'")
    found_paths = search_file_in_bucket(bucket_name, filename)
    
    # Step 3: Verify file exists at expected path
    print(f"\n✅ STEP 3: VERIFYING FILE AT EXPECTED PATH")
    exists = verify_file_exists(bucket_name, file_to_delete)
    
    # Step 4: Attempt deletion
    print(f"\n🗑️ STEP 4: ATTEMPTING DELETION")
    if found_paths:
        print(f"Found file(s), trying to delete from: {found_paths[0]}")
        delete_file_from_supabase(bucket_name, found_paths[0])
    else:
        print(f"File not found, trying original path anyway: {file_to_delete}")
        delete_file_from_supabase(bucket_name, file_to_delete)
    
    print("\n" + "=" * 50)
    print("🏁 DEBUGGING COMPLETE")
    print("=" * 50)
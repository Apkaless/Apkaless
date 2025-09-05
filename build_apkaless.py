#!/usr/bin/env python3
"""
Build script for Apkaless.py using the built-in py2exe functionality
"""

import os
import sys
import subprocess

def build_apkaless():
    """Build Apkaless.py into an executable"""
    
    print("🚀 Building Apkaless.py into executable...")
    print("=" * 50)
    
    # Get the current directory
    current_dir = os.getcwd()
    apkaless_path = os.path.join(current_dir, "Apkaless.py")
    
    # Check if Apkaless.py exists
    if not os.path.exists(apkaless_path):
        print("❌ Apkaless.py not found!")
        return False
    
    print(f"📁 Source file: {apkaless_path}")
    print(f"📁 Output directory: {current_dir}")
    
    try:
        # Import the enhanced_py2exe function from Apkaless.py
        sys.path.insert(0, current_dir)
        
        # Set up the global variables that the function needs
        import os
        tool_parent_dir = os.getcwd()
        
        # Import the function
        from Apkaless import enhanced_py2exe
        
        print("\n🔧 Starting build process...")
        
        # Build Apkaless.py (no icon for now)
        result = enhanced_py2exe(apkaless_path, None)
        
        if result:
            print("\n✅ Build completed successfully!")
            print("📦 Executable should be in the 'dist' folder")
            
            # Check if dist folder exists and list contents
            dist_folder = os.path.join(current_dir, "dist")
            if os.path.exists(dist_folder):
                print(f"\n📂 Contents of {dist_folder}:")
                for item in os.listdir(dist_folder):
                    item_path = os.path.join(dist_folder, item)
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path)
                        print(f"  📄 {item} ({size:,} bytes)")
                    else:
                        print(f"  📁 {item}/")
            else:
                print("⚠️ Dist folder not found")
                
        else:
            print("\n❌ Build failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Build error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🎯 Apkaless Build Script")
    print("=" * 30)
    
    success = build_apkaless()
    
    if success:
        print("\n🎉 Build process completed!")
        print("💡 You can now run the executable from the dist folder")
    else:
        print("\n💥 Build process failed!")
        print("🔍 Check the error messages above for details")
    
    input("\nPress Enter to exit...")

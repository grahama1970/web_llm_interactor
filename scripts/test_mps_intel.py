#!/usr/bin/env python3
"""
Test script to verify MPS support on Intel Macs.

This script will:
1. Check system architecture
2. Set the required environment variable
3. Check if MPS is available
4. Run a simple tensor operation on MPS if available
"""

import os
import sys
import platform

def main():
    # Print system info
    system = platform.system()
    machine = platform.machine()
    python_version = platform.python_version()
    
    print("=" * 60)
    print("MPS Support Test for Intel Macs")
    print("=" * 60)
    print(f"System: {system}")
    print(f"Architecture: {machine}")
    print(f"Python: {python_version}")
    print("-" * 60)
    
    # Check if this is an Intel Mac
    is_intel_mac = system == "Darwin" and machine == "x86_64"
    if is_intel_mac:
        print("Intel Mac detected!")
    else:
        print("This is not an Intel Mac. Standard PyTorch MPS support should work if this is Apple Silicon.")
    
    # Set environment variable for Intel Mac MPS support
    if is_intel_mac:
        print("Setting PYTORCH_ENABLE_MPS_FALLBACK=1")
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    
    # Try to import torch
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        
        # Check if the version is suitable for Intel Mac MPS
        version = torch.__version__
        is_nightly = "dev" in version or "a0" in version
        
        if is_intel_mac and not is_nightly:
            print("WARNING: You're not using the nightly build of PyTorch.")
            print("MPS support for Intel Macs is only available in nightly builds.")
            print("Consider running: ./install_intel_mac.sh")
            
        # Check for MPS
        mps_exists = hasattr(torch.backends, 'mps')
        
        if not mps_exists:
            print("PyTorch was built without MPS support.")
            print("This is typical for older versions or non-macOS platforms.")
            return
        
        # Try to check MPS availability
        try:
            mps_available = torch.backends.mps.is_available()
            print(f"MPS available: {mps_available}")
            
            if is_intel_mac and not mps_available:
                print("MPS is not available on this Intel Mac.")
                print("Make sure you've set PYTORCH_ENABLE_MPS_FALLBACK=1")
                print("And installed the nightly build with: ./install_intel_mac.sh")
                return
                
            if mps_available:
                # Try a simple tensor operation on MPS
                print("\nTesting MPS with a simple tensor operation...")
                device = torch.device("mps")
                x = torch.ones(5, device=device)
                y = x + 1
                print(f"Tensor on {device}: {y}")
                print("\nSUCCESS! MPS is working correctly.")
                
                # Report memory usage if possible
                try:
                    if hasattr(torch.mps, 'current_allocated_memory'):
                        mem = torch.mps.current_allocated_memory() / 1024 / 1024
                        print(f"MPS memory allocated: {mem:.2f} MB")
                except:
                    pass
            else:
                print("MPS is not available. Using CPU instead.")
                
        except Exception as e:
            print(f"Error checking MPS availability: {e}")
            
    except ImportError:
        print("PyTorch is not installed.")
        print("Please run: ./install_intel_mac.sh")
        
if __name__ == "__main__":
    main()
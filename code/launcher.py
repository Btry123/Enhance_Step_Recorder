#!/usr/bin/env python3
"""
Enhanced Step Recorder Pro - Main Launcher
A comprehensive screen recording and documentation tool with advanced features.

Features:
- Smart screenshot capture with window change detection
- Mouse and keyboard analytics
- Workflow management with bookmarks and comments
- Multi-format export (DOCX, HTML, Markdown, JSON)
- Video timelapse creation
- Performance optimization
- Modern GUI with customtkinter
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog
import tkinter.filedialog
import tkinter.messagebox
import tkinter.colorchooser
import tkinter.commondialog
import tkinter.font
import tkinter.ttk

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing_deps = []
    
    required_deps = [
        ('pynput', 'pynput'),
        ('PIL', 'Pillow'),
        ('docx', 'python-docx'),
        ('psutil', 'psutil')
    ]
    
    optional_deps = [
        ('customtkinter', 'customtkinter'),
        ('cv2', 'opencv-python'),
        ('moviepy', 'moviepy'),
        ('easyocr', 'easyocr'),
        ('transformers', 'transformers'),
        ('torch', 'torch')
    ]
    
    # Check required dependencies
    for module, package in required_deps:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(package)
    
    # Check optional dependencies
    optional_missing = []
    for module, package in optional_deps:
        try:
            __import__(module)
        except ImportError:
            optional_missing.append(package)
    
    return missing_deps, optional_missing

def install_dependencies():
    """Install missing dependencies."""
    import subprocess
    
    missing_deps, optional_missing = check_dependencies()
    
    if missing_deps:
        print("Installing required dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_deps)
            print("Required dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install required dependencies.")
            return False
    
    if optional_missing:
        print("Installing optional dependencies for enhanced features...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + optional_missing)
            print("Optional dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("Some optional dependencies failed to install. Basic features will still work.")
    
    return True

def show_feature_summary():
    """Show a summary of available features."""
    # Removed message box - just print to console
    print("🎬 Enhanced Step Recorder Pro v2.0")
    print("All features are available and ready to use!")

def main():
    """Main launcher function."""
    print("🎬 Enhanced Step Recorder Pro v2.0")
    print("=" * 50)
    
    # Check dependencies
    missing_deps, optional_missing = check_dependencies()
    
    if missing_deps:
        print(f"Missing required dependencies: {', '.join(missing_deps)}")
        # Use GUI dialog instead of input()
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        response = messagebox.askyesno(
            "Missing Dependencies",
            f"Missing required dependencies: {', '.join(missing_deps)}\n\nWould you like to install them automatically?"
        )
        root.destroy()
        
        if response:
            if not install_dependencies():
                print("Failed to install dependencies. Please install manually:")
                print(f"pip install {' '.join(missing_deps)}")
                return
        else:
            print("Please install required dependencies manually:")
            print(f"pip install {' '.join(missing_deps)}")
            return
    
    if optional_missing:
        print(f"Optional dependencies missing: {', '.join(optional_missing)}")
        print("Enhanced features will be limited. Install with:")
        print(f"pip install {' '.join(optional_missing)}")
    
    # Show feature summary
    show_feature_summary()
    
    # Launch the main application
    try:
        from step_recorder_enhanced import EnhancedStepRecorder
        
        root = tk.Tk()
        app = EnhancedStepRecorder(root)
        
        print("Application started successfully!")
        print("Press Ctrl+C to exit or close the window.")
        
        root.mainloop()
        
    except ImportError as e:
        print(f"Error importing main application: {e}")
        print("Please ensure all files are in the same directory.")
        # Show error dialog instead of input()
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Import Error", f"Error importing main application: {e}\nPlease ensure all files are in the same directory.")
        root.destroy()
    except Exception as e:
        print(f"Error starting application: {e}")
        # Show error dialog instead of input()
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Error starting application: {e}")
        root.destroy()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Show error dialog instead of input()
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Unexpected Error", f"Unexpected error: {e}")
            root.destroy()
        except:
            pass  # If even the error dialog fails, just exit 
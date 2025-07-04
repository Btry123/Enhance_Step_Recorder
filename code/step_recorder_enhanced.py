import os
import queue
import time
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk

from PIL import ImageGrab, ImageDraw, ImageFont
from pynput import mouse, keyboard

from docx import Document
from docx.shared import Inches

# Import our new modules
from recorder_core import StepRecorderCore, RecordingSession
from exporters import ExportManager
from smart_capture import SmartCapture
from analytics import Analytics
from workflow_collaboration import WorkflowManager
from video_export import VideoExporter
from ai_documentation import AIDocumentation

# Optional imports
try:
    from docx2pdf import convert
    DOCX2PDF = True
except ImportError:
    DOCX2PDF = False

try:
    import win32gui
except ImportError:
    win32gui = None

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False


class EnhancedStepRecorder:
    """Enhanced step recorder with all advanced features integrated."""

    def __init__(self, master):
        self.master = master
        self.setup_window()
        
        # Initialize core recorder
        self.recorder = StepRecorderCore()
        
        # Initialize advanced features
        self.smart_capture = SmartCapture()
        self.analytics = Analytics()
        self.ai_documentation = AIDocumentation()
        self.workflow_manager = None  # Will be initialized when recording starts
        self.video_exporter = None    # Will be initialized when recording starts
        
        # Export manager
        self.export_manager = None
        
        # UI state
        self.save_path = None
        self.recording = False
        self.paused = False
        self.step = 0
        self.start_time = None
        self.total_steps = 0
        
        # Timer thread
        self.timer_running = False
        self.timer_thread = None
        
        # Create UI
        self.create_ui()
        
        # Set up callbacks
        self.setup_callbacks()
        
        # Set up cleanup on window close
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """Setup window properties."""
        if CTK_AVAILABLE:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            self.master.title("🎬 Enhanced Step Recorder Pro v2.0")
            
            # Make window full screen and resizable
            self.master.state('zoomed')  # Full screen on Windows
            self.master.resizable(True, True)
            
            # Set minimum size
            self.master.minsize(800, 600)
            
        else:
            self.master.title("Enhanced Step Recorder Pro v2.0")
            
            # Make window full screen and resizable
            self.master.state('zoomed')  # Full screen on Windows
            self.master.resizable(True, True)
            
            # Set minimum size
            self.master.minsize(700, 500)

    def create_ui(self):
        """Create the user interface."""
        if CTK_AVAILABLE:
            self.create_modern_ui()
        else:
            self.create_standard_ui()

    def create_modern_ui(self):
        """Create modern UI with customtkinter."""
        # Main container with scrollbar and responsive design
        main_frame = ctk.CTkScrollableFrame(self.master, width=1200, height=800)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid weights for responsive layout
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🎬 Enhanced Step Recorder Pro v2.0", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(0, 30))

        # Create a responsive grid layout
        # Top row: Timer and File Selection
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill="x", padx=10, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        
        # Timer Section (Left)
        timer_frame = ctk.CTkFrame(top_frame)
        timer_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.create_timer_section(timer_frame)
        
        # File Section (Right)
        file_frame = ctk.CTkFrame(top_frame)
        file_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.create_file_section(file_frame)
        
        # Middle row: Controls and AI Features
        middle_frame = ctk.CTkFrame(main_frame)
        middle_frame.pack(fill="x", padx=10, pady=10)
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(1, weight=1)
        
        # Control Section (Left)
        control_frame = ctk.CTkFrame(middle_frame)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.create_control_section(control_frame)
        
        # AI Features Section (Right)
        ai_frame = ctk.CTkFrame(middle_frame)
        ai_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.create_ai_features_section(ai_frame)
        
        # Bottom row: Advanced Features and Statistics
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        
        # Advanced Features Section (Left)
        advanced_frame = ctk.CTkFrame(bottom_frame)
        advanced_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.create_advanced_features_section(advanced_frame)
        
        # Statistics Section (Right)
        stats_frame = ctk.CTkFrame(bottom_frame)
        stats_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.create_stats_section(stats_frame)
        
        # Analytics Section (Full width)
        self.create_analytics_section(main_frame)
        
        # Instructions (Full width)
        self.create_instructions_section(main_frame)

    def create_timer_section(self, parent):
        """Create timer and progress section."""
        timer_label = ctk.CTkLabel(parent, text="⏱️ Recording Timer", font=ctk.CTkFont(size=18))
        timer_label.pack(pady=(15, 10))

        # Timer display
        self.timer_label = ctk.CTkLabel(
            parent, 
            text="00:00:00", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="lightgreen"
        )
        self.timer_label.pack(pady=10)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(parent)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)

        # Step counter
        self.step_label = ctk.CTkLabel(
            parent, 
            text="Steps: 0", 
            font=ctk.CTkFont(size=16)
        )
        self.step_label.pack(pady=10)

    def create_file_section(self, parent):
        """Create file selection section."""
        file_label = ctk.CTkLabel(parent, text="📁 Output File", font=ctk.CTkFont(size=18))
        file_label.pack(pady=(15, 10))

        self.select_file_btn = ctk.CTkButton(
            parent, 
            text="Choose Save Location", 
            command=self.select_save_path,
            fg_color="#2E8B57",
            hover_color="#228B22",
            height=40
        )
        self.select_file_btn.pack(pady=10)

        self.path_label = ctk.CTkLabel(
            parent, 
            text="No file selected", 
            text_color="gray",
            font=ctk.CTkFont(size=14)
        )
        self.path_label.pack(pady=10)

    def create_control_section(self, parent):
        """Create control buttons section."""
        control_label = ctk.CTkLabel(parent, text="🎮 Recording Controls", font=ctk.CTkFont(size=18))
        control_label.pack(pady=(15, 15))

        # Start button
        self.start_btn = ctk.CTkButton(
            parent, 
            text="▶️ Start Recording", 
            command=self.start_recording,
            fg_color="#4CAF50",
            hover_color="#45a049",
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.start_btn.pack(fill="x", pady=8)

        # Pause button
        self.pause_btn = ctk.CTkButton(
            parent, 
            text="⏸️ Pause", 
            command=self.toggle_pause,
            fg_color="#FF9800",
            hover_color="#F57C00",
            height=40,
            state="disabled"
        )
        self.pause_btn.pack(fill="x", pady=8)

        # Note button
        self.note_btn = ctk.CTkButton(
            parent, 
            text="📝 Add Note", 
            command=self.add_note,
            fg_color="#2196F3",
            hover_color="#1976D2",
            height=40
        )
        self.note_btn.pack(fill="x", pady=8)

        # Stop button
        self.stop_btn = ctk.CTkButton(
            parent, 
            text="⏹️ Stop Recording", 
            command=self.stop_recording,
            fg_color="#f44336",
            hover_color="#da190b",
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled"
        )
        self.stop_btn.pack(fill="x", pady=8)

    def create_advanced_features_section(self, parent):
        """Create advanced features section."""
        advanced_label = ctk.CTkLabel(parent, text="🚀 Advanced Features", font=ctk.CTkFont(size=18))
        advanced_label.pack(pady=(15, 15))

        # Bookmark button
        self.bookmark_btn = ctk.CTkButton(
            parent,
            text="🔖 Add Bookmark",
            command=self.add_bookmark,
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            height=35
        )
        self.bookmark_btn.pack(fill="x", pady=5)

        # Comment button
        self.comment_btn = ctk.CTkButton(
            parent,
            text="💬 Add Comment",
            command=self.add_comment,
            fg_color="#607D8B",
            hover_color="#455A64",
            height=35
        )
        self.comment_btn.pack(fill="x", pady=5)

        # Export button
        self.export_btn = ctk.CTkButton(
            parent,
            text="📤 Export All Formats",
            command=self.export_all_formats,
            fg_color="#795548",
            hover_color="#5D4037",
            height=35
        )
        self.export_btn.pack(fill="x", pady=5)

        # Cleanup button
        self.cleanup_btn = ctk.CTkButton(
            parent,
            text="🗑️ Clean Screenshots",
            command=self.manual_cleanup_screenshots,
            fg_color="#FF5722",
            hover_color="#D84315",
            height=35
        )
        self.cleanup_btn.pack(fill="x", pady=5)

        # Video export button
        self.video_btn = ctk.CTkButton(
            parent,
            text="🎥 Create Video",
            command=self.create_video,
            fg_color="#E91E63",
            hover_color="#C2185B",
            height=35
        )
        self.video_btn.pack(fill="x", pady=5)

    def create_stats_section(self, parent):
        """Create statistics section."""
        stats_label = ctk.CTkLabel(parent, text="📊 Live Statistics", font=ctk.CTkFont(size=18))
        stats_label.pack(pady=(15, 10))

        # Stats display
        self.stats_text = ctk.CTkTextbox(parent, height=150, font=ctk.CTkFont(size=14))
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)

    def create_analytics_section(self, parent):
        """Create analytics section."""
        analytics_frame = ctk.CTkFrame(parent)
        analytics_frame.pack(fill="x", padx=10, pady=10)

        analytics_label = ctk.CTkLabel(analytics_frame, text="📈 Live Analytics", font=ctk.CTkFont(size=18))
        analytics_label.pack(pady=(15, 10))

        # Analytics display
        self.analytics_text = ctk.CTkTextbox(analytics_frame, height=120, font=ctk.CTkFont(size=14))
        self.analytics_text.pack(fill="x", padx=10, pady=10)

    def create_ai_features_section(self, parent):
        """Create AI features section."""
        ai_label = ctk.CTkLabel(parent, text="🤖 AI Documentation", font=ctk.CTkFont(size=18))
        ai_label.pack(pady=(15, 15))

        # AI Enable Switch
        self.ai_enable_switch = ctk.CTkSwitch(
            parent,
            text="Enable AI Documentation",
            command=self.toggle_ai_features,
            onvalue=True,
            offvalue=False
        )
        self.ai_enable_switch.pack(pady=10)

        # AI Mode Selection
        mode_label = ctk.CTkLabel(parent, text="AI Mode:", font=ctk.CTkFont(size=14))
        mode_label.pack(pady=5)

        self.ai_mode_var = ctk.StringVar(value="Simple")
        self.ai_mode_menu = ctk.CTkOptionMenu(
            parent,
            values=["Simple", "Moderate", "Advanced"],
            variable=self.ai_mode_var,
            command=self.change_ai_mode
        )
        self.ai_mode_menu.pack(pady=5)

        # Mode descriptions
        mode_desc_label = ctk.CTkLabel(
            parent,
            text="Simple: Fast, no dependencies\nModerate: OCR text recognition\nAdvanced: Full AI capabilities",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        mode_desc_label.pack(pady=5)

        # Language Selection
        language_label = ctk.CTkLabel(parent, text="Language:", font=ctk.CTkFont(size=14))
        language_label.pack(pady=5)

        self.language_var = ctk.StringVar(value="English")
        self.language_menu = ctk.CTkOptionMenu(
            parent,
            values=["English", "Turkish"],
            variable=self.language_var,
            command=self.change_ai_language
        )
        self.language_menu.pack(pady=10)

        # AI Features
        self.ai_auto_describe = ctk.CTkSwitch(
            parent,
            text="Auto-generate descriptions",
            onvalue=True,
            offvalue=False
        )
        self.ai_auto_describe.pack(pady=5)

        self.ai_smart_categorize = ctk.CTkSwitch(
            parent,
            text="Smart categorization",
            onvalue=True,
            offvalue=False
        )
        self.ai_smart_categorize.pack(pady=5)

        self.ai_extract_text = ctk.CTkSwitch(
            parent,
            text="Extract text from screenshots",
            onvalue=True,
            offvalue=False
        )
        self.ai_extract_text.pack(pady=5)

        # AI Status
        self.ai_status_label = ctk.CTkLabel(
            parent,
            text="AI: Disabled",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        )
        self.ai_status_label.pack(pady=5)

        # AI Progress Bar
        self.ai_progress_bar = ctk.CTkProgressBar(parent)
        self.ai_progress_bar.pack(fill="x", padx=10, pady=5)
        self.ai_progress_bar.set(0)
        self.ai_progress_bar.pack_forget()  # Hide initially

        # AI Status Text
        self.ai_status_text = ctk.CTkLabel(
            parent,
            text="",
            text_color="lightblue",
            font=ctk.CTkFont(size=10)
        )
        self.ai_status_text.pack(pady=2)

    def create_instructions_section(self, parent):
        """Create instructions section."""
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(fill="x", padx=10, pady=10)

        info_text = """
💡 Instructions:
• Select save location first
• Click 'Start Recording' to begin
• Press ESC to stop recording
• Use Pause to temporarily stop
• Add notes, bookmarks, and comments anytime
• Export to multiple formats when done
• Create timelapse videos from recordings
        """
        
        info_label = ctk.CTkLabel(
            info_frame, 
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(pady=10)

    def create_standard_ui(self):
        """Create standard UI with tkinter."""
        # Title
        title_label = tk.Label(
            self.master, 
            text="Enhanced Step Recorder Pro v2.0", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Timer frame
        timer_frame = tk.Frame(self.master)
        timer_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(timer_frame, text="⏱️ Timer:", font=("Arial", 12, "bold")).pack()
        self.timer_label = tk.Label(timer_frame, text="00:00:00", font=("Arial", 14))
        self.timer_label.pack()
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(timer_frame, mode='determinate')
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        
        self.step_label = tk.Label(timer_frame, text="Steps: 0", font=("Arial", 10))
        self.step_label.pack()

        # File selection
        tk.Button(
            self.master, 
            text="📁 Select Save File", 
            command=self.select_save_path,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(padx=10, pady=4)
        
        self.path_label = tk.Label(
            self.master, 
            text="No file selected", 
            fg="grey",
            font=("Arial", 9)
        )
        self.path_label.pack()

        # Control buttons
        self.start_btn = tk.Button(
            self.master, 
            text="▶️ Start Recording", 
            command=self.start_recording,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.start_btn.pack(padx=10, pady=4)
        
        self.pause_btn = tk.Button(
            self.master, 
            text="⏸️ Pause", 
            command=self.toggle_pause,
            bg="#FF9800",
            fg="white",
            state="disabled"
        )
        self.pause_btn.pack(padx=10, pady=4)
        
        tk.Button(
            self.master, 
            text="📝 Add Note", 
            command=self.add_note,
            bg="#FF9800",
            fg="white"
        ).pack(padx=10, pady=4)
        
        self.stop_btn = tk.Button(
            self.master, 
            text="⏹️ Stop Recording", 
            command=self.stop_recording,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            state="disabled"
        )
        self.stop_btn.pack(padx=10, pady=4)

        # Status
        self.status_label = tk.Label(
            self.master, 
            text="Ready to record",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=(8, 0))

    def setup_callbacks(self):
        """Set up callbacks for the core recorder."""
        self.recorder.on_step_recorded = self.on_step_recorded
        self.recorder.on_statistics_updated = self.on_statistics_updated
        self.recorder.on_recording_state_changed = self.on_recording_state_changed

    def on_step_recorded(self, step_data):
        """Callback when a step is recorded."""
        # Process with AI if enabled
        enhanced_step = self.process_step_with_ai(step_data)
        
        # Debug: Print AI processing results
        if self.ai_documentation.settings.enabled and enhanced_step.get('ai_description'):
            print(f"AI Description: {enhanced_step['ai_description']}")
        
        # Update analytics
        if enhanced_step.get('type') == 'keystroke':
            keystrokes = enhanced_step.get('keystrokes', [])
            for key in keystrokes:
                self.analytics.record_key(key)
        elif enhanced_step.get('type') == 'click':
            coords = enhanced_step.get('coordinates', (0, 0))
            self.analytics.record_mouse_move(*coords)
        
        # Update UI
        self.update_analytics_display()

    def on_statistics_updated(self, statistics):
        """Callback when statistics are updated."""
        self.update_stats_display()

    def on_recording_state_changed(self, is_recording):
        """Callback when recording state changes."""
        self.recording = is_recording
        self.update_ui_state()

    def toggle_ai_features(self):
        """Toggle AI features on/off."""
        enabled = self.ai_enable_switch.get()
        
        if enabled:
            # Show loading progress
            self.ai_progress_bar.pack(fill="x", padx=10, pady=5)
            self.ai_progress_bar.set(0.1)
            self.ai_status_text.configure(text="Initializing AI...")
            self.ai_status_label.configure(text="AI: Initializing...", text_color="orange")
            
            # Initialize AI in background
            self.master.after(100, self._initialize_ai_background)
        else:
            self.ai_documentation.enable_ai(False)
            self.ai_progress_bar.pack_forget()
            self.ai_status_text.configure(text="")
            self.ai_status_label.configure(text="AI: Disabled", text_color="gray")

    def _initialize_ai_background(self):
        """Initialize AI in background with progress updates."""
        try:
            print("=== AI Initialization Debug ===")
            
            # Update progress
            self.ai_progress_bar.set(0.3)
            self.ai_status_text.configure(text="Loading AI models...")
            self.master.update()
            
            # Set AI settings BEFORE initialization
            self.ai_documentation.settings.auto_describe = self.ai_auto_describe.get()
            self.ai_documentation.settings.smart_categorize = self.ai_smart_categorize.get()
            self.ai_documentation.settings.extract_text = self.ai_extract_text.get()
            
            # Set AI mode BEFORE initialization
            mode = self.ai_mode_var.get()
            self.ai_documentation.settings.ai_mode = mode
            
            print(f"AI Mode: {mode}")
            print(f"AI Enabled: {self.ai_documentation.settings.enabled}")
            print(f"Auto Describe: {self.ai_documentation.settings.auto_describe}")
            print(f"Smart Categorize: {self.ai_documentation.settings.smart_categorize}")
            print(f"Extract Text: {self.ai_documentation.settings.extract_text}")
            
            # Enable AI BEFORE initialization
            self.ai_documentation.settings.enabled = True
            
            print("Calling ai_documentation.initialize()...")
            
            # Initialize AI
            success = self.ai_documentation.initialize()
            
            print(f"AI initialization result: {success}")
            
            if success:
                # Status message based on mode
                if mode == "Simple":
                    status_text = "AI ready! (Simple mode)"
                elif mode == "Moderate":
                    status_text = "AI ready! (Moderate mode)"
                else:  # Advanced
                    status_text = "AI ready! (Advanced mode)"
                
                self.ai_status_text.configure(text=status_text)
                
                # Complete progress
                self.ai_progress_bar.set(1.0)
                self.ai_status_label.configure(text="AI: Ready", text_color="lightgreen")
                
                # Hide progress bar after delay
                self.master.after(2000, self.ai_progress_bar.pack_forget)
                self.master.after(3000, lambda: self.ai_status_text.configure(text=""))
                
            else:
                self.ai_progress_bar.pack_forget()
                self.ai_status_text.configure(text="AI initialization failed")
                self.ai_status_label.configure(text="AI: Failed", text_color="red")
                self.ai_enable_switch.deselect()
                
        except Exception as e:
            print(f"AI initialization error: {e}")
            self.ai_progress_bar.pack_forget()
            self.ai_status_text.configure(text=f"Error: {str(e)[:50]}...")
            self.ai_status_label.configure(text="AI: Error", text_color="red")
            self.ai_enable_switch.deselect()

    def change_ai_language(self, language):
        """Change AI language."""
        self.ai_documentation.set_language(language)
        print(f"AI language changed to: {language}")

    def change_ai_mode(self, mode):
        """Change AI mode."""
        self.ai_documentation.settings.ai_mode = mode
        print(f"AI mode changed to: {mode}")
        
        # Reinitialize if AI is already enabled
        if self.ai_documentation.settings.enabled:
            self.ai_documentation.initialized = False
            self._initialize_ai_background()

    def process_step_with_ai(self, step_data):
        """Process a step with AI enhancements."""
        if self.ai_documentation.settings.enabled and self.ai_documentation.initialized:
            try:
                enhanced_step = self.ai_documentation.process_step(step_data)
                
                # Add AI description to the step
                if enhanced_step.get('ai_description'):
                    # Update the description field for the document
                    enhanced_step['description'] = enhanced_step['ai_description']
                    
                    # Also add to the original step data for the recorder
                    step_data['description'] = enhanced_step['ai_description']
                
                return enhanced_step
            except Exception as e:
                print(f"Error processing step with AI: {e}")
                return step_data
        return step_data

    def select_save_path(self):
        """Select save file path."""
        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")],
            title="Select output .docx file",
        )
        if path:
            self.save_path = path
            filename = os.path.basename(path)
            if CTK_AVAILABLE:
                self.path_label.configure(text=filename, text_color="white")
            else:
                self.path_label.config(text=filename, fg="black")

    def start_recording(self):
        """Start recording session."""
        if self.recording:
            return
        if not self.save_path:
            messagebox.showwarning("No file", "Please select where to save first.")
            return

        try:
            # Start core recording
            success = self.recorder.start_recording()
            if not success:
                return
            
            # Initialize workflow manager and video exporter
            self.workflow_manager = WorkflowManager(self.recorder.get_session_data())
            self.video_exporter = VideoExporter(self.recorder.get_session_data())
            
            # Initialize export manager
            self.export_manager = ExportManager(self.recorder.get_session_data())
            
            # Start timer
            self.start_timer()
            
            # Start queue processing
            self.master.after(100, self._process_queue)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {e}")

    def stop_recording(self):
        """Stop recording session."""
        if not self.recording:
            return
        
        # Stop core recording
        self.recorder.stop_recording()
        
        # Stop timer
        self.stop_timer()
        
        # Auto-save workflow data
        if self.workflow_manager:
            self.workflow_manager.auto_save(self.save_path)
        
        # Save recording
        self.save_recording()

    def toggle_pause(self):
        """Toggle pause state."""
        if not self.recording:
            return
        
        if self.paused:
            self.recorder.resume_recording()
            self.resume_timer()
        else:
            self.recorder.pause_recording()
            self.pause_timer()
        
        self.paused = not self.paused
        self.update_ui_state()

    def add_note(self):
        """Add a note to the recording."""
        if not self.recording:
            return
        
        note = simpledialog.askstring("Add Note", "Enter your note:")
        if note:
            self.recorder.add_note(note)

    def add_bookmark(self):
        """Add a bookmark to the current step."""
        if not self.recording or not self.workflow_manager:
            return
        
        current_step = self.recorder.step
        title = simpledialog.askstring("Add Bookmark", "Bookmark title:")
        if title:
            description = simpledialog.askstring("Add Bookmark", "Description (optional):")
            tags = simpledialog.askstring("Add Bookmark", "Tags (comma-separated, optional):")
            tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
            
            success = self.workflow_manager.add_bookmark(current_step, title, description, tag_list)
            if success:
                messagebox.showinfo("Success", f"Bookmark added to step {current_step}")

    def add_comment(self):
        """Add a comment to the current step."""
        if not self.recording or not self.workflow_manager:
            return
        
        current_step = self.recorder.step
        author = simpledialog.askstring("Add Comment", "Your name:")
        if author:
            text = simpledialog.askstring("Add Comment", "Comment:")
            if text:
                success = self.workflow_manager.add_comment(current_step, author, text)
                if success:
                    messagebox.showinfo("Success", f"Comment added to step {current_step}")

    def export_all_formats(self):
        """Export to all available formats."""
        if not self.export_manager:
            messagebox.showwarning("No Data", "No recording data to export.")
            return
        
        try:
            results = self.export_manager.export_all(self.save_path)
            
            # Show results
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            messagebox.showinfo("Export Complete", 
                              f"Exported {success_count}/{total_count} formats successfully.\n"
                              f"Files saved to: {os.path.dirname(self.save_path)}")
            
            # Clean up screenshots after successful export
            if success_count > 0:
                self.cleanup_screenshots()
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def manual_cleanup_screenshots(self):
        """Manually clean up screenshot files."""
        try:
            session_data = self.recorder.get_session_data()
            if hasattr(session_data, 'screenshots'):
                screenshots = session_data.screenshots
            else:
                screenshots = session_data.get('screenshots', [])
            
            if not screenshots:
                messagebox.showinfo("Cleanup", "No screenshots to clean up.")
                return
            
            # Ask for confirmation
            result = messagebox.askyesno(
                "Confirm Cleanup", 
                f"Are you sure you want to delete {len(screenshots)} screenshot files?\n"
                "This action cannot be undone."
            )
            
            if result:
                self.cleanup_screenshots()
                messagebox.showinfo("Cleanup Complete", f"Deleted {len(screenshots)} screenshot files.")
            
        except Exception as e:
            messagebox.showerror("Cleanup Error", f"Failed to clean up screenshots: {e}")

    def create_video(self):
        """Create a timelapse video from the recording."""
        if not self.video_exporter:
            messagebox.showwarning("No Data", "No recording data to create video from.")
            return
        
        try:
            video_path = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                filetypes=[("MP4 Video", "*.mp4")],
                title="Save video as"
            )
            
            if video_path:
                success = self.video_exporter.create_timelapse(video_path)
                if success:
                    messagebox.showinfo("Success", f"Video created: {video_path}")
                else:
                    messagebox.showerror("Error", "Failed to create video")
                    
        except Exception as e:
            messagebox.showerror("Video Error", f"Failed to create video: {e}")

    def start_timer(self):
        """Start the recording timer."""
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        """Stop the recording timer."""
        self.timer_running = False

    def pause_timer(self):
        """Pause the timer."""
        self.timer_running = False

    def resume_timer(self):
        """Resume the timer."""
        self.start_timer()

    def _timer_loop(self):
        """Timer loop for updating display."""
        while self.timer_running and self.recording:
            if not self.paused:
                elapsed = self.recorder.get_recording_duration()
                self.master.after(0, self._update_timer_display, elapsed)
            time.sleep(1)

    def _update_timer_display(self, elapsed):
        """Update timer display."""
        timer_text = str(timedelta(seconds=int(elapsed.total_seconds())))
        if CTK_AVAILABLE:
            self.timer_label.configure(text=timer_text)
        else:
            self.timer_label.config(text=timer_text)

    def _process_queue(self):
        """Process the event queue."""
        self.recorder.process_queue()
        if self.recording:
            self.master.after(100, self._process_queue)

    def update_ui_state(self):
        """Update UI state based on recording status."""
        if CTK_AVAILABLE:
            if self.recording:
                self.start_btn.configure(state="disabled")
                self.stop_btn.configure(state="normal")
                self.pause_btn.configure(state="normal")
                self.pause_btn.configure(
                    text="⏸️ Paused" if self.paused else "⏸️ Pause"
                )
            else:
                self.start_btn.configure(state="normal")
                self.stop_btn.configure(state="disabled")
                self.pause_btn.configure(state="disabled")
        else:
            if self.recording:
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
                self.pause_btn.config(state="normal")
                self.pause_btn.config(
                    text="⏸️ Paused" if self.paused else "⏸️ Pause"
                )
            else:
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.pause_btn.config(state="disabled")

    def update_stats_display(self):
        """Update statistics display."""
        stats = self.recorder.get_statistics()
        stats_text = f"""
Clicks: {stats['clicks']}
Keystrokes: {stats['keystrokes']}
Notes: {stats['notes']}
Applications: {len(stats['applications'])}
Total Steps: {stats['total_steps']}
Duration: {stats['current_duration']:.1f}s
        """
        
        if CTK_AVAILABLE:
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", stats_text)
        else:
            # For standard tkinter, we'll update step label
            self.step_label.config(text=f"Steps: {stats['total_steps']}")

    def update_analytics_display(self):
        """Update analytics display."""
        analytics_summary = self.analytics.get_summary()
        analytics_text = f"""
Typing Speed: {analytics_summary['typing_speed_cps']} chars/sec
Mouse Distance: {analytics_summary['mouse_distance_px']} px
Shortcuts Used: {len(analytics_summary['shortcut_counts'])}
Errors Detected: {len(analytics_summary['error_patterns'])}
        """
        
        if CTK_AVAILABLE:
            self.analytics_text.delete("1.0", "end")
            self.analytics_text.insert("1.0", analytics_text)

    def save_recording(self):
        """Save the recording to file."""
        if self.save_path:
            try:
                # Save using export manager
                if self.export_manager:
                    success = self.export_manager.export_to_format('docx', self.save_path)
                    if success:
                        messagebox.showinfo("Saved", f"Recording saved to: {self.save_path}")
                        # Clean up screenshots after successful save
                        self.cleanup_screenshots()
                    else:
                        messagebox.showerror("Error", "Failed to save recording")
                        
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def cleanup_screenshots(self):
        """Clean up screenshot files after recording is saved."""
        try:
            # Get all screenshot files from the session
            session_data = self.recorder.get_session_data()
            if hasattr(session_data, 'screenshots'):
                screenshots = session_data.screenshots
            else:
                screenshots = session_data.get('screenshots', [])
            
            deleted_count = 0
            for screenshot_path in screenshots:
                if os.path.exists(screenshot_path):
                    try:
                        os.remove(screenshot_path)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting screenshot {screenshot_path}: {e}")
            
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} screenshot files")
                
                # Clear the screenshots list in session data
                if hasattr(session_data, 'screenshots'):
                    session_data.screenshots = []
                else:
                    session_data['screenshots'] = []
                
        except Exception as e:
            print(f"Error during screenshot cleanup: {e}")

    def cleanup_all_screenshots(self):
        """Clean up all screenshot files in the project directory."""
        try:
            import glob
            
            # Get the current directory
            current_dir = os.getcwd()
            
            # Find all PNG files in the current directory
            png_files = glob.glob(os.path.join(current_dir, "*.png"))
            
            deleted_count = 0
            for png_file in png_files:
                try:
                    # Check if it's a screenshot file (contains timestamp or step info)
                    filename = os.path.basename(png_file)
                    if any(keyword in filename.lower() for keyword in ['screenshot', 'step', 'recording', 'capture']):
                        os.remove(png_file)
                        deleted_count += 1
                        print(f"Deleted screenshot: {filename}")
                except Exception as e:
                    print(f"Error deleting {png_file}: {e}")
            
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} screenshot files on exit")
            else:
                print("No screenshot files found to clean up")
                
        except Exception as e:
            print(f"Error during cleanup on exit: {e}")

    def on_closing(self):
        """Handle application closing."""
        try:
            print("Application closing, cleaning up...")
            
            # Stop recording if active
            if self.recording:
                print("Stopping active recording...")
                self.stop_recording()
            
            # Stop timer
            if self.timer_running:
                print("Stopping timer...")
                self.stop_timer()
            
            # Clean up all screenshots
            print("Cleaning up screenshot files...")
            self.cleanup_all_screenshots()
            
            # Clean up AI components
            if hasattr(self, 'ai_documentation') and self.ai_documentation:
                print("Cleaning up AI components...")
                self.ai_documentation.enable_ai(False)
            
            print("Cleanup completed. Closing application...")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        finally:
            # Destroy the window
            self.master.destroy()


if __name__ == "__main__":
    if CTK_AVAILABLE:
        root = ctk.CTk()
    else:
        root = tk.Tk()
    
    app = EnhancedStepRecorder(root)
    root.mainloop() 

    
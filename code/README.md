# 🎬 Enhanced Step Recorder Pro v2.0

## 🚦 Motivation

Frustrated by the Windows Step Recorder's 999 screenshot limit and the fact that most alternatives are paid or limited? Enhanced Step Recorder Pro is a free, unlimited, and advanced solution for anyone needing professional step-by-step documentation, tutorials, or process capture.

- **No screenshot limits**
- **No paywalls or subscriptions**
- **Modern, AI-powered features**

> _Developed using the [Cursor](https://cursor.so) editor for a modern Python workflow._

## ✨ Features

### 📋 Core Recording
- **Smart Screenshot Capture**: Automatic screenshots with window change detection
- **Mouse & Keyboard Tracking**: Records clicks, keystrokes, and mouse movements
- **Automatic Step Numbering**: Sequential step tracking with timestamps
- **Pause/Resume**: Flexible recording control
- **Notes & Annotations**: Add descriptions to any step
- **AI-Powered Step Descriptions**: Automatic, context-aware step documentation (see AI Modes below)

### 🤖 AI & OCR
- **AI Modes**: Simple (fast, no dependencies), Moderate (OCR), Advanced (AI/translation)
- **OCR Text Extraction**: Reads on-screen text in English & Turkish (Moderate/Advanced)
- **Automatic Translation**: Translate steps to multiple languages (Advanced)
- **Real Typed Text Extraction**: Captures actual user input for accurate documentation

### 📊 Advanced Analytics
- **Mouse Analytics**: Movement tracking, heatmaps, drag detection
- **Keyboard Analytics**: Typing speed, shortcut detection, error patterns
- **Application Statistics**: Usage tracking across different applications
- **Performance Metrics**: Real-time statistics and insights

### 🔧 Workflow Management
- **Bookmarks**: Mark important steps for quick reference
- **Comments**: Add collaborative notes and feedback
- **Version History**: Track changes with undo/redo functionality
- **Auto-Save**: Automatic session recovery and backup
- **Step Review**: Comprehensive step management interface

### 📤 Multi-Format Export
- **Microsoft Word (.docx)**: Professional documentation with rich formatting
- **HTML**: Web-ready documentation with interactive elements
- **Markdown**: Clean, readable documentation for developers
- **JSON**: Raw data export for custom processing
- **Video Timelapse**: Create video summaries from recordings

### ⚡ Performance Optimization
- **Memory Management**: Efficient resource usage and cleanup
- **Screenshot Compression**: Optimized image storage
- **Background Processing**: Non-blocking operations
- **Resource Monitoring**: Real-time performance tracking

### 🎨 Modern UI
- **Dark/Light Themes**: Customizable appearance
- **Responsive Design**: Adapts to different screen sizes
- **Real-time Updates**: Live statistics and progress tracking
- **Intuitive Controls**: Easy-to-use interface

## 🚀 Quick Start

### Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the launcher**:
   ```bash
   python launcher.py
   ```

### Basic Usage

1. **Select Save Location**: Choose where to save your documentation
2. **Start Recording**: Click "Start Recording" to begin
3. **Perform Actions**: Use your computer normally - the recorder will capture everything
4. **Add Notes**: Click "Add Note" to add descriptions to steps
5. **Stop Recording**: Click "Stop Recording" or press ESC to finish
6. **Export**: Choose your preferred export format

## 📁 Project Structure

```
Screen_capture/
├── launcher.py                 # Main launcher script
├── step_recorder_enhanced.py   # Enhanced main application
├── recorder_core.py           # Core recording functionality
├── smart_capture.py           # Smart screenshot logic
├── analytics.py               # Analytics and statistics
├── workflow_collaboration.py  # Workflow management
├── video_export.py            # Video creation
├── performance_optimizer.py   # Performance optimization
├── exporters.py               # Multi-format export
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🔧 Advanced Features

### Smart Screenshot Capture
The smart capture system automatically detects when windows change and takes screenshots at optimal moments, reducing unnecessary captures while ensuring important changes are documented.

### Analytics Dashboard
Real-time analytics provide insights into:
- Mouse movement patterns and efficiency
- Keyboard usage and typing speed
- Application switching patterns
- Error detection and correction patterns

### Workflow Collaboration
- **Bookmarks**: Mark critical steps for team review
- **Comments**: Add feedback and notes for collaboration
- **Version Control**: Track changes with full history
- **Auto-Save**: Never lose work with automatic backups

### Video Export
Create professional timelapse videos from your recordings:
- Customizable frame rates and durations
- Text overlays with step information
- Progress bars and highlights
- Multiple export formats

## 📖 Detailed Usage Guide

### Recording Modes

#### Standard Recording
- Captures all mouse clicks and keystrokes
- Takes screenshots at each interaction
- Automatic step numbering

#### Smart Recording
- Intelligent screenshot timing
- Window change detection
- Reduced file sizes

#### Analytics Mode
- Enhanced tracking for detailed insights
- Performance monitoring
- Usage pattern analysis

### Export Options

#### Microsoft Word (.docx)
- Professional formatting
- Automatic table of contents
- Screenshot integration
- Step-by-step instructions

#### HTML Export
- Web-ready documentation
- Interactive elements
- Responsive design
- Easy sharing

#### Markdown Export
- Developer-friendly format
- Version control compatible
- Clean, readable structure
- Easy to edit

#### JSON Export
- Raw data format
- Custom processing
- API integration
- Data analysis

### Performance Optimization

The application includes several optimization features:
- **Memory Management**: Automatic cleanup and optimization
- **Screenshot Compression**: Reduced file sizes
- **Background Processing**: Non-blocking operations
- **Resource Monitoring**: Real-time performance tracking

## 🛠️ Configuration

### Customization Options

You can customize various aspects of the recorder:

```python
# Performance settings
optimizer.set_memory_threshold(80)  # Memory usage threshold
optimizer.set_screenshot_quality(85)  # JPEG quality
optimizer.set_max_screenshot_size(1920, 1080)  # Max dimensions

# Analytics settings
analytics.set_tracking_enabled(True)  # Enable/disable tracking
analytics.set_heatmap_resolution(50)  # Heatmap resolution

# Export settings
export_manager.set_default_format('docx')  # Default export format
```

## 🔍 Troubleshooting

### Common Issues

1. **Dependencies Missing**
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Errors**
   - Run as administrator on Windows
   - Grant accessibility permissions

3. **Performance Issues**
   - Reduce screenshot quality
   - Increase memory threshold
   - Close unnecessary applications

4. **Export Failures**
   - Check file permissions
   - Ensure sufficient disk space
   - Verify export format support

### Debug Mode

Enable debug mode for detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **pynput**: For mouse and keyboard input handling
- **Pillow**: For image processing
- **python-docx**: For Word document generation
- **customtkinter**: For modern UI components
- **moviepy**: For video creation

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the documentation

## 🤖 AI Modes

Enhanced Step Recorder Pro offers three AI-powered documentation modes:

- **Simple**: Fast, no extra dependencies. Generates basic step descriptions using only captured events.
- **Moderate**: Adds OCR (EasyOCR required) for extracting on-screen text in English and Turkish, improving step context.
- **Advanced**: Full AI (EasyOCR + HuggingFace Transformers + translation). Provides the richest, most accurate, and multi-language step documentation.

Switch modes in real time from the GUI. Requirements for each mode are shown in the app.

## 🖥️ Professional Windows Installer

- **Easy for end users**: Just run the installer—no technical knowledge required.
- **Includes everything**: Bundles Python, all dependencies, and the app itself.
- **Creates desktop/start menu shortcuts**
- **Uninstaller and Add/Remove Programs integration**
- **Automatic Python/runtime setup if missing**
- **Distribution-ready**: Share the generated `EnhancedStepRecorder_Setup.exe` with anyone.

### NSIS Installer Creation (for Developers)

After building with PyInstaller, create the Windows installer using NSIS:

1. Open a terminal in the `install` directory.
2. Run the following command (adjust path if needed):
   ```powershell
   & "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
   ```
3. The installer will be created as `EnhancedStepRecorder_Setup.exe` in the `install` directory.

**Note:**
- If you use PyInstaller's `--onedir` mode, make sure your `installer.nsi` script references files in `dist\EnhancedStepRecorder\` (not just `dist\`).
- If you change the output folder or EXE name, update the NSIS script accordingly.
- For more details, see [`install/README_INSTALLER.md`](install/README_INSTALLER.md).

---

**Enhanced Step Recorder Pro v2.0** - Making documentation creation effortless and professional! 🎬 
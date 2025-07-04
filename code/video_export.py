import os
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import tempfile

try:
    from moviepy.editor import ImageSequenceClip, CompositeVideoClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

class VideoExporter:
    """Create timelapse videos from screenshots and recording data."""
    
    def __init__(self, session_data):
        self.session = session_data
        self.temp_dir = None
    
    def create_timelapse(self, output_path: str, fps: int = 2, duration_per_frame: float = 1.0, 
                        add_text_overlay: bool = True, add_progress_bar: bool = True) -> bool:
        """Create a timelapse video from screenshots."""
        if not MOVIEPY_AVAILABLE:
            print("MoviePy not available. Install with: pip install moviepy")
            return False
        
        try:
            # Create temporary directory for processed images
            self.temp_dir = tempfile.mkdtemp()
            processed_images = []
            
            # Process each screenshot
            for i, step in enumerate(self.session.steps):
                screenshot = step.get('screenshot')
                if not screenshot or not os.path.exists(screenshot):
                    continue
                
                # Load and process image
                img = Image.open(screenshot)
                
                if add_text_overlay:
                    img = self._add_text_overlay(img, step, i + 1, len(self.session.steps))
                
                if add_progress_bar:
                    img = self._add_progress_bar(img, i + 1, len(self.session.steps))
                
                # Save processed image
                processed_path = os.path.join(self.temp_dir, f"frame_{i:04d}.png")
                img.save(processed_path)
                processed_images.append(processed_path)
            
            if not processed_images:
                print("No screenshots found for video creation")
                return False
            
            # Create video clip
            clip = ImageSequenceClip(processed_images, fps=fps)
            
            # Use clip directly since title overlay is not available
            final_clip = clip
            
            # Write video
            final_clip.write_videofile(output_path, fps=fps, codec='libx264')
            
            # Cleanup
            final_clip.close()
            clip.close()
            
            return True
            
        except Exception as e:
            print(f"Error creating timelapse: {e}")
            return False
        finally:
            self._cleanup_temp_files()
    
    def create_highlight_video(self, output_path: str, fps: int = 5, 
                             highlight_steps: List[int] = None) -> bool:
        """Create a highlight video focusing on specific steps."""
        if not MOVIEPY_AVAILABLE:
            print("MoviePy not available. Install with: pip install moviepy")
            return False
        
        try:
            self.temp_dir = tempfile.mkdtemp()
            processed_images = []
            
            # If no specific steps provided, highlight bookmarked or commented steps
            if highlight_steps is None:
                highlight_steps = self._get_highlighted_steps()
            
            # Process highlighted screenshots with longer duration
            for step_num in highlight_steps:
                step = self._get_step_by_number(step_num)
                if not step:
                    continue
                
                screenshot = step.get('screenshot')
                if not screenshot or not os.path.exists(screenshot):
                    continue
                
                # Load and process image with highlight effect
                img = Image.open(screenshot)
                img = self._add_highlight_effect(img, step, step_num)
                
                # Save processed image
                processed_path = os.path.join(self.temp_dir, f"highlight_{step_num:04d}.png")
                img.save(processed_path)
                processed_images.append(processed_path)
            
            if not processed_images:
                print("No highlighted screenshots found")
                return False
            
            # Create video with longer duration for highlights
            clip = ImageSequenceClip(processed_images, fps=fps)
            
            # Write video
            clip.write_videofile(output_path, fps=fps, codec='libx264')
            clip.close()
            
            return True
            
        except Exception as e:
            print(f"Error creating highlight video: {e}")
            return False
        finally:
            self._cleanup_temp_files()
    
    def _add_text_overlay(self, img: Image.Image, step: Dict[str, Any], 
                         step_num: int, total_steps: int) -> Image.Image:
        """Add text overlay to image."""
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Step number and type
        step_text = f"Step {step_num:03d} of {total_steps}"
        step_type = step.get('type', 'unknown').upper()
        timestamp = step.get('timestamp', datetime.now())
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Draw background rectangle
        text_width = max(draw.textlength(step_text, font=font_large),
                        draw.textlength(step_type, font=font_small))
        bg_rect = [10, 10, 10 + text_width + 20, 80]
        draw.rectangle(bg_rect, fill=(0, 0, 0, 180))
        
        # Draw text
        draw.text((20, 15), step_text, fill=(255, 255, 255), font=font_large)
        draw.text((20, 45), step_type, fill=(255, 255, 0), font=font_small)
        draw.text((20, 65), time_str, fill=(200, 200, 200), font=font_small)
        
        return img
    
    def _add_progress_bar(self, img: Image.Image, current_step: int, total_steps: int) -> Image.Image:
        """Add progress bar to image."""
        draw = ImageDraw.Draw(img)
        
        # Progress bar dimensions
        bar_width = img.width - 40
        bar_height = 8
        bar_x = 20
        bar_y = img.height - 30
        
        # Draw background bar
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                      fill=(100, 100, 100))
        
        # Draw progress
        progress_width = int((current_step / total_steps) * bar_width)
        if progress_width > 0:
            draw.rectangle([bar_x, bar_y, bar_x + progress_width, bar_y + bar_height], 
                          fill=(0, 255, 0))
        
        return img
    
    def _add_highlight_effect(self, img: Image.Image, step: Dict[str, Any], 
                            step_num: int) -> Image.Image:
        """Add highlight effect to image."""
        draw = ImageDraw.Draw(img)
        
        # Add border
        border_width = 10
        draw.rectangle([0, 0, img.width - 1, img.height - 1], 
                      outline=(255, 255, 0), width=border_width)
        
        # Add highlight text
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except Exception:
            font = ImageFont.load_default()
        
        highlight_text = f"HIGHLIGHT - Step {step_num}"
        text_width = draw.textlength(highlight_text, font=font)
        
        # Background for text
        text_bg = [img.width - text_width - 20, 20, img.width - 20, 60]
        draw.rectangle(text_bg, fill=(255, 255, 0, 200))
        
        # Text
        draw.text((img.width - text_width - 15, 25), highlight_text, 
                 fill=(0, 0, 0), font=font)
        
        return img
    
    def _create_title_clip(self, duration: float):
        """Create title clip with session information."""
        # For now, return None since TextClip is not available
        # This can be enhanced later with PIL-based text overlay
        return None
    
    def _get_highlighted_steps(self) -> List[int]:
        """Get steps that should be highlighted (bookmarked, commented, etc.)."""
        highlighted = set()
        
        # Add bookmarked steps
        for bookmark in getattr(self.session, 'bookmarks', []):
            highlighted.add(bookmark.step_number)
        
        # Add commented steps
        for comment in getattr(self.session, 'comments', []):
            highlighted.add(comment.step_number)
        
        return sorted(list(highlighted))
    
    def _get_step_by_number(self, step_num: int) -> Optional[Dict[str, Any]]:
        """Get step by step number."""
        for step in self.session.steps:
            if step.get('step_number') == step_num:
                return step
        return None
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                for file in os.listdir(self.temp_dir):
                    os.remove(os.path.join(self.temp_dir, file))
                os.rmdir(self.temp_dir)
            except Exception as e:
                print(f"Error cleaning up temp files: {e}")
    
    def get_video_summary(self) -> Dict[str, Any]:
        """Get summary of video export capabilities."""
        return {
            'moviepy_available': MOVIEPY_AVAILABLE,
            'screenshots_count': len([s for s in self.session.steps if s.get('screenshot')]),
            'session_duration': self.session.statistics.get('recording_duration', 0),
            'total_steps': self.session.statistics.get('total_steps', 0)
        } 
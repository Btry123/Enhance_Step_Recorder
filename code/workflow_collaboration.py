import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from copy import deepcopy

@dataclass
class Bookmark:
    """Bookmark for important steps."""
    step_number: int
    title: str
    description: str
    timestamp: datetime
    tags: List[str]

@dataclass
class Comment:
    """Comment on a step."""
    step_number: int
    author: str
    text: str
    timestamp: datetime
    is_resolved: bool = False

@dataclass
class StepVersion:
    """Version history for a step."""
    step_number: int
    version: int
    data: Dict[str, Any]
    timestamp: datetime
    author: str

class WorkflowManager:
    """Workflow and collaboration features: review, undo, bookmarks, comments, auto-save."""
    
    def __init__(self, session_data):
        self.session = session_data
        self.bookmarks: List[Bookmark] = []
        self.comments: List[Comment] = []
        self.step_versions: List[StepVersion] = []
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self.auto_save_interval = 30  # seconds
        self.last_auto_save = time.time()
        self.auto_save_path = None
        
    def add_bookmark(self, step_number: int, title: str, description: str, tags: List[str] = None) -> bool:
        """Add a bookmark to a step."""
        try:
            bookmark = Bookmark(
                step_number=step_number,
                title=title,
                description=description,
                timestamp=datetime.now(),
                tags=tags or []
            )
            self.bookmarks.append(bookmark)
            return True
        except Exception as e:
            print(f"Error adding bookmark: {e}")
            return False
    
    def remove_bookmark(self, step_number: int) -> bool:
        """Remove a bookmark from a step."""
        self.bookmarks = [b for b in self.bookmarks if b.step_number != step_number]
        return True
    
    def get_bookmarks(self, step_number: Optional[int] = None) -> List[Bookmark]:
        """Get bookmarks, optionally filtered by step number."""
        if step_number is None:
            return self.bookmarks.copy()
        return [b for b in self.bookmarks if b.step_number == step_number]
    
    def add_comment(self, step_number: int, author: str, text: str) -> bool:
        """Add a comment to a step."""
        try:
            comment = Comment(
                step_number=step_number,
                author=author,
                text=text,
                timestamp=datetime.now()
            )
            self.comments.append(comment)
            return True
        except Exception as e:
            print(f"Error adding comment: {e}")
            return False
    
    def resolve_comment(self, comment_index: int) -> bool:
        """Mark a comment as resolved."""
        if 0 <= comment_index < len(self.comments):
            self.comments[comment_index].is_resolved = True
            return True
        return False
    
    def get_comments(self, step_number: Optional[int] = None) -> List[Comment]:
        """Get comments, optionally filtered by step number."""
        if step_number is None:
            return self.comments.copy()
        return [c for c in self.comments if c.step_number == step_number]
    
    def save_step_version(self, step_number: int, author: str = "System") -> bool:
        """Save a version of a step for undo/redo."""
        try:
            # Find the step
            step = None
            for s in self.session.steps:
                if s.get('step_number') == step_number:
                    step = s
                    break
            
            if step:
                version = StepVersion(
                    step_number=step_number,
                    version=len([v for v in self.step_versions if v.step_number == step_number]) + 1,
                    data=deepcopy(step),
                    timestamp=datetime.now(),
                    author=author
                )
                self.step_versions.append(version)
                return True
        except Exception as e:
            print(f"Error saving step version: {e}")
        return False
    
    def undo_step(self, step_number: int) -> bool:
        """Undo the last change to a step."""
        try:
            # Find the last version of this step
            versions = [v for v in self.step_versions if v.step_number == step_number]
            if not versions:
                return False
            
            last_version = max(versions, key=lambda v: v.timestamp)
            
            # Save current state to redo stack
            current_step = None
            for s in self.session.steps:
                if s.get('step_number') == step_number:
                    current_step = s
                    break
            
            if current_step:
                self.redo_stack.append(deepcopy(current_step))
            
            # Restore the previous version
            for i, step in enumerate(self.session.steps):
                if step.get('step_number') == step_number:
                    self.session.steps[i] = deepcopy(last_version.data)
                    return True
            
        except Exception as e:
            print(f"Error undoing step: {e}")
        return False
    
    def redo_step(self, step_number: int) -> bool:
        """Redo the last undone change to a step."""
        if not self.redo_stack:
            return False
        
        try:
            redo_data = self.redo_stack.pop()
            for i, step in enumerate(self.session.steps):
                if step.get('step_number') == step_number:
                    self.session.steps[i] = redo_data
                    return True
        except Exception as e:
            print(f"Error redoing step: {e}")
        return False
    
    def auto_save(self, base_path: str) -> bool:
        """Auto-save the current session."""
        try:
            current_time = time.time()
            if current_time - self.last_auto_save >= self.auto_save_interval:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                auto_save_path = f"{base_path}_autosave_{timestamp}.json"
                
                # Save session data
                session_data = {
                    'session': {
                        'start_time': self.session.start_time.isoformat() if self.session.start_time else None,
                        'end_time': self.session.end_time.isoformat() if self.session.end_time else None,
                        'statistics': self.session.statistics.copy(),
                        'steps': [step.copy() for step in self.session.steps],
                        'screenshots': self.session.screenshots.copy(),
                        'metadata': self.session.metadata.copy()
                    },
                    'workflow': {
                        'bookmarks': [asdict(b) for b in self.bookmarks],
                        'comments': [asdict(c) for c in self.comments],
                        'step_versions': [asdict(v) for v in self.step_versions]
                    },
                    'auto_save_time': datetime.now().isoformat()
                }
                
                # Convert datetime objects to strings
                session_data['session']['statistics']['applications'] = list(session_data['session']['statistics']['applications'])
                for step in session_data['session']['steps']:
                    step['timestamp'] = step['timestamp'].isoformat()
                
                with open(auto_save_path, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, default=str)
                
                self.last_auto_save = current_time
                self.auto_save_path = auto_save_path
                return True
                
        except Exception as e:
            print(f"Error auto-saving: {e}")
        return False
    
    def load_auto_save(self, auto_save_path: str) -> bool:
        """Load an auto-saved session."""
        try:
            with open(auto_save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restore session data
            session_data = data['session']
            workflow_data = data.get('workflow', {})
            
            # Restore session
            if session_data.get('start_time'):
                self.session.start_time = datetime.fromisoformat(session_data['start_time'])
            if session_data.get('end_time'):
                self.session.end_time = datetime.fromisoformat(session_data['end_time'])
            
            self.session.statistics = session_data['statistics']
            self.session.statistics['applications'] = set(self.session.statistics['applications'])
            
            # Restore steps
            self.session.steps = []
            for step_data in session_data['steps']:
                step_data['timestamp'] = datetime.fromisoformat(step_data['timestamp'])
                self.session.steps.append(step_data)
            
            self.session.screenshots = session_data['screenshots']
            self.session.metadata = session_data['metadata']
            
            # Restore workflow data
            self.bookmarks = []
            for bookmark_data in workflow_data.get('bookmarks', []):
                bookmark_data['timestamp'] = datetime.fromisoformat(bookmark_data['timestamp'])
                self.bookmarks.append(Bookmark(**bookmark_data))
            
            self.comments = []
            for comment_data in workflow_data.get('comments', []):
                comment_data['timestamp'] = datetime.fromisoformat(comment_data['timestamp'])
                self.comments.append(Comment(**comment_data))
            
            self.step_versions = []
            for version_data in workflow_data.get('step_versions', []):
                version_data['timestamp'] = datetime.fromisoformat(version_data['timestamp'])
                self.step_versions.append(StepVersion(**version_data))
            
            return True
            
        except Exception as e:
            print(f"Error loading auto-save: {e}")
            return False
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get a summary of workflow data."""
        return {
            'bookmarks_count': len(self.bookmarks),
            'comments_count': len(self.comments),
            'resolved_comments_count': len([c for c in self.comments if c.is_resolved]),
            'step_versions_count': len(self.step_versions),
            'undo_stack_size': len(self.undo_stack),
            'redo_stack_size': len(self.redo_stack),
            'last_auto_save': self.auto_save_path
        }
    
    def export_workflow_data(self, output_path: str) -> bool:
        """Export workflow data (bookmarks, comments, versions) to JSON."""
        try:
            workflow_data = {
                'bookmarks': [asdict(b) for b in self.bookmarks],
                'comments': [asdict(c) for c in self.comments],
                'step_versions': [asdict(v) for v in self.step_versions],
                'export_time': datetime.now().isoformat()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error exporting workflow data: {e}")
            return False 
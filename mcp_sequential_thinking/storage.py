import json
import logging
import os
import threading
from typing import List, Optional
from pathlib import Path
from datetime import datetime

import portalocker

from .models import ThoughtData, ThoughtStage
from .logging_conf import configure_logging

logger = configure_logging("sequential-thinking.storage")


class ThoughtStorage:
    """Storage manager for thought data."""

    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize the storage manager.

        Args:
            storage_dir: Directory to store thought data files. If None, uses a default directory.
        """
        if storage_dir is None:
            # Use user's home directory by default
            home_dir = Path.home()
            self.storage_dir = home_dir / ".mcp_sequential_thinking"
        else:
            self.storage_dir = Path(storage_dir)

        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Default session file
        self.current_session_file = self.storage_dir / "current_session.json"
        self.lock_file = self.storage_dir / "current_session.lock"

        # Thread safety
        self._lock = threading.RLock()
        self.thought_history: List[ThoughtData] = []

        # Load existing session if available
        self._load_session()

    def _load_session(self) -> None:
        """Load thought history from the current session file if it exists."""
        if self.current_session_file.exists():
            try:
                # Use file locking to ensure thread safety
                with portalocker.Lock(self.lock_file, timeout=10) as _:
                    with open(self.current_session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    with self._lock:
                        self.thought_history = [
                            ThoughtData.from_dict(thought_dict)
                            for thought_dict in data.get("thoughts", [])
                        ]
            except (json.JSONDecodeError, KeyError) as e:
                # Handle corrupted file
                logger.error(f"Error loading session: {e}")
                # Create backup of corrupted file
                backup_file = self.current_session_file.with_suffix(f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}")
                self.current_session_file.rename(backup_file)
                with self._lock:
                    self.thought_history = []

    def _save_session(self) -> None:
        """Save the current thought history to the session file."""
        # Use thread lock to ensure consistent data
        with self._lock:
            # Include IDs when saving to storage
            thoughts_with_ids = []
            for thought in self.thought_history:
                # Set flag to include ID in dictionary
                thought._include_id_in_dict = True
                thoughts_with_ids.append(thought.to_dict())
                # Reset flag
                thought._include_id_in_dict = False

            data = {
                "thoughts": thoughts_with_ids,
                "lastUpdated": datetime.now().isoformat()
            }

        # Use file locking to ensure thread safety when writing
        with portalocker.Lock(self.lock_file, timeout=10) as _:
            with open(self.current_session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def add_thought(self, thought: ThoughtData) -> None:
        """Add a thought to the history and save the session.

        Args:
            thought: The thought data to add
        """
        with self._lock:
            self.thought_history.append(thought)
        self._save_session()

    def get_all_thoughts(self) -> List[ThoughtData]:
        """Get all thoughts in the current session.

        Returns:
            List[ThoughtData]: All thoughts in the current session
        """
        with self._lock:
            # Return a copy to avoid external modification
            return list(self.thought_history)

    def get_thoughts_by_stage(self, stage: ThoughtStage) -> List[ThoughtData]:
        """Get all thoughts in a specific stage.

        Args:
            stage: The thinking stage to filter by

        Returns:
            List[ThoughtData]: Thoughts in the specified stage
        """
        with self._lock:
            return [t for t in self.thought_history if t.stage == stage]

    def clear_history(self) -> None:
        """Clear the thought history and save the empty session."""
        with self._lock:
            self.thought_history.clear()
        self._save_session()

    def export_session(self, file_path: str) -> None:
        """Export the current session to a file.

        Args:
            file_path: Path to save the exported session
        """
        with self._lock:
            # Include IDs when exporting
            thoughts_with_ids = []
            for thought in self.thought_history:
                # Set flag to include ID in dictionary
                thought._include_id_in_dict = True
                thoughts_with_ids.append(thought.to_dict())
                # Reset flag
                thought._include_id_in_dict = False

            data = {
                "thoughts": thoughts_with_ids,
                "exportedAt": datetime.now().isoformat(),
                "metadata": {
                    "totalThoughts": len(self.thought_history),
                    "stages": {
                        stage.value: len([t for t in self.thought_history if t.stage == stage])
                        for stage in ThoughtStage
                    }
                }
            }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def import_session(self, file_path: str) -> None:
        """Import a session from a file.

        Args:
            file_path: Path to the file to import

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
            KeyError: If the file doesn't contain valid thought data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        thoughts = [
            ThoughtData.from_dict(thought_dict)
            for thought_dict in data.get("thoughts", [])
        ]

        with self._lock:
            self.thought_history = thoughts

        self._save_session()

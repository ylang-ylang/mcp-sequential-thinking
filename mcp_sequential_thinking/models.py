from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from uuid import uuid4, UUID
from pydantic import BaseModel, Field, field_validator


class ThoughtStage(Enum):
    """Basic thinking stages for structured sequential thinking."""
    PROBLEM_DEFINITION = "Problem Definition"
    RESEARCH = "Research"
    ANALYSIS = "Analysis"
    SYNTHESIS = "Synthesis"
    CONCLUSION = "Conclusion"

    @classmethod
    def from_string(cls, value: str) -> 'ThoughtStage':
        """Convert a string to a thinking stage.

        Args:
            value: The string representation of the thinking stage

        Returns:
            ThoughtStage: The corresponding ThoughtStage enum value

        Raises:
            ValueError: If the string does not match any valid thinking stage
        """
        # Case-insensitive comparison
        for stage in cls:
            if stage.value.casefold() == value.casefold():
                return stage

        # If no match found
        valid_stages = ", ".join(stage.value for stage in cls)
        raise ValueError(f"Invalid thinking stage: '{value}'. Valid stages are: {valid_stages}")


class ThoughtData(BaseModel):
    """Data structure for a single thought in the sequential thinking process."""
    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    stage: ThoughtStage
    tags: List[str] = Field(default_factory=list)
    axioms_used: List[str] = Field(default_factory=list)
    assumptions_challenged: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    id: UUID = Field(default_factory=uuid4)

    def __hash__(self):
        """Make ThoughtData hashable based on its ID."""
        return hash(self.id)

    def __eq__(self, other):
        """Compare ThoughtData objects based on their ID."""
        if not isinstance(other, ThoughtData):
            return False
        return self.id == other.id

    @field_validator('thought')
    def thought_not_empty(cls, v: str) -> str:
        """Validate that thought content is not empty."""
        if not v or not v.strip():
            raise ValueError("Thought content cannot be empty")
        return v

    @field_validator('thought_number')
    def thought_number_positive(cls, v: int) -> int:
        """Validate that thought number is positive."""
        if v < 1:
            raise ValueError("Thought number must be positive")
        return v

    @field_validator('total_thoughts')
    def total_thoughts_valid(cls, v: int, values: Dict[str, Any]) -> int:
        """Validate that total thoughts is valid."""
        thought_number = values.data.get('thought_number')
        if thought_number is not None and v < thought_number:
            raise ValueError("Total thoughts must be greater or equal to current thought number")
        return v

    def validate(self) -> bool:
        """Legacy validation method for backward compatibility.

        Returns:
            bool: True if the thought data is valid

        Raises:
            ValueError: If any validation checks fail
        """
        # Validation is now handled by Pydantic automatically
        return True

    def to_dict(self) -> dict:
        """Convert the thought data to a dictionary representation.

        Returns:
            dict: Dictionary representation of the thought data
        """
        result = {
            "thought": self.thought,
            "thoughtNumber": self.thought_number,
            "totalThoughts": self.total_thoughts,
            "nextThoughtNeeded": self.next_thought_needed,
            "stage": self.stage.value,
            "tags": self.tags,
            "axiomsUsed": self.axioms_used,
            "assumptionsChallenged": self.assumptions_challenged,
            "timestamp": self.timestamp
        }

        # Include ID only for internal use, not for test comparisons
        if hasattr(self, '_include_id_in_dict') and self._include_id_in_dict:
            result["id"] = str(self.id)

        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'ThoughtData':
        """Create a ThoughtData instance from a dictionary.

        Args:
            data: Dictionary containing thought data

        Returns:
            ThoughtData: A new ThoughtData instance
        """
        # Convert legacy dictionary format to new model
        model_data = {
            "thought": data["thought"],
            "thought_number": data["thoughtNumber"],
            "total_thoughts": data["totalThoughts"],
            "next_thought_needed": data["nextThoughtNeeded"],
            "stage": ThoughtStage.from_string(data["stage"]),
            "tags": data.get("tags", []),
            "axioms_used": data.get("axiomsUsed", []),
            "assumptions_challenged": data.get("assumptionsChallenged", []),
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }

        # Add ID if present, otherwise generate a new one
        if "id" in data:
            try:
                model_data["id"] = UUID(data["id"])
            except (ValueError, TypeError):
                model_data["id"] = uuid4()

        return cls(**model_data)

    model_config = {
        "arbitrary_types_allowed": True
    }

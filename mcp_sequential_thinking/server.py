from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import json
from enum import Enum
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.style import Style

console = Console(stderr=True)

class ThoughtStage(Enum):
    PROBLEM_DEFINITION = "Problem Definition"
    PLAN = "Plan"
    RESEARCH = "Research"
    ANALYSIS = "Analysis"
    IDEATION = "Ideation"
    SYNTHESIS = "Synthesis"
    EVALUATION = "Evaluation"
    REFINEMENT = "Refinement"
    IMPLEMENTATION = "Implementation"
    CONCLUSION = "Conclusion"
    
    @classmethod
    def from_string(cls, value: str) -> 'ThoughtStage':
        """Convert string to ThoughtStage with better error handling."""
        try:
            # Try direct conversion first
            return cls(value)
        except ValueError:
            # Try case-insensitive match
            upper_value = value.upper()
            for stage in cls:
                if stage.name.upper() == upper_value:
                    return stage
            # Try matching the value part
            for stage in cls:
                if stage.value.upper() == upper_value:
                    return stage
            raise ValueError(f"Invalid stage: {value}. Valid stages are: {[stage.value for stage in cls]}")

@dataclass
class CognitiveContext:
    working_memory: Dict[str, Any] = field(default_factory=dict)
    long_term_memory: Dict[str, Any] = field(default_factory=dict)
    attention_focus: Optional[str] = None
    confidence_level: float = 0.0
    reasoning_chain: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    context_tags: List[str] = field(default_factory=list)

@dataclass
class ThoughtData:
    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    stage: ThoughtStage
    is_revision: Optional[bool] = None
    revises_thought: Optional[int] = None
    branch_from_thought: Optional[int] = None
    branch_id: Optional[str] = None
    needs_more_thoughts: Optional[bool] = None
    score: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> None:
        """Validate thought data consistency."""
        if self.thought_number < 1:
            raise ValueError("Thought number must be positive")
        if self.total_thoughts < self.thought_number:
            raise ValueError("Total thoughts must be greater than or equal to thought number")
        if self.score is not None and not (0 <= self.score <= 1):
            raise ValueError("Score must be between 0 and 1")
        if self.revises_thought is not None and self.revises_thought >= self.thought_number:
            raise ValueError("Cannot revise a future thought")

@dataclass
class EnhancedThoughtData(ThoughtData):
    context: CognitiveContext = field(default_factory=CognitiveContext)
    dependencies: List[int] = field(default_factory=list)
    confidence_score: float = 0.0
    reasoning_type: str = "deductive"
    metacognition_notes: List[str] = field(default_factory=list)
    priority: int = 1
    complexity: int = 1

class MemoryManager:
    def __init__(self):
        self.short_term_buffer: List[ThoughtData] = []
        self.long_term_storage: Dict[str, List[ThoughtData]] = {}
        self.importance_threshold: float = 0.7
        self.max_buffer_size: int = 10
        
    def consolidate_memory(self, thought: ThoughtData) -> None:
        """Move important thoughts from short-term to long-term memory."""
        self.short_term_buffer.append(thought)
        
        if len(self.short_term_buffer) > self.max_buffer_size:
            self._process_buffer()
            
        if thought.score and thought.score >= self.importance_threshold:
            category = thought.stage.value
            if category not in self.long_term_storage:
                self.long_term_storage[category] = []
            self.long_term_storage[category].append(thought)
    
    def _process_buffer(self) -> None:
        """Process and clean up short-term memory buffer."""
        self.short_term_buffer = self.short_term_buffer[-self.max_buffer_size:]
            
    def retrieve_relevant_thoughts(self, current_thought: ThoughtData) -> List[ThoughtData]:
        """Find related thoughts based on tags and content similarity."""
        relevant = []
        for thoughts in self.long_term_storage.values():
            for thought in thoughts:
                if set(thought.tags).intersection(current_thought.tags):
                    relevant.append(thought)
        return relevant

    def clear(self) -> None:
        """Clear all memory storages."""
        self.short_term_buffer.clear()
        self.long_term_storage.clear()

class ReasoningEngine:
    def __init__(self):
        self.reasoning_patterns = {
            "deductive": self.apply_deductive_reasoning,
            "inductive": self.apply_inductive_reasoning,
            "abductive": self.apply_abductive_reasoning,
            "analogical": self.apply_analogical_reasoning,
            "creative": self.apply_creative_reasoning
        }
    
    def apply_deductive_reasoning(self, thought: ThoughtData) -> ThoughtData:
        """Apply deductive reasoning pattern."""
        thought.tags.append("deductive")
        return thought
    
    def apply_inductive_reasoning(self, thought: ThoughtData) -> ThoughtData:
        """Apply inductive reasoning pattern."""
        thought.tags.append("inductive")
        return thought
    
    def apply_abductive_reasoning(self, thought: ThoughtData) -> ThoughtData:
        """Apply abductive reasoning pattern."""
        thought.tags.append("abductive")
        return thought
    
    def apply_analogical_reasoning(self, thought: ThoughtData) -> ThoughtData:
        """Apply analogical reasoning pattern."""
        thought.tags.append("analogical")
        return thought

    def apply_creative_reasoning(self, thought: ThoughtData) -> ThoughtData:
        """Apply creative reasoning pattern."""
        thought.tags.append("creative")
        return thought
        
    def analyze_thought_pattern(self, thought: ThoughtData) -> str:
        """Determine the most appropriate reasoning pattern."""
        # Simple pattern matching based on stage
        if thought.stage in [ThoughtStage.ANALYSIS, ThoughtStage.EVALUATION]:
            return "deductive"
        elif thought.stage == ThoughtStage.IDEATION:
            return "creative"
        elif thought.stage == ThoughtStage.SYNTHESIS:
            return "inductive"
        return "deductive"
        
    def apply_reasoning_strategy(self, thought: ThoughtData) -> ThoughtData:
        """Apply the most appropriate reasoning strategy to enhance the thought."""
        pattern = self.analyze_thought_pattern(thought)
        return self.reasoning_patterns[pattern](thought)

class MetacognitiveMonitor:
    def __init__(self):
        self.quality_metrics = {
            "coherence": 0.0,
            "depth": 0.0,
            "creativity": 0.0,
            "practicality": 0.0,
            "relevance": 0.0,
            "clarity": 0.0
        }
        
    def evaluate_thought_quality(self, thought: ThoughtData) -> Dict[str, float]:
        """Evaluate various aspects of thought quality."""
        metrics = self.quality_metrics.copy()
        
        # Basic metric calculation
        if thought.score:
            base_score = thought.score
            metrics["coherence"] = base_score
            metrics["depth"] = base_score * 0.8
            metrics["creativity"] = base_score * 0.7
            metrics["practicality"] = base_score * 0.9
            metrics["relevance"] = base_score * 0.85
            metrics["clarity"] = base_score * 0.95
            
        # Adjust based on stage
        if thought.stage == ThoughtStage.IDEATION:
            metrics["creativity"] *= 1.2
        elif thought.stage == ThoughtStage.EVALUATION:
            metrics["practicality"] *= 1.2
            
        return metrics
        
    def generate_improvement_suggestions(self, metrics: Dict[str, float]) -> List[str]:
        """Generate suggestions based on metrics."""
        suggestions = []
        for metric, value in metrics.items():
            if value < 0.7:
                if metric == "coherence":
                    suggestions.append("Consider strengthening logical connections")
                elif metric == "depth":
                    suggestions.append("Try exploring the concept more thoroughly")
                elif metric == "creativity":
                    suggestions.append("Consider adding more innovative elements")
                elif metric == "practicality":
                    suggestions.append("Focus on practical applications")
                elif metric == "relevance":
                    suggestions.append("Ensure alignment with main objectives")
                elif metric == "clarity":
                    suggestions.append("Try expressing ideas more clearly")
        return suggestions
        
    def suggest_improvements(self, thought: ThoughtData) -> List[str]:
        """Generate suggestions for improving the thought process."""
        metrics = self.evaluate_thought_quality(thought)
        return self.generate_improvement_suggestions(metrics)

class SequentialThinkingServer:
    def __init__(self):
        self.thought_history: List[ThoughtData] = []
        self.branches: Dict[str, List[ThoughtData]] = {}
        self.active_branch_id: Optional[str] = None

    def _validate_thought_data(self, input_data: dict) -> ThoughtData:
        """Validate and convert input data to ThoughtData."""
        try:
            # Convert stage string to enum
            stage = ThoughtStage.from_string(input_data["stage"])
            
            thought_data = ThoughtData(
                thought=input_data["thought"],
                thought_number=input_data["thoughtNumber"],
                total_thoughts=input_data["totalThoughts"],
                next_thought_needed=input_data["nextThoughtNeeded"],
                stage=stage,
                is_revision=input_data.get("isRevision"),
                revises_thought=input_data.get("revisesThought"),
                branch_from_thought=input_data.get("branchFromThought"),
                branch_id=input_data.get("branchId"),
                needs_more_thoughts=input_data.get("needsMoreThoughts"),
                score=input_data.get("score"),
                tags=input_data.get("tags", [])
            )
            
            # Validate the created thought data
            thought_data.validate()
            return thought_data
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e)}")
        except Exception as e:
            raise ValueError(f"Invalid thought data: {str(e)}")

    def _format_thought(self, thought: ThoughtData) -> Panel:
        """Format a thought for display."""
        # Create title with stage color coding
        stage_colors = {
            ThoughtStage.PROBLEM_DEFINITION: "bold red",
            ThoughtStage.PLAN: "bold yellow",
            ThoughtStage.ANALYSIS: "bold blue",
            ThoughtStage.IDEATION: "bold green",
            ThoughtStage.EVALUATION: "bold magenta",
            ThoughtStage.CONCLUSION: "bold cyan"
        }
        
        title = f"Thought {thought.thought_number}/{thought.total_thoughts}"
        if thought.branch_id:
            title += f" (Branch: {thought.branch_id})"
        if thought.is_revision:
            title += f" (Revision of {thought.revises_thought})"
            
        content = Group(
            Text(thought.thought),
            Text(f"\nStage: {thought.stage.value}", 
                 style=stage_colors.get(thought.stage, "white")),
            Text(f"Tags: {', '.join(thought.tags)}" if thought.tags else ""),
            Text(f"Score: {thought.score:.2f}" if thought.score is not None else "")
        )
        
        return Panel(
            content,
            title=title,
            border_style=stage_colors.get(thought.stage, "white")
        )

    def generate_summary(self) -> str:
        """Generate a summary of the thinking process."""
        if not self.thought_history:
            return json.dumps({"summary": "No thoughts recorded yet"})
            
        stages = {}
        for thought in self.thought_history:
            if thought.stage.value not in stages:
                stages[thought.stage.value] = []
            stages[thought.stage.value].append(thought)
            
        # Calculate various metrics
        summary = {
            "totalThoughts": len(self.thought_history),
            "stages": {
                stage: {
                    "count": len(thoughts),
                    "averageScore": sum(t.score or 0 for t in thoughts) / len(thoughts) if thoughts else 0
                }
                for stage, thoughts in stages.items()
            },
            "branches": {
                branch_id: len(thoughts)
                for branch_id, thoughts in self.branches.items()
            },
            "revisions": sum(1 for t in self.thought_history if t.is_revision),
            "timeline": [
                {
                    "number": t.thought_number,
                    "stage": t.stage.value,
                    "score": t.score,
                    "branch": t.branch_id
                }
                for t in self.thought_history
            ]
        }
        
        return json.dumps({"summary": summary}, indent=2)

class EnhancedSequentialThinkingServer(SequentialThinkingServer):
    def __init__(self):
        super().__init__()
        self.memory_manager = MemoryManager()
        self.reasoning_engine = ReasoningEngine()
        self.metacognitive_monitor = MetacognitiveMonitor()
        
    def process_thought(self, input_data: Any) -> dict:
        """Process a thought with enhanced cognitive capabilities."""
        try:
            # Validate and create thought data
            thought_data = self._validate_thought_data(input_data)
            
            # Apply reasoning strategy
            thought_data = self.reasoning_engine.apply_reasoning_strategy(thought_data)
            
            # Store in memory
            self.memory_manager.consolidate_memory(thought_data)
            
            # Get metacognitive insights
            improvements = self.metacognitive_monitor.suggest_improvements(thought_data)
            
            # Get related thoughts
            related_thoughts = self.memory_manager.retrieve_relevant_thoughts(thought_data)
            
            # Store thought in history
            self.thought_history.append(thought_data)
            
            # Handle branching
            if thought_data.branch_from_thought and thought_data.branch_id:
                if thought_data.branch_id not in self.branches:
                    self.branches[thought_data.branch_id] = []
                self.branches[thought_data.branch_id].append(thought_data)
            
            # Display formatted thought
            console.print(self._format_thought(thought_data))
            # Enhanced response format
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "thoughtAnalysis": {
                            "currentThought": {
                                "thoughtNumber": thought_data.thought_number,
                                "totalThoughts": thought_data.total_thoughts,
                                "nextThoughtNeeded": thought_data.next_thought_needed,
                                "stage": thought_data.stage.value,
                                "score": thought_data.score,
                                "tags": thought_data.tags,
                                "timestamp": thought_data.created_at.isoformat(),
                                "branch": thought_data.branch_id
                            },
                            "analysis": {
                                "relatedThoughtsCount": len(related_thoughts),
                                "qualityMetrics": self.metacognitive_monitor.evaluate_thought_quality(thought_data),
                                "suggestedImprovements": improvements
                            },
                            "context": {
                                "activeBranches": list(self.branches.keys()),
                                "thoughtHistoryLength": len(self.thought_history),
                                "currentStage": thought_data.stage.value
                            }
                        }
                    }, indent=2)
                }]
            }
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed",
                        "errorType": type(e).__name__,
                        "timestamp": datetime.now().isoformat()
                    }, indent=2)
                }],
                "isError": True
            }

    def clear_history(self) -> None:
        """Clear all thought history and related data."""
        self.thought_history.clear()
        self.branches.clear()
        self.memory_manager.clear()
        self.active_branch_id = None

def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP("sequential-thinking")
    thinking_server = EnhancedSequentialThinkingServer()
    
    @mcp.tool()
    async def sequential_thinking(
        thought: str,
        thought_number: int,
        total_thoughts: int,
        next_thought_needed: bool,
        stage: str,
        is_revision: Optional[bool] = None,
        revises_thought: Optional[int] = None,
        branch_from_thought: Optional[int] = None,
        branch_id: Optional[str] = None,
        needs_more_thoughts: Optional[bool] = None,
        score: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        An advanced tool for dynamic and reflective problem-solving through structured thoughts.
        
        Args:
            thought: The content of the current thought
            thought_number: Current position in the sequence
            total_thoughts: Expected total number of thoughts
            next_thought_needed: Whether another thought should follow
            stage: Current thinking stage (e.g., "Problem Definition", "Analysis")
            is_revision: Whether this revises a previous thought
            revises_thought: Number of thought being revised
            branch_from_thought: Starting point for a new thought branch
            branch_id: Identifier for the current branch
            needs_more_thoughts: Whether additional thoughts are needed
            score: Quality score (0.0 to 1.0)
            tags: Categories or labels for the thought
            
        Returns:
            JSON string containing thought analysis and metadata
        """
        input_data = {
            "thought": thought,
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "nextThoughtNeeded": next_thought_needed,
            "stage": stage,
            "isRevision": is_revision,
            "revisesThought": revises_thought,
            "branchFromThought": branch_from_thought,
            "branchId": branch_id,
            "needsMoreThoughts": needs_more_thoughts,
            "score": score,
            "tags": tags or []
        }
        
        result = thinking_server.process_thought(input_data)
        return result["content"][0]["text"]

    @mcp.tool()
    async def get_thinking_summary() -> str:
        """
        Generate a comprehensive summary of the entire thinking process.
        
        Returns:
            JSON string containing analysis of thought history
        """
        return thinking_server.generate_summary()

    @mcp.tool()
    async def clear_thinking_history() -> str:
        """
        Clear all recorded thoughts and reset the server state.
        
        Returns:
            Confirmation message
        """
        thinking_server.clear_history()
        return json.dumps({"status": "success", "message": "Thinking history cleared"})

    return mcp

def main():
    """Main entry point for the sequential thinking server."""
    server = create_server()
    console.print("[bold green]Sequential Thinking Server Starting...[/bold green]")
    return server.run()

if __name__ == "__main__":
    try:
        server = create_server()
        console.print("[bold green]Sequential Thinking Server[/bold green]")
        console.print("Version: 1.0.0")
        console.print("Available stages:", ", ".join(stage.value for stage in ThoughtStage))
        server.run()
    except Exception as e:
        console.print(f"[bold red]Fatal Error:[/bold red] {str(e)}")
        raise
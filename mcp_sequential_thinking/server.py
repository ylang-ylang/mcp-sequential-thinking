from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from enum import Enum
from mcp.server.fastmcp import FastMCP
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.console import Group

console = Console(stderr=True)

class ThoughtStage(Enum):
    PROBLEM_DEFINITION = "Problem Definition"
    ANALYSIS = "Analysis"
    IDEATION = "Ideation"
    EVALUATION = "Evaluation"
    CONCLUSION = "Conclusion"

@dataclass
class CognitiveContext:
    working_memory: Dict[str, Any] = field(default_factory=dict)
    long_term_memory: Dict[str, Any] = field(default_factory=dict)
    attention_focus: Optional[str] = None
    confidence_level: float = 0.0
    reasoning_chain: List[str] = field(default_factory=list)

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

@dataclass
class EnhancedThoughtData(ThoughtData):
    context: CognitiveContext = field(default_factory=CognitiveContext)
    dependencies: List[int] = field(default_factory=list)
    confidence_score: float = 0.0
    reasoning_type: str = "deductive"  # deductive, inductive, abductive
    metacognition_notes: List[str] = field(default_factory=list)

class MemoryManager:
    def __init__(self):
        self.short_term_buffer: List[ThoughtData] = []
        self.long_term_storage: Dict[str, List[ThoughtData]] = {}
        self.importance_threshold: float = 0.7
        
    def consolidate_memory(self, thought: ThoughtData):
        """Move important thoughts from short-term to long-term memory"""
        if thought.score and thought.score >= self.importance_threshold:
            category = thought.stage.value
            if category not in self.long_term_storage:
                self.long_term_storage[category] = []
            self.long_term_storage[category].append(thought)
            
    def retrieve_relevant_thoughts(self, current_thought: ThoughtData) -> List[ThoughtData]:
        """Find related thoughts based on tags and content similarity"""
        relevant = []
        for thoughts in self.long_term_storage.values():
            for thought in thoughts:
                if set(thought.tags).intersection(current_thought.tags):
                    relevant.append(thought)
        return relevant

class ReasoningEngine:
    def __init__(self):
        self.reasoning_patterns = {
            "deductive": self.apply_deductive_reasoning,
            "inductive": self.apply_inductive_reasoning,
            "abductive": self.apply_abductive_reasoning,
            "analogical": self.apply_analogical_reasoning
        }
    
    def apply_deductive_reasoning(self, thought: ThoughtData) -> ThoughtData:
        """Apply deductive reasoning pattern"""
        return thought
    
    def apply_inductive_reasoning(self, thought: ThoughtData) -> ThoughtData:
        """Apply inductive reasoning pattern"""
        return thought
    
    def apply_abductive_reasoning(self, thought: ThoughtData) -> ThoughtData:
        """Apply abductive reasoning pattern"""
        return thought
    
    def apply_analogical_reasoning(self, thought: ThoughtData) -> ThoughtData:
        """Apply analogical reasoning pattern"""
        return thought
        
    def analyze_thought_pattern(self, thought: ThoughtData) -> str:
        """Determine the most appropriate reasoning pattern"""
        return "deductive"  # Default pattern
        
    def apply_reasoning_strategy(self, thought: ThoughtData) -> ThoughtData:
        """Apply the most appropriate reasoning strategy to enhance the thought"""
        pattern = self.analyze_thought_pattern(thought)
        return self.reasoning_patterns[pattern](thought)

class MetacognitiveMonitor:
    def __init__(self):
        self.quality_metrics = {
            "coherence": 0.0,
            "depth": 0.0,
            "creativity": 0.0,
            "practicality": 0.0
        }
        
    def evaluate_thought_quality(self, thought: ThoughtData) -> Dict[str, float]:
        """Evaluate various aspects of thought quality"""
        # Simple initial implementation
        metrics = self.quality_metrics.copy()
        if thought.score:
            metrics["coherence"] = thought.score
            metrics["depth"] = thought.score
        return metrics
        
    def generate_improvement_suggestions(self, metrics: Dict[str, float]) -> List[str]:
        """Generate suggestions based on metrics"""
        suggestions = []
        for metric, value in metrics.items():
            if value < 0.7:
                suggestions.append(f"Consider improving {metric}")
        return suggestions
        
    def suggest_improvements(self, thought: ThoughtData) -> List[str]:
        """Generate suggestions for improving the thought process"""
        metrics = self.evaluate_thought_quality(thought)
        return self.generate_improvement_suggestions(metrics)

class SequentialThinkingServer:
    def __init__(self):
        self.thought_history = []
        self.branches = {}

    def _validate_thought_data(self, input_data: dict) -> ThoughtData:
        """Validate and convert input data to ThoughtData."""
        try:
            stage = ThoughtStage(input_data["stage"])
            return ThoughtData(
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
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid thought data: {str(e)}")

    def _format_thought(self, thought: ThoughtData) -> Panel:
        """Format a thought for display."""
        title = f"Thought {thought.thought_number}/{thought.total_thoughts}"
        if thought.branch_id:
            title += f" (Branch: {thought.branch_id})"
        if thought.is_revision:
            title += f" (Revision of {thought.revises_thought})"
            
        content = Group(
            Text(thought.thought),
            Text(f"\nStage: {thought.stage.value}"),
            Text(f"Tags: {', '.join(thought.tags)}" if thought.tags else "")
        )
        
        return Panel(content, title=title)

    def generate_summary(self) -> str:
        """Generate a summary of the thinking process."""
        if not self.thought_history:
            return json.dumps({"summary": "No thoughts recorded yet"})
            
        stages = {}
        for thought in self.thought_history:
            if thought.stage.value not in stages:
                stages[thought.stage.value] = []
            stages[thought.stage.value].append(thought)
            
        summary = {
            "totalThoughts": len(self.thought_history),
            "stages": {stage: len(thoughts) for stage, thoughts in stages.items()},
            "branches": len(self.branches),
            "revisions": sum(1 for t in self.thought_history if t.is_revision)
        }
        
        return json.dumps({"summary": summary}, indent=2)

class EnhancedSequentialThinkingServer(SequentialThinkingServer):
    def __init__(self):
        super().__init__()
        self.memory_manager = MemoryManager()
        self.reasoning_engine = ReasoningEngine()
        self.metacognitive_monitor = MetacognitiveMonitor()
        
    def process_thought(self, input_data: Any) -> dict:
        """Process a thought with enhanced cognitive capabilities"""
        try:
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
                                "tags": thought_data.tags
                            },
                            "relatedThoughtsCount": len(related_thoughts),
                            "qualityMetrics": self.metacognitive_monitor.quality_metrics,
                            "suggestedImprovements": improvements,
                            "branches": list(self.branches.keys()),
                            "thoughtHistoryLength": len(self.thought_history)
                        }
                    }, indent=2)
                }]
            }
            
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, indent=2)
                }],
                "isError": True
            }

def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP("sequential-thinking")
    thinking_server = EnhancedSequentialThinkingServer()  # Using enhanced server
    
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
        """An advanced tool for dynamic and reflective problem-solving through structured thoughts."""
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
        """Generate a summary of the entire thinking process."""
        return thinking_server.generate_summary()

    return mcp

def main():
    """Main entry point for the sequential thinking server."""
    server = create_server()
    return server.run()

if __name__ == "__main__":
    server = create_server()
    server.run()

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
from mcp.server.fastmcp import FastMCP
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console(stderr=True)

@dataclass
class ThoughtData:
    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    is_revision: Optional[bool] = None
    revises_thought: Optional[int] = None
    branch_from_thought: Optional[int] = None
    branch_id: Optional[str] = None
    needs_more_thoughts: Optional[bool] = None

class SequentialThinkingServer:
    def __init__(self):
        self.thought_history: List[ThoughtData] = []
        self.branches: Dict[str, List[ThoughtData]] = {}
        
    def _validate_thought_data(self, input_data: dict) -> ThoughtData:
        """Validate and convert input dictionary to ThoughtData."""
        required_fields = {
            "thought": str,
            "thoughtNumber": int,
            "totalThoughts": int,
            "nextThoughtNeeded": bool
        }
        
        for field, field_type in required_fields.items():
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(input_data[field], field_type):
                raise ValueError(f"Invalid type for {field}: expected {field_type}")
        
        return ThoughtData(
            thought=input_data["thought"],
            thought_number=input_data["thoughtNumber"],
            total_thoughts=input_data["totalThoughts"],
            next_thought_needed=input_data["nextThoughtNeeded"],
            is_revision=input_data.get("isRevision"),
            revises_thought=input_data.get("revisesThought"),
            branch_from_thought=input_data.get("branchFromThought"),
            branch_id=input_data.get("branchId"),
            needs_more_thoughts=input_data.get("needsMoreThoughts")
        )

    def _format_thought(self, thought_data: ThoughtData) -> Panel:
        """Format a thought into a rich Panel with appropriate styling."""
        if thought_data.is_revision:
            prefix = "🔄 Revision"
            context = f" (revising thought {thought_data.revises_thought})"
            style = "yellow"
        elif thought_data.branch_from_thought:
            prefix = "🌿 Branch"
            context = f" (from thought {thought_data.branch_from_thought}, ID: {thought_data.branch_id})"
            style = "green"
        else:
            prefix = "💭 Thought"
            context = ""
            style = "blue"

        header = Text(f"{prefix} {thought_data.thought_number}/{thought_data.total_thoughts}{context}", style=style)
        content = Text(thought_data.thought)
        
        return Panel.fit(
            content,
            title=header,
            border_style=style,
            padding=(1, 2)
        )

    def process_thought(self, input_data: Any) -> dict:
        """Process a thought and return formatted response."""
        try:
            thought_data = self._validate_thought_data(input_data)
            
            # Adjust total thoughts if needed
            if thought_data.thought_number > thought_data.total_thoughts:
                thought_data.total_thoughts = thought_data.thought_number
            
            # Store thought in history
            self.thought_history.append(thought_data)
            
            # Handle branching
            if thought_data.branch_from_thought and thought_data.branch_id:
                if thought_data.branch_id not in self.branches:
                    self.branches[thought_data.branch_id] = []
                self.branches[thought_data.branch_id].append(thought_data)
            
            # Display formatted thought
            console.print(self._format_thought(thought_data))
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "thoughtNumber": thought_data.thought_number,
                        "totalThoughts": thought_data.total_thoughts,
                        "nextThoughtNeeded": thought_data.next_thought_needed,
                        "branches": list(self.branches.keys()),
                        "thoughtHistoryLength": len(self.thought_history)
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
    thinking_server = SequentialThinkingServer()
    
    @mcp.tool()
    async def sequential_thinking(
        thought: str,
        thought_number: int,
        total_thoughts: int,
        next_thought_needed: bool,
        is_revision: Optional[bool] = None,
        revises_thought: Optional[int] = None,
        branch_from_thought: Optional[int] = None,
        branch_id: Optional[str] = None,
        needs_more_thoughts: Optional[bool] = None
    ) -> str:
        """A detailed tool for dynamic and reflective problem-solving through thoughts.
        
        This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
        Each thought can build on, question, or revise previous insights as understanding deepens.
        
        Args:
            thought: Your current thinking step
            thought_number: Current thought number in sequence
            total_thoughts: Current estimate of thoughts needed
            next_thought_needed: Whether another thought step is needed
            is_revision: Whether this revises previous thinking
            revises_thought: Which thought is being reconsidered
            branch_from_thought: Branching point thought number
            branch_id: Branch identifier
            needs_more_thoughts: If more thoughts are needed
        """
        input_data = {
            "thought": thought,
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "nextThoughtNeeded": next_thought_needed,
            "isRevision": is_revision,
            "revisesThought": revises_thought,
            "branchFromThought": branch_from_thought,
            "branchId": branch_id,
            "needsMoreThoughts": needs_more_thoughts
        }
        
        result = thinking_server.process_thought(input_data)
        return result["content"][0]["text"]

    return mcp

def main():
    """Main entry point for the sequential thinking server."""
    server = create_server()
    return server.run()

if __name__ == "__main__":
    server = create_server()
    server.run()
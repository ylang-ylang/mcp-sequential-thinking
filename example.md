# Customizing the Sequential Thinking MCP Server

This guide provides examples for customizing and extending the Sequential Thinking server to fit your specific needs.

## 1. Modifying Thinking Stages

You can customize the thinking stages by modifying the `ThoughtStage` enum in `models.py`:

```python
class ThoughtStage(Enum):
    """Custom thinking stages for your specific workflow."""
    OBSERVE = "Observe"
    HYPOTHESIZE = "Hypothesize"
    EXPERIMENT = "Experiment"
    ANALYZE = "Analyze"
    CONCLUDE = "Conclude"
```

## 2. Enhancing Thought Data Structure

Extend the `ThoughtData` class to include additional fields:

```python
@dataclass
class EnhancedThoughtData(ThoughtData):
    """Enhanced thought data with additional fields."""
    confidence_level: float = 0.0
    supporting_evidence: List[str] = field(default_factory=list)
    counter_arguments: List[str] = field(default_factory=list)

    def validate(self) -> bool:
        """Validate enhanced thought data."""
        # First validate base fields
        super().validate()

        # Then validate enhanced fields
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValueError("Confidence level must be between 0.0 and 1.0")

        return True
```

## 3. Adding Persistence with a Database

Implement a database-backed storage solution:

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class ThoughtModel(Base):
    """SQLAlchemy model for thought data."""
    __tablename__ = "thoughts"

    id = Column(Integer, primary_key=True)
    thought = Column(String, nullable=False)
    thought_number = Column(Integer, nullable=False)
    total_thoughts = Column(Integer, nullable=False)
    next_thought_needed = Column(Boolean, nullable=False)
    stage = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)

    tags = relationship("TagModel", back_populates="thought")
    axioms = relationship("AxiomModel", back_populates="thought")
    assumptions = relationship("AssumptionModel", back_populates="thought")

class DatabaseStorage:
    """Database-backed storage for thought data."""

    def __init__(self, db_url: str = "sqlite:///thoughts.db"):
        """Initialize database connection."""
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_thought(self, thought: ThoughtData) -> None:
        """Add a thought to the database."""
        with self.Session() as session:
            # Convert ThoughtData to ThoughtModel
            thought_model = ThoughtModel(
                thought=thought.thought,
                thought_number=thought.thought_number,
                total_thoughts=thought.total_thoughts,
                next_thought_needed=thought.next_thought_needed,
                stage=thought.stage.value,
                timestamp=thought.timestamp
            )

            session.add(thought_model)
            session.commit()
```

## 4. Implementing Enhanced Analysis

Add more sophisticated analysis capabilities:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class AdvancedAnalyzer:
    """Advanced thought analysis using NLP techniques."""

    def __init__(self):
        """Initialize the analyzer."""
        self.vectorizer = TfidfVectorizer()
        self.thought_vectors = None
        self.thoughts = []

    def add_thought(self, thought: ThoughtData) -> None:
        """Add a thought to the analyzer."""
        self.thoughts.append(thought)
        # Recompute vectors
        self._compute_vectors()

    def _compute_vectors(self) -> None:
        """Compute TF-IDF vectors for all thoughts."""
        if not self.thoughts:
            return

        thought_texts = [t.thought for t in self.thoughts]
        self.thought_vectors = self.vectorizer.fit_transform(thought_texts)

    def find_similar_thoughts(self, thought: ThoughtData, top_n: int = 3) -> List[Tuple[ThoughtData, float]]:
        """Find thoughts similar to the given thought using cosine similarity."""
        if thought not in self.thoughts:
            self.add_thought(thought)

        thought_idx = self.thoughts.index(thought)
        thought_vector = self.thought_vectors[thought_idx]

        # Compute similarities
        similarities = cosine_similarity(thought_vector, self.thought_vectors).flatten()

        # Get top N similar thoughts (excluding self)
        similar_indices = np.argsort(similarities)[::-1][1:top_n+1]

        return [(self.thoughts[idx], similarities[idx]) for idx in similar_indices]
```

## 5. Creating Custom Prompts

Add custom prompts to guide the thinking process:

```python
from mcp.server.fastmcp.prompts import base

@mcp.prompt()
def problem_definition_prompt(problem_statement: str) -> list[base.Message]:
    """Create a prompt for the Problem Definition stage."""
    return [
        base.SystemMessage(
            "You are a structured thinking assistant helping to define a problem clearly."
        ),
        base.UserMessage(f"I need to define this problem: {problem_statement}"),
        base.UserMessage(
            "Please help me create a clear problem definition by addressing:\n"
            "1. What is the core issue?\n"
            "2. Who is affected?\n"
            "3. What are the boundaries of the problem?\n"
            "4. What would a solution look like?\n"
            "5. What constraints exist?"
        )
    ]

@mcp.prompt()
def research_prompt(problem_definition: str) -> list[base.Message]:
    """Create a prompt for the Research stage."""
    return [
        base.SystemMessage(
            "You are a research assistant helping to gather information about a problem."
        ),
        base.UserMessage(f"I've defined this problem: {problem_definition}"),
        base.UserMessage(
            "Please help me research this problem by:\n"
            "1. Identifying key information needed\n"
            "2. Suggesting reliable sources\n"
            "3. Outlining research questions\n"
            "4. Proposing a research plan"
        )
    ]
```

## 6. Advanced Configuration

Implement a configuration system for your server:

```python
import yaml
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ServerConfig:
    """Configuration for the Sequential Thinking server."""
    server_name: str
    storage_type: str = "file"  # "file" or "database"
    storage_path: Optional[str] = None
    database_url: Optional[str] = None
    default_stages: List[str] = None
    max_thoughts_per_session: int = 100
    enable_advanced_analysis: bool = False

    @classmethod
    def from_yaml(cls, file_path: str) -> "ServerConfig":
        """Load configuration from a YAML file."""
        with open(file_path, 'r') as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    def to_yaml(self, file_path: str) -> None:
        """Save configuration to a YAML file."""
        with open(file_path, 'w') as f:
            yaml.dump(self.__dict__, f)

# Usage
config = ServerConfig.from_yaml("config.yaml")

# Initialize storage based on configuration
if config.storage_type == "file":
    storage = ThoughtStorage(config.storage_path)
else:
    storage = DatabaseStorage(config.database_url)
```

## 7. Web UI Integration

Create a simple web UI for your server:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Sequential Thinking UI")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ThoughtRequest(BaseModel):
    """Request model for adding a thought."""
    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    stage: str
    tags: List[str] = []
    axioms_used: List[str] = []
    assumptions_challenged: List[str] = []

@app.post("/thoughts/")
async def add_thought(request: ThoughtRequest):
    """Add a new thought."""
    try:
        # Convert stage string to enum
        thought_stage = ThoughtStage.from_string(request.stage)

        # Create thought data
        thought_data = ThoughtData(
            thought=request.thought,
            thought_number=request.thought_number,
            total_thoughts=request.total_thoughts,
            next_thought_needed=request.next_thought_needed,
            stage=thought_stage,
            tags=request.tags,
            axioms_used=request.axioms_used,
            assumptions_challenged=request.assumptions_challenged
        )

        # Validate and store
        thought_data.validate()
        storage.add_thought(thought_data)

        # Analyze the thought
        all_thoughts = storage.get_all_thoughts()
        analysis = ThoughtAnalyzer.analyze_thought(thought_data, all_thoughts)

        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/thoughts/")
async def get_thoughts():
    """Get all thoughts."""
    all_thoughts = storage.get_all_thoughts()
    return {
        "thoughts": [t.to_dict() for t in all_thoughts]
    }

@app.get("/summary/")
async def get_summary():
    """Get a summary of the thinking process."""
    all_thoughts = storage.get_all_thoughts()
    return ThoughtAnalyzer.generate_summary(all_thoughts)
```

## 8. Visualization Tools

Add visualization capabilities to your server:

```python
import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict, Any

class ThoughtVisualizer:
    """Visualization tools for thought data."""

    @staticmethod
    def create_stage_distribution_chart(thoughts: List[ThoughtData]) -> str:
        """Create a pie chart showing distribution of thoughts by stage."""
        # Count thoughts by stage
        stage_counts = {}
        for thought in thoughts:
            stage = thought.stage.value
            if stage not in stage_counts:
                stage_counts[stage] = 0
            stage_counts[stage] += 1

        # Create pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(
            stage_counts.values(),
            labels=stage_counts.keys(),
            autopct='%1.1f%%',
            startangle=90
        )
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Thought Distribution by Stage')

        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def create_thinking_timeline(thoughts: List[ThoughtData]) -> str:
        """Create a timeline visualization of the thinking process."""
        # Sort thoughts by number
        sorted_thoughts = sorted(thoughts, key=lambda t: t.thought_number)

        # Create stage colors
        stages = list(ThoughtStage)
        colors = plt.cm.viridis(np.linspace(0, 1, len(stages)))
        stage_colors = {stage.value: colors[i] for i, stage in enumerate(stages)}

        # Create timeline
        plt.figure(figsize=(12, 6))

        for i, thought in enumerate(sorted_thoughts):
            plt.scatter(
                thought.thought_number,
                0,
                s=100,
                color=stage_colors[thought.stage.value],
                label=thought.stage.value if i == 0 or thought.stage != sorted_thoughts[i-1].stage else ""
            )

            # Add connecting lines
            if i > 0:
                plt.plot(
                    [sorted_thoughts[i-1].thought_number, thought.thought_number],
                    [0, 0],
                    'k-',
                    alpha=0.3
                )

        # Remove duplicate legend entries
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), title="Thinking Stages")

        plt.title('Thinking Process Timeline')
        plt.xlabel('Thought Number')
        plt.yticks([])
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{img_str}"
```

## 9. Integration with External Tools

Connect your server to external tools and APIs:

```python
import requests
from typing import Dict, Any, List, Optional

class ExternalToolsIntegration:
    """Integration with external tools and APIs."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with optional API key."""
        self.api_key = api_key

    def search_research_papers(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for research papers related to a query."""
        # Example using Semantic Scholar API
        url = f"https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,year,abstract,url"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("data", [])

    def generate_mind_map(self, central_topic: str, related_topics: List[str]) -> str:
        """Generate a mind map visualization."""
        # This is a placeholder - in a real implementation, you might use
        # a mind mapping API or library to generate the visualization
        pass

    def export_to_notion(self, thoughts: List[ThoughtData], database_id: str) -> Dict[str, Any]:
        """Export thoughts to a Notion database."""
        if not self.api_key:
            raise ValueError("API key required for Notion integration")

        # Example using Notion API
        url = "https://api.notion.com/v1/pages"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        results = []

        for thought in thoughts:
            data = {
                "parent": {"database_id": database_id},
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": f"Thought #{thought.thought_number}: {thought.stage.value}"
                                }
                            }
                        ]
                    },
                    "Content": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": thought.thought
                                }
                            }
                        ]
                    },
                    "Stage": {
                        "select": {
                            "name": thought.stage.value
                        }
                    },
                    "Tags": {
                        "multi_select": [
                            {"name": tag} for tag in thought.tags
                        ]
                    }
                }
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            results.append(response.json())

        return {"exported": len(results), "results": results}
```

## 10. Collaborative Thinking

Implement collaborative features for team thinking:

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
import uuid

@dataclass
class User:
    """User information."""
    id: str
    name: str
    email: str

@dataclass
class Comment:
    """Comment on a thought."""
    id: str
    user_id: str
    content: str
    timestamp: str

    @classmethod
    def create(cls, user_id: str, content: str) -> 'Comment':
        """Create a new comment."""
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content=content,
            timestamp=datetime.now().isoformat()
        )

@dataclass
class CollaborativeThoughtData(ThoughtData):
    """Thought data with collaborative features."""
    created_by: str
    last_modified_by: str
    comments: List[Comment] = field(default_factory=list)
    upvotes: Set[str] = field(default_factory=set)

    def add_comment(self, user_id: str, content: str) -> Comment:
        """Add a comment to the thought."""
        comment = Comment.create(user_id, content)
        self.comments.append(comment)
        return comment

    def toggle_upvote(self, user_id: str) -> bool:
        """Toggle upvote for a user."""
        if user_id in self.upvotes:
            self.upvotes.remove(user_id)
            return False
        else:
            self.upvotes.add(user_id)
            return True

class CollaborativeSession:
    """Session for collaborative thinking."""

    def __init__(self, session_id: str, name: str, created_by: str):
        """Initialize a collaborative session."""
        self.id = session_id
        self.name = name
        self.created_by = created_by
        self.participants: Dict[str, User] = {}
        self.thoughts: List[CollaborativeThoughtData] = []
        self.created_at = datetime.now().isoformat()

    def add_participant(self, user: User) -> None:
        """Add a participant to the session."""
        self.participants[user.id] = user

    def add_thought(self, thought: CollaborativeThoughtData) -> None:
        """Add a thought to the session."""
        thought.validate()
        self.thoughts.append(thought)
```

These examples should help you customize and extend the Sequential Thinking server to fit your specific needs. Feel free to mix and match these approaches or use them as inspiration for your own implementations.
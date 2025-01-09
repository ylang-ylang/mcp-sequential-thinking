# Sequential Thinking MCP Server 🧠

A powerful Model Context Protocol (MCP) server that helps break down complex problems into clear, sequential steps. This tool enhances structured problem-solving by managing thought sequences, allowing revisions, and supporting multiple solution paths.

## 🌟 Key Features

- **Sequential Problem Solving**: Break down complex problems step-by-step
- **Full MCP Integration**: Seamless integration with Claude Desktop

## 🚀 Getting Started

### System Requirements
- Python 3.10+
- UV package manager (preferred) or pip
- Claude Desktop application

### Step-by-Step Installation

1. **Set Up Environment**
  ```bash
  # Create and activate virtual environment
  uv venv
  .venv\Scripts\activate  # Windows
  source .venv/bin/activate  # Unix/Mac
  ```

2. **Install Package**
  ```bash
  uv venv
.venv\Scripts\activate
uv pip install -e .
  ```

3. **Launch Server**
  ```bash
  mcp-sequential-thinking
  ```

4. **Configure Claude Desktop**
  Add to `claude_desktop_config.json`:
  ```json
  {
    "mcpServers": {
     "sequential-thinking": {
      "command": "C:\\path\\to\\your\\.venv\\Scripts\\mcp-sequential-thinking.exe"
     }
    }
  }
  ```

## 🛠️ Core Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `thought` | Current thinking step | Yes |
| `thought_number` | Step sequence number | Yes |
| `total_thoughts` | Estimated steps needed | Yes |
| `next_thought_needed` | Indicates if more steps required | Yes |
| `is_revision` | Marks thought revision | No |
| `revises_thought` | Identifies thought being revised | No |
| `branch_from_thought` | Starting point for new branch | No |
| `branch_id` | Unique branch identifier | No |

## 🔄 Response Format

The server returns JSON with:
- `thoughtNumber`: Current step number
- `totalThoughts`: Total steps estimated
- `nextThoughtNeeded`: Whether more steps needed
- `branches`: List of active branch IDs
- `thoughtHistoryLength`: Total thoughts recorded

## 👩‍💻 Development Setup

1. Clone repository
2. Create development environment:
  ```bash
  uv venv
  source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
  uv pip install -e .
  ```

## 📝 Example Usage

To use with Claude:
1. Start the server
2. In Claude, begin with: "Use sequential thinking to solve this problem..."
3. Enjoy

## 🤝 Contributing & Support

- Submit issues for bugs or suggestions
- Pull requests are welcome
- Follow coding standards in CONTRIBUTING.md

## 📄 License

This project is licensed under the [MIT License](LICENSE).

# Sequential Thinking MCP Server

A Model Context Protocol (MCP) server that helps break down complex problems into clear, sequential steps. This tool enhances structured problem-solving by managing thought sequences, allowing revisions, and supporting multiple solution paths.

## Features

- 🧠 **Sequential Problem Solving**: Break down complex problems step-by-step
- 📊 **Progress Tracking**: Monitor thought sequences and branches

## Prerequisites

- Python 3.11 or higher
- UV package manager ([Install Guide](https://github.com/astral-sh/uv))

## Project Structure

```
mcp-sequential-thinking/
├── mcp_sequential_thinking/
│   ├── server.py
│   └── __init__.py
├── README.md
└── pyproject.toml
```

## Quick Start

1. **Set Up Project**
   ```bash
   # Create and activate virtual environment
   uv venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Unix
   
   # Install package and dependencies
   uv pip install -e .
   ```

## Claude Desktop Integration

Add to your Claude Desktop configuration (`%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\your\\mcp-sequential-thinking\\mcp_sequential_thinking",
        "run",
        "server.py"
      ]
    }
  }
}
```

## Development

Test the server manually:
```bash
cd mcp_sequential_thinking
uv run server.py
```

## Troubleshooting

Common issues:

- **Server Connection Issues**
  - Verify paths in claude_desktop_config.json
  - Check Claude Desktop logs: `%APPDATA%\Claude\logs`
  - Test manual server start

## Parameters

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

## License

MIT License

## Acknowledgments

- Model Context Protocol framework
- Claude Desktop team
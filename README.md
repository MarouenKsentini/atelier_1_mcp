# 📄 Facturation MCP Server

A Model Context Protocol (MCP) server built in Python using FastMCP that acts as an intelligent bridge between AI assistants and an external billing REST API. 

---

## 🏗️ Architecture
The application uses a clean 4-layer architecture to completely isolate network transport from business logic:
1. **Client MCP**: The AI assistant (e.g., Claude Desktop) dispatching JSON-RPC requests via **Streamable HTTP**.
2. **Main Server (`server.py`)**: The primary HTTP entry point that assembles and mounts all tool sub-servers.
3. **Tools Modules (`tools/*.py`)**: Specialized modules translating assistant prompts into structured business logic and JSON payloads.
4. **API Client (`api/myApi.py`)**: A dedicated HTTP access layer communicating with the remote REST backend via `httpx`.

---

## ⚙️ Prerequisites & Installation

* **Python**: Version **3.13 or higher**.
* **Package Manager**: `uv` (recommended for ultra-fast environment and dependency management).

### Quick Start
Run the following commands in your terminal to set up the project environment:

```bash
# Initialize the project
uv init atelier-mcp
cd atelier-mcp

# Create and activate the virtual environment
uv venv
.venv\Scripts\activate  # On Windows (use source .venv/bin/activate on Linux/macOS)

# Install required dependencies
uv add httpx fastmcp load-dotenv

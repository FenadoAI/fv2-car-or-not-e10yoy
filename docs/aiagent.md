# AI Agents Library

Extensible AI agents with LangChain and MCP support.

## Architecture

- **BaseAgent**: Core class with LangChain integration
- **SearchAgent**: Web search capabilities via MCP
- **ChatAgent**: Conversational assistant
- **AgentConfig**: Environment-based configuration

## Environment Variables

```bash
# LiteLLM proxy
LITELLM_BASE_URL="https://litellm-docker-545630944929.us-central1.run.app"
LITELLM_AUTH_TOKEN=""
CODEXHUB_MCP_AUTH_TOKEN=""

# Provider compatibility
OPENAI_API_BASE="${LITELLM_BASE_URL}"
OPENAI_API_KEY="${LITELLM_AUTH_TOKEN}"
ANTHROPIC_API_BASE="${LITELLM_BASE_URL}"
ANTHROPIC_API_KEY="${LITELLM_AUTH_TOKEN}"
GEMINI_API_BASE="${LITELLM_BASE_URL}"
GEMINI_API_KEY="${LITELLM_AUTH_TOKEN}"

# Model selection
AI_MODEL_NAME=gemini-2.5-pro
```

## Supported Models

**Gemini:**
- `gemini-2.5-pro` - Complex tasks
- `gemini-2.5-flash` - General use
- `gemini-2.5-flash-lite` - Simple tasks

**Claude:**
- `claude-4-sonnet` - Balanced performance
- `claude-4-haiku` - Fast tasks

## Usage

### Basic Chat
```python
from ai_agents import ChatAgent, AgentConfig

config = AgentConfig()
agent = ChatAgent(config)
response = await agent.execute("Hello")
```

### Web Search
```python
from ai_agents import SearchAgent, AgentConfig

config = AgentConfig()
agent = SearchAgent(config)
response = await agent.execute("Latest AI news", use_tools=True)
```

### Custom Agent
```python
from ai_agents import BaseAgent, AgentConfig

class MyAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config, "Custom system prompt")

agent = MyAgent(AgentConfig())
```

## MCP Integration

The AI agents have access to powerful MCPs from codexhub.ai that extend their capabilities significantly. These MCPs are pre-configured and available through the `CODEXHUB_MCP_AUTH_TOKEN` environment variable.

### Available MCPs

**Web MCP:**
```json
"web": {
  "url": "https://mcp.codexhub.ai/web/mcp",
  "headers": {
    "x-team-key": "$CODEXHUB_MCP_AUTH_TOKEN"
  }
}
```
- **Capabilities**: Web search and crawling
- **Usage**: Agents can search the web for real-time information and crawl specific websites
- **Auto-configured**: Available in SearchAgent by default

**Image MCP:**
```json
"image": {
  "url": "https://mcp.codexhub.ai/image/mcp",
  "headers": {
    "x-team-key": "$CODEXHUB_MCP_AUTH_TOKEN"
  }
}
```
- **Capabilities**: Image generation based on user prompts
- **Usage**: Agents can create images, illustrations, and visual content on demand
- **Integration**: Available to all agents through the shared configuration

### Using MCPs in Agents

**Web Search & Crawling:**
```python
# SearchAgent automatically uses web MCP
agent = SearchAgent(config)
response = await agent.execute("Latest tech trends", use_tools=True)
```

**Image Generation:**
```python
# Any agent can access image generation
agent = ChatAgent(config)
response = await agent.execute("Generate an image of a sunset over mountains", use_tools=True)
```

**Custom MCP Setup:**
```python
server_configs = [
    {"type": "http", "url": "https://your-mcp.com/mcp", 
     "headers": {"x-api-key": "token"}}
]
agent.setup_mcp(server_configs)
```

## API Endpoints

- `POST /api/chat` - Chat with agents
- `POST /api/search` - Web search with AI
- `GET /api/agents/capabilities` - List capabilities

## Design Principles

- **SOLID**: Single responsibility, extensible design
- **DRY**: Minimal code duplication, reusable patterns

## Configuration

**AgentConfig Properties:**
- `api_base_url` - LiteLLM endpoint
- `model_name` - Model to use  
- `api_key` - Authentication token
from server import llm   # ← import the ready-made client
from google.adk.agents import LlmAgent
from google.adk.runners import Runner, RunConfig
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters
from fastapi import FastAPI, Body, Header, HTTPException
import asyncio
from dotenv import load_dotenv
from google.genai import types
from server import mcp  # ← bring the MCP tool in
from pathlib import Path

FLOW_MD = Path(__file__).with_name("flow.md").read_text(encoding="utf-8")


load_dotenv()
app = FastAPI()
SESSION_SVC = InMemorySessionService()

@app.on_event("startup")
async def startup():
    toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="python",
                args=["server.py"],
                timeout=300,
            )
        )
    )
    agent = LlmAgent(
    model="gemini-2.5-pro",
    name="Design_Repository_agent",
    instruction=FLOW_MD,
    tools=[toolset],   # contains get_current_data + all others
)

    app.state.runner = Runner(
        app_name="travel_bot",
        agent=agent,
        session_service=SESSION_SVC,
    )

@app.post("/chat")
async def chat(
    query: str = Body(..., media_type="text/plain"),
    history: str = Header("", alias="X-History")
):
    
    runner = app.state.runner
    session = await SESSION_SVC.create_session(
        state={},
        app_name="travel_bot",
        user_id="user_fs"
    )
    content = types.Content(role="user", parts=[types.Part(text=query)])

    texts = []
    
    async for event in runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content,
        run_config=RunConfig()
    ):
        if event.content and event.content.parts:
            texts.extend(p.text for p in event.content.parts if p.text)

    return {"response": " ".join(texts)}

@app.get("/health")
def health():
    return {"status": "ok"}


print("Registered routes:")
for route in app.routes:
    print(route.path, route.methods)

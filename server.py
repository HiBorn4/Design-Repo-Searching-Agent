from mcp.server.fastmcp import FastMCP
from loguru import logger
from langchain_openai import AzureChatOpenAI
import os, json
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Design Repository MCP Server")
logger.info(f"Starting server {mcp.name}")

llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-01-preview"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
)

def process_llm_response(raw: str) -> str:
    # 1. Remove markdown code fence if present
    raw = raw.removeprefix("```json").removesuffix("```").strip()

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "response" in parsed:
            return json.dumps({"response": parsed["response"]})
        return json.dumps({"response": [raw]})
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return json.dumps({"response": [raw]})
# -------------------------------------------------------------------
# Tool 1: Emailers and Newsletters
# -------------------------------------------------------------------
@mcp.tool(name="emailer_and_newsletters")
def emailer_and_newsletters(user_query: str) -> str:
    logger.info("emailer_and_newsletters called")
    try:
        with open("data/emailer_&_newsletter.json", "r", encoding="utf-8") as f:
            data = dict(list(json.load(f).items()))
    except Exception as e:
        logger.error(f"Failed to load emailer_and_newsletters data: {e}")
        return json.dumps({"response": ["Error loading emailer/newsletter data"]})

    prompt = f"""
You are an assistant specialized in **email marketing assets**.
Find emailer or newsletter templates/campaigns relevant to the user request.

User query: "{user_query}"

JSON data sample (top 50):
{json.dumps(data, indent=2)}

Return JSON like: {{ "response": ["<file_name1>", "<file_name2>"] }}
"""
    raw = llm.invoke(prompt).content.strip()
    logger.info(f"LLM raw response: {raw}")
    return process_llm_response(raw)


# -------------------------------------------------------------------
# Tool 2: Icon Repository
# -------------------------------------------------------------------
@mcp.tool(name="icon_repository")
def icon_repository(user_query: str) -> str:
    logger.info("icon_repository called")
    try:
        with open("data/icon_repository.json", "r", encoding="utf-8") as f:
            data = dict(list(json.load(f).items()))
    except Exception as e:
        logger.error(f"Failed to load icon_repository data: {e}")
        return json.dumps({"response": ["Error loading icon repository data"]})

    prompt = f"""
You are an **icon library curator**.
Identify icons or icon sets matching the user query.

User query: "{user_query}"

JSON data sample:
{json.dumps(data, indent=2)}

Respond in JSON: {{ "response": ["<icon_file>"] }}
"""
    raw = llm.invoke(prompt).content.strip()
    
    logger.info(f"LLM raw response: {raw}")
    return process_llm_response(raw)


# -------------------------------------------------------------------
# Tool 3: Internal Logos
# -------------------------------------------------------------------
@mcp.tool(name="internal_logos")
def internal_logos(user_query: str) -> str:
    logger.info("internal_logos called")
    try:
        with open("data/internal_logos.json", "r", encoding="utf-8") as f:
            data = dict(list(json.load(f).items()))
    except Exception as e:
        logger.error(f"Failed to load internal_logos data: {e}")
        return json.dumps({"response": ["Error loading internal logos data"]})

    prompt = f"""
You are a **brand logo archivist**.
Locate internal or department-specific logos that match the user query.

User query: "{user_query}"

JSON data sample:
{json.dumps(data, indent=2)}

Return JSON: {{ "response": ["<logo_file>"] }}
"""
    raw = llm.invoke(prompt).content.strip()
    
    logger.info(f"LLM raw response: {raw}")
    return process_llm_response(raw)


# -------------------------------------------------------------------
# Tool 4: Mahindra Branding Guidelines
# -------------------------------------------------------------------
@mcp.tool(name="mahindra_branding_guideline")
def mahindra_branding_guideline(user_query: str) -> str:
    logger.info("mahindra_branding_guideline called")
    try:
        with open("data/mahindra_branding.json", "r", encoding="utf-8") as f:
            data = dict(list(json.load(f).items()))
    except Exception as e:
        logger.error(f"Failed to load branding data: {e}")
        return json.dumps({"response": ["Error loading branding guideline data"]})

    prompt = f"""
You are a **brand guideline expert**.
Retrieve Mahindra branding rules, colors, typography, or template files.

User query: "{user_query}"

JSON data sample:
{json.dumps(data, indent=2)}

Respond as: {{ "response": ["<guideline_file>"] }}
"""
    raw = llm.invoke(prompt).content.strip()
    
    logger.info(f"LLM raw response: {raw}")
    return process_llm_response(raw)


# -------------------------------------------------------------------
# Tool 5: PowerPoint Repository
# -------------------------------------------------------------------
@mcp.tool(name="ppt_repository")
def ppt_repository(user_query: str) -> str:
    logger.info("ppt_repository called")
    try:
        with open("data/ppt_repository.json", "r", encoding="utf-8") as f:
            data = dict(list(json.load(f).items()))
    except Exception as e:
        logger.error(f"Failed to load ppt_repository data: {e}")
        return json.dumps({"response": ["Error loading PPT repository data"]})

    prompt = f"""
You are a **presentation deck finder**.
Suggest PowerPoint templates or slide decks that fit the user's topic or style.

User query: "{user_query}"

JSON data sample:
{json.dumps(data, indent=2)}

Return JSON: {{ "response": ["<ppt_file>"] }}
"""
    raw = llm.invoke(prompt).content.strip()
    
    logger.info(f"LLM raw response: {raw}")
    return process_llm_response(raw)


if __name__ == "__main__":
    mcp.run(transport="stdio")

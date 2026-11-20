import io
import re
import json
import math
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session

from app.config import settings
from app.models import UserKnowledge, ChatMessage

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import StructuredTool


# --- EMBEDDINGS & CO-SINE SIMILARITY (pgvector-free RAG) ---

def check_gemini_config():
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not configured. AI capabilities are disabled.")


def get_embeddings_model():
    check_gemini_config()
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.GEMINI_API_KEY
    )


def compute_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes standard cosine similarity between two float vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a*a for a in v1))
    norm_b = math.sqrt(sum(b*b for b in v2))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def get_relevant_user_facts(db: Session, user_id: uuid.UUID, query: str, limit: int = 5) -> List[str]:
    """
    Retrieves facts from the user profile database matching the query
    calculated through cosine similarity.
    """
    if not settings.GEMINI_API_KEY:
        return []
    try:
        embed_model = get_embeddings_model()
        query_vector = embed_model.embed_query(query)
        
        # Pull all facts for this user
        db_facts = db.query(UserKnowledge).filter(UserKnowledge.user_id == user_id).all()
        if not db_facts:
            return []
            
        scored_facts = []
        for f in db_facts:
            try:
                fact_vector = json.loads(f.embedding_str)
                sim = compute_cosine_similarity(query_vector, fact_vector)
                scored_facts.append((sim, f.fact))
            except Exception:
                continue
                
        # Sort by similarity descending
        scored_facts.sort(key=lambda x: x[0], reverse=True)
        return [fact for sim, fact in scored_facts[:limit]]
    except Exception as e:
        print(f"RAG search error: {e}")
        return []


def learn_user_fact(db: Session, user_id: uuid.UUID, fact: str) -> UserKnowledge:
    """
    Generates embedding for a fact and saves it to the database.
    """
    check_gemini_config()
    embed_model = get_embeddings_model()
    vector = embed_model.embed_query(fact)
    
    db_fact = UserKnowledge(
        user_id=user_id,
        fact=fact,
        embedding_str=json.dumps(vector)
    )
    db.add(db_fact)
    db.commit()
    db.refresh(db_fact)
    return db_fact


# --- SATORIDOCS REST API CLIENT ---

class SatoriDocsClient:
    """
    HTTP REST Client that makes calls to SatoriDocs microservice,
    forwarding the authenticated user's JWT.
    """
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.base_url = settings.SATORIDOCS_URL

    def list_documents(self) -> str:
        """List all documents owned by you in SatoriDocs."""
        import httpx
        try:
            r = httpx.get(f"{self.base_url}/documents/", headers=self.headers, timeout=10.0)
            if r.status_code != 200:
                return f"Failed to retrieve documents: {r.text}"
            docs = r.json()
            if not docs:
                return "You have no documents."
            return "\n".join([f"- ID: {d['id']}, Title: '{d['title']}', Description: {d['description'] or 'None'}" for d in docs])
        except Exception as e:
            return f"Error connecting to SatoriDocs: {str(e)}"

    def get_document_outline(self, document_id: str) -> str:
        """Get the outline structure (modules and sections hierarchy) of a specific document using its ID."""
        import httpx
        try:
            r = httpx.get(f"{self.base_url}/documents/{document_id}/export/json", headers=self.headers, timeout=10.0)
            if r.status_code != 200:
                return f"Failed to retrieve outline: {r.text}"
            data = r.json()
            lines = [f"Document Title: '{data['title']}' (ID: {data['id']})", f"Description: {data['description'] or ''}\nStructure:"]
            for m in data.get("modules", []):
                lines.append(f"- Module: '{m['title']}' (ID: {m['id']})")
                for s in m.get("sections", []):
                    lines.append(f"  * Section: '{s['title']}' (ID: {s['id']}, Level: H{s['level']})")
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving document outline: {str(e)}"

    def read_section(self, section_id: str) -> str:
        """Read the detailed text/markdown content of a specific section by its ID."""
        import httpx
        try:
            r = httpx.get(f"{self.base_url}/sections/{section_id}", headers=self.headers, timeout=10.0)
            if r.status_code != 200:
                return f"Failed to read section: {r.text}"
            data = r.json()
            return f"Section: '{data['title']}'\nContent:\n{data['content'] or 'Empty'}"
        except Exception as e:
            return f"Error reading section: {str(e)}"

    def edit_section(self, section_id: str, instruction: str) -> str:
        """Edit or refine the content of a specific section by its ID using natural language instructions."""
        import httpx
        try:
            r = httpx.post(
                f"{self.base_url}/sections/{section_id}/edit",
                headers=self.headers,
                json={"instruction": instruction},
                timeout=20.0
            )
            if r.status_code != 200:
                return f"Failed to edit section: {r.text}"
            data = r.json()
            return f"Section '{data['title']}' edited successfully. Refined Content:\n{data['content']}"
        except Exception as e:
            return f"Error editing section: {str(e)}"


# --- SATORIAI TOOL-CALLING CONVERSATIONAL AGENT ---

def run_satori_agent(db: Session, user_id: uuid.UUID, token: str, session_id: str, message: str) -> str:
    """
    Executes a conversational LLM loop, matching user context against profile memories
    and exposing SatoriDocs operations as agent tools.
    """
    check_gemini_config()
    
    # 1. Fetch relevant memories (RAG)
    user_facts = get_relevant_user_facts(db, user_id, message, limit=5)
    
    # 2. Setup SatoriDocs HTTP Client and define tools
    docs_client = SatoriDocsClient(token)
    
    # Nested tool helpers to close over the active database session and user ID
    def remember_user_fact_tool(fact: str) -> str:
        try:
            learn_user_fact(db, user_id, fact)
            return f"Fact remembered successfully: '{fact}'."
        except Exception as e:
            return f"Failed to remember fact: {str(e)}"
            
    langchain_tools = [
        StructuredTool.from_function(
            func=docs_client.list_documents,
            name="list_documents",
            description="List all documents owned by you in SatoriDocs. Use this when the user asks to see their documents."
        ),
        StructuredTool.from_function(
            func=docs_client.get_document_outline,
            name="get_document_outline",
            description="Get the outline of a specific document (its modules and sections hierarchy) using its ID."
        ),
        StructuredTool.from_function(
            func=docs_client.read_section,
            name="read_section",
            description="Read the detailed text/markdown content of a specific section by its ID."
        ),
        StructuredTool.from_function(
            func=docs_client.edit_section,
            name="edit_section",
            description="Edit or refine the content of a specific section by its ID using natural language instructions."
        ),
        StructuredTool.from_function(
            func=remember_user_fact_tool,
            name="remember_user_fact",
            description="Save or remember a personal detail, preference, or fact about the user for future context customization."
        )
    ]
    
    # 3. Instantiate Gemini model and bind tools
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.4
    )
    llm_with_tools = llm.bind_tools(langchain_tools)
    
    # 4. Construct System Prompt injecting RAG facts and Satori Ecosystem metadata
    facts_str = "\n".join([f"- {f}" for f in user_facts]) if user_facts else "No facts recorded yet."
    system_prompt = (
        "You are SatoriAI, the central AI assistant for Satori. "
        "You help users coordinate actions across the Satori ecosystem.\n\n"
        "Here are facts you know about the user (use these to customize responses):\n"
        f"{facts_str}\n\n"
        "Available Services:\n"
        "- SatoriBackend: Main .NET Core API on port 8080 (User logs, tracking, JWTs).\n"
        "- SatoriDocs: Document compiler on port 8000 (Modules, sections, Word DOCX/Markdown exports).\n"
        "- SatoriAi: This assistant service on port 8002.\n\n"
        "Use tools to fetch outlines, read sections, edit sections, or remember facts. "
        "Explain any edits you perform clearly."
    )
    
    # 5. Fetch past chat history (Conversational Memory)
    history_records = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id,
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    messages = [SystemMessage(content=system_prompt)]
    for msg in history_records:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
            
    messages.append(HumanMessage(content=message))
    
    # 6. Execute Agent Loop
    for _ in range(5):
        res = llm_with_tools.invoke(messages)
        messages.append(res)
        
        # If no tool is requested, we have the final reply
        if not res.tool_calls:
            break
            
        # Execute tool calls and insert back into conversation context
        for tc in res.tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            tool_id = tc["id"]
            
            if tool_name == "list_documents":
                output = docs_client.list_documents(**tool_args)
            elif tool_name == "get_document_outline":
                output = docs_client.get_document_outline(**tool_args)
            elif tool_name == "read_section":
                output = docs_client.read_section(**tool_args)
            elif tool_name == "edit_section":
                output = docs_client.edit_section(**tool_args)
            elif tool_name == "remember_user_fact":
                output = remember_user_fact_tool(**tool_args)
            else:
                output = f"Tool '{tool_name}' not found."
                
            messages.append(ToolMessage(content=output, tool_call_id=tool_id))
            
    # 7. Persist chat message history logs
    db_user_msg = ChatMessage(session_id=session_id, user_id=user_id, role="user", content=message)
    db_ai_msg = ChatMessage(session_id=session_id, user_id=user_id, role="assistant", content=res.content)
    db.add(db_user_msg)
    db.add(db_ai_msg)
    db.commit()
    
    return res.content

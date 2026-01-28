"""
FastAPI application - Main entry point for AI Yoga Coach
"""
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root so GROQ_API_KEY, etc. are available
load_dotenv(Path(__file__).resolve().parent / ".env")

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List

from config import Config
from core.body_engine import BodyStateEngine
from core.pose_pool import PosePool
from rag.retriever import RAGRetriever
from agents.planner import PlannerAgent
from agents.sequencer import SequencerAgent
from agents.cue_writer import CueWriterAgent
from db.session_repo import SessionRepository
from db.user_repo import UserRepository
from db.database_factory import DatabaseFactory
from llm.client import create_llm_client
from rag.knowledge_io import save_knowledge_to_file, get_knowledge_path
from rag.ingest import ingest_from_text
from prompts.chat_prompt import CHAT_SYSTEM_PROMPT, format_chat_user_prompt

app = FastAPI(
    title="AI Yoga Coach API",
    description="Body-Aware + Rule-Guided + RAG-Enhanced LLM System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Training focus: display value -> internal pose type
TRAINING_FOCUS_MAP = {
    "seated": "seated",
    "forward_fold": "forward_fold",
    "backbend": "backbend",
    "twist": "twist",
    "side_bend": "side_bend",
    "balance": "balance",
    "inversion": "inversion",
}


# Request/Response models
class YogaFlowRequest(BaseModel):
    """Request model for generating yoga flow"""
    last_period_date: str
    cycle_length: int = 28
    energy: int = 3  # 1-5 scale
    pain: int = 1    # 1-5 scale
    duration: int = 20  # minutes
    user_id: Optional[str] = None
    training_focus: Optional[list[str]] = None  # e.g. ["seated", "forward_fold", "balance"]


class YogaFlowResponse(BaseModel):
    """Response model for yoga flow"""
    body_state: dict
    structure: dict
    sequence: dict
    cues: dict
    session_id: Optional[str] = None


# RAG knowledge entry (one pose/topic)
class KnowledgeEntry(BaseModel):
    pose: str = Field(..., description="Pose or topic id, e.g. child_pose or yoga_sutras_1_1")
    alignment: List[str] = Field(default_factory=list, description="Alignment cues")
    contraindications: List[str] = Field(default_factory=list, description="Contraindications")
    benefits: List[str] = Field(default_factory=list, description="Benefits")
    breathing: str = Field(default="", description="Breathing guidance")
    modifications: str = Field(default="", description="Modifications")


class InsertKnowledgeRequest(BaseModel):
    """Request body for inserting knowledge into RAG."""
    entries: List[KnowledgeEntry] = Field(..., description="One or more knowledge entries to merge into RAG")


class InsertKnowledgeResponse(BaseModel):
    """Response after inserting knowledge."""
    saved: int = Field(..., description="Number of entries now in the RAG store")
    path: str = Field(..., description="File path where RAG knowledge is stored")


class IngestFromTextRequest(BaseModel):
    """Request to ingest knowledge from raw text (LLM extracts structured entries)."""
    text: str = Field(..., min_length=1, description="Raw text to ingest (e.g. from a .txt file)")
    source_is_philosophy: bool = Field(
        default=False,
        description="If true, treat as yoga philosophy (e.g. 瑜伽经); entries use topic/sutra ids instead of pose names"
    )


class IngestFromTextResponse(BaseModel):
    """Response from text ingest."""
    ingested: int = Field(..., description="Number of entries extracted and merged into RAG")
    poses: List[str] = Field(default_factory=list, description="Pose/topic ids that were added or updated")
    path: str = Field(..., description="RAG knowledge file path")
    message: str = Field(..., description="Human-readable status")


class ChatRequest(BaseModel):
    """Request for yoga Q&A chat."""
    message: str = Field(..., min_length=1, description="User question about yoga")


class ChatResponse(BaseModel):
    """Response from yoga Q&A chat."""
    reply: str = Field(..., description="Assistant reply grounded in yoga knowledge")


# Initialize components (LLM optional: set GROQ_API_KEY, GEMINI_API_KEY, or LLM_PROVIDER=ollama)
_llm = create_llm_client()
body_engine = BodyStateEngine()
pose_pool = PosePool()
rag_retriever = RAGRetriever()
planner_agent = PlannerAgent(llm_client=_llm)
sequencer_agent = SequencerAgent(llm_client=_llm)
cue_writer_agent = CueWriterAgent(llm_client=_llm)
session_repo = SessionRepository()
user_repo = UserRepository()


def generate_yoga_flow(user_input: dict) -> dict:
    """
    Main pipeline for generating yoga flow.
    
    This is the "technical soul" of the system.
    """
    # 1. Body State Engine (deterministic)
    body_state = body_engine.process(user_input)
    
    # 2. Filter pose candidates
    pose_candidates = pose_pool.filter_by_types(body_state.allowed_pose_types)
    
    # 3. RAG enrichment
    enriched_poses = rag_retriever.enrich_poses(pose_candidates, body_state.cycle_phase)
    
    # 4. Planner Agent
    structure = planner_agent.generate_structure(body_state, enriched_poses)
    
    # 5. Sequencer Agent
    sequence = sequencer_agent.generate_sequence(structure, body_state, enriched_poses)
    
    # 6. Cue Writer Agent
    cues = cue_writer_agent.generate_cues(sequence, body_state)
    
    return {
        "body_state": body_engine.to_dict(body_state),
        "structure": structure,
        "sequence": sequence,
        "cues": cues
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/v1/yoga-flow", response_model=YogaFlowResponse)
async def create_yoga_flow(request: YogaFlowRequest):
    """
    Generate a personalized yoga flow.
    
    This is the main endpoint that orchestrates the entire pipeline.
    """
    try:
        # Prepare user input: normalize training_focus to internal pose types
        raw_focus = request.training_focus or []
        training_focus = [TRAINING_FOCUS_MAP.get(str(x).strip(), x) for x in raw_focus]
        training_focus = [t for t in training_focus if t in set(TRAINING_FOCUS_MAP.values())]
        
        user_input = {
            "last_period_date": request.last_period_date,
            "cycle_length": request.cycle_length,
            "energy": request.energy,
            "pain": request.pain,
            "duration": request.duration,
            "training_focus": training_focus if training_focus else None
        }
        
        # Generate flow
        result = generate_yoga_flow(user_input)
        
        # Save session if user_id provided
        session_id = None
        if request.user_id:
            session_data = {
                "user_input": user_input,
                **result
            }
            session_repo.save_session(request.user_id, session_data)
            session_id = f"session_{request.user_id}_{hash(str(session_data))}"
        
        return YogaFlowResponse(
            body_state=result["body_state"],
            structure=result["structure"],
            sequence=result["sequence"],
            cues=result["cues"],
            session_id=session_id
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/body-state")
async def get_body_state(
    last_period_date: str,
    cycle_length: int = 28,
    energy: int = 3,
    pain: int = 1
):
    """
    Get body state calculation (for testing/debugging).
    """
    try:
        user_input = {
            "last_period_date": last_period_date,
            "cycle_length": cycle_length,
            "energy": energy,
            "pain": pain,
            "duration": 20
        }
        body_state = body_engine.process(user_input)
        return body_engine.to_dict(body_state)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/rag/knowledge", response_model=InsertKnowledgeResponse)
async def insert_rag_knowledge(request: InsertKnowledgeRequest):
    """
    Insert knowledge entries into the RAG store (data/yoga_knowledge.json).
    Entries are merged by `pose`; existing entries with the same pose are overwritten.
    Restart the app or redeploy for new entries to be used in flow generation.
    """
    try:
        entries = [e.model_dump() for e in request.entries]
        if not entries:
            raise HTTPException(status_code=400, detail="At least one entry is required")
        path = get_knowledge_path()
        saved = save_knowledge_to_file(entries, path, merge=True)
        return InsertKnowledgeResponse(saved=saved, path=str(path))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _do_ingest_from_text(text: str, source_is_philosophy: bool) -> IngestFromTextResponse:
    """Shared logic for text ingest; returns response or raises HTTPException."""
    entries = ingest_from_text(
        text.strip(),
        vector_store=None,
        save_to_rag=True,
        source_is_philosophy=source_is_philosophy,
    )
    path = get_knowledge_path()
    poses = [e.get("pose") for e in entries if isinstance(e, dict) and e.get("pose")]
    if not entries:
        raise HTTPException(
            status_code=422,
            detail="No entries extracted. Set GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env for text extraction."
        )
    return IngestFromTextResponse(
        ingested=len(entries),
        poses=poses,
        path=str(path),
        message=f"Ingested {len(entries)} entries into {path}. Restart the app to use them in flows and chat."
    )


@app.post("/api/v1/rag/ingest", response_model=IngestFromTextResponse)
async def ingest_text_to_rag(request: IngestFromTextRequest):
    """
    Ingest knowledge from raw text into RAG (JSON body).

    **Postman:** Body → raw → JSON: `{"text": "your text...", "source_is_philosophy": false}`
    Inside the "text" string, escape double quotes as \\" and newlines as \\n, or use the
    plain-text endpoint instead to avoid escaping.
    """
    try:
        return _do_ingest_from_text(request.text, request.source_is_philosophy)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/rag/ingest/text", response_model=IngestFromTextResponse)
async def ingest_text_to_rag_plain(request: Request, source_is_philosophy: bool = False):
    """
    Ingest knowledge from raw text (plain-text body). No JSON escaping needed.

    **Postman:** Body → raw → Text (not JSON). Paste your full .txt content as-is.
    Add query param: ?source_is_philosophy=true for 瑜伽经 / philosophy.
    """
    try:
        body = await request.body()
        text = body.decode("utf-8", errors="replace")
        if not text.strip():
            raise HTTPException(status_code=400, detail="Body is empty. Send the raw text in the body.")
        return _do_ingest_from_text(text, source_is_philosophy)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _answer_yoga_question(user_message: str) -> str:
    """Use RAG + LLM to answer a yoga question. Returns reply text."""
    context = rag_retriever.search_for_chat(user_message, limit=6)
    if not context:
        context = "(No specific pose/knowledge matched; answer from general yoga best practices.)"
        logger.info("[Chat] LLM using built-in/general knowledge only (no RAG context for this question)")
    else:
        logger.info("[Chat] LLM using RAG context (retrieved knowledge + general knowledge)")
    prompt = format_chat_user_prompt(context=context, user_message=user_message)
    if _llm:
        return _llm.generate(prompt, system_prompt=CHAT_SYSTEM_PROMPT, temperature=0.4)
    return "Chat requires an LLM. Set GROQ_API_KEY (or GEMINI/OPENAI) in .env to use the yoga Q&A chatbot."


@app.post("/api/v1/chat", response_model=ChatResponse)
async def yoga_chat(request: ChatRequest):
    """
    Yoga Q&A chatbot. Ask questions about poses, alignment, breathing, philosophy, etc.
    Uses RAG (yoga knowledge base) + LLM to ground answers.
    """
    try:
        reply = _answer_yoga_question(request.message.strip())
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve frontend static files when present (single-port deploy). API stays at /api/* and /health.
# Next.js static export uses out/chat.html for /chat; StaticFiles alone looks for "chat" and 404s.
# So we try path, path.html, path/index.html, then index.html for SPA fallback.
_static_dir = Path(__file__).resolve().parent / "static"
if _static_dir.exists():
    @app.get("/{full_path:path}")
    async def serve_static(full_path: str):
        if full_path.startswith("api/") or full_path == "health":
            raise HTTPException(status_code=404, detail="Not found")
        base = (_static_dir / full_path).resolve()
        if not str(base).startswith(str(_static_dir.resolve())):
            raise HTTPException(status_code=404, detail="Not found")
        # Try: exact file, dir/index.html, path.html (Next.js export), then index.html (SPA fallback)
        candidates = [base]
        if base.suffix == "":
            candidates.append(base / "index.html")
            candidates.append(base.with_name(base.name + ".html"))
        else:
            candidates.append(base / "index.html" if base.is_dir() else None)
        candidates.append(_static_dir / "index.html")
        for p in candidates:
            if p and p.is_file():
                return FileResponse(p, media_type="text/html" if p.suffix == ".html" else None)
        raise HTTPException(status_code=404, detail="Not found")
else:
    @app.get("/")
    async def root():
        return {"message": "AI Yoga Coach API v1.0", "architecture": "Body-Aware + Rule-Guided + RAG-Enhanced LLM System"}


if __name__ == "__main__":
    import uvicorn
    Config.validate()
    uvicorn.run(
        "app:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.DEBUG
    )

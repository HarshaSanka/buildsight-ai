import os
import secrets
import sqlite3
import threading
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from app.knowledge import Knowledge
from app.workflows import build_graph
from app.integrations import MockProcore, MockAutodesk


class Query(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class Run(Query):
    kind: Literal["rfi", "schedule", "risk"]
    as_of: date = date(2026, 11, 7)


class Decision(BaseModel):
    approve: bool
    reason: str = Field(min_length=3, max_length=1000)


def create_app(db_path=None):
    @asynccontextmanager
    async def lifespan(app):
        path = db_path or os.getenv("BUILDSIGHT_DB", "state/buildsight.sqlite")
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        app.state.conn = conn
        app.state.lock = threading.Lock()
        app.state.knowledge = Knowledge()
        app.state.graph = build_graph(app.state.knowledge, SqliteSaver(conn))
        yield
        conn.close()

    app = FastAPI(title="BuildSight AI — synthetic construction portfolio", lifespan=lifespan)

    def authenticate(x_api_key: str = Header(default="")):
        key = os.getenv("BUILDSIGHT_API_KEY", "local-demo-key")
        if not secrets.compare_digest(x_api_key, key):
            raise HTTPException(401, "Invalid API key")
        return "local-reviewer"

    def snapshot(run_id):
        s = app.state.graph.get_state({"configurable": {"thread_id": run_id}})
        if not s.values:
            raise HTTPException(404, "Run not found")
        return {
            "id": run_id,
            "status": "awaiting_approval" if s.next else s.values.get("status", "unknown"),
            "state": s.values,
        }

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "data": "synthetic",
            "generation": "optional_ollama" if os.getenv("BUILDSIGHT_OLLAMA_MODEL") else "extractive; no LLM",
        }

    @app.get("/", response_class=HTMLResponse)
    def home():
        return Path(__file__).with_name("index.html").read_text()

    @app.post("/ask", dependencies=[Depends(authenticate)])
    def ask(q: Query):
        return app.state.knowledge.answer(q.question)

    @app.get("/graph", dependencies=[Depends(authenticate)])
    def graph():
        g = app.state.knowledge.graph
        return {
            "nodes": [{"id": n, **v} for n, v in g.nodes(data=True)],
            "edges": [{"source": a, "target": b, **v} for a, b, v in g.edges(data=True)],
        }

    @app.get("/integrations/{vendor}", dependencies=[Depends(authenticate)])
    def integrations(vendor: Literal["procore", "autodesk"]):
        connector = MockProcore if vendor == "procore" else MockAutodesk
        return {"simulated": True, "records": connector(app.state.knowledge).list_records()}

    @app.post("/runs", dependencies=[Depends(authenticate)])
    def run(body: Run):
        run_id = str(uuid4())
        with app.state.lock:
            app.state.graph.invoke(
                {"kind": body.kind, "question": body.question, "as_of": body.as_of.isoformat()},
                {"configurable": {"thread_id": run_id}},
            )
            return snapshot(run_id)

    @app.get("/runs/{run_id}", dependencies=[Depends(authenticate)])
    def read(run_id: str):
        with app.state.lock:
            return snapshot(run_id)

    @app.post("/runs/{run_id}/decision")
    def decide(run_id: str, body: Decision, reviewer=Depends(authenticate)):
        with app.state.lock:
            current = snapshot(run_id)
            if current["status"] != "awaiting_approval":
                raise HTTPException(409, "Run already decided")
            app.state.graph.invoke(
                Command(
                    resume={
                        **body.model_dump(),
                        "reviewer": reviewer,
                        "decided_at": datetime.now(timezone.utc).isoformat(),
                    }
                ),
                {"configurable": {"thread_id": run_id}},
            )
            return snapshot(run_id)

    return app


app = create_app()

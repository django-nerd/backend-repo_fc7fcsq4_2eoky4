import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Contact, Project

app = FastAPI(title="Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Portfolio API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

@app.post("/api/contact")
async def submit_contact(contact: Contact):
    try:
        doc_id = create_document("contact", contact)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects", response_model=List[Project])
def list_projects():
    try:
        docs = get_documents("project", {}, limit=50)
        # Map DB docs to Project model
        projects: List[Project] = []
        for d in docs:
            projects.append(Project(
                title=d.get("title", "Untitled"),
                description=d.get("description"),
                tags=d.get("tags", []),
                repo=d.get("repo"),
                demo=d.get("demo"),
            ))
        return projects
    except Exception:
        # Fallback sample data if DB not configured
        return [
            Project(title="Realtime Chat App", description="Full-stack chat app with websockets, auth, and sleek UI.", tags=["React", "FastAPI", "WebSockets", "MongoDB"], repo="https://github.com/"),
            Project(title="Design System Kit", description="Composable components, tokens, and docs powered by Storybook.", tags=["React", "TypeScript", "Storybook"], repo="https://github.com/"),
            Project(title="AI Image Playground", description="Modern UI to explore image generation with server-side pipelines.", tags=["Next.js", "Python", "Inference"], demo="https://example.com"),
        ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
FastAPI Server for DistroFlow Browser Extension

Provides REST API and WebSocket endpoints for the browser extension
to communicate with DistroFlow automation.
"""

import asyncio
import logging
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from distroflow.core.scheduler import Scheduler, Frequency
from distroflow.core.content_transformer import ContentTransformer, Platform
from distroflow.platforms.base import AuthConfig, PostResult
from distroflow.platforms.twitter import TwitterPlatform
from distroflow.platforms.reddit import RedditPlatform
from distroflow.platforms.hackernews import HackerNewsPlatform
from distroflow.platforms.instagram import InstagramPlatform

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DistroFlow API",
    description="API for DistroFlow browser extension",
    version="0.1.0",
)

# CORS middleware for extension communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Browser extensions need wildcard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Pydantic Models
# ============================================================================


class PostRequest(BaseModel):
    """Request to post content to platforms"""

    platforms: List[str]
    content: str
    title: Optional[str] = None
    url: Optional[str] = None
    media: Optional[List[str]] = None


class ScheduleRequest(BaseModel):
    """Request to schedule a post"""

    workflow_name: str
    platforms: List[str]
    frequency: str
    content: str
    title: Optional[str] = None
    url: Optional[str] = None
    next_run: Optional[str] = None


class StatusResponse(BaseModel):
    """API status response"""

    status: str
    version: str
    authenticated_platforms: List[str]


class PostResponse(BaseModel):
    """Response from posting operation"""

    success: bool
    results: List[Dict]
    timestamp: str


# ============================================================================
# WebSocket Connection Manager
# ============================================================================


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(
            f"WebSocket disconnected. Active connections: {len(self.active_connections)}"
        )

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")


manager = ConnectionManager()


# ============================================================================
# Helper Functions
# ============================================================================


def load_auth_config(platform_name: str) -> Optional[AuthConfig]:
    """Load authentication config for a platform"""
    auth_dir = Path.home() / ".distroflow"
    auth_file = auth_dir / f"{platform_name}_auth.json"

    if not auth_file.exists():
        return None

    return AuthConfig(auth_type="cookies", credentials={"cookie_path": str(auth_file)})


def get_platform_instance(platform_name: str):
    """Get platform instance by name"""
    platform_map = {
        "twitter": TwitterPlatform,
        "reddit": RedditPlatform,
        "hackernews": HackerNewsPlatform,
        "instagram": InstagramPlatform,
    }

    platform_class = platform_map.get(platform_name.lower())
    if not platform_class:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform_name}")

    return platform_class()


async def post_to_platform(
    platform_name: str, content: str, title: Optional[str] = None, url: Optional[str] = None
) -> PostResult:
    """Post content to a single platform"""
    try:
        # Get platform instance
        platform = get_platform_instance(platform_name)

        # Load authentication
        auth_config = load_auth_config(platform_name)
        if not auth_config:
            return PostResult(
                success=False,
                platform=platform_name,
                error=f"Authentication not configured for {platform_name}",
            )

        # Setup authentication
        auth_success = await platform.setup_auth(auth_config)
        if not auth_success:
            return PostResult(
                success=False,
                platform=platform_name,
                error=f"Authentication failed for {platform_name}",
            )

        # Transform content for platform
        transformer = ContentTransformer()
        platform_enum = Platform[platform_name.upper()]
        transformed_content = transformer.transform_for_platform(content, platform_enum)

        # Post content
        result = await platform.post(transformed_content, title=title, url=url)

        return result

    except Exception as e:
        logger.error(f"Error posting to {platform_name}: {e}")
        return PostResult(success=False, platform=platform_name, error=str(e))


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/", response_model=StatusResponse)
async def root():
    """API status endpoint"""
    # Check which platforms have authentication configured
    auth_dir = Path.home() / ".distroflow"
    authenticated = []

    for platform in ["twitter", "reddit", "hackernews", "instagram"]:
        auth_file = auth_dir / f"{platform}_auth.json"
        if auth_file.exists():
            authenticated.append(platform)

    return StatusResponse(
        status="ok", version="0.1.0", authenticated_platforms=authenticated
    )


@app.post("/post", response_model=PostResponse)
async def post_content(request: PostRequest):
    """
    Post content to multiple platforms

    Example:
        POST /post
        {
            "platforms": ["twitter", "reddit"],
            "content": "Hello world!",
            "title": "My First Post"
        }
    """
    logger.info(f"Posting to platforms: {request.platforms}")

    # Broadcast start event
    await manager.broadcast(
        {"type": "post_start", "platforms": request.platforms, "timestamp": datetime.now().isoformat()}
    )

    # Post to each platform
    results = []
    for platform_name in request.platforms:
        # Broadcast platform start
        await manager.broadcast(
            {
                "type": "platform_start",
                "platform": platform_name,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Post to platform
        result = await post_to_platform(
            platform_name, request.content, request.title, request.url
        )

        # Convert to dict
        result_dict = {
            "success": result.success,
            "platform": result.platform,
            "post_id": result.post_id,
            "url": result.url,
            "error": result.error,
        }
        results.append(result_dict)

        # Broadcast platform result
        await manager.broadcast(
            {
                "type": "platform_result",
                "platform": platform_name,
                "result": result_dict,
                "timestamp": datetime.now().isoformat(),
            }
        )

    # Check overall success
    success = all(r["success"] for r in results)

    # Broadcast completion
    await manager.broadcast(
        {
            "type": "post_complete",
            "success": success,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }
    )

    return PostResponse(success=success, results=results, timestamp=datetime.now().isoformat())


@app.post("/schedule")
async def schedule_post(request: ScheduleRequest):
    """
    Schedule a post for later

    Example:
        POST /schedule
        {
            "workflow_name": "daily_update",
            "platforms": ["twitter"],
            "frequency": "daily",
            "content": "Daily update!",
            "next_run": "2025-11-29T09:00:00"
        }
    """
    try:
        scheduler = Scheduler()
        frequency_enum = Frequency[request.frequency.upper()]

        next_run = None
        if request.next_run:
            next_run = datetime.fromisoformat(request.next_run)

        task_id = await scheduler.schedule_task(
            workflow_name=request.workflow_name,
            frequency=frequency_enum,
            platforms=request.platforms,
            content=request.content,
            title=request.title,
            url=request.url,
            next_run=next_run,
        )

        return {"success": True, "task_id": task_id, "message": "Task scheduled successfully"}

    except Exception as e:
        logger.error(f"Error scheduling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks")
async def list_tasks():
    """List all scheduled tasks"""
    try:
        scheduler = Scheduler()
        tasks = await scheduler.list_tasks()

        return {"success": True, "tasks": tasks}

    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/tasks/{task_id}")
async def cancel_task(task_id: int):
    """Cancel a scheduled task"""
    try:
        scheduler = Scheduler()
        success = await scheduler.cancel_task(task_id)

        if success:
            return {"success": True, "message": f"Task {task_id} cancelled"}
        else:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/platforms")
async def list_platforms():
    """List all available platforms and their authentication status"""
    platforms = ["twitter", "reddit", "hackernews", "instagram"]
    auth_dir = Path.home() / ".distroflow"

    result = []
    for platform in platforms:
        auth_file = auth_dir / f"{platform}_auth.json"
        result.append(
            {
                "name": platform,
                "authenticated": auth_file.exists(),
                "auth_file": str(auth_file) if auth_file.exists() else None,
            }
        )

    return {"success": True, "platforms": result}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates

    Clients can connect to receive live updates about posting operations
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")

            # Echo back for connection testing
            await websocket.send_json({"type": "echo", "message": data})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ============================================================================
# Server Startup
# ============================================================================


def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the FastAPI server"""
    import uvicorn

    logger.info(f"Starting DistroFlow API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_server()

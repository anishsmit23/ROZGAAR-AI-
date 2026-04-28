from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.search import router as search_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.applications import router as applications_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.ws import router as ws_router

router = APIRouter()
router.include_router(search_router, tags=["search"])
router.include_router(jobs_router, tags=["jobs"])
router.include_router(applications_router, tags=["applications"])
router.include_router(tasks_router, tags=["tasks"])
router.include_router(ws_router, tags=["ws"])

import os
import shutil
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.core.config import settings
from backend.app.core.logging import logger

router = APIRouter(prefix="/sources", tags=["Video Sources & Uploads"])


@router.get("/videos", response_model=List[dict])
async def list_available_videos():
    """List road video files available for playback and simulation."""
    os.makedirs(settings.SAMPLE_VIDEOS_DIR, exist_ok=True)
    videos = []
    for fname in os.listdir(settings.SAMPLE_VIDEOS_DIR):
        ext = fname.split(".")[-1].lower()
        if ext in settings.ALLOWED_EXTENSIONS:
            full_path = os.path.join(settings.SAMPLE_VIDEOS_DIR, fname)
            size_mb = round(os.path.getsize(full_path) / (1024 * 1024), 2)
            videos.append({
                "filename": fname,
                "path": full_path,
                "size_mb": size_mb,
                "extension": ext
            })
    return videos


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_video(file: UploadFile = File(...)):
    """Upload a new road video for camera stream simulation with path-traversal protection."""
    # Sanitize filename
    clean_filename = os.path.basename(file.filename)
    if not clean_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename provided."
        )

    ext = clean_filename.split(".")[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    os.makedirs(settings.SAMPLE_VIDEOS_DIR, exist_ok=True)
    dest_path = os.path.join(settings.SAMPLE_VIDEOS_DIR, clean_filename)

    # Save to disk
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size_mb = round(os.path.getsize(dest_path) / (1024 * 1024), 2)
        logger.info(f"Video uploaded successfully: {dest_path} ({file_size_mb} MB)")
        return {
            "status": "success",
            "message": "Video uploaded successfully",
            "filename": clean_filename,
            "path": dest_path,
            "size_mb": file_size_mb
        }
    except Exception as e:
        logger.error(f"Failed to save uploaded video: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file to disk: {str(e)}"
        )
    finally:
        await file.close()


class ProcessVideoRequest(BaseModel):
    filename: str
    camera_id: str = "BUS-001"
    max_frames: Optional[int] = None


@router.post("/process-video")
async def process_video_stream(
    request: ProcessVideoRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Run the end-to-end computer vision vertical slice on a local or uploaded video.
    Executes neural vehicle detection, road defect detection, evidence capture, and event persistence.
    """
    clean_filename = os.path.basename(request.filename)
    video_path = os.path.join(settings.SAMPLE_VIDEOS_DIR, clean_filename)

    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video '{clean_filename}' not found in sample_videos directory."
        )

    from backend.app.services.video_service import video_service
    try:
        result = await video_service.process_video(
            video_path=video_path,
            camera_id=request.camera_id,
            db=db,
            max_frames=request.max_frames
        )
        return result
    except Exception as e:
        logger.error(f"Error processing video {video_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference pipeline error: {str(e)}"
        )


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from users import User, get_current_user

router = APIRouter()


class Video(BaseModel):
    id: int
    course_id: int
    title: str
    url: str
    duration_minutes: int


class VideoCreate(BaseModel):
    id: int
    course_id: int
    title: str
    url: str
    duration_minutes: int


class VideoUpdate(BaseModel):
    title: str | None = None
    url: str | None = None
    duration_minutes: int | None = None


videos: list[Video] = []


def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Teacher access required"
        )
    return current_user


@router.get("/videos", response_model=list[Video])
def get_all_videos(current_user: User = Depends(get_current_user)):
    return videos


@router.get("/videos/{video_id}", response_model=Video)
def get_video(video_id: int, current_user: User = Depends(get_current_user)):
    for video in videos:
        if video.id == video_id:
            return video
    raise HTTPException(status_code=404, detail="Video not found")



@router.post("/videos", response_model=Video, status_code=201)
def create_video(video: VideoCreate, current_user: User = Depends(require_teacher)):
    if any(v.id == video.id for v in videos):
        raise HTTPException(status_code=400, detail="Video ID already exists")

    new_video = Video(**video.model_dump())
    videos.append(new_video)
    return new_video


@router.put("/videos/{video_id}", response_model=Video)
def update_video(video_id: int, updated_data: VideoUpdate, current_user: User = Depends(require_teacher)):
    for index, video in enumerate(videos):
        if video.id == video_id:
            update_dict = updated_data.model_dump(exclude_unset=True)
            video_dict = video.model_dump()
            video_dict.update(update_dict)

            updated_video = Video(**video_dict)
            videos[index] = updated_video
            return updated_video

    raise HTTPException(status_code=404, detail="Video not found")


@router.delete("/videos/{video_id}")
def delete_video(video_id: int, current_user: User = Depends(require_teacher)):
    for index, video in enumerate(videos):
        if video.id == video_id:
            videos.pop(index)
            return {"message": f"Video {video_id} deleted successfully"}

    raise HTTPException(status_code=404, detail="Video not found")


@router.get("/courses/{course_id}/videos", response_model=list[Video])
def get_course_videos(course_id: int, current_user: User = Depends(get_current_user)):
    return [v for v in videos if v.course_id == course_id]
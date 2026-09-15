from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from users import login #this is the function that will be used to get the current user role

router = APIRouter()

class Course(BaseModel):
    id: int
    title: str
    description: str
    teacher_id: int

courses = []

#bouns task
@router.get("/courses/search")
def search_courses(q: str, current_user = Depends(login)):
    matches = []
    for course in courses:

        if q.lower() in course.title.lower():
            matches.append(course)
    return matches

@router.get("/courses")
def get_all_courses(current_user = Depends(login)):
    return courses

@router.get("/courses/{course_id}")
def get_course(course_id: int, current_user = Depends(login)):
    for course in courses:
        if course.id == course_id:
            return course
    raise HTTPException(status_code=404, detail="Course not found")


@router.post("/courses")
def add_course(course: Course, current_user = Depends(login)):
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=403, 
            detail="Forbidden: Only teachers can create courses"
        )
    
    courses.append(course)
    return course


# 4. Update
@router.put("/courses/{course_id}")
def edit_course(course_id: int, updated_course: Course, current_user = (login)):
    for index, existing_course in enumerate(courses):
        if existing_course.id == course_id:
            courses[index] = updated_course
            return {"message": "Course updated successfully", "course": updated_course}
    raise HTTPException(status_code=404, detail="Course not found")


@router.delete("/courses/{course_id}")
def delete_course(course_id: int, current_user = Depends(login)):
    for index, existing_course in enumerate(courses):
        if existing_course.id == course_id:
            deleted_course = courses.pop(index)
            return {"message": "Course deleted successfully", "course": deleted_course}
    raise HTTPException(status_code=404, detail="Course not found")
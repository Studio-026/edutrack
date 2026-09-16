from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from users import get_current_user 

router = APIRouter()

class Course(BaseModel):
    id: int
    title: str
    description: str
    teacher_id: int

courses = []

@router.get("/courses")
def get_all_courses(search_word: str = None, user = Depends(get_current_user)):
    if search_word:
        return [course for course in courses if search_word.lower() in course.title.lower()]
    return courses

@router.get("/courses/{course_id}")
def get_course(course_id: int, user = Depends(get_current_user)):
    for course in courses:
        if course.id == course_id:
            return course
    raise HTTPException(status_code=404, detail="course not found")






@router.post("/courses")
def add_course(course: Course, user = Depends(get_current_user)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can create courses")
    courses.append(course)
    return course






@router.put("/courses/{course_id}")
def edit_course(course_id: int, updated_course: Course, user = Depends(get_current_user)):

    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can update courses")
        
    for index, existing_course in enumerate(courses):

        if existing_course.id == course_id:
            courses[index] = updated_course
            return {"message": "course updated successfully", "course": updated_course}
        
    raise HTTPException(status_code=404, detail="course not found")






@router.delete("/courses/{course_id}")
def delete_course(course_id: int, user = Depends(get_current_user)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="only teachers can delete courses")
        
    for index, existing_course in enumerate(courses):

        if existing_course.id == course_id:

            deleted_course = courses.pop(index)
            
            return {"message": "course deleted successfully", "course": deleted_course}
    raise HTTPException(status_code=404, detail="course not found")
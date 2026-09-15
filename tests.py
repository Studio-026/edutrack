from fastapi import APIRouter, HTTPException
from users import login
from pydantic import BaseModel

router = APIRouter()
tests = []
submissions = []

class Question(BaseModel):
    id: int
    text: str
    options: list[int]
    correct_answer: int

class Test(BaseModel):
    id: int
    course_id: int 
    title: str
    questions: list[Question]

# class Submission(BaseModel):
#     id: int
#     test_id: int    
#     student_id: int 
#     student_answers: dict[int, str] 
#     score: int


@router.post("/tests")
def create_test(username: str, password: str, new_test: Test):
    user = login(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login")
        
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create tests")
        
    tests.append(new_test)
    return new_test

@router.get("/courses/{course_id}/tests")
def get_tests_for_course(course_id: int, username: str, password: str):
    user = login(username, password)
    course_tests = []
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login")
        
    for t in tests:
        if t.course_id == course_id:
           course_tests.append(t)

    return course_tests

@router.get("/tests/{test_id}")
def get_single_test(test_id: int, username: str, password: str):
    user = login(username, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login")
        
    if user.role == "teacher" or user.role == "student":
        for t in tests:
            if t.id == test_id:
                return t
        raise HTTPException(status_code=404, detail="Test not found")
    
@router.put("/tests/{test_id}")
def update_test(test_id: int, username: str, password: str, updated_test: Test):
    user = login(username, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login")
        
    if user.role == "teacher":
        for index, t in enumerate(tests):
            if t.id == test_id:
                tests[index] = updated_test
                return updated_test
        raise HTTPException(status_code=404, detail="Test not found")
        
    if user.role == "student":
        raise HTTPException(status_code=403, detail="Students cannot edit tests")


@router.delete("/tests/{test_id}")
def delete_test(test_id: int, username: str, password: str):
    user = login(username, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login")
        
    if user.role == "teacher":
        for index, t in enumerate(tests):
            if t.id == test_id:
                tests.pop(index)
                return "Test deleted successfully"
        raise HTTPException(status_code=404, detail="Test not found")
        
    if user.role == "student":
        raise HTTPException(status_code=403, detail="Students cannot delete tests")

    
# @router.post("/submissions")
# def submit_test(username: str, password: str, submission: Submission):
#     user = login(username, password)
#     specific_test = None
#     score = 0

#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid login")
        
#     if user.role != "student":
#         raise HTTPException(status_code=403, detail="Only students can submit tests")
        
#     for t in tests:
#         if t.id == submission.test_id:
#             specific_test = t
#             break

#     if not specific_test:
#         raise HTTPException(status_code=404, detail="Test not found")
        
#     for question in specific_test.questions:
#         if submission.student_answers.get(question.id) == question.correct_answer:
#             score += 1
            
#     submission.score = score
#     submissions.append(submission)
    
#     return submission
from fastapi import APIRouter, HTTPException
from final import login, User
from pydantic import BaseModel

router = APIRouter()
tests = []
submissions = []

class Question(BaseModel):
    id: int
    text: str
    correct_answer: str

class Test(BaseModel):
    id: int
    course_id: int 
    title: str
    questions: list[Question]

class Submission(BaseModel):
    id: int
    test_id: int    
    student_id: int 
    student_answers: dict[int, str] 
    score: int


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

@router.post("/submissions")
def submit_test(username: str, password: str, submission: Submission):
    user = login(username, password)
    specific_test = None
    score = 0

    if not user:
        raise HTTPException(status_code=401, detail="Invalid login")
        
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit tests")
        
    for t in tests:
        if t.id == submission.test_id:
            specific_test = t
            break

    if not specific_test:
        raise HTTPException(status_code=404, detail="Test not found")
        
    for question in specific_test.questions:
        if submission.student_answers.get(question.id) == question.correct_answer:
            score += 1
            
    submission.score = score
    submissions.append(submission)
    
    return submission
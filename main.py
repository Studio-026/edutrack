from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import users
import course
import videos
import tests_questions

app = FastAPI(title="EduTrack")

app.include_router(users.router)
app.include_router(course.router)
app.include_router(videos.router)
app.include_router(tests_questions.router)

# Enrollments and Submissions routers get added here once their PRs merge.

app.mount("/", StaticFiles(directory="static", html=True), name="static")

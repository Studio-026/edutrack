Subject: Onboarding & Task Distribution: EduTrack Backend Development

Team,

We're kicking off development for EduTrack (repository: https://github.com/Huna-Studio/edutrack). This covers the architecture, the workflow, and the six tracks available.

**Architecture & Stack**

Backend in FastAPI, in-memory, no database — same as every exercise you've built so far, just six lists instead of one.

- **Modular routing** — no second `FastAPI()` app anywhere. Each track's file defines a `router = APIRouter()` and its routes on it. `main.py` isn't anyone's task — it's small enough that I'll wire each router into it myself as your PR gets merged, so don't worry about it.
- **Login is required on every single endpoint, no exceptions.** Write one `login(username, password) -> User | None` function; every `GET`/`POST`/`PUT`/`DELETE` you build, across all six tracks, calls it first and returns a 401 if it fails. Teacher-only actions (like creating a course) build on the exact same function — check the returned user's `teacher` flag before continuing. Full pattern is in the README. You're not locked into this exact shape if you want to try something more elegant — the bar is that every operation actually requires a real login, however you get there.
- **Marking a teacher**: minimum is a boolean `teacher` field (default `False`) on `User`. An Enum works too if you prefer. Either is fine — if you've got a better idea, use it.
- **Core models**: `User`, `Course`, `Video`, `Test` + nested `Question`, `Enrollment`, `Submission`. Grading is fully automatic. Full detail per track is on each GitHub Issue.

**No AI usage anywhere in this project** — same rule as the rest of training.

**Git Workflow**

1. Never push directly to `main`. Every change goes through a feature branch and a Pull Request.
2. The repo's `README.md` has the exact commands for every step — use it as a cheatsheet.
3. Your task is already a GitHub Issue — find yours once tracks are assigned, self-assign it, and reference it (`Closes #N`) in your PR.
4. Try to work through a problem yourself first — search, read the docs, check the code — before pinging the team.
5. I'll review every PR personally.

**The Six Tracks**

1. Users & Login
2. Courses
3. Videos
4. Tests & Questions
5. Enrollments
6. Submissions

Full scope for each is on its GitHub Issue. Who takes which track gets decided on WhatsApp — vote there and confirm before you self-assign the Issue and start your first branch.

Mistakes are expected here — this is exactly where they're supposed to happen. Ask questions and iterate rather than trying to get it perfect on the first pass.

Technology Sector Head,
Mahmoud Elkholany

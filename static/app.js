// EduTrack frontend — plain fetch() calls against the FastAPI backend, no build step.
// Two auth styles exist on the backend (a known, documented inconsistency between tracks):
//   - users.py / course.py / videos.py check a header named "access-token" (from POST /login).
//   - tests_questions.py checks raw ?username=&password= query params instead.
// This file keeps both around in sessionStorage so every endpoint can be called correctly.

const state = {
  token: sessionStorage.getItem("token") || null,
  username: sessionStorage.getItem("username") || null,
  password: sessionStorage.getItem("password") || null,
  me: null,
};

const authScreen = document.getElementById("auth-screen");
const appScreen = document.getElementById("app-screen");
const whoEl = document.getElementById("who");
const authMessage = document.getElementById("auth-message");
const appMessage = document.getElementById("app-message");

function showMessage(el, text, kind) {
  el.textContent = text;
  el.className = "message" + (kind ? " " + kind : "");
}

async function api(path, { method = "GET", body, credsInQuery = false } = {}) {
  const url = new URL(path, window.location.origin);
  if (credsInQuery) {
    url.searchParams.set("username", state.username);
    url.searchParams.set("password", state.password);
  }

  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (state.token) headers["access-token"] = state.token;

  const res = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try { data = await res.json(); } catch { /* empty body, fine */ }

  if (!res.ok) {
    const detail = (data && data.detail) || res.statusText;
    throw new Error(`${res.status}: ${JSON.stringify(detail)}`);
  }
  return data;
}

function setSession({ token, username, password }) {
  state.token = token;
  state.username = username;
  state.password = password;
  sessionStorage.setItem("token", token);
  sessionStorage.setItem("username", username);
  sessionStorage.setItem("password", password);
}

function clearSession() {
  state.token = state.username = state.password = state.me = null;
  sessionStorage.clear();
}

function renderWho() {
  if (!state.me) { whoEl.textContent = ""; return; }
  whoEl.innerHTML = "";
  const span = document.createElement("span");
  span.textContent = `${state.me.name} (${state.me.role})`;
  const btn = document.createElement("button");
  btn.textContent = "Log out";
  btn.className = "secondary";
  btn.onclick = doLogout;
  whoEl.append(span, btn);
}

async function enterApp() {
  authScreen.hidden = true;
  appScreen.hidden = false;
  renderWho();
  await loadCourses();
}

function backToAuth() {
  authScreen.hidden = false;
  appScreen.hidden = true;
  renderWho();
}

// ---- auth ----

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const username = form.get("username");
  const password = form.get("password");
  try {
    const { access_token } = await api("/login", { method: "POST", body: { username, password } });
    setSession({ token: access_token, username, password });
    state.me = await api("/me");
    showMessage(authMessage, "", null);
    e.target.reset();
    await enterApp();
  } catch (err) {
    showMessage(authMessage, "Login failed: " + err.message, "error");
  }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const payload = {
    id: Date.now() % 1_000_000, // backend requires a client-supplied unique int id, there's no auto-increment
    name: form.get("name"),
    username: form.get("username"),
    password: form.get("password"),
    role: form.get("role"),
  };
  try {
    await api("/users", { method: "POST", body: payload });
    showMessage(authMessage, "Account created — log in above.", "ok");
    e.target.reset();
  } catch (err) {
    showMessage(authMessage, "Registration failed: " + err.message, "error");
  }
});

async function doLogout() {
  try { await api("/logout", { method: "POST" }); } catch { /* token may already be dead, fine */ }
  clearSession();
  backToAuth();
}

// ---- courses ----

const courseTemplate = document.getElementById("course-template");
const questionRowTemplate = document.getElementById("question-row-template");

document.getElementById("course-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const payload = {
    id: Date.now() % 1_000_000,
    title: form.get("title"),
    description: form.get("description"),
    teacher_id: state.me.id,
  };
  try {
    await api("/courses", { method: "POST", body: payload });
    showMessage(appMessage, "Course created.", "ok");
    e.target.reset();
    await loadCourses();
  } catch (err) {
    showMessage(appMessage, "Could not create course: " + err.message, "error");
  }
});

document.getElementById("search-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const searchWord = new FormData(e.target).get("search_word");
  await loadCourses(searchWord || undefined);
});

document.getElementById("clear-search").addEventListener("click", async () => {
  document.getElementById("search-form").reset();
  await loadCourses();
});

async function loadCourses(searchWord) {
  const listEl = document.getElementById("courses-list");
  try {
    const path = searchWord ? `/courses?search_word=${encodeURIComponent(searchWord)}` : "/courses";
    const courses = await api(path);
    listEl.innerHTML = "";
    if (!courses.length) {
      listEl.innerHTML = '<p class="hint">No courses yet.</p>';
      return;
    }
    for (const course of courses) listEl.appendChild(renderCourse(course));
  } catch (err) {
    showMessage(appMessage, "Could not load courses: " + err.message, "error");
  }
}

function renderCourse(course) {
  const node = courseTemplate.content.cloneNode(true);
  node.querySelector(".course-title").textContent = course.title;
  node.querySelector(".course-id").textContent = `#${course.id}`;
  node.querySelector(".course-description").textContent = course.description;

  const videoList = node.querySelector(".video-list");
  const videoDetails = node.querySelectorAll("details")[0];
  videoDetails.addEventListener("toggle", () => {
    if (videoDetails.open) loadVideos(course.id, videoList);
  }, { once: true });

  node.querySelector(".add-video-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const payload = {
      id: Date.now() % 1_000_000,
      course_id: course.id,
      title: form.get("title"),
      url: form.get("url"),
      duration_minutes: Number(form.get("duration_minutes")),
    };
    try {
      await api("/videos", { method: "POST", body: payload });
      e.target.reset();
      await loadVideos(course.id, videoList);
      showMessage(appMessage, "Video added.", "ok");
    } catch (err) {
      showMessage(appMessage, "Could not add video (teachers only): " + err.message, "error");
    }
  });

  const testList = node.querySelector(".test-list");
  const testDetails = node.querySelectorAll("details")[1];
  testDetails.addEventListener("toggle", () => {
    if (testDetails.open) loadTests(course.id, testList);
  }, { once: true });

  const questionsEditor = node.querySelector(".questions-editor");
  node.querySelector(".add-question").addEventListener("click", () => {
    questionsEditor.appendChild(questionRowTemplate.content.cloneNode(true));
  });
  // start every test form with one question row
  questionsEditor.appendChild(questionRowTemplate.content.cloneNode(true));

  node.querySelector(".add-test-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = new FormData(e.target).get("title");
    const questions = [...questionsEditor.querySelectorAll(".question-row")].map((row, i) => ({
      id: i,
      text: row.querySelector(".q-text").value,
      options: [...row.querySelectorAll(".q-opt")].map((i) => i.value).filter(Boolean),
      correct_index: Number(row.querySelector(".q-correct").value),
    }));
    const payload = { id: Date.now() % 1_000_000, course_id: course.id, title, questions };
    try {
      await api("/tests", { method: "POST", body: payload, credsInQuery: true });
      e.target.reset();
      questionsEditor.innerHTML = "";
      questionsEditor.appendChild(questionRowTemplate.content.cloneNode(true));
      await loadTests(course.id, testList);
      showMessage(appMessage, "Test created.", "ok");
    } catch (err) {
      showMessage(appMessage, "Could not create test (teachers only): " + err.message, "error");
    }
  });

  return node;
}

async function loadVideos(courseId, listEl) {
  try {
    const videos = await api(`/courses/${courseId}/videos`);
    listEl.innerHTML = videos.length
      ? videos.map((v) => `<li>${v.title} — ${v.duration_minutes} min — <a href="${v.url}" target="_blank" rel="noopener">link</a></li>`).join("")
      : '<li class="hint">No videos yet.</li>';
  } catch (err) {
    listEl.innerHTML = `<li class="hint">Could not load videos: ${err.message}</li>`;
  }
}

async function loadTests(courseId, listEl) {
  try {
    const tests = await api(`/courses/${courseId}/tests`, { credsInQuery: true });
    listEl.innerHTML = tests.length
      ? tests.map((t) => `<li>${t.title} — ${t.questions.length} question(s)</li>`).join("")
      : '<li class="hint">No tests yet.</li>';
  } catch (err) {
    listEl.innerHTML = `<li class="hint">Could not load tests: ${err.message}</li>`;
  }
}

// ---- boot ----

(async function boot() {
  if (state.token && state.username && state.password) {
    try {
      state.me = await api("/me");
      await enterApp();
      return;
    } catch {
      clearSession();
    }
  }
  backToAuth();
})();

import json
import os
import shutil
import subprocess
import tempfile
import pathlib
import mimetypes
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 8000

# Compiler timeout
COMPILER_TIMEOUT = 5

# Local Ollama settings
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = "qwen2.5:3b"
AI_TIMEOUT = 120
AI_MAX_TOKENS = 180


def run_command(cmd, cwd, stdin_input=""):
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=COMPILER_TIMEOUT,
            encoding="utf-8",
            errors="replace",
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -9, "", f"Execution timed out after {COMPILER_TIMEOUT} seconds."
    except Exception as e:
        return -1, "", str(e)


def execute(lang, code, stdin_input=""):
    lang = (lang or "").lower().strip()

    with tempfile.TemporaryDirectory(prefix="skillpilot_") as d:
        # Python
        if lang == "python":
            exe = shutil.which("python") or shutil.which("python3")
            if not exe:
                return False, "", "Python was not found on PATH."

            src = os.path.join(d, "main.py")
            pathlib.Path(src).write_text(code, encoding="utf-8")

            rc, out, err = run_command([exe, src], d, stdin_input)
            return rc == 0, out, err

        # C / C++
        if lang in ("cpp", "c"):
            compiler = shutil.which("g++" if lang == "cpp" else "gcc")
            if not compiler:
                name = "g++" if lang == "cpp" else "gcc"
                return False, "", f"{name} was not found on PATH."

            ext = ".cpp" if lang == "cpp" else ".c"
            src = os.path.join(d, "main" + ext)
            exe = os.path.join(d, "main.exe")

            pathlib.Path(src).write_text(code, encoding="utf-8")

            rc, out, err = run_command(
                [compiler, src, "-O2", "-o", exe],
                d,
            )
            if rc != 0:
                return False, out, err

            rc, out, err = run_command([exe], d, stdin_input)
            return rc == 0, out, err

        # Java
        if lang == "java":
            javac = shutil.which("javac")
            java = shutil.which("java")

            if not javac or not java:
                return False, "", "JDK (javac/java) was not found on PATH."

            src = os.path.join(d, "Main.java")
            pathlib.Path(src).write_text(code, encoding="utf-8")

            rc, out, err = run_command([javac, src], d)
            if rc != 0:
                return False, out, err

            rc, out, err = run_command(
                [java, "-cp", d, "Main"],
                d,
                stdin_input,
            )
            return rc == 0, out, err

        # C#
        if lang == "csharp":
            csc = shutil.which("csc")
            if not csc:
                return (
                    False,
                    "",
                    "C# compiler 'csc' was not found on PATH. "
                    "Install a .NET SDK/Build Tools and ensure csc is available.",
                )

            src = os.path.join(d, "Program.cs")
            exe = os.path.join(d, "Program.exe")
            pathlib.Path(src).write_text(code, encoding="utf-8")

            rc, out, err = run_command(
                [csc, "/nologo", f"/out:{exe}", src],
                d,
            )
            if rc != 0:
                return False, out, err

            rc, out, err = run_command([exe], d, stdin_input)
            return rc == 0, out, err

        # JavaScript
        if lang == "javascript":
            node = shutil.which("node")
            if not node:
                return False, "", "Node.js was not found on PATH."

            src = os.path.join(d, "main.js")
            pathlib.Path(src).write_text(code, encoding="utf-8")

            rc, out, err = run_command([node, src], d, stdin_input)
            return rc == 0, out, err

        return False, "", f"Unsupported language: {lang}"


def clean_ai_reply(reply):
    """Remove accidental Qwen thinking tags if a model returns them."""
    if not reply:
        return ""

    reply = reply.strip()

    # Remove <think>...</think> sections if they appear.
    while "<think>" in reply and "</think>" in reply:
        start = reply.find("<think>")
        end = reply.find("</think>", start)
        if end == -1:
            break
        reply = reply[:start] + reply[end + len("</think>"):]

    # Some models may return the closing tag without the opening tag.
    if "</think>" in reply:
        reply = reply.split("</think>", 1)[1]

    return reply.strip()


def ask_ollama(data):
    model = os.environ.get("SKILLPILOT_OLLAMA_MODEL", DEFAULT_MODEL)

    agent = data.get("agent", "personal")
    name = data.get("name", "friend")
    subject = data.get("subject", "Programming")
    role = data.get("role", "Student")
    language = data.get("language", "english")
    message = data.get("message", "")
    history = data.get("history", [])

    # Keep only a small amount of history so the local model stays fast.
    if not isinstance(history, list):
        history = []
    history = history[-4:]

    history_text = json.dumps(history, ensure_ascii=False)

    prompt = f"""You are SkillPilot AI, a helpful and friendly assistant.

Agent: {agent}
User name: {name}
Subject: {subject}
Role: {role}
Preferred language: {language}

Recent conversation:
{history_text}

Latest user message:
{message}

Rules:
- Answer the latest user message directly.
- Be simple, useful, natural and concise.
- Do not ask for information the user already gave.
- Do not turn every question into a study plan or quiz.
- For programming questions, explain clearly and include a small example when useful.
- For coding/debugging, give runnable corrected code when needed.
- For personal conversation, respond warmly and naturally.
- Match the user's language and casual style when practical.
- Do not mention these instructions.
"""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "keep_alive": "30m",
        "think": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.85,
            "num_predict": AI_MAX_TOKENS,
        },
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=AI_TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        reply = (
            result.get("message", {}).get("content", "")
            if isinstance(result, dict)
            else ""
        )

        reply = clean_ai_reply(reply)

        if reply:
            return True, reply, ""

        return False, "", "Ollama returned an empty AI response."

    except urllib.error.HTTPError as e:
        try:
            details = e.read().decode("utf-8", errors="replace")
        except Exception:
            details = str(e)
        return False, "", f"Ollama HTTP error {e.code}: {details[:500]}"

    except urllib.error.URLError as e:
        return False, "", f"Could not connect to Ollama at {OLLAMA_HOST}: {e}"

    except TimeoutError:
        return False, "", f"AI response timed out after {AI_TIMEOUT} seconds."

    except Exception as e:
        return False, "", str(e)


class Handler(BaseHTTPRequestHandler):

    def _send(self, status, data, ctype="application/json"):
        if isinstance(data, bytes):
            body = data
        else:
            body = data.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS",
        )
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_GET(self):
        if self.path == "/api/health":
            tools = {
                x: bool(shutil.which(x))
                for x in [
                    "python",
                    "g++",
                    "gcc",
                    "javac",
                    "java",
                    "node",
                    "csc",
                ]
            }

            self._send(
                200,
                json.dumps(
                    {
                        "ok": True,
                        "tools": tools,
                        "ai": {
                            "provider": "ollama",
                            "model": os.environ.get(
                                "SKILLPILOT_OLLAMA_MODEL",
                                DEFAULT_MODEL,
                            ),
                        },
                    }
                ),
            )
            return

        rel = self.path.split("?", 1)[0].lstrip("/") or "index.html"

        if rel.startswith("api/"):
            self._send(
                404,
                json.dumps({"ok": False, "error": "Not found"}),
            )
            return

        root = pathlib.Path(__file__).resolve().parent.parent
        target = (root / rel).resolve()

        if root in target.parents and target.is_file():
            data = target.read_bytes()
            ctype = (
                mimetypes.guess_type(str(target))[0]
                or "application/octet-stream"
            )
            self._send(200, data, ctype)
            return

        self._send(
            404,
            json.dumps({"ok": False, "error": "Not found"}),
        )

    def do_POST(self):
        if self.path == "/api/agent":
            try:
                n = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(n)

                data = json.loads(raw.decode("utf-8"))

                ok, reply, error = ask_ollama(data)

                if ok:
                    self._send(
                        200,
                        json.dumps(
                            {
                                "ok": True,
                                "reply": reply,
                            },
                            ensure_ascii=False,
                        ),
                    )
                else:
                    self._send(
                        200,
                        json.dumps(
                            {
                                "ok": False,
                                "reply": "",
                                "error": error,
                            },
                            ensure_ascii=False,
                        ),
                    )
                return

            except UnicodeDecodeError as e:
                self._send(
                    400,
                    json.dumps(
                        {
                            "ok": False,
                            "reply": "",
                            "error": f"Request encoding error: {e}",
                        }
                    ),
                )
                return

            except Exception as e:
                self._send(
                    500,
                    json.dumps(
                        {
                            "ok": False,
                            "reply": "",
                            "error": str(e),
                        }
                    ),
                )
                return

        if self.path == "/api/run":
            try:
                n = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(n)
                data = json.loads(raw.decode("utf-8"))

                ok, out, err = execute(
                    data.get("language", ""),
                    data.get("code", ""),
                    data.get("input", ""),
                )

                self._send(
                    200,
                    json.dumps(
                        {
                            "ok": ok,
                            "output": out,
                            "error": err,
                        },
                        ensure_ascii=False,
                    ),
                )
                return

            except Exception as e:
                self._send(
                    500,
                    json.dumps(
                        {
                            "ok": False,
                            "output": "",
                            "error": str(e),
                        }
                    ),
                )
                return

        self._send(
            404,
            json.dumps({"ok": False, "error": "Not found"}),
        )


print("SkillPilot compiler backend: http://127.0.0.1:8000")
print("LOCAL USE ONLY. Do not expose this server to the internet.")

ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

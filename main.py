from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import urllib.request
import json

# -----------------------------------------
# CREATE FASTAPI APP
# -----------------------------------------

app = FastAPI()


# -----------------------------------------
# CORS
# -----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# -----------------------------------------
# REQUEST MODEL
# -----------------------------------------

class WebsiteRequest(BaseModel):
    prompt: str


# -----------------------------------------
# TEST AGENT
# -----------------------------------------

def test_website(website_code):

    print("================================")
    print("TEST AGENT STARTED")
    print("================================")

    errors = []

    if "<html" not in website_code.lower():
        errors.append("HTML tag missing")

    if "</html>" not in website_code.lower():
        errors.append("Closing HTML tag missing")

    if "<body" not in website_code.lower():
        errors.append("Body tag missing")

    if "</body>" not in website_code.lower():
        errors.append("Closing body tag missing")

    if "<style" not in website_code.lower():
        errors.append("CSS style missing")

    if "<script" not in website_code.lower():
        errors.append("JavaScript missing")

    if len(errors) == 0:

        print("TEST RESULT: PASSED")

        return True, errors

    else:

        print("TEST RESULT: FAILED")
        print("Errors:", errors)

        return False, errors


# -----------------------------------------
# SELF-REPAIR AGENT
# -----------------------------------------

def self_repair_website(website_code, errors):

    print("================================")
    print("SELF-REPAIR AGENT STARTED")
    print("================================")

    repair_prompt = f"""
You are a Self-Repair Agent.

The generated website has the following problems:

{errors}

Repair the website completely.

Website code:

{website_code}

Requirements:

1. Fix all detected problems.
2. Keep the original design.
3. Make the HTML valid.
4. Include CSS inside <style>.
5. Include JavaScript inside <script>.
6. Make the website responsive.
7. Return ONLY complete HTML code.
"""

    data = {
        "model": "qwen2.5-coder:1.5b",
        "prompt": repair_prompt,
        "stream": False
    }

    request_data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=request_data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        print("Sending code to Ollama for repair...")

        with urllib.request.urlopen(
            req,
            timeout=600
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        repaired_code = result.get(
            "response",
            ""
        )

        repaired_code = repaired_code.replace(
            "```html",
            ""
        )

        repaired_code = repaired_code.replace(
            "```",
            ""
        )

        # Keep only HTML
        if "<!DOCTYPE html>" in repaired_code:

            repaired_code = repaired_code[
                repaired_code.find("<!DOCTYPE html>"):
            ]

        if "</html>" in repaired_code:

            repaired_code = repaired_code[
                :repaired_code.rfind("</html>") + 7
            ]

        repaired_code = repaired_code.strip()

        print("Self-Repair completed!")

        return repaired_code

    except Exception as e:

        print("Self-Repair Error:", e)

        return website_code


# -----------------------------------------
# HOME / API TEST
# -----------------------------------------

@app.get("/api")
def home():

    return {
        "message": "AI Website Generator is running!"
    }


# -----------------------------------------
# WEBSITE GENERATION
# -----------------------------------------

@app.post("/generate")
def generate_website(request: WebsiteRequest):

    print("================================")
    print("NEW WEBSITE REQUEST")
    print("================================")

    print("User Prompt:")
    print(request.prompt)

    print("================================")

    # -------------------------------------
    # PROMPT FOR LOCAL AI
    # -------------------------------------

    ollama_prompt = f"""
Create a simple portfolio website for an AI student.

User request:
{request.prompt}

Requirements:
- Home
- About
- Skills
- Projects
- Education
- Contact
- Use HTML, CSS and JavaScript
- Return ONLY complete HTML code
- Start with <!DOCTYPE html>
- End with </html>
"""

    # -------------------------------------
    # OLLAMA REQUEST
    # -------------------------------------

    data = {

        "model": "qwen2.5-coder:1.5b",

        "prompt": ollama_prompt,

        "stream": False
    }

    request_data = json.dumps(
        data
    ).encode("utf-8")

    req = urllib.request.Request(

        "http://127.0.0.1:11434/api/generate",

        data=request_data,

        headers={
            "Content-Type": "application/json"
        },

        method="POST"
    )

    try:

        print("Connecting to Ollama...")

        with urllib.request.urlopen(
            req,
            timeout=600
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        website_code = result.get(
            "response",
            ""
        )

        print("AI generation completed!")

        # ---------------------------------
        # CLEAN AI RESPONSE
        # ---------------------------------

        website_code = website_code.replace(
            "```html",
            ""
        )

        website_code = website_code.replace(
            "```",
            ""
        )

        website_code = website_code.strip()

        # Keep only actual HTML
        if "<!DOCTYPE html>" in website_code:

            website_code = website_code[
                website_code.find("<!DOCTYPE html>"):
            ]

        if "</html>" in website_code:

            website_code = website_code[
                :website_code.rfind("</html>") + 7
            ]

        # ---------------------------------
        # TEST AGENT
        # ---------------------------------

        passed, errors = test_website(
            website_code
        )

        # ---------------------------------
        # SELF-REPAIR IF FAILED
        # ---------------------------------

        if not passed:

            print(
                "Website failed testing."
            )

            website_code = self_repair_website(
                website_code,
                errors
            )

            # Test repaired website again
            passed, errors = test_website(
                website_code
            )

        else:

            print(
                "Website passed testing."
            )

        # ---------------------------------
        # FINAL RESPONSE
        # ---------------------------------

        print("================================")
        print("WEBSITE READY")
        print("================================")

        return {

            "message":
            "Website generated successfully!",

            "response":
            website_code,

            "test_passed":
            passed,

            "errors":
            errors
        }

    except Exception as e:

        print("================================")
        print("OLLAMA ERROR")
        print("================================")

        print(e)

        return {

            "message":
            "Ollama connection failed",

            "response":
            "",

            "error":
            str(e)
        }


# -----------------------------------------
# FRONTEND
# -----------------------------------------

frontend_path = (
    Path(__file__).resolve().parent
    / "frontend"
)


app.mount(

    "/",

    StaticFiles(
        directory=frontend_path,
        html=True
    ),

    name="frontend"
)
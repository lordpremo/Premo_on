import os
import base64
import httpx
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Broken Image Generation API",
    description="Image generation API powered by Stability AI.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"

@app.get("/")
def home():
    return {
        "message": "Karibu Broken Image Generation API 🎨👑",
        "endpoint": "/generate-image",
        "example_request": {
            "prompt": "a golden lion wearing a crown in neon cyberpunk style"
        }
    }

@app.post("/generate-image")
async def generate_image(prompt: str = Form(...)):
    if not STABILITY_API_KEY:
        return JSONResponse(
            {
                "error": "STABILITY_API_KEY haijawekwa.",
                "hint": "Weka STABILITY_API_KEY kwenye Environment Variables za Vercel."
            },
            status_code=500
        )

    prompt = prompt.strip()
    if not prompt:
        return JSONResponse({"error": "Prompt haiwezi kuwa tupu."}, status_code=400)

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json"
    }

    form_data = {
        "prompt": prompt,
        "output_format": "png"
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                STABILITY_API_URL,
                headers=headers,
                data=form_data
            )

        if r.status_code != 200:
            return JSONResponse(
                {
                    "error": "Stability API imerudisha error.",
                    "status_code": r.status_code,
                    "details": r.text
                },
                status_code=500
            )

        data = r.json()
        # Stability hurudisha base64 image kwenye "image" au "images"
        image_base64 = None

        if "image" in data:
            image_base64 = data["image"]
        elif "images" in data and len(data["images"]) > 0:
            image_base64 = data["images"][0].get("image")

        if not image_base64:
            return JSONResponse(
                {"error": "Haikupatikana image_base64 kwenye response ya API."},
                status_code=500
            )

        return {
            "image_base64": image_base64,
            "info": "Hii ni base64 ya PNG. Ui-decode upande wa client."
        }

    except Exception as e:
        return JSONResponse(
            {"error": f"Hitilafu wakati wa kuwasiliana na Stability API: {str(e)}"},
            status_code=500
)

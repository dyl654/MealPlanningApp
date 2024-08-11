import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import recipe_to_pdf

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_meal_planning():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@app.get("/api/recipes")
def get_recipes():
    return {"message": "Not Implemented"}


@app.post("/api/recipes")
async def create_recipe_from_url(request: Request):
    data = await request.json()
    url = data.get("url")
    sunday = data.get("sunday")
    monday = data.get("monday")
    tuesday = data.get("tuesday")
    wednesday = data.get("wednesday")
    thursday = data.get("thursday")
    friday = data.get("friday")
    saturday = data.get("saturday")
    if not url:
        return {"error": "URL is required"}
    recipe_to_pdf.main(url, sunday, monday, tuesday, wednesday, thursday, friday, saturday)
    return {"message": "Recipe processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

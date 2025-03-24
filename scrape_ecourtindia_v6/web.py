from tinydb import TinyDB

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

db = TinyDB('db.json')
app = FastAPI()

app.mount("/html", StaticFiles(directory="html"), name="html")
app.mount("/pdf", StaticFiles(directory="pdf"), name="pdf")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
            request=request, name="index.html", context={ 'views': db.all() }
    )

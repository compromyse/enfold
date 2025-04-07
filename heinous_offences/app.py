from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
import gradio as gr
import csv
from tinydb import TinyDB, Query
import shutil

DB_FILE = "db.json"
ADMIN_PASSWORD = "shivermetimbers"

db = TinyDB(DB_FILE)

name_from_key = {
    'ipc': 'Indian Penal Code',
    'bns': 'Bhartiya Nyay Sanhita',
    'pocso': 'POCSO, 2012',
    'scst': 'SCST Act, 1989',
    'ndps': 'NDPS Act, 1985',
    'arms': 'Arms Act, 1959',
    'motor': 'Motor Vehicle Act, 1988',
    'it': 'IT Act, 2000'
}

key_from_name = { value: key for key, value in name_from_key.items() }

crime_query = Query()

# ---------- Gradio Logic ----------
def lookup_crime(section, act_key):
    if section <= 0:
        return "Please enter a valid section number.", "", "", ""

    table = db.table(key_from_name[act_key])
    results = table.search(crime_query.section == str(section))

    if not results:
        return f"No record found for section {section} under {name_from_key.get(act_key)}.", "", "", ""

    offence = results[0]
    return [
        f"## Severity: {offence.get('severity', 'N/A')}",
        f"{offence.get('section_text', 'N/A')}",
        f"### Minimum Punishment: {offence.get('minimum_punishment', 'N/A')}",
        f"Comments: {offence.get('comment', 'N/A')}"
    ]

gradio_ui = gr.Blocks()
with gradio_ui:
    gr.Markdown("## Heinous Crime Lookup Tool")

    with gr.Row():
        section_input = gr.Number(label="Enter Section Number", value=0)
        act_dropdown = gr.Dropdown(choices=list(name_from_key.values()), label="Select Act")

    submit_btn = gr.Button("Lookup")
    severity = gr.Markdown()
    section_text = gr.Markdown()
    punishment = gr.Markdown()
    comment = gr.Markdown()

    submit_btn.click(
        fn=lookup_crime,
        inputs=[section_input, act_dropdown],
        outputs=[severity, section_text, punishment, comment]
    )

# ---------- FastAPI Logic ----------
app = FastAPI()

@app.get("/admin", response_class=HTMLResponse)
async def admin_form():
    options_html = "".join(
        f"<option value='{key}'>{label}</option>" for key, label in name_from_key.items()
    )
    return f"""
    <html>
        <head><title>Admin Upload</title></head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"
        >
        <body>
        <main class='container'>
            <h2>Admin Panel - Upload CSV</h2>
            <form action="/admin" method="post" enctype="multipart/form-data">
                <label>Password:</label>
                <input type="password" name="password" required><br><br>

                <label>Select Act:</label>
                <select name="act" required>
                    {options_html}
                </select><br><br>

                <label>CSV File:</label>
                <input type="file" name="file" accept=".csv" required><br><br>
                <input type="submit" value="Upload & Replace DB">
            </form>
        </main>
        </body>
    </html>
    """

@app.post("/admin")
async def handle_admin_upload(
    password: str = Form(...),
    act: str = Form(...),
    file: UploadFile = Form(...)
):
    if password != ADMIN_PASSWORD:
        return HTMLResponse("<h3>Incorrect password.</h3>", status_code=401)

    if act not in name_from_key:
        return HTMLResponse("<h3>Invalid Act selected.</h3>", status_code=400)

    with open('tmp.csv', "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db.drop_table(act)
    table = db.table(act)

    with open('tmp.csv', "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 5:
                continue
            table.insert({
                "section": row[0],
                "section_text": row[1],
                "minimum_punishment": row[2],
                "severity": row[3],
                "comment": row[4],
            })

    return RedirectResponse("/admin", status_code=303)

# Mount Gradio on "/"
gr.mount_gradio_app(app, gradio_ui, path="/")

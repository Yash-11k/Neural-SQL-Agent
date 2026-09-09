from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from backend.sql_agent import run_pipeline, is_query_ambiguous
from backend.analytics import get_telemetry_metrics
from backend.db_setup import make_database, load_csv_to_db, get_dynamic_schema

app = FastAPI(title="NeuralSQL Simple API")

# Input model
class QueryInput(BaseModel):
    question: str
    table_name: str | None = None  # hint: which table to prioritize (e.g. an uploaded CSV)

# Build database automatically on start
@app.on_event("startup")
def startup_event():
    make_database()

@app.post("/check-ambiguity")
def check_ambiguity_endpoint(data: QueryInput):
    return is_query_ambiguous(data.question)

@app.post("/ask")
def ask_endpoint(data: QueryInput):
    return run_pipeline(data.question, preferred_table=data.table_name)

@app.get("/analytics")
def analytics_endpoint():
    return get_telemetry_metrics()

@app.post("/upload-csv")
def upload_csv_endpoint(file: UploadFile = File(...)):
    # UploadFile.file is a file-like object - pandas can read it directly,
    # same as load_csv_to_db already expects from Streamlit's uploader.
    table_name, columns = load_csv_to_db(file.file, table_name="user_data")
    return {
        "table_name": table_name,
        "columns": columns,
        "schema": get_dynamic_schema()
    }
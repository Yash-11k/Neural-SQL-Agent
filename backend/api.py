from fastapi import FastAPI
from pydantic import BaseModel
from sql_agent import run_pipeline, is_query_ambiguous
from analytics import get_telemetry_metrics
from db_setup import make_database

app = FastAPI(title="NeuralSQL Simple API")

# Input model
class QueryInput(BaseModel):
    question: str

# Build database automatically on start
@app.on_event("startup")
def startup_event():
    make_database()

@app.post("/check-ambiguity")
def check_ambiguity_endpoint(data: QueryInput):
    return is_query_ambiguous(data.question)

@app.post("/ask")
def ask_endpoint(data: QueryInput):
    return run_pipeline(data.question)

@app.get("/analytics")
def analytics_endpoint():
    return get_telemetry_metrics()
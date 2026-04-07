from fastapi import FastAPI
import uvicorn

app = FastAPI(title="News Aggregator Bot")

@app.get("/")
def read_root():
    return {"status": "online", "message": "The News Aggregator Engine is running."}

@app.post("/trigger-pipeline")
def trigger_etl_pipeline():
    # We will build this out later to run the extract -> transform -> load sequence
    return {"status": "success", "message": "Pipeline triggered manually."}

if __name__ == "__main__":
    # Runs the server locally on port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
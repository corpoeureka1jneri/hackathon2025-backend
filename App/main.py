from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/start")
def start_sim(ticks: int):
    
    return {"message": "Simulation started"}


@app.get("/download")
def download_data():
    return {"message": "Simulation stopped"}





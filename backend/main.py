from fastapi import FastAPI

# start fastapi application
app = FastAPI()

@app.get("/health")
def check_status():
	return {"status": "ok"}


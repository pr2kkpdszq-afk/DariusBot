from fastapi import FastAPI

app = FastAPI(title="DariusBot")

@app.get("/")
def home():
    return {"message": "Hello from DariusBot on Fly.io! 🚀"}

@app.get("/health")
def health():
    return {"status": "healthy"}




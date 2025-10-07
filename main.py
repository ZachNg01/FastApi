from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def home():
    return {
        "message": "Cooking School Survey is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cooking-school-survey"}

@app.get("/survey")
async def survey():
    return {"message": "Survey endpoint - add your HTML forms here"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
from fastapi import FastAPI

app = FastAPI(title="Smart Baby Band API")


@app.get("/")
async def root():
    return {"message": "Smart Baby Band API is running"}t 
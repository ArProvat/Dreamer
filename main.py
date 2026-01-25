import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.three_story_overview.three_story_overview_router import router as three_stroy_router

app = FastAPI(title="Dreamer AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,     
    allow_methods=["*"],
    allow_headers=["*"]
    )


app.include_router(three_stroy_router,prefix='/v1',tags=["Three_story_router"])

@app.get('/' ,tags=['health'])
async def health():
    return{
        "status": "healthy",
        "service": "firecomme AI"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )

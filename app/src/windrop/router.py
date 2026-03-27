from fastapi import APIRouter

router = APIRouter()

@router.get("/enroll")
async def enroll():
    return None

@router.post("/upload")
async def upload():
    return None
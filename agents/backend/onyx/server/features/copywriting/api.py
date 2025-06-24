from fastapi import APIRouter, HTTPException
from .models import CopywritingInput, CopywritingOutput
from .service import CopywritingService

router = APIRouter(prefix="/copywriting", tags=["copywriting"])

@router.post("/generate", response_model=CopywritingOutput)
async def generate_copywriting(request: CopywritingInput):
    """Genera copywriting a partir de un input estructurado."""
    try:
        result = await CopywritingService.generate(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
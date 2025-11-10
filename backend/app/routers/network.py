from fastapi import APIRouter

router = APIRouter(prefix="/network", tags=["Network"])

@router.get("/")
def get_network_info():
    return {"message": "Network API placeholder — à implémenter"}

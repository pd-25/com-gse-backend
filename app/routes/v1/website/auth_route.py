from fastapi import APIRouter

router = APIRouter()

@router.get('/v1/website/auths')
def get_all():
    return []

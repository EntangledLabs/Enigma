from fastapi import APIRouter
from fastapi import Request

auth_router = APIRouter(prefix='/auth')

@auth_router.post('/get_token')
async def get_token(request: Request):
    pass
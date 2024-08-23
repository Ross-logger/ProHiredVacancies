from fastapi import FastAPI, HTTPException, Cookie, Response, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import create_db_and_tables, get_async_session
from contextlib import asynccontextmanager
from src import crud, utils, schemas
from src.config import HOST, PORT
from src.database import get_async_session



@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title="ProHired", lifespan=lifespan)


@app.post("/v1/vacancies/")
async def create_vacancy(request: Request, db=Depends(get_async_session)):
    # print(request.headers)
    jwt_token = request.headers.get("usersAuth")
    # print("JWT TOKEN:", jwt_token)
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Token not found")

    new_vacancy_data = await request.json()

    print("TOKEN:", utils.verify_token(jwt_token))

    user_id = utils.verify_token(jwt_token)
    print(request)

    new_vacancy = await crud.create_vacancy(new_vacancy_data, db, user_id)

    return new_vacancy


@app.get("/v1/vacancies/{vacancy_id}")
async def get_vacancy(vacancy_id: int, db: AsyncSession = Depends(get_async_session)):
    vacancy = await crud.get_vacancy(vacancy_id, db)
    return vacancy


@app.delete("/v1/vacancies/{vacancy_id}")
async def delete_vacancy(vacancy_id: int, db: AsyncSession = Depends(get_async_session)):
    vacancy = await crud.delete_vacancy(vacancy_id, db)
    return vacancy


@app.get("/v1/vacancies/")
async def list_vacancies(db: AsyncSession = Depends(get_async_session), limit: int = 100):
    vacancies = await crud.list_vacancies(db, limit)
    return vacancies


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host=HOST, port=int(PORT), reload=True)

from fastapi import FastAPI, HTTPException, Cookie, Response, Request, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import create_db_and_tables, get_async_session
from contextlib import asynccontextmanager
from src.database import crud
from src import utils, schemas
from config import HOST, PORT


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title="ProHired", lifespan=lifespan)


@app.post("/v1/vacancies/")
async def create_vacancy(request: Request, db=Depends(get_async_session)):
    jwt_token = request.headers.get("usersAuth")
    if not jwt_token:
        raise HTTPException(status_code=401, detail="Token not found")

    new_vacancy_data = await request.json()
    user_id = utils.verify_token(jwt_token)

    new_vacancy = await crud.create_vacancy(new_vacancy_data, db, user_id)
    return new_vacancy


@app.get("/v1/vacancies/count")
async def get_count_vacancies(db: AsyncSession = Depends(get_async_session)):
    count = await crud.get_vacancies_count(db)
    return {"count": count}


@app.get("/v1/vacancies/{vacancy_id}")
async def get_vacancy(vacancy_id: int, db: AsyncSession = Depends(get_async_session)):
    vacancy = await crud.get_vacancy(vacancy_id, db)
    return vacancy


@app.delete("/v1/vacancies/{vacancy_id}")
async def delete_vacancy(request: Request, vacancy_id: int, db: AsyncSession = Depends(get_async_session)):
    vacancy = await crud.get_vacancy(vacancy_id, db)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found.")
    user_id = request.headers.get("user_id")
    print("USER_ID:", user_id)
    print("OWNER_ID:", vacancy.user_id)
    if vacancy.user_id != int(user_id):
        raise HTTPException(status_code=403, detail="You are not allowed to delete this vacancy.")
    response = await crud.delete_vacancy(vacancy_id, db)
    return response


@app.get("/v1/vacancies/")
async def list_vacancies(db: AsyncSession = Depends(get_async_session), limit: int = 100):
    vacancies = await crud.list_vacancies(db, limit)
    return vacancies


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host=HOST, port=int(PORT), reload=True)

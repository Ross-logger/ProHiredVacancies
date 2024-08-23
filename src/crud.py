from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src import schemas
from src import models
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound, SQLAlchemyError


async def create_vacancy(new_vacancy_data: dict, db: AsyncSession, user_id: int):
    new_vacancy = models.Vacancy(**new_vacancy_data)
    new_vacancy.user_id = user_id
    db.add(new_vacancy)
    await db.commit()
    await db.refresh(new_vacancy)
    return new_vacancy


async def delete_vacancy(vacancy_id: int, db: AsyncSession):
    try:
        row = await db.execute(
            select(models.Vacancy).where(models.Vacancy.id == vacancy_id)
        )
        vacancy = row.scalar_one()

        await db.delete(vacancy)
        await db.commit()

        return {"message": f"Successfully deleted Vacancy with id {vacancy_id}"}

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Vacancy not found.")

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


async def get_vacancy(vacancy_id: int, db: AsyncSession):
    vacancy_row = await db.execute(select(models.Vacancy).where(models.Vacancy.id == int(vacancy_id)))
    vacancy = vacancy_row.scalars().all()
    print("VACANCY:", vacancy)
    return vacancy


async def list_vacancies(db: AsyncSession, limit: int = 100):
    result = await db.execute(select(models.Vacancy).limit(limit))
    return result.scalars().all()

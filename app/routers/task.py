from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from app.backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])

@router.get('/')
async def all_tasks(get_db: Annotated[Session, Depends(get_db)]):
    tasks = get_db.scalars(select(Task)).all()
    return tasks

@router.get('/task_id')
async def task_by_id(get_db: Annotated[Session, Depends(get_db)], task_id: int):
    task = get_db.scalars(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    else:
        return task

@router.post('/create')
async def create_task(get_db: Annotated[Session, Depends(get_db)], create_task: CreateTask, user_id: int):
    user = get_db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    else:
        get_db.execute(insert(Task).values(title = create_task.title,
                                            content = create_task.content,
                                            priority = create_task.priority,
                                            user_id = user_id,
                                            slug=slugify(create_task.title)))
        get_db.commit()
        return{
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }


@router.put('/update')
async def update_task(get_db: Annotated[Session, Depends(get_db)], task_id: int ,update_task: UpdateTask):
    task = get_db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    else:
        get_db.execute(update(Task).where(Task.id==task_id).values(
            title = update_task.title,
            content = update_task.content,
            priorty = update_task.priority,
            slug = slugify(task.title)))
        get_db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Task update is successful!'
        }

@router.delete('/delete')
async def delete_task(get_db: Annotated[Session, Depends(get_db)], task_id: int):
    task = get_db.scalars(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    else:
        get_db.execute(delete(Task).where(Task.id == task_id))
        get_db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Task delete is successful!'
        }
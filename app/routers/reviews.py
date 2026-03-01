from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas import ReviewRead, ReviewCreate # изменить
from app.db_depends import get_async_db
from app.auth import get_current_buyer, get_current_user
from app.utils import update_product_rating

# Создаем маршрутизатор с префиксом и тегом
router = APIRouter(
    prefix='/reviews',
    tags=['reviews'],
)

@router.get('/', response_model=list[ReviewRead], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных отзывов
    """
    # Выборка отзывов
    stmt = select(ReviewModel).where(ReviewModel.is_active)
    result = await db.scalars(stmt)
    reviews = result.all()
    return reviews


@router.get('/{product_id}/reviews', response_model=list[ReviewRead], status_code=status.HTTP_200_OK)
async def get_reviews_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список активных отзывов у продукта
    """
    # Выборка продуктов
    stmt = select(ProductModel).where(ReviewModel.is_active)
    result = await db.scalars(stmt)
    product = result.first()
    # Проверка, что товар существует/активный
    if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
    # Выборка отзывов
    stmt = select(ReviewModel).where(ReviewModel.product_id == product_id, ReviewModel.is_active)
    result = await db.scalars(stmt)
    reviews = result.all()
    return reviews


@router.post('/', response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer)
):
    """
    Создание нового отзыва
    """
    # Выборка продукта
    stmt = select(ProductModel).where(ProductModel.id == review_data.product_id)
    result = await db.scalars(stmt)
    product = result.first()
    # Если продукт не найден/не активный
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found or inactive')
    # Выборка комментария
    stmt = select(ReviewModel).where(ReviewModel.user_id == current_user.id)
    result = await db.scalars(stmt)
    review = result.all()
    # Проверка на дублирование
    if review:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='No create multiple comments under one product')
    # Создание нового отзыва
    review = ReviewModel(**review_data.model_dump(), user_id=current_user.id)
    db.add(review)
    await db.commit()
    await db.refresh(review)
    await update_product_rating(db, review_data.product_id)
    return review


@router.delete('/reviews/{review_id}')
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Мягко удаляет существующий/активный отзыв
    """
    # Выборка отзывов
    stmt = select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active)
    result = await db.scalars(stmt)
    review = result.first()
    # Проверка на существование/активность отзывов
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Reviews not found or inactive')
    # Проверка на права для удаления
    if (not(current_user.id == review.user_id or current_user.role == 'admin')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only creator or admin can perform this action')
    # Мягкое удаление
    stmt = update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False)
    await db.execute(stmt)
    await db.commit()
    return {'message': 'Review deleted'}
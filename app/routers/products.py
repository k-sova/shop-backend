from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_async_db

# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_async_db)):
    """
    Возвращает список всех товаров.
    """
    stmt = (select(ProductModel).join(CategoryModel).where(ProductModel.is_active == True,
                                                            CategoryModel.is_active == True,
                                                            ProductModel.stock > 0))
    result = await db.scalars(stmt)
    products = result.all()
    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_async_db)):
    """
    Создаёт новый товар.
    """
    # Проверка на активную категорию
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                    CategoryModel.is_active == True)
    result = await db.scalars(stmt)    
    category = result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}",
            response_model=list[ProductSchema],
            status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Session = Depends(get_async_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    # Проверяем, существует ли активная категория
    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                    CategoryModel.is_active == True)
    result = db.scalars(stmt)
    category = result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found or inactive")
        
    stmt = select(ProductModel).where(ProductModel.category_id == category_id,
                                      ProductModel.is_active == True)
    result = await db.scalars(stmt)
    products = result.first()
    return products


@router.get("/{product_id}",
            response_model=ProductSchema,
            status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    # db_product = db.get(ProductModel, product_id)
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    result = db.scalars(stmt)
    db_product = result.first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found product')
    
    # Проверяем, существует ли активная категория
    stmt = select(CategoryModel).where(CategoryModel.id == db_product.category_id, CategoryModel.is_active)
    result = await db.scalars(stmt)
    category = result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found or inactive")
    
    return db_product


@router.put("/{product_id}",
            response_model=ProductSchema,
            status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_async_db)):
    """
    Обновляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    result = await db.scalars(stmt)
    db_product = result.first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found product')
    
    # Проверяем, существует ли активная категория
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                    CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")
    stmt = (update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump()))
    await db.execute(stmt)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_async_db)):
    """
    Удаляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    result = await db.scalars(stmt)
    db_product = result.first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found product')
    stmt = update(ProductModel).where(ProductModel.id == product_id).values(is_active=False)
    await db.execute(stmt)
    await db.commit()
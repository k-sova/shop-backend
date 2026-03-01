
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict, EmailStr, StringConstraints, PositiveInt, NonNegativeInt
from decimal import Decimal
import datetime

str30 = Annotated[
    str,
    StringConstraints(min_length=1, max_length=30, strip_whitespace=True)
]
str100 = Annotated[
    str,
    StringConstraints(min_length=1, max_length=100, strip_whitespace=True)
]
str500 = Annotated[
    str,
    StringConstraints(min_length=1, max_length=500, strip_whitespace=True)
]
str200 = Annotated[
    str,
    StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
]
IsActive = Annotated[
    bool,
    Field(
        ...,
        description='Активна ли запись'
    )
]

class Category(BaseModel):
    """
        Родительская схема для категорий
    """
    name: Annotated[
        str30,
        Field(description='Название категории',
              examples=['Машины', 'Холодильники'])
    ]
    parent_id: Annotated[
        int | None,
        Field(description='Идентификатор родительской категории')
    ]

class CategoryCreate(Category):
    """
        Схема для создания и обновления категории.
        Используется в POST и PUT запросах.
    """
    pass

class CategoryRead(Category):
    """
        Схема для ответа с данными категории.
        Используется в GET-запросах.
    """
    id: Annotated[
        int,
        Field(
            ..., 
            description='Уникальный идентификатор категории'
        )
    ]
    is_active: IsActive

    model_config = ConfigDict(from_attributes=True)

class Product(BaseModel):
    """
    Родительская схема для продуктов
    """
    name: Annotated[
        str100,
        Field(
            ..., 
            description='Название товара',
            examples=['Порш', 'Самсунг']
        )
    ]
    description: Annotated[
        str500 | None,
        Field(
            None,
            description='Описание товара',
            examples=['Быстрее лошади']
        )
    ]
    price: Annotated[
        Decimal,
        Field(
            ...,
            gt=0,
            description='Цена товара',
            examples=['2.05', '1213.23'],
            decimal_places=2
        )
    ]
    image_url: Annotated[
        str200 | None,
        Field(
            None,
            description='URL изображения товара'
        )
    ]
    stock: Annotated[
        PositiveInt,
        Field(
            ...,
            description='Количество товара на складе'
        )
    ]
    category_id: Annotated[
        int,
        Field(
            ...,
            description='ID категории, к которой относится товар'
        )
    ]

class ProductCreate(Product):
    """
        Модель для создания и обновления товара.
        Используется в POST и PUT запросах.
    """
    pass

class ProductRead(Product):
    """
        Модель для ответа с данными товара.
        Используется в GET-запросах.
    """
    id: Annotated[
        int,
        Field(
            ..., 
            description='Уникальный идентификатор товара'
        )
    ]
    is_active: IsActive
    rating: Annotated[
        float,
        Field(
            ..., 
            description='Рейтинг товара'
        )
    ]
    
    model_config = ConfigDict(from_attributes=True)
    
    
class User(BaseModel):
    email: Annotated[
        EmailStr,
        Field(
            ...,
            description='Email пользователя'
        )
    ]
    role: Annotated[
        str, 
        Field(
            default='buyer', 
            pattern='^(buyer|seller|admin)$', 
            description='Роль: "admin", "buyer" или "seller"'
        )
    ]


class UserCreate(User):
    """
        Схема для создания пользователя
    """
    password: Annotated[
        str30,
        Field(
            ...,
            description='Пароль (минимум 8 символов)'
        )
    ]


class UserRead(BaseModel):
    """
        Схема для ответа с данными пользователя
    """
    id: int
    is_active: IsActive
    model_config = ConfigDict(from_attributes=True)
    

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
    
class Review(BaseModel):
    product_id: Annotated[
        int,
        Field(
            ..., 
            description='Идентификатор комментируемого товара'
        )
    ]
    comment: Annotated[
        str500 | None,
        Field(
            None,
            description='Текстовый комментатор'
        )
    ]
    grade: Annotated[
        int, 
        Field(
            ...,
            description='Оставленная оцена товару', 
            ge=0, 
            le=5
        )
    ]


class ReviewRead(Review):
    """
        Модель для ответа с данными комментария
    """
    id: Annotated[
        int,
        Field(
            ..., 
            description='Уникальный идентификатор товара'
        )
    ]
    user_id: Annotated[
        int,
        Field(
            ...,
            description='Идентификатор комментатора'
        )
    ]
    comment_date: Annotated[
        datetime.datetime, 
        Field(
            ..., 
            description='Дата и время написания комментария'
        )
    ]
    is_active: IsActive


class ReviewCreate(Review):
    """
    Схема для создания комментария
    """
    pass


class ProductList(BaseModel):
    """
    Список пагинации для товаров.
    """
    items: Annotated[
        list[ProductRead],
        Field(
            description="Товары для текущей страницы"
        )
    ]
    total: Annotated[
        NonNegativeInt, 
        Field(
            ge=0, 
            description="Общее количество товаров"
        )
    ]
    page: Annotated[
        PositiveInt,
        Field(
            ge=1,
            description="Номер текущей страницы"
        )
    ]
    page_size: Annotated[
        PositiveInt,
        Field(
            ge=1, 
            description="Количество элементов на странице"
        )
    ]
    
    model_config = ConfigDict(from_attributes=True)  # Для чтения из ORM-объектов
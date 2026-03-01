from typing import TYPE_CHECKING
from sqlalchemy import Integer, Text, DateTime, Boolean, ForeignKey, SmallInteger, text, CheckConstraint
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

import datetime

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.products import Product
    from app.models.users import User


class Review(Base):
    __tablename__ = 'reviews'
    
    __table_args__ = (
        CheckConstraint(
            "grade >= 1 AND grade <= 5",
            name="check_grade_range"
        ),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, server_default=func.now())
    grade: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text('TRUE'))
    
    user: Mapped['User'] = relationship('User', back_populates='reviews')
    product: Mapped['Product'] = relationship('Product', back_populates='reviews')
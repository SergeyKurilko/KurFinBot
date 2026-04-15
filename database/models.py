from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """Пользователь"""

    __tablename__ = "user"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_boss: Mapped[bool] = mapped_column(Boolean, default=False)
    username: Mapped[str] = mapped_column(nullable=False)

    # Добавляем обратную связь
    money: Mapped["Money"] = relationship("Money", back_populates="user", uselist=False)


class Money(Base):
    """Вознаграждение"""

    __tablename__ = "money"
    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[int] = mapped_column(Integer)
    scores: Mapped[int] = mapped_column(Integer)
    daily_reward: Mapped[int] = mapped_column(Integer)
    last_reward: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    # Добавляем связь
    user: Mapped["User"] = relationship("User", back_populates="money")

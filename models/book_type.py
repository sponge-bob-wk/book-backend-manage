# -*- coding: utf-8 -*-
"""图书类型实体类（对应数据库表 book_type）。"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class BookType(Base):
    """图书类型表。

    表名：book_type     主键：id（自动增长）
    id        id           整数  主键
    typeName  图书类型名称  字符串 非空
    """

    __tablename__ = "book_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    typeName: Mapped[str] = mapped_column("typeName", String(50), nullable=False)

    # 该类型下的图书（由 BookInfo.bookType 反向引用）
    books = relationship("BookInfo", back_populates="bookTypeRef")

    def __repr__(self):
        return "<BookType id=%s typeName=%s>" % (self.id, self.typeName)
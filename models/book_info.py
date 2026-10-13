# -*- coding: utf-8 -*-
"""图书信息实体类（对应数据库表 book_info）。"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

import config
from models.base import Base


class BookInfo(Base):
    """图书信息表。

    表名：book_info   主键：bookId（自动增长）

    bookId          图书ID        整数   主键
    bookCode        图书编号      字符串 非空
    bookName        图书名称      字符串 非空
    bookType        图书类型      整数   非空（外键 -> book_type.id）
    bookAuthor      图书作者      字符串 非空
    publishPress    出版社        字符串 非空
    publishDate     出版日期      日期   非空
    borrowed        是否借阅      整数   非空（1 已借阅 / 0 未借阅）
    createdBy       入库人        字符串 非空
    creationTime    入库时间      日期   非空
    lastUpdatetime  最新更新时间  日期

    说明：试卷字段表中 bookAuthor 的「类型」列写的是「整数」，但界面示例
    取值为「金庸」「（英）Martin Fowler」等字符串，属试卷笔误，此处按字符串建表。
    """

    __tablename__ = "book_info"

    bookId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bookCode: Mapped[str] = mapped_column(String(30), nullable=False)
    bookName: Mapped[str] = mapped_column(String(100), nullable=False)
    bookType: Mapped[int] = mapped_column(Integer, ForeignKey("book_type.id"), nullable=False)
    bookAuthor: Mapped[str] = mapped_column(String(100), nullable=False)
    publishPress: Mapped[str] = mapped_column(String(100), nullable=False)
    publishDate: Mapped[date] = mapped_column(Date, nullable=False)
    borrowed: Mapped[int] = mapped_column(Integer, nullable=False, default=config.BORROWED_NO)
    createdBy: Mapped[str] = mapped_column(String(50), nullable=False)
    creationTime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    lastUpdatetime: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # 图书类型（多对一）
    bookTypeRef = relationship("BookType", back_populates="books", lazy="joined")

    # ---------- 展示用辅助属性（模板只读，不做二次查询） ----------

    @property
    def borrowText(self):
        """是否借阅的中文显示。"""
        return "已借阅" if self.borrowed == config.BORROWED_YES else "未借阅"

    @property
    def typeName(self):
        """图书类型名称（列表页「图书分类」列）。"""
        return self.bookTypeRef.typeName if self.bookTypeRef else ""

    @property
    def creationTimeText(self):
        """入库时间按「年-月-日」显示（试卷要求 10.C）。"""
        return self.creationTime.strftime(config.DATE_FORMAT) if self.creationTime else ""

    @property
    def publishDateText(self):
        """出版日期按「年-月-日」显示。"""
        return self.publishDate.strftime(config.DATE_FORMAT) if self.publishDate else ""

    def __repr__(self):
        return "<BookInfo bookId=%s bookCode=%s bookName=%s>" % (
            self.bookId, self.bookCode, self.bookName)
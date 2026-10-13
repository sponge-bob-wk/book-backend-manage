# -*- coding: utf-8 -*-
"""数据访问层（DAO）：图书信息表 book_info。"""
from abc import ABC, abstractmethod

from sqlalchemy import func, select

from models import BookInfo, Session


class BookInfoDao(ABC):
    """图书信息 DAO 接口（对应试卷第 6 步）。"""

    @abstractmethod
    def findPage(self, keyword=None, page=1, page_size=5):
        """分页查询图书，按入库时间降序。返回 (rows, total)。"""

    @abstractmethod
    def findById(self, book_id):
        """按主键查询单条图书。"""

    @abstractmethod
    def insert(self, book):
        """新增图书。"""

    @abstractmethod
    def update(self, book):
        """修改图书。"""

    @abstractmethod
    def deleteById(self, book_id):
        """按主键删除图书，返回受影响行数。"""

    @abstractmethod
    def count(self):
        """图书总数。"""


class BookInfoDaoImpl(BookInfoDao):
    """图书信息 DAO 实现类。

    只负责 SQL/ORM 语句，不 commit ——事务边界由 service 层的
    @transactional 统一管理（声明式事务）。
    """

    def findPage(self, keyword=None, page=1, page_size=5):
        session = Session()
        stmt = select(BookInfo)
        count_stmt = select(func.count(BookInfo.bookId))

        if keyword:
            like = "%" + keyword.strip() + "%"
            stmt = stmt.where(BookInfo.bookName.like(like))
            count_stmt = count_stmt.where(BookInfo.bookName.like(like))

        total = session.execute(count_stmt).scalar() or 0

        # 入库时间降序；同一时间按主键降序保证分页稳定
        stmt = stmt.order_by(BookInfo.creationTime.desc(), BookInfo.bookId.desc())
        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        rows = list(session.execute(stmt).scalars().unique())
        return rows, total

    def findById(self, book_id):
        session = Session()
        return session.get(BookInfo, book_id)

    def insert(self, book):
        session = Session()
        session.add(book)
        session.flush()          # 取回自增主键
        return book

    def update(self, book):
        session = Session()
        session.add(book)
        session.flush()
        return book

    def deleteById(self, book_id):
        session = Session()
        book = session.get(BookInfo, book_id)
        if book is None:
            return 0
        session.delete(book)
        session.flush()
        return 1

    def count(self):
        session = Session()
        return session.execute(select(func.count(BookInfo.bookId))).scalar() or 0
# -*- coding: utf-8 -*-
"""数据访问层（DAO）：图书类型表 book_type。"""
from abc import ABC, abstractmethod

from sqlalchemy import select

from models import BookType, Session


class BookTypeDao(ABC):
    """图书类型 DAO 接口。"""

    @abstractmethod
    def findAll(self):
        """查询全部图书类型（新增/修改页面的下拉框数据来源）。"""

    @abstractmethod
    def findById(self, type_id):
        """按主键查询图书类型。"""


class BookTypeDaoImpl(BookTypeDao):
    """图书类型 DAO 实现类。

    试卷要求：新增/修改页面的图书类型必须来源于 book_type 表，
    不允许在页面写死选项。
    """

    def findAll(self):
        session = Session()
        return list(session.execute(select(BookType).order_by(BookType.id)).scalars())

    def findById(self, type_id):
        session = Session()
        return session.get(BookType, type_id)
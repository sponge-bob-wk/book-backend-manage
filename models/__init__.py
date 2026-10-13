# -*- coding: utf-8 -*-
"""实体层包：声明持久化类与映射文件的位置（对应试卷第 5 步）。"""
from models.base import Base, Session, engine, DB_BACKEND, init_database, remove_session
from models.book_info import BookInfo
from models.book_type import BookType

__all__ = [
    "Base", "Session", "engine", "DB_BACKEND", "init_database", "remove_session",
    "BookInfo", "BookType",
]
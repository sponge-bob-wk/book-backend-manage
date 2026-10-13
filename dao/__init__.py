# -*- coding: utf-8 -*-
"""持久层包：DAO 接口及其实现类（对应试卷第 6 步）。"""
from dao.book_info_dao import BookInfoDao, BookInfoDaoImpl
from dao.book_type_dao import BookTypeDao, BookTypeDaoImpl

# DAO 单例：由 controller -> service -> dao 逐层注入
book_info_dao = BookInfoDaoImpl()
book_type_dao = BookTypeDaoImpl()

__all__ = ["BookInfoDao", "BookInfoDaoImpl", "BookTypeDao", "BookTypeDaoImpl",
           "book_info_dao", "book_type_dao"]
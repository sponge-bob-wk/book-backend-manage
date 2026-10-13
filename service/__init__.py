# -*- coding: utf-8 -*-
"""业务层包：Service 接口及其实现类（对应试卷第 7 步）。

Service 单例在此装配，内部持 DAO 引用（controller -> service -> dao）。
"""
from service.book_info_service import (
    BookInfoService, BookInfoServiceImpl, PageResult,
)
from service.transaction import transactional

book_info_service = BookInfoServiceImpl()

__all__ = ["BookInfoService", "BookInfoServiceImpl", "PageResult",
           "transactional", "book_info_service"]
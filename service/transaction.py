# -*- coding: utf-8 -*-
"""声明式事务支持（对应试卷第 9 步：「以代码方式实现事务不得分」）。

业务类不写 begin/commit/rollback，只在方法上加 @transactional 装饰器，
由装饰器统一开启事务、提交或回滚，等价于 Spring 的声明式事务。
"""
import functools
import logging

from models import Session

logger = logging.getLogger(__name__)


def transactional(func):
    """声明式事务装饰器：正常返回则提交，抛异常则回滚并向上抛出。"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        if not session.in_transaction():
            session.begin()
        try:
            result = func(*args, **kwargs)
            session.commit()
            return result
        except Exception:
            session.rollback()
            logger.exception("事务回滚：%s", func.__qualname__)
            raise

    return wrapper
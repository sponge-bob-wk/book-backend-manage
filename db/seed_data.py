# -*- coding: utf-8 -*-
"""测试数据（试卷第 1 步：每个表中至少 5 条测试数据）。

图书类型与图书样例取自试卷图-1、图-3 的界面示例，另补充若干条，
使列表页能体现「每页 5 条 + 分页」的效果。
"""
import logging
from datetime import date, datetime

from models import BookInfo, BookType, Session

logger = logging.getLogger(__name__)

# ---------- 图书类型表 book_type（试卷列举的 8 类） ----------
BOOK_TYPES = [
    (1, "小说"),
    (2, "文学"),
    (3, "传记"),
    (4, "艺术"),
    (5, "少儿"),
    (6, "经济"),
    (7, "管理"),
    (8, "科技"),
]

# ---------- 图书信息表 book_info ----------
# 字段顺序：bookCode, bookName, 类型id, 作者, 出版社, 出版日期, 是否借阅, 入库人, 入库时间
BOOKS = [
    ("BK000023", "企业应用架构模式", 8, "（英）Martin Fowler", "机械工业出版社",
     date(2014, 6, 20), 0, "系统管理员", datetime(2014, 7, 3, 9, 30, 0)),
    ("BK000024", "精通Hibernate", 8, "刘洋", "电子工业出版社",
     date(2014, 4, 18), 1, "系统管理员", datetime(2014, 5, 3, 14, 5, 0)),
    ("BK000025", "天龙八部", 1, "金庸", "中原出版社",
     date(2014, 2, 28), 0, "系统管理员", datetime(2014, 3, 12, 10, 15, 0)),
    ("BK000026", "寻找家园", 4, "高尔泰", "北京十月文艺出版社",
     date(2014, 2, 10), 0, "系统管理员", datetime(2014, 3, 1, 16, 40, 0)),
    ("BK000027", "小猫莫格成长系列", 5, "（英）朱迪斯·克尔", "接力出版社",
     date(2013, 12, 1), 1, "系统管理员", datetime(2014, 1, 1, 11, 0, 0)),
    ("BK000028", "三国演义", 1, "罗贯中", "人民文学出版社",
     date(2013, 11, 5), 0, "系统管理员", datetime(2013, 12, 18, 9, 0, 0)),
    ("BK000029", "活着", 1, "余华", "作家出版社",
     date(2013, 10, 12), 1, "系统管理员", datetime(2013, 11, 26, 15, 20, 0)),
    ("BK000030", "经济学原理", 6, "（美）曼昆", "北京大学出版社",
     date(2013, 9, 8), 0, "系统管理员", datetime(2013, 10, 30, 8, 45, 0)),
    ("BK000031", "管理学", 7, "周三多", "高等教育出版社",
     date(2013, 8, 15), 0, "系统管理员", datetime(2013, 9, 21, 13, 10, 0)),
    ("BK000032", "苏东坡传", 3, "林语堂", "湖南文艺出版社",
     date(2013, 7, 3), 1, "系统管理员", datetime(2013, 8, 14, 17, 25, 0)),
    ("BK000033", "文学回忆录", 2, "木心", "广西师范大学出版社",
     date(2013, 6, 9), 0, "系统管理员", datetime(2013, 7, 7, 10, 50, 0)),
    ("BK000034", "深入理解计算机系统", 8, "（美）Randal E. Bryant", "机械工业出版社",
     date(2013, 5, 21), 0, "系统管理员", datetime(2013, 6, 2, 9, 5, 0)),
]


def seed_all():
    """在表为空时灌入测试数据（重复调用安全）。"""
    session = Session()

    if session.query(BookType).count() == 0:
        for type_id, name in BOOK_TYPES:
            session.add(BookType(id=type_id, typeName=name))
        session.flush()
        logger.info("已初始化图书类型 %d 条", len(BOOK_TYPES))

    if session.query(BookInfo).count() == 0:
        for (code, name, type_id, author, press, pub_date,
             borrowed, created_by, created_time) in BOOKS:
            session.add(BookInfo(
                bookCode=code, bookName=name, bookType=type_id,
                bookAuthor=author, publishPress=press, publishDate=pub_date,
                borrowed=borrowed, createdBy=created_by,
                creationTime=created_time, lastUpdatetime=None,
            ))
        logger.info("已初始化图书信息 %d 条", len(BOOKS))

    session.commit()
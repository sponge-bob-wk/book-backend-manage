# -*- coding: utf-8 -*-
"""工程配置文件。

数据库目标：MySQL 5（匹配试卷的「Oracle 10g/11g 或 MySQL 5」要求）。
考虑到本机可能尚未安装 MySQL 服务，若 MySQL 连接失败则自动回退到
SQLite 单文件库，保证工程开箱即可运行、页面可演示。

可用环境变量覆盖连接参数：MYSQL_HOST / MYSQL_PORT / MYSQL_USER /
MYSQL_PASSWORD / MYSQL_DB / DB_URL。
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- MySQL 连接参数 ----------
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")
MYSQL_DB = os.environ.get("MYSQL_DB", "book_borrow")

MYSQL_URL = (
    "mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4".format(
        user=MYSQL_USER, pwd=MYSQL_PASSWORD, host=MYSQL_HOST,
        port=MYSQL_PORT, db=MYSQL_DB,
    )
)

# ---------- SQLite 回退（单文件库） ----------
SQLITE_FILE = os.path.join(BASE_DIR, "db", "book_borrow.db")
SQLITE_URL = "sqlite:///" + SQLITE_FILE.replace("\\", "/")

# DB_URL 显式指定时优先使用；否则先试 MySQL，失败再退 SQLite
DB_URL = os.environ.get("DB_URL") or MYSQL_URL

# ---------- 业务参数 ----------
PAGE_SIZE = 5                      # 试卷要求：图书列表每页显示五条数据
DATE_FORMAT = "%Y-%m-%d"           # 试卷要求：入库时间显示为「年-月-日」
DEFAULT_OPERATOR = "系统管理员"     # 未实现登录功能，入库人固定为系统管理员(admin)

# 是否借阅：1 已借阅 / 0 未借阅
BORROWED_YES = 1
BORROWED_NO = 0
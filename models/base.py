# -*- coding: utf-8 -*-
"""持久层基础设施：引擎创建、Session 工厂、声明式基类。

对应试卷「四、具体要求及推荐实现步骤」第 3 步（添加数据库支持）与
第 9 步（声明式事务）——事务由 service 层的 @transactional 统一控制，
业务代码中不出现手工 commit。
"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

import config

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """所有实体类的基类（声明式基类）。"""


def _build_engine(url, label):
    """按 URL 创建引擎；SQLite 需要额外参数让多线程测试客户端可用。"""
    kwargs = {"echo": False, "future": True, "pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        kwargs.pop("pool_pre_ping")
    logger.info("使用 %s 数据库：%s", label, url)
    return create_engine(url, **kwargs)


def create_app_engine(url=None):
    """创建引擎，并返回 (engine, 实际使用的数据库标识)。

    url 为空时按 config.DB_URL 走：先试 MySQL，连不上则回退 SQLite。
    """
    url = url or config.DB_URL
    if url.startswith("mysql"):
        try:
            engine = _build_engine(url, "MySQL")
            with engine.connect() as conn:      # 主动探活，尽早发现服务未启动
                conn.exec_driver_sql("SELECT 1")
            return engine, "MySQL"
        except Exception as exc:                # 驱动缺失或服务未启动
            logger.warning("MySQL 不可用（%s），回退到 SQLite。", exc.__class__.__name__)
            print("[警告] MySQL 连接失败（%s），已自动回退到 SQLite：%s"
                  % (exc.__class__.__name__, config.SQLITE_FILE))
            sqlite_engine = _build_engine(config.SQLITE_URL, "SQLite")
            return sqlite_engine, "SQLite"
    return _build_engine(url, "SQLite" if url.startswith("sqlite") else url), \
        "SQLite" if url.startswith("sqlite") else url


# 全局引擎与 Session 工厂（scoped_session：按线程隔离，适配 Flask 多线程）
engine, DB_BACKEND = create_app_engine()
Session = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
)


def init_database(create_tables=True, seed=True):
    """建表 + 灌入测试数据（试卷第 1 步、第 15 步要求）。

    仅在表不存在时创建；seed 只在表为空时执行，重复调用是安全的。
    """
    from models import book_info, book_type  # noqa: F401  导入以注册映射

    if create_tables:
        Base.metadata.create_all(engine)
    if seed:
        from db.seed_data import seed_all
        seed_all()


def remove_session(exception=None):
    """请求结束时释放 Session（由 Flask teardown 调用）。"""
    Session.remove()
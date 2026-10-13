# -*- coding: utf-8 -*-
"""工程入口（等价于 Java Web 工程里的 web.xml + Spring 容器装配）。

启动：
    python app.py
然后浏览器访问 http://127.0.0.1:5000/

数据库：默认连接 MySQL（可用环境变量覆盖）；若本机 MySQL 未启动，
自动回退到 SQLite 单文件库 db/book_borrow.db，保证页面可直接演示。
"""
import logging
import os

from flask import Flask

import config
from controller import book
from models import DB_BACKEND, init_database, remove_session


def create_app(database_url=None):
    """应用工厂：装配控制器、初始化数据库、注册请求级 Session 回收。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.environ.get("SECRET_KEY", "book-backend-manage-secret")

    # 模板全局变量与过滤器
    app.jinja_env.globals["DEFAULT_OPERATOR"] = config.DEFAULT_OPERATOR
    app.jinja_env.filters["datefmt"] = _datefmt

    # 控制器：图书业务
    app.register_blueprint(book)

    # 请求结束时释放 ORM Session
    app.teardown_appcontext(remove_session)

    if database_url:
        # 测试场景：显式指定数据库（例如临时 SQLite 文件）
        import models.base as base
        base.engine, backend = base.create_app_engine(database_url)
        base.Session.remove()                    # 清掉已登记的 Session，使重绑定生效
        base.Session.configure(bind=base.engine)
        app.config["DB_BACKEND"] = backend
        init_database()
    else:
        init_database()
        app.config["DB_BACKEND"] = DB_BACKEND

    print("=" * 62)
    print(" 图书借阅系统-后台管理  已就绪")
    print(" 当前数据库后端：%s" % app.config["DB_BACKEND"])
    print(" 访问地址：http://127.0.0.1:5000/")
    print("=" * 62)
    return app


def _datefmt(value, fmt=None):
    """模板过滤器：日期按「年-月-日」显示（试卷要求 10.C）。"""
    if value is None or value == "":
        return ""
    try:
        return value.strftime(fmt or config.DATE_FORMAT)
    except AttributeError:
        return str(value)


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
# -*- coding: utf-8 -*-
"""回归测试（对应 quiz07.md 第 6 条：使用 Actions 进行回归测试）。

覆盖试卷的功能要求：
    1. 列表默认按入库时间降序、每页 5 条、日期「年-月-日」、隔行变色、分页
    2. 按图书名称模糊查询 + 查询条件记忆
    3. 查看详细信息（只读）+ 返回保留查询条件
    4. 新增（默认值、必填校验、提示信息）
    5. 修改（入库人/入库时间只读）
    6. 删除（确认 + 成功/失败提示）
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config                                    # noqa: E402
import models.base as base                       # noqa: E402
from flask import Flask                          # noqa: E402


@pytest.fixture()
def app(tmp_path):
    """每个用例使用独立的临时 SQLite 库，互不干扰。"""
    db_file = tmp_path / "test_book.db"
    url = "sqlite:///" + str(db_file).replace("\\", "/")

    engine, _backend = base.create_app_engine(url)
    base.Session.remove()                        # 清掉已登记的 Session，使重绑定生效
    base.engine = engine
    base.Session.configure(bind=engine)
    base.Base.metadata.create_all(engine)

    from db.seed_data import seed_all
    seed_all()

    from controller import book

    application = Flask(
        "book_backend_manage_test",
        static_folder=os.path.join(ROOT, "static"),
        template_folder=os.path.join(ROOT, "templates"),
    )
    application.secret_key = "test"
    application.jinja_env.globals["DEFAULT_OPERATOR"] = config.DEFAULT_OPERATOR
    application.jinja_env.filters["datefmt"] = _datefmt
    application.register_blueprint(book)
    application.teardown_appcontext(base.remove_session)

    yield application
    base.remove_session()
    engine.dispose()


def _datefmt(value, fmt=None):
    """与 app.py 保持一致的日期过滤器（年-月-日）。"""
    if value is None or value == "":
        return ""
    try:
        return value.strftime(fmt or config.DATE_FORMAT)
    except AttributeError:
        return str(value)


@pytest.fixture()
def client(app):
    return app.test_client()


def html(resp):
    return resp.get_data(as_text=True)


def test_list_default_order_and_paging(client):
    """向后端要列表页的数据：降序 + 每页 5 条。"""
    from service import book_info_service as service
    page1 = service.listBooks("", 1)
    assert len(page1.rows) == 5
    assert page1.total == 12
    assert page1.totalPages == 3

    times = [r.creationTime for r in page1.rows]
    assert times == sorted(times, reverse=True), "必须按入库时间降序"

    page2 = service.listBooks("", 2)
    assert len(page2.rows) == 5
    assert page1.rows[0].bookId != page2.rows[0].bookId

    page3 = service.listBooks("", 3)
    assert len(page3.rows) == 2


def test_list_page_renders_key_elements(client):
    """页面元素：标题、表头、日期格式、隔行变色样式类、分页条。"""
    body = html(client.get("/"))
    assert "图书借阅系统-后台管理" in body
    for header in ["图书编号", "图书分类", "图书名称", "作者", "出版社",
                   "入库时间", "是否借阅", "操作"]:
        assert header in body, "列表表头缺少列：%s" % header

    assert "2014-07-03" in body, "入库时间需按「年-月-日」显示"
    assert "2014-07-03 09:30:00" not in body, "不应显示完整时间"
    assert "查看" in body and "修改" in body and "删除" in body
    assert "共3页" in body, "分页条需显示总页数"
    assert "上一页" in body and "下一页" in body
    # 隔行变色由静态样式实现
    css = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "static", "css", "style.css"), encoding="utf-8").read()
    assert "nth-child(even)" in css


def test_search_by_name_and_remember_keyword(client):
    """模糊查询 + 查询条件记忆 + 结果仍按入库时间降序。"""
    from service import book_info_service as service
    result = service.listBooks("天龙", 1)
    assert result.total == 1
    assert result.rows[0].bookName == "天龙八部"

    result = service.listBooks("系", 1)          # 模糊匹配：系列 / 系统
    assert result.total >= 2

    body = html(client.get("/book/list?bookName=天龙"))
    assert 'value="天龙"' in body, "输入框需记忆查询条件"
    assert "天龙八部" in body


def test_view_page_is_readonly_and_back_keeps_query(client):
    """查看页面字段只读，返回按钮保留查询条件。"""
    client.get("/book/list?bookName=天龙&page=1")
    body = html(client.get("/book/view/3?bookName=天龙&page=1"))
    assert "查看图书信息" in body
    assert "BK000025" in body
    assert body.count('readonly="readonly"') >= 8, "查看页所有字段应为只读"
    assert "返回" in body
    assert "bookName=%E5%A4%A9%E9%BE%99" in body or "bookName=天龙" in body


def test_add_book_with_defaults(client):
    """新增：默认入库人=系统管理员、默认入库时间=今天、默认未借阅，成功有提示。"""
    from service import book_info_service as service

    form = {
        "bookCode": "BK000099",
        "bookName": "测试图书",
        "bookType": "1",
        "bookAuthor": "测试作者",
        "publishPress": "测试出版社",
        "borrowed": "0",
        "createdBy": config.DEFAULT_OPERATOR,
        "creationTime": "2015-01-01",
    }
    resp = client.post("/book/add", data=form, follow_redirects=True)
    body = html(resp)
    assert "新增成功！" in body, "新增后需给出提示信息"
    assert form["bookCode"] in body, "新增后应回到列表页并能看到新记录"

    saved = service.listBooks("测试图书", 1).rows[0]
    assert saved.createdBy == config.DEFAULT_OPERATOR
    assert saved.borrowed == config.BORROWED_NO
    assert saved.lastUpdatetime is None


def test_add_page_defaults_and_type_options(client):
    """新增页：类型下拉来源于 book_type、入库人默认系统管理员、必填项标 *。"""
    body = html(client.get("/book/add"))
    for name in ["小说", "文学", "传记", "艺术", "少儿", "经济", "管理", "科技"]:
        assert name in body, "图书类型必须来源于 book_type 表：%s" % name
    assert 'value="系统管理员"' in body, "入库人默认当前登录用户（系统管理员）"
    assert body.count('class="star"') >= 6, "必填项需标注 *"
    assert "jquery-1.8.3.min.js" in body, "必填项校验使用 jQuery"


def test_add_book_validation_failure(client):
    """必填项缺失时新增失败并给出提示。"""
    resp = client.post("/book/add", data={"bookCode": "", "bookName": "",
                                          "bookType": "", "borrowed": ""},
                       follow_redirects=True)
    assert "新增失败！" in html(resp)


def test_edit_book_and_readonly_fields(client):
    """修改：可改名称/类型，入库人与入库时间只读不受影响，成功有提示。"""
    from service import book_info_service as service
    before = service.getBook(3)
    created_by, creation_time = before.createdBy, before.creationTime

    form = {
        "bookCode": before.bookCode,
        "bookName": "天龙八部（修订版）",
        "bookType": "2",
        "bookAuthor": before.bookAuthor,
        "publishPress": before.publishPress,
        "borrowed": "1",
        "createdBy": "黑客",
        "creationTime": "1999-01-01",
    }
    resp = client.post("/book/edit/3", data=form, follow_redirects=True)
    assert "修改成功！" in html(resp)

    after = service.getBook(3)
    assert after.bookName == "天龙八部（修订版）"
    assert after.bookType == 2
    assert after.borrowed == 1
    assert after.createdBy == created_by, "入库人为只读字段，不可修改"
    assert after.creationTime == creation_time, "入库时间为只读字段，不可修改"
    assert after.lastUpdatetime is not None, "修改后应更新最新更新时间"

    body = html(client.get("/book/edit/3"))
    assert body.count('readonly="readonly"') >= 2, "修改页入库人/入库时间应只读"


def test_delete_book_and_message(client):
    """删除：成功提示 + 记录消失 + 越界页码自动回落。"""
    from service import book_info_service as service
    client.get("/book/list")
    resp = client.get("/book/delete/3", follow_redirects=True)
    assert "删除成功！" in html(resp)

    assert service.getBook(3) is None
    assert service.listBooks("天龙", 1).total == 0

    # 删除不存在的记录 -> 失败提示
    resp = client.get("/book/delete/999999", follow_redirects=True)
    assert "删除失败！" in html(resp)


def test_delete_confirm_and_alert_script(client):
    """删除前确认框与提示信息脚本存在（试卷 14.A、图-8/图-9）。"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    js = open(os.path.join(root, "static", "js", "book.js"), encoding="utf-8").read()
    assert "确定删除该图书信息？" in js
    assert "confirm(" in js
    assert "alert(" in js


def test_pagination_out_of_range_falls_back(client):
    """页码越界时回落到最后一页而不是空列表。"""
    from service import book_info_service as service
    result = service.listBooks("", 99)
    assert result.page == result.totalPages == 3
    assert len(result.rows) == 2


def test_mysql_sql_script_exists():
    """试卷第 15 步：需提交建表 + 主键自增 + 测试数据的 SQL 文件。"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_path = os.path.join(root, "db", "book_borrow.sql")
    assert os.path.exists(sql_path)
    sql = open(sql_path, encoding="utf-8").read()
    assert "CREATE DATABASE" in sql
    assert "AUTO_INCREMENT" in sql
    assert "INSERT INTO `book_info`" in sql
    assert "INSERT INTO `book_type`" in sql
    assert sql.count("BK0000") >= 5, "图书信息表至少 5 条测试数据"
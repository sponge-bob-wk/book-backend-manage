# -*- coding: utf-8 -*-
"""控制器层（Controller）：图书借阅系统后台管理的全部请求入口。

对应试卷第 8 步：控制器中持有 Service 引用，负责组织结果与提示信息，
并导航到指定页面完成显示。

页面清单：
    GET  /                 图书信息列表（默认全部，入库时间降序，每页 5 条）
    GET  /book/list        同上，支持 ?bookName=xxx&page=n
    GET  /book/view/<id>   查看图书信息（全部只读）
    GET  /book/add         跳转新增页面
    POST /book/add         保存新增
    GET  /book/edit/<id>   跳转修改页面
    POST /book/edit/<id>   保存修改
    GET  /book/delete/<id> 删除指定图书
"""
import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for

import config
from service import book_info_service as service

logger = logging.getLogger(__name__)

book = Blueprint("book", __name__)


def _back_params(keyword, page):
    """查询条件回传参数：查看/新增/修改/删除后返回列表要保留查询条件与结果。"""
    params = {}
    if keyword:
        params["bookName"] = keyword
    if page and str(page) != "1":
        params["page"] = page
    return params


@book.route("/")
@book.route("/book/list")
def list_books():
    """图书信息列表：默认显示全部图书，按入库时间降序，每页五条，隔行变色。"""
    keyword = request.args.get("bookName", "")
    page = request.args.get("page", "1")

    result = service.listBooks(keyword, page)
    # 查询条件记忆：把本次条件回填输入框（试卷要求 2）
    return render_template(
        "list.html",
        result=result,
        keyword=keyword.strip(),
        page=result.page,
        active="list",
    )


@book.route("/book/view/<int:book_id>")
def view_book(book_id):
    """查看图书详细信息：所有显示字段只读不可写。"""
    info = service.getBook(book_id)
    if info is None:
        flash("该图书不存在或已被删除！", "error")
        return redirect(url_for("book.list_books",
                                **_back_params(request.args.get("bookName"),
                                               request.args.get("page"))))
    return render_template(
        "view.html",
        info=info,
        keyword=request.args.get("bookName", ""),
        page=request.args.get("page", "1"),
        active="view",
    )


@book.route("/book/add", methods=["GET"])
def add_page():
    """跳转新增图书页面。"""
    return render_template(
        "add.html",
        types=service.listBookTypes(),
        default_operator=config.DEFAULT_OPERATOR,
        default_time=_now_text(),
        keyword=request.args.get("bookName", ""),
        page=request.args.get("page", "1"),
        active="add",
    )


@book.route("/book/add", methods=["POST"])
def add_submit():
    """保存新增图书：无论成功失败都给出提示信息，确定后回到列表页。"""
    form = request.form.to_dict()
    back = _back_params(form.get("backKeyword"), form.get("backPage"))
    try:
        service.addBook(form)
        flash("新增成功！", "success")
    except Exception as exc:
        logger.warning("新增图书失败：%s", exc)
        flash("新增失败！%s" % ("（%s）" % exc if _detail_enabled() else ""), "error")
    return redirect(url_for("book.list_books", **back))


@book.route("/book/edit/<int:book_id>", methods=["GET"])
def edit_page(book_id):
    """跳转修改图书页面：「入库人」和「入库时间」为只读，不可修改。"""
    info = service.getBook(book_id)
    if info is None:
        flash("该图书不存在或已被删除！", "error")
        return redirect(url_for("book.list_books",
                                **_back_params(request.args.get("bookName"),
                                               request.args.get("page"))))
    return render_template(
        "edit.html",
        info=info,
        types=service.listBookTypes(),
        keyword=request.args.get("bookName", ""),
        page=request.args.get("page", "1"),
        active="edit",
    )


@book.route("/book/edit/<int:book_id>", methods=["POST"])
def edit_submit(book_id):
    """保存修改：无论成功失败都给出提示信息，确定后回到列表页。"""
    form = request.form.to_dict()
    back = _back_params(form.get("backKeyword"), form.get("backPage"))
    try:
        service.modifyBook(book_id, form)
        flash("修改成功！", "success")
    except Exception as exc:
        logger.warning("修改图书失败：%s", exc)
        flash("修改失败！%s" % ("（%s）" % exc if _detail_enabled() else ""), "error")
    return redirect(url_for("book.list_books", **back))


@book.route("/book/delete/<int:book_id>")
def delete_book(book_id):
    """删除图书：列表页弹出确认框确认后提交，回到列表页显示删除成功/失败。"""
    keyword = request.args.get("bookName", "")
    page = request.args.get("page", "1")
    back = _back_params(keyword, page)
    try:
        ok = service.removeBook(book_id)
        flash("删除成功！" if ok else "删除失败！", "success" if ok else "error")
    except Exception as exc:
        logger.warning("删除图书失败：%s", exc)
        flash("删除失败！", "error")
    # 删除后若当前页已空，交由 service 的越界保护自动回落
    return redirect(url_for("book.list_books", **back))


def _now_text():
    """入库时间默认值（当前时间）。"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def _detail_enabled():
    """是否在提示信息中附带失败原因（方便联调；正式演示保持试卷要求的短提示）。"""
    return request.args.get("detail") == "1"
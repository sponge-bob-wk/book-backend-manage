# -*- coding: utf-8 -*-
"""业务逻辑层（Service）：图书信息。"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime

import config
from dao import book_info_dao, book_type_dao
from models import BookInfo
from service.transaction import transactional

logger = logging.getLogger(__name__)


class PageResult(object):
    """分页查询结果。"""

    def __init__(self, rows, total, page, page_size):
        self.rows = rows
        self.total = total
        self.pageSize = page_size
        self.totalPages = max(1, (total + page_size - 1) // page_size)
        self.page = min(max(1, page), self.totalPages)

    @property
    def hasPrev(self):
        return self.page > 1

    @property
    def hasNext(self):
        return self.page < self.totalPages

    @property
    def pageNumbers(self):
        """页码序列（试卷图-1：上一页 ‹ 1 2 3 4 5 6 7 8 9 › 下一页）。

        总页数超过 9 页时只显示当前页附近的一窗口页码，避免分页条过长。
        """
        total = self.totalPages
        if total <= 9:
            return list(range(1, total + 1))
        start = max(1, min(self.page - 4, total - 8))
        return list(range(start, start + 9))


class BookInfoService(ABC):
    """图书信息 Service 接口（对应试卷第 7 步）。"""

    @abstractmethod
    def listBooks(self, keyword, page):
        """按图书名称模糊查询 + 分页（入库时间降序）。"""

    @abstractmethod
    def getBook(self, book_id):
        """查询单个图书。"""

    @abstractmethod
    def addBook(self, form):
        """新增图书，成功返回 True。"""

    @abstractmethod
    def modifyBook(self, book_id, form):
        """修改图书，成功返回 True。"""

    @abstractmethod
    def removeBook(self, book_id):
        """删除图书，成功返回 True。"""

    @abstractmethod
    def listBookTypes(self):
        """全部图书类型。"""


class BookInfoServiceImpl(BookInfoService):
    """图书信息 Service 实现类：持有 DAO 引用，事务由装饰器声明。"""

    def __init__(self, info_dao=None, type_dao=None):
        # 依赖注入，便于单元测试替换
        self.infoDao = info_dao or book_info_dao
        self.typeDao = type_dao or book_type_dao

    # ---------------- 查询 ----------------

    @transactional
    def listBooks(self, keyword, page):
        """图书列表：默认全部，按名称模糊查询，入库时间降序，每页 5 条。"""
        keyword = (keyword or "").strip()
        try:
            page = int(page or 1)
        except (TypeError, ValueError):
            page = 1
        page = max(1, page)

        rows, total = self.infoDao.findPage(keyword, page, config.PAGE_SIZE)
        result = PageResult(rows, total, page, config.PAGE_SIZE)
        # 页码越界时（例如删除后当前页空了）回落到最后一页重新取数
        if page > result.totalPages:
            rows, total = self.infoDao.findPage(keyword, result.totalPages, config.PAGE_SIZE)
            result = PageResult(rows, total, result.totalPages, config.PAGE_SIZE)
        return result

    @transactional
    def getBook(self, book_id):
        return self.infoDao.findById(book_id)

    @transactional
    def listBookTypes(self):
        return self.typeDao.findAll()

    # ---------------- 增删改 ----------------

    @transactional
    def addBook(self, form):
        """新增图书。

        试卷要求：
          * 图书编号/图书名称/图书类型/是否借阅/入库人/入库时间为必填；
          * 入库时间默认当前时间，入库人默认为当前登录用户（固定「系统管理员」），
            是否借阅默认未借阅。
        返回 True 表示成功；校验不通过抛 ValueError（由 controller 转为「新增失败！」）。
        """
        data = self._parse(form, for_update=False)
        book = BookInfo(**data)
        self.infoDao.insert(book)
        logger.info("新增图书成功：bookId=%s bookCode=%s", book.bookId, book.bookCode)
        return True

    @transactional
    def modifyBook(self, book_id, form):
        """修改图书；「入库人」和「入库时间」为只读，不参与更新。"""
        book = self.infoDao.findById(book_id)
        if book is None:
            raise ValueError("图书不存在：bookId=%s" % book_id)

        data = self._parse(form, for_update=True)
        book.bookCode = data["bookCode"]
        book.bookName = data["bookName"]
        book.bookType = data["bookType"]
        book.bookAuthor = data["bookAuthor"]
        book.publishPress = data["publishPress"]
        book.borrowed = data["borrowed"]
        book.publishDate = data["publishDate"]
        book.lastUpdatetime = datetime.now()        # 最新更新时间
        self.infoDao.update(book)
        logger.info("修改图书成功：bookId=%s", book_id)
        return True

    @transactional
    def removeBook(self, book_id):
        """删除图书，返回 True/False。"""
        affected = self.infoDao.deleteById(book_id)
        logger.info("删除图书：bookId=%s 受影响行数=%s", book_id, affected)
        return affected > 0

    # ---------------- 内部工具 ----------------

    def _parse(self, form, for_update):
        """把页面表单转成实体字段字典，并做必填校验。"""
        book_code = (form.get("bookCode") or "").strip()
        book_name = (form.get("bookName") or "").strip()
        type_text = (form.get("bookType") or "").strip()
        author = (form.get("bookAuthor") or "").strip()
        press = (form.get("publishPress") or "").strip()
        borrowed_text = (form.get("borrowed") or "").strip()
        created_by = (form.get("createdBy") or "").strip()
        creation_text = (form.get("creationTime") or "").strip()

        errors = []
        if not book_code:
            errors.append("图书编号不能为空")
        if not book_name:
            errors.append("图书名称不能为空")
        if not type_text:
            errors.append("图书类型不能为空")
        if borrowed_text not in ("0", "1"):
            errors.append("是否借阅不能为空")
        if not for_update:
            if not created_by:
                errors.append("入库人不能为空")
            if not creation_text:
                errors.append("入库时间不能为空")
        if errors:
            raise ValueError("；".join(errors))

        # 图书类型必须来源于 book_type 表
        try:
            type_id = int(type_text)
        except ValueError:
            raise ValueError("图书类型不合法")
        if self.typeDao.findById(type_id) is None:
            raise ValueError("图书类型不存在：id=%s" % type_text)

        # 入库时间：新增时为空则取当前时间；修改时为只读字段，缺省沿用原值
        creation_time = None
        if creation_text:
            creation_time = self._parse_datetime(creation_text)
        publish_text = (form.get("publishDate") or "").strip()
        publish_date = self._parse_date(publish_text) if publish_text else None

        return {
            "bookCode": book_code,
            "bookName": book_name,
            "bookType": type_id,
            "bookAuthor": author,
            "publishPress": press,
            "publishDate": publish_date or (creation_time.date() if creation_time
                                            else datetime.now().date()),
            "borrowed": int(borrowed_text) if borrowed_text in ("0", "1") else config.BORROWED_NO,
            "createdBy": created_by or config.DEFAULT_OPERATOR,
            "creationTime": creation_time or datetime.now(),
        }

    @staticmethod
    def _parse_datetime(text):
        """支持 yyyy-MM-dd 与 yyyy-MM-dd HH:mm:ss 两种页面输入。"""
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", config.DATE_FORMAT):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        raise ValueError("日期格式不正确：%s" % text)

    @staticmethod
    def _parse_date(text):
        return BookInfoServiceImpl._parse_datetime(text).date()
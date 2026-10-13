# 图书借阅系统（后台管理）BookBackendManage

> 2016 年 10 月学士后 JAVA 毕业考试机试试卷-2 ·「图书借阅系统(后台)」的实现。
> 试卷规定的语言是 Java（Struts2/SpringMVC + Spring + Hibernate/MyBatis），
> 本工程按题目要求改用 **Python** 实现，功能点、数据库结构、页面效果与试卷图-1 ~ 图-9 一一对应。

技术栈：**Python 3 + Flask + SQLAlchemy + MySQL（未安装 MySQL 时自动回退 SQLite）+ Jinja2 + jQuery 1.8.3**

---

## 一、功能清单（对照试卷「二、功能要求」）

| 编号 | 功能 | 实现说明 |
| --- | --- | --- |
| 1 | 查看所有图书信息 | 首页/列表页默认显示全部图书，按入库时间 `creationTime` **降序**；日期显示为「年-月-日」；列表**隔行变色**；**分页每页 5 条** |
| 2 | 查询图书 | 按图书名称**模糊查询**（`like %关键词%`），结果仍按入库时间降序；输入框**记忆**上次查询条件 |
| 3 | 查看图书详细信息 | 「查看」链接进入只读详情页，字段：图书编号/图书名称/图书类型/作者/出版社/是否借阅/入库人/入库时间；「返回」回列表并**保留查询条件与结果** |
| 4 | 新增图书 | 「新增」进入新增页；类型下拉数据**来源于 book_type 表**；入库时间默认当前时间、入库人默认「系统管理员」、是否借阅默认未借阅；**必填项 jQuery 校验**；成功/失败均提示，确定后回列表 |
| 5 | 修改图书 | 「修改」进入编辑页；**入库人、入库时间为只读不可改**；必填项校验；成功/失败均提示，确定后回列表 |
| 6 | 删除图书 | 「删除」先弹确认框「确定删除该图书信息？」，确认后提交服务器删除，回到列表并提示「删除成功/删除失败」 |

## 二、技术架构（对照试卷「四、具体要求及推荐实现步骤」）

```
BookBackendManage/
├── app.py                          入口：装配控制器 + 初始化数据库（等价 web.xml + Spring 容器）
├── config.py                       配置：数据库连接、每页条数、日期格式、默认入库人
├── models/                         【第 5 步】持久化类（实体 + 映射）
│   ├── base.py                     引擎 / Session 工厂 / 声明式基类
│   ├── book_info.py                BookInfo  → 表 book_info
│   └── book_type.py                BookType  → 表 book_type
├── dao/                            【第 6 步】数据访问层 DAO 接口及其实现类
│   ├── book_info_dao.py            BookInfoDao / BookInfoDaoImpl
│   └── book_type_dao.py            BookTypeDao / BookTypeDaoImpl
├── service/                        【第 7、9 步】业务层 Service 接口及其实现类 + 声明式事务
│   ├── transaction.py              @transactional 声明式事务装饰器
│   └── book_info_service.py        BookInfoService / BookInfoServiceImpl（持有 DAO 引用）
├── controller/                     【第 8 步】控制器（持有 Service 引用，负责导航与提示信息）
│   └── book_controller.py          图书列表/查询/查看/新增/修改/删除
├── templates/                      页面：list / view / add / edit
├── static/                         css + js（jQuery 1.8.3 本地副本）
├── db/
│   ├── book_borrow.sql             【第 15 步】MySQL 建库建表 + 主键自增 + 测试数据脚本
│   └── seed_data.py                SQLite 回退库的测试数据（与 SQL 脚本内容一致）
├── tests/test_regression.py        回归测试（列表/查询/查看/新增/修改/删除/分页/校验）
└── .github/workflows/regression.yml  GitHub Actions 回归测试
```

分层调用关系：`Controller → Service（@transactional）→ DAO → ORM → 数据库`。

事务按试卷第 9 步要求以**声明式**方式实现：业务代码里没有一行 `commit()`，
事务边界全部由 `service/transaction.py` 的 `@transactional` 装饰器统一开启/提交/回滚。

## 三、快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库（二选一）
#    方式 A：MySQL —— 导入 SQL 脚本（建库、建表、测试数据）
mysql -uroot -p < db/book_borrow.sql
#    方式 B：不装 MySQL —— 直接运行，程序自动创建 SQLite 库 db/book_borrow.db 并灌入测试数据

# 3. 启动（默认 http://127.0.0.1:5000/）
python app.py
```

数据库连接参数可用环境变量覆盖，无需改代码：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MYSQL_HOST` / `MYSQL_PORT` | `127.0.0.1` / `3306` | MySQL 地址 |
| `MYSQL_USER` / `MYSQL_PASSWORD` | `root` / `root` | MySQL 账号 |
| `MYSQL_DB` | `book_borrow` | 库名 |
| `DB_URL` | 空 | 直接指定 SQLAlchemy 连接串，优先级最高 |

> 说明：`config.DB_URL` 默认指向 MySQL；若本机没有 MySQL 服务，程序在启动时会主动探活失败并
> **自动回退到 SQLite 单文件库**（打印一条警告），保证页面可以直接演示，不影响 MySQL 上的正式运行。

## 四、页面路由

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/`、`/book/list` | 图书列表（`?bookName=关键词&page=页码`） |
| GET | `/book/view/<bookId>` | 查看图书（只读） |
| GET / POST | `/book/add` | 新增页面 / 保存新增 |
| GET / POST | `/book/edit/<bookId>` | 修改页面 / 保存修改 |
| GET | `/book/delete/<bookId>` | 删除图书 |

查看/新增/修改/返回都会带回 `bookName`、`page` 参数，保证**返回列表时保留查询条件与查询结果**。

## 五、数据库设计（对照试卷「三、数据库设计」）

### book_info 图书信息表

| 字段 | 说明 | 类型 | 约束 |
| --- | --- | --- | --- |
| bookId | 图书ID | int | 主键，自动增长 |
| bookCode | 图书编号 | varchar(30) | 非空 |
| bookName | 图书名称 | varchar(100) | 非空，模糊查询字段 |
| bookType | 图书类型 | int | 非空，外键 → `book_type.id` |
| bookAuthor | 图书作者 | varchar(100) | 非空 |
| publishPress | 出版社 | varchar(100) | 非空 |
| publishDate | 出版日期 | date | 非空 |
| borrowed | 是否借阅 | int | 非空，1 已借阅 / 0 未借阅 |
| createdBy | 创建人（入库人） | varchar(50) | 非空 |
| creationTime | 创建时间（入库时间） | datetime | 非空，列表排序字段 |
| lastUpdatetime | 最新更新时间 | datetime | 可空，修改时更新 |

### book_type 图书类型表

| 字段 | 说明 | 类型 | 约束 |
| --- | --- | --- | --- |
| id | id | int | 主键，自动增长 |
| typeName | 图书类型名称 | varchar(50) | 非空 |

测试数据：`book_type` 8 条（小说、文学、传记、艺术、少儿、经济、管理、科技），
`book_info` 12 条（含试卷图-1 中的 BK000023 ~ BK000027），每表均满足「至少 5 条」的要求。

**与试卷的两处说明（已在代码注释中标明）：**

1. 试卷字段表中 `bookAuthor` 的「类型」列写作**整数**，但界面示例取值为「金庸」「（英）Martin Fowler」
   等字符串，判为试卷笔误，本工程按 **varchar** 建表。
2. 试卷的 `book_info` 要求 `publishDate`（出版日期）非空，但新增页（图-4）与查看页（图-3）
   都没有该字段，故新增时 `publishDate` 缺省取入库时间当天（表单中仍可显式传入）。

## 六、测试

```bash
pytest -v tests/
```

覆盖：列表默认排序与分页、页面关键元素（表头/日期格式/隔行变色样式/分页条）、
模糊查询与条件记忆、查看页只读与返回保留条件、新增默认值与必填校验、
修改时入库人/入库时间只读、删除成功/失败提示、页码越界回落、SQL 脚本完整性。

`.github/workflows/regression.yml` 会在 push / PR 时于 Python 3.10、3.12 上自动执行同一套回归测试，
并额外做一次「启动应用 + 访问首页」的冒烟测试。

## 七、注意事项（对照试卷「五、注意事项」）

* 界面：列表、查看、新增、修改四处页面均按图-1 ~ 图-9 的布局复原，控件对齐、隔行变色、提示信息齐全。
* 代码：分层清晰、命名规范（实体/DAO/Service/Controller 与试卷要求同名），关键位置均有中文注释。
* 异常处理：DAO 不吞异常，Service 的事务在异常时回滚，Controller 捕获后统一转换为
  「新增失败！」「修改失败！」「删除失败！」提示信息，保证任何失败路径都有反馈。
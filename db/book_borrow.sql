-- =====================================================================
--  图书借阅系统（后台）——数据库脚本
--  数据库：MySQL 5.x / 8.x        字符集：utf8mb4
--  对应试卷「三、数据库设计」与「四、具体要求」第 1、15 步
--
--  内容：
--    1. 创建数据库 book_borrow
--    2. 创建图书类型表 book_type   （主键 id       自动增长）
--    3. 创建图书信息表 book_info   （主键 bookId   自动增长，外键 bookType）
--    4. 插入测试数据（每表均 ≥ 5 条）
--
--  导入方式： mysql -uroot -p < book_borrow.sql
-- =====================================================================

DROP DATABASE IF EXISTS `book_borrow`;
CREATE DATABASE `book_borrow` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `book_borrow`;

-- ---------------------------------------------------------------------
-- 表 1：图书类型表
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `book_type`;
CREATE TABLE `book_type` (
  `id`        INT          NOT NULL AUTO_INCREMENT COMMENT 'id',
  `typeName`  VARCHAR(50)  NOT NULL                COMMENT '图书类型名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书类型表';

-- ---------------------------------------------------------------------
-- 表 2：图书信息表
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `book_info`;
CREATE TABLE `book_info` (
  `bookId`          INT          NOT NULL AUTO_INCREMENT COMMENT '图书ID',
  `bookCode`        VARCHAR(30)  NOT NULL                COMMENT '图书编号',
  `bookName`        VARCHAR(100) NOT NULL                COMMENT '图书名称',
  `bookType`        INT          NOT NULL                COMMENT '图书类型（book_type.id）',
  `bookAuthor`      VARCHAR(100) NOT NULL                COMMENT '图书作者',
  `publishPress`    VARCHAR(100) NOT NULL                COMMENT '出版社',
  `publishDate`     DATE         NOT NULL                COMMENT '出版日期',
  `borrowed`        INT          NOT NULL DEFAULT 0      COMMENT '是否借阅：1 已借阅 / 0 未借阅',
  `createdBy`       VARCHAR(50)  NOT NULL                COMMENT '创建人（入库人）',
  `creationTime`    DATETIME     NOT NULL                COMMENT '创建时间（入库时间）',
  `lastUpdatetime`  DATETIME     DEFAULT NULL            COMMENT '最新更新时间',
  PRIMARY KEY (`bookId`),
  KEY `idx_book_name` (`bookName`),
  KEY `idx_creation_time` (`creationTime`),
  CONSTRAINT `fk_book_info_type` FOREIGN KEY (`bookType`) REFERENCES `book_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书信息表';

-- ---------------------------------------------------------------------
-- 测试数据：图书类型表（试卷列举的 8 个类型）
-- ---------------------------------------------------------------------
INSERT INTO `book_type` (`id`, `typeName`) VALUES
  (1, '小说'),
  (2, '文学'),
  (3, '传记'),
  (4, '艺术'),
  (5, '少儿'),
  (6, '经济'),
  (7, '管理'),
  (8, '科技');

-- ---------------------------------------------------------------------
-- 测试数据：图书信息表
-- ---------------------------------------------------------------------
INSERT INTO `book_info`
  (`bookId`, `bookCode`, `bookName`, `bookType`, `bookAuthor`, `publishPress`,
   `publishDate`, `borrowed`, `createdBy`, `creationTime`, `lastUpdatetime`)
VALUES
  (1,  'BK000023', '企业应用架构模式',     8, '（英）Martin Fowler',   '机械工业出版社',       '2014-06-20', 0, '系统管理员', '2014-07-03 09:30:00', NULL),
  (2,  'BK000024', '精通Hibernate',        8, '刘洋',                  '电子工业出版社',       '2014-04-18', 1, '系统管理员', '2014-05-03 14:05:00', NULL),
  (3,  'BK000025', '天龙八部',             1, '金庸',                  '中原出版社',           '2014-02-28', 0, '系统管理员', '2014-03-12 10:15:00', NULL),
  (4,  'BK000026', '寻找家园',             4, '高尔泰',                '北京十月文艺出版社',   '2014-02-10', 0, '系统管理员', '2014-03-01 16:40:00', NULL),
  (5,  'BK000027', '小猫莫格成长系列',     5, '（英）朱迪斯·克尔',     '接力出版社',           '2013-12-01', 1, '系统管理员', '2014-01-01 11:00:00', NULL),
  (6,  'BK000028', '三国演义',             1, '罗贯中',                '人民文学出版社',       '2013-11-05', 0, '系统管理员', '2013-12-18 09:00:00', NULL),
  (7,  'BK000029', '活着',                 1, '余华',                  '作家出版社',           '2013-10-12', 1, '系统管理员', '2013-11-26 15:20:00', NULL),
  (8,  'BK000030', '经济学原理',           6, '（美）曼昆',            '北京大学出版社',       '2013-09-08', 0, '系统管理员', '2013-10-30 08:45:00', NULL),
  (9,  'BK000031', '管理学',               7, '周三多',                '高等教育出版社',       '2013-08-15', 0, '系统管理员', '2013-09-21 13:10:00', NULL),
  (10, 'BK000032', '苏东坡传',             3, '林语堂',                '湖南文艺出版社',       '2013-07-03', 1, '系统管理员', '2013-08-14 17:25:00', NULL),
  (11, 'BK000033', '文学回忆录',           2, '木心',                  '广西师范大学出版社',   '2013-06-09', 0, '系统管理员', '2013-07-07 10:50:00', NULL),
  (12, 'BK000034', '深入理解计算机系统',   8, '（美）Randal E. Bryant', '机械工业出版社',      '2013-05-21', 0, '系统管理员', '2013-06-02 09:05:00', NULL);

-- ---------------------------------------------------------------------
-- 校验
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS type_rows FROM `book_type`;
SELECT COUNT(*) AS book_rows FROM `book_info`;
SELECT b.bookId, b.bookCode, b.bookName, t.typeName, b.bookAuthor,
       b.creationTime, b.borrowed
  FROM `book_info` b JOIN `book_type` t ON b.bookType = t.id
 ORDER BY b.creationTime DESC
 LIMIT 5;
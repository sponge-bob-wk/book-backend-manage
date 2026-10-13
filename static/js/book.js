# -*- coding: utf-8 -*-
"""页面脚本：jQuery 必填项验证、删除确认、操作提示信息、分页跳转。

对应试卷要求：
    12.C 页面中的必填项需要使用 jQuery 做验证
    13.C 修改页面必填项验证（入库人/入库时间只读不可改）
    14.A 删除前弹出确认删除信息的提示
    图-5/7/9 操作成功或失败给出提示信息
"""
$(function () {

    /* ---------------- 操作提示信息（图-5 / 图-7 / 图-9） ---------------- */
    var $flash = $('#flashBox');
    if ($flash.length) {
        var msg = $flash.attr('data-message');
        if (msg) {
            alert(msg);
        }
    }

    /* ---------------- 新增 / 修改页面：jQuery 必填项验证 ---------------- */
    var $form = $('#bookForm');
    if ($form.length) {
        $form.submit(function () {
            var errors = [];
            // 图书编号、图书名称、图书类型、是否借阅为必填（入库人/入库时间在新增页也必填）
            var required = [
                {id: 'bookCode', label: '图书编号'},
                {id: 'bookName', label: '图书名称'},
                {id: 'bookType', label: '图书类型'},
                {id: 'borrowed', label: '是否借阅'}
            ];
            if ($('#createdBy').length) {
                required.push({id: 'createdBy', label: '入库人'});
                required.push({id: 'creationTime', label: '入库时间'});
            }

            $.each(required, function (i, item) {
                var val = $.trim($('#' + item.id).val() || '');
                if (val === '') {
                    errors.push(item.label + '不能为空！');
                }
            });

            // 入库时间格式校验（yyyy-MM-dd）
            var dt = $.trim($('#creationTime').val() || '');
            if (dt !== '' && !/^\d{4}-\d{2}-\d{2}$/.test(dt)) {
                errors.push('入库时间格式应为「年-月-日」！');
            }

            if (errors.length) {
                alert(errors.join('\n'));
                return false;     // 阻止提交
            }
            return true;
        });
    }

    /* ---------------- 列表页：删除前确认（图-8） ---------------- */
    $('#bookTable a.del').click(function () {
        var name = $(this).attr('data-name') || '';
        return confirm('确定删除该图书信息？' + (name ? '\n（' + name + '）' : ''));
    });

    /* ---------------- 列表页：分页跳转 ---------------- */
    $('#jumpBtn').click(function () {
        var ctx = $('#pageCtx');
        var total = parseInt(ctx.attr('data-total'), 10) || 1;
        var base = ctx.attr('data-base') || '';
        var target = parseInt($.trim($('#jumpPage').val()), 10);

        if (isNaN(target) || target < 1 || target > total) {
            alert('请输入 1 - ' + total + ' 之间的页码！');
            return;
        }
        window.location.href = base + (base.indexOf('?') >= 0 ? '&' : '?') + 'page=' + target;
    });

    // 回车即跳转
    $('#jumpPage').keydown(function (e) {
        if (e.which === 13) {
            $('#jumpBtn').click();
            return false;
        }
    });
});
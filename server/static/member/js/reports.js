
var $table = $('#table1')

$(function() {

  $table.bootstrapTable({
    striped: true,                      //是否显示行间隔色
    cache: false,   //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
    pagination: true,   //是否显示分页（*）
    pageNumber:1,   //初始化加载第一页，默认第一页
    pageSize: 10,   //每页的记录行数（*）
    pageList: [10, 20, 30, 40, 50, 60, 70, 80, 90], //可供选择的每页的行数（*）
    paginationParts: ['pageList', 'pageInfoShort', 'pageSize'],
    paginationHAlign: "right",
    paginationDetailHAlign: "left",
    smartDisplay: false,
    paginationShowPageGo: false,
    sortable: true,   //是否启用排序
    sortOrder: "asc",   //排序方式
    clickToSelect: false,  //是否启用点击选中行
    uniqueId: "at_id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'at_id', title: 'ID', sortable: true}, 
              {field: 'nick_name', title: '暱稱', sortable: true}, 
              {field: 'gold_total', title: '金幣', sortable: true}, 
              {field: 'phone_number', title: '手機號碼', sortable: true},
              {field: 'register_mac_addr', title: 'MAC位址', sortable: true}, 
              {field: 'bind_player_name', title: '推薦人', class: 'text-blue'},                
              {field: 'total_run', title: '歷史場數', sortable: true},
              {field: 'average_run', title: '日平均場', sortable: true}, 
              {field: 'score', title: '正負分', sortable: true}, 
              {field: 'last_login_date', title: '最後登入時間', sortable: true},
              {field: 'created_date', title: '註冊時間', sortable: true}, 
              {field: 'permission', title: '狀態', sortable: true}]

  })

})

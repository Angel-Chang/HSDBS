
var $table1 = $('#table1')
var $table2 = $('#table2')
var $table3 = $('#table3')
var $table4 = $('#table4')
var $table5 = $('#table5')
var $table6 = $('#table6')

$(function() {
  // 登入紀錄
  $table1.bootstrapTable({
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
    uniqueId: "id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'id', title: 'ID', visible: false}, 
              {field: 'login_ip', title: '登入IP', sortable: true}, 
              {field: 'created_date', title: '登入時間', sortable: true}]
  })
  // 轉幣紀錄 
  $table2.bootstrapTable({
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
    uniqueId: "id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'id', title: 'ID', visible: false}, 
              {field: 'jewel', title: '貨幣種類', sortable: true}, 
              {field: 'sender_id', title: '贈送人ID', visible: false}, 
              {field: 'sender', title: '贈送人', sortable: true, formatter: senderFormatter}, 
              {field: 'sender_gold', title: '贈送人金幣', visible: false}, 
              {field: 'receiver_id', title: '接收人ID', visible: false}, 
              {field: 'receiver', title: '接收人', sortable: true, formatter: receiverFormatter}, 
              {field: 'receiver_gold', title: '接收人金幣', visible: false} , 
              {field: 'amount', title: '轉幣額', sortable: true, formatter: goldFormatter}, 
              {field: 'created_date', title: '時間', sortable: true}]
  })

  function senderFormatter(value, row, index) {
    return ['<span>' + value + '(@' + row.sender_id + ')<br>',
            '' + row.sender_gold +'</span>'].join('');
  }

  function receiverFormatter(value, row, index) {
    return ['<span>' + value + '(@' + row.receiver_id + ')<br>',
            '' + row.receiver_gold +'</span>'].join('');
  }

  // 補幣紀錄 
  $table3.bootstrapTable({
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
    uniqueId: "id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'id', title: 'ID', visible: false}, 
              {field: 'jewel', title: '貨幣種類', sortable: true}, 
              {field: 'admin_account', title: '補幣者', sortable: true}, 
              {field: 'gold', title: '補幣金額', sortable: true, formatter: goldFormatter}, 
              {field: 'description', title: '補幣事由', sortable: true}, 
              {field: 'created_date', title: '時間', sortable: true}]
  })
  function goldFormatter(value, row, index) {
    return '<span>$' + value + '</span>';
  }
  // 金流異動 
  $table4.bootstrapTable({
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
    sortable: false,   //是否启用排序
    sortOrder: "asc",   //排序方式
    clickToSelect: false,  //是否启用点击选中行
    uniqueId: "id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'id', title: 'ID', visible: false}, 
              {field: 'tradetype', title: '異動管道'}, 
              {field: 'amount', title: '異動金額'},
              {field: 'goldflow', title: '金流異動'}, 
              {field: 'created_date', title: '時間'}]
  })
  // 歷史場次
  $table5.bootstrapTable({
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
    sortable: false,   //是否启用排序
    sortOrder: "asc",   //排序方式
    clickToSelect: false,  //是否启用点击选中行
    uniqueId: "run_id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'gametype', title: '遊戲類型', formatter: gametypeFormatter}, 
              {field: 'run_id', title: '遊戲局號'}, 
              {field: 'area', title: '區域'}, 
              {field: 'created_date', title: '日期'}, 
              // {field: 'detail', title: '詳細', formatter: detailFormatter},
              {field: 'state', title: '狀態'}, 
              {field: 'all_bonus', title: '總抽水'}]
  })
  function gametypeFormatter(value, row, index) {
    return '<p>四人麻將(底：<span class="text-danger">' + value + '</span>)</p>';
  }

  // 鑽石紀錄
  $table6.bootstrapTable({
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
    sortable: false,   //是否启用排序
    sortOrder: "asc",   //排序方式
    clickToSelect: false,  //是否启用点击选中行
    uniqueId: "id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'id', title: 'ID', visible: false}, 
              {field: 'star_type', title: '類別'}, 
              {field: 'star', title: '異動鑽石數量'}, 
              {field: 'starflow', title: '鑽石流異動'},              
              {field: 'created_date', title: '時間'}]
  })

  $("#btnQuery").on("click", function() {
    var startTime1 = $("#startTime1").val();
    var endTime1 = $("#endTime1").val();
    var para = {'startTime1':startTime1, 
                'endTime1':endTime1}
    var url = "/member/player1"

    $.ajax({
      type: 'GET',
      url: url, 
      data: para,
      dataType: 'json',
      success: function(data_get){
        var rs1 = data_get['rs1'];
        var rs2 = data_get['rs2'];
        var rs3 = data_get['rs3'];
        var rs4 = data_get['rs4'];
        var rs5 = data_get['rs5'];
        var rs6 = data_get['rs6'];
        
        $table1.bootstrapTable('load',rs1);
        $table1.bootstrapTable('refresh');
        $table2.bootstrapTable('load',rs2);
        $table2.bootstrapTable('refresh');
        $table3.bootstrapTable('load',rs3);
        $table3.bootstrapTable('refresh');
        $table4.bootstrapTable('load',rs4);
        $table4.bootstrapTable('refresh');
        $table5.bootstrapTable('load',rs5);
        $table5.bootstrapTable('refresh');
        $table6.bootstrapTable('load',rs6);
        $table6.bootstrapTable('refresh');
      }
    })
  })

})

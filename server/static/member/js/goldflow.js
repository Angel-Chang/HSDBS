
var $table1 = $('#table1')
var $table2 = $('#table2')
var $table3 = $('#table3')
var $table4 = $('#table4')
var $table5 = $('#table5')

$(function() {
  // 發行紀錄
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
              {field: 'amount', title: '發行金額', sortable: true}, 
              {field: 'admin_userid', title: '發行人', sortable: true}, 
              {field: 'created_date', title: '發行時間', sortable: true}]
  })
  // 補幣紀錄 
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
              {field: 'admin_account', title: '補幣者', sortable: true}, 
              {field: 'player', title: '補幣對象', sortable: true}, 
              {field: 'gold', title: '補幣金額', sortable: true, formatter: goldFormatter }, 
              {field: 'description', title: '補幣事由', sortable: true}, 
              {field: 'created_date', title: '時間', sortable: true}]
  })
  function goldFormatter(value, row, index) {
    return '<span>$' + value + '</span>';
  }
  // 轉幣紀錄 
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
  // 玩家入金紀錄 
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
              {field: 'player', title: '玩家', sortable: true}, 
              {field: 'admin_account', title: '操作者', sortable: true}, 
              {field: 'gold', title: '金額', sortable: true, formatter: goldFormatter }, 
              {field: 'created_date', title: '時間', sortable: true}]
  })

  // 鑽石紀錄
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
    uniqueId: "id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'id', title: 'ID', visible: false}, 
              {field: 'star_type', title: '類別'}, 
              {field: 'player_id', title: '玩家ID'}, 
              {field: 'player', title: '玩家名稱'}, 
              {field: 'star', title: '異動鑽石數量'}, 
              {field: 'created_date', title: '時間'}]
  })

  $("#btnQuery").on("click", function() {
    var startTime1 = $("#startTime1").val();
    var endTime1 = $("#endTime1").val();
    var para = {'startTime1':startTime1, 'endTime1':endTime1}
    var url = "/member/goldflow"

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
        $("#total_amount").html(data_get['total_amount']);
        $("#available_amount").html(data_get['available_amount']);
        $("#flow_amount").html(data_get['flow_amount']);
        $("#star_amount").html(data_get['star_amount']);
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
      }
    })
  })

  $('#addGold').on('show.bs.modal', function (event) {
    var modal = $(this);
    modal.find('.clear').val('');
    $('#addGold').modal();
  })

  // 儲存發行金幣資料
  $("#btnSave").on('click', function() {
    var amount = $("#amount").val();
    var user_pwd = $("#user_pwd").val();
    // to do : 檢查欄位是否有缺
    if (amount == '') {
      alert("請輸入金幣數量!!");
    } else {
      // 檢查玩家ID格式
      if(!/^[0-9]+$/.test(amount)) {
        alert("金幣只能輸入數字!!");
      } else {
        if (user_pwd == '') {
          alert("請輸入密碼!!");
        } else {
            // call ajax 傳送資料
            var url = "/member/addGold/";
            var token = $('input[name=csrfmiddlewaretoken]').val();    
            var para = {
              'csrfmiddlewaretoken':token,
              'amount':amount,
              'user_pwd':user_pwd};
        
            $.ajax({
              url: url, 
              data: para,
              type: 'POST',
              dataType: 'json',
              success: function(data_get){
                var msg = data_get['msg']
                alert(msg);
              },
              error: function (data_get) {
                var msg = data_get['msg']
                alert(msg);
              }
            });
          }
      }
    }
  })
})

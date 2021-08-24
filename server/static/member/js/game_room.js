var $table = $('#table1')
var $table_detail = $('#table2')

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
    sortable: false,   //是否启用排序
    sortOrder: "asc",   //排序方式
    clickToSelect: false,  //是否启用点击选中行
    uniqueId: "id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'id', title: 'ID', visible: false}, 
              {field: 'room', title: '房號'}, 
              {field: 'area', title: '區域'}, 
              {field: 'created_date', title: '日期'}, 
              {field: 'detail', title: '詳細', formatter: actionFormatter}, 
              {field: 'state', title: '狀態', formatter: stateFormatter}, 
              {field: 'total_commission', title: '總抽水'}] 
  })

  function actionFormatter(value, row, index) {
      return [
        '<button type="button" class="showdetail btn btn-sm" style="background-color:#FFBE00" ',
        'data-id=' + row.id , 
        ' ">詳細</button>'
      ].join('');
  }

  function stateFormatter(value, row, index) {
    if (value == '進行中') {
      return '<span class="text-danger">進行中</span>';
    } else {
      return value;
    }
  }

  $("#btnQuery").on('click', function() {
    var room = $("#room").val();
    var startTime1 = $("#startTime1").val();
    var endTime1 = $("#endTime1").val();
    var para = {'room':room, 
                'startTime1':startTime1, 
                'endTime1':endTime1}
    var url = "/member/game_room"

    $.ajax({
      type: 'GET',
      url: url, 
      data: para,
      dataType: 'json',
      success: function(data_get){
        var rs1 = data_get['rs1'];
        $table.bootstrapTable('load',rs1);
        $table.bootstrapTable('refresh');
      }
    })
  })
  // show detail
  //$('.showdetail').on('click', function() {
  $('#table1 tbody').on('click','tr td .showdetail', function() {   
    var button = $(this);
    var room_id = button.data('id');
    if (room_id !='') {
      var url = "/member/gameroom_detail?room_id="+room_id;
      location.href = url;
    }
  })

  $('#detail').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var modal = $(this);

    // 取得那一行的資料
    var idx = button.data('id');
    var rowdata = $table.bootstrapTable('getRowByUniqueId', idx);
    var create_date = rowdata.created_date;
    var room = rowdata.room;
    var state = rowdata.state;

    modal.find('#uid').val(idx);
    $("#create_date").html(create_date);
    $("#room").html(room);
    if (state == '進行中') {
      $("#state").html("<span class='text-danger'>進行中</span>");
    } else {
      $("#state").html(state);
    }
    modal.find('.modal-body input').val(check_date)
    var url = "/member/gameroom_detail"
    modal.find("#detailform").attr("action", url)

    $.ajax({
      type: 'GET',
      url: url, 
      data: para,
      dataType: 'json',
      success: function(data_get){
        var rs2 = data_get['rs2'];
        $table_detail.bootstrapTable('destroy');
        $table_detail.bootstrapTable({
          data: rs2,  //请求后台的URL（*）
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
          uniqueId: "chk_hour",   //每一行的唯一标识，一般为主键列
          classes:"table table-hover table-sm table-bordered text-center table-striped",
          theadClasses: "thead-dark",
          columns: [{field: 'online_count', title: '上線人數', sortable: true}, 
                    {field: 'bonus', title: '抽水金額', sortable: true},
                    {field: 'chk_hour', title: '時間', sortable: true}]
        })
      }
    })

    // $('#detail').modal();
  })
})

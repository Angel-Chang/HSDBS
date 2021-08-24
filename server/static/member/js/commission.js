
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
    sortable: true,   //是否启用排序
    sortOrder: "asc",   //排序方式
    clickToSelect: false,  //是否启用点击选中行
    uniqueId: "chk_date",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'chk_date', title: '日期', sortable: true}, 
              {field: 'bonus', title: '抽水金額', sortable: true}, 
              {field: 'game_count', title: '遊戲場數', sortable: true}, 
              {field: 'online_count', title: '上線人數', sortable: true}, 
              {field: 'action', title: '當日紀錄', formatter: actionFormatter}]
  })

  function actionFormatter(value, row, index) {
    return [
      '<button type="button" class="query btn btn-sm btn-primary" ',
      'data-toggle="modal" data-target="#detail" data-chkdate=' + value , 
      ' οnclick="getdetail(this)">查詢</button>'
    ].join('');

  }

  $("#get_db_data").on("click", function() {
    var checkMonth = $("#checkMonth").val();
    var para = {'checkMonth':checkMonth}
    var url = "/member/bonus_list"

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

  // Show check date's every hour records
  $('#detail').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var check_date = button.data('chkdate') // Extract info from data-* attributes
    var para = {'check_date':check_date}

    var modal = $(this)
    modal.find('.modal-body input').val(check_date)
    var url = "/member/bonus_detail"
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
    
  })
})

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
    sortable: false,   //是否启用排序
    sortOrder: "asc",   //排序方式
    clickToSelect: false,  //是否启用点击选中行
    uniqueId: "rank",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'rank', title: '名次'}, 
              {field: 'playerName', title: '玩家名稱'}, 
              {field: 'playerID', title: 'ID'}, 
              {field: 'gold', title: '金幣'}, 
              {field: 'score', title: '正負分'}, 
              {field: 'playCount', title: '次數'}]
  })

  $("#btnQuery").on('click', function() {
    var orderby = $("#orderby").val();
    var base = $("#base").val();
    var daterange = $("#daterange").val();

    var para = {'orderby': orderby,
                'base': base,
                'daterange': daterange}
    var url = "/member/leaderboard"

    $.ajax({
      type: 'GET',
      url: url, 
      data: para,
      dataType: 'json',
      success: function(data_get){
        var rs1 = data_get['rs1'];
        $table.bootstrapTable('load',rs1);
        $table.bootstrapTable('refresh');
      },
      error: function () {
        $table.bootstrapTable('destroy');
        alert('查詢異常，請通知工程師處理。')
      }
    })
  })

})

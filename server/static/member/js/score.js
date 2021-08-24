var $table = $('#table1')
var $player = $('#player')
var $player_name = $('#player_name')

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
              {field: 'score_type', title: '戰績總計'}, 
              {field: 'day_count', title: '日計'}, 
              {field: 'week_count', title: '週計'}, 
              {field: 'month_count', title: '月計'}]
  })

  $("#btnQuery").on('click', function() {
    var player = $("#player").val();
    if (player == '') {
      alert('請輸入玩家ID！')
    } else {
      if(!/^[0-9]+$/.test(player)) {
        alert('玩家ID格式錯誤，請重新輸入！')
      } else  {
        var para = {'player':player}
        var url = "/member/show_score"
    
        $.ajax({
          type: 'GET',
          url: url, 
          data: para,
          dataType: 'json',
          success: function(data_get){
            var player_name = data_get['player_name']
            document.getElementById("player_name").innerHTML= player_name;
            var rs1 = data_get['rs1'];
            $table.bootstrapTable('load',rs1);
            $table.bootstrapTable('refresh');
          },
          error: function () {
            $table.bootstrapTable('destroy');
            document.getElementById("player_name").innerHTML= "";
            alert('查詢異常，請通知工程師處理。')
          }
        })
      }
    }
  })

})

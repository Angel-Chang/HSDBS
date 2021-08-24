
var $table1 = $('#table1')

$(function() {
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
    columns: [{field: 'id', title: 'ID', formatter: idFormatter}, 
              {field: 'nick_name', title: '暱稱'}, 
              {field: 'gold', title: '金幣'}, 
              {field: 'star', title: '鑽石'}, 
              {field: 'phone_number', title: '手機號碼'}, 
              {field: 'register_mac_addr', title: 'MAC位址'}, 
              {field: 'bind_playerid', title: '推薦人ID', visible: false}, 
              {field: 'bind_playername', title: '推薦人', class: 'text-blue'},  
              {field: 'history_game_runs', title: '歷史場數'}, 
              {field: 'score', title: '正負分', formatter: scoreFormatter}, 
              {field: 'last_login_date', title: '最後登入時間'}, 
              {field: 'created_date', title: '註冊時間'}, 
              {field: 'player_type', title: '會員身份ID', visible: false}, 
              {field: 'permission_type', title: '會員身份', visible: false}, 
              {field: 'state', title: '狀態', formatter: stateFormatter}]
  })

  function idFormatter(value, row, index) {
    return [
      '<button type="button" class="showplayer btn btn-sm btn-white border-0 text-blue"' +
      'data-id=' + row.id ,
      ' ">@' + value +'</button>'
    ].join('');

  }
  function scoreFormatter(value, row, index) {
    if (value > 0) {
      return '<span class="text-primary">贏 '+value+'</span>';
    } else if (value < 0) {
      return '<span class="text-danger">輸 '+Math.abs(value)+'</span>';
    } else {
      return value;
    }
  }
  function stateFormatter(value, row, index) {
    ptype = row.permission_type
    if (value == '1') {          // 鎖定
      return '<span class="text-danger">鎖定</span>'+' (' + ptype +')';
    } else {
      return '<span class="text-primary">正常</span>'+' (' + ptype +')';
    }
  }

  $('#table1 tbody').on('click','tr td .showplayer', function() {
    
    var button = $(this);
    var idx = button.data('id');

    var rowdata = $table1.bootstrapTable('getRowByUniqueId', idx);

    var player_id = rowdata.id;
    var nick_name = rowdata.nick_name;
    var gold = rowdata.gold;
    var star = rowdata.star;
    var score = rowdata.score;
    var last_login_date = rowdata.last_login_date;
    var created_date = rowdata.created_date;
    var player_type = rowdata.player_type;
    var permission_type = rowdata.permission_type;
    var bind_playerid = rowdata.bind_playerid;
    var bind_playername = rowdata.bind_playername;
    var history_game_runs = rowdata.history_game_runs;
    var state = rowdata.state

    // var url = "/member/player?player_id="+player_id+
    //                         "&nick_name="+nick_name+
    //                         "&gold="+gold+
    //                         "&star="+star+
    //                         "&score="+score+
    //                         "&last_login_date="+last_login_date+
    //                         "&created_date="+created_date+
    //                         "&player_type="+player_type+
    //                         "&bind_playerid="+bind_playerid+
    //                         "&bind_playername="+bind_playername+
    //                         "&permission_type="+permission_type+
    //                         "&history_game_runs="+history_game_runs+
    //                         "&state="+state;
    var url = "/member/player?player_id="+player_id;
    location.href = url;

  })

  $("#btnQuery").on("click", function() {
    var startTime1 = $("#startTime1").val();
    var endTime1 = $("#endTime1").val();
    var args = $("#args").val();
    var para = {'startTime1':startTime1, 
                'endTime1':endTime1,
                'args':args};
    var url = "/member/playerlist";

    $.ajax({
      type: 'GET',
      url: url, 
      data: para,
      dataType: 'json',
      success: function(data_get){
        var rs1 = data_get['rs1'];
        $("#all_count").html(data_get['all_count']);
        $("#this_year_count").html(data_get['this_year_count']);
        $("#this_month_count").html(data_get['this_month_count']);
        $("#today_registers").html(data_get['today_registers']);
        $("#day_avg_count").html(data_get['day_avg_count']);
        $table1.bootstrapTable('load',rs1);
        $table1.bootstrapTable('refresh');
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

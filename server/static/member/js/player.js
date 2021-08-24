
var $table1 = $('#table1')
var $table2 = $('#table2')
var $table3 = $('#table3')
var $table4 = $('#table4')
var $table5 = $('#table5')
var $table6 = $('#table6')

$(function() {
  getPara();
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
  // function detailFormatter(value, row, index) {
  //   return [
  //     '<button type="button" class="showdetail btn btn-sm btn-warning" ',
  //     'data-id=' + row.run_id ,
  //     ' ">詳細</button>'
  //   ].join('');
  // }
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

  function getPara(){
    let url = new URL(location.href);
    let params = url.searchParams;
    var player_id = params.get("player_id");
    //$("#src_player_id").val(player_id);
    // var nick_name = params.get("nick_name");
    //$("#src_player_nickname").val(nick_name);
    // var gold = '$ '+ params.get("gold");
    // var score = params.get("score");
    // var star = '◈ '+ params.get("star");
    // var last_login_date = params.get("last_login_date");
    // var created_date = params.get("created_date");
    // var permission_type = params.get("permission_type");
    // var player_type = params.get("player_type");
    // $("#src_player_type").val(player_type);
    // var bind_playerid = params.get("bind_playerid");
    // $("#src_bind_player_id").val(bind_playerid);
    // var bind_playername = params.get("bind_playername");
    // var src_agent_name = params.get("bind_playername");
    // $("#src_bind_player_name").val(src_agent_name);
    // if (bind_playername == '') {
    //   bind_playername = '無';
    // } 
    // var history_game_runs = params.get("history_game_runs");
    // var state = params.get("state");
    // $("#src_player_state").val(state);
    // var player_name = nick_name + '(' + player_id + ')'
    // $("#player_name").text(player_name);
    // $("#bind_playername").text(bind_playername);
    // if (state == '1') {          // 鎖定
    //   $("#state").text('鎖定');
    //   $("#state").addClass("text-danger");
    // } else {
    //   $("#state").text('正常');
    //   $("#state").addClass("text-dark");
    // }

    // $("#permission_type").text(permission_type);
    // $("#last_login_date").text(last_login_date);
    // $("#created_date").text(created_date);
    // $("#gold").text(gold);
    // $("#score").text(score);
    // $("#history_game_runs").text(history_game_runs);
    // $("#star").text(star);
  }

  $("#btnQuery").on("click", function() {
    var player_id = $("#src_player_id").val();
    var startTime1 = $("#startTime1").val();
    var endTime1 = $("#endTime1").val();
    var para = {'player_id':player_id,
                'startTime1':startTime1, 
                'endTime1':endTime1}
    var url = "/member/player"

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
  // 修改
  $('#btnModify').on('show.bs.modal', function (event) {
    var player_state = $("#src_player_state").val();  // 會員狀態
    var player_type = $("#src_player_type").val();    // 會員身份

    var modal = $(this);
    modal.find('.clear').val('');

    modal.find('#player_state').val(player_state)
    modal.find('#player_type').val(player_type)
    $('#btnModify').modal();
  })

  // 玩家入金
  $('#addValue1').on('show.bs.modal', function (event) {
    var modal = $(this);
    modal.find('.clear').val('');
    var player_id =  $("#src_player_id").val();         // 玩家ID
    modal.find('#player_id2').val(player_id);
    var player_name = $("#src_player_nickname").val();  // 玩家名稱
    modal.find('#player_name2').val(player_name);
    var admin_account = $("#admin_account").val();
    modal.find('#admin_account2').val(admin_account);

    $('#addValue1').modal();
  })

  // 補幣
  $('#addValue').on('show.bs.modal', function (event) {
    var modal = $(this);
    modal.find('.clear').val('');
    var player_id =  $("#src_player_id").val();         // 玩家ID
    modal.find('#player_id').val(player_id);
    var player_name = $("#src_player_nickname").val();  // 玩家名稱
    modal.find('#player_name').val(player_name);
    var admin_account = $("#admin_account").val();
    modal.find('#admin_account3').val(admin_account);

    $('#addValue').modal();
  })

  // 儲存[修改]頁面的資料
  $("#btnModifySave").on('click', function() {
    var player_id = $("#src_player_id").val();
    var player_state = $("#player_state").val();
    var player_type = $("#player_type").val();
    var user_pwd = $("#user_pwd1").val();
    // 檢查欄位是否有缺
    if (user_pwd == '') {
      alert("請輸入密碼!!");
    } else {
      // call ajax 傳送資料
      var url = "/member/modify_player_type/";
      var token = $('input[name=csrfmiddlewaretoken]').val();    
      var para = {
        'csrfmiddlewaretoken':token,
        'player_id':player_id,
        'player_state':player_state,
        'player_type':player_type,
        'user_pwd':user_pwd};
    
      $.ajax({
        url: url, 
        data: para,
        type: 'POST',
        dataType: 'json',
        success: function(data_get){
          var msg = data_get['msg']
          //alert(msg);
        },
        error: function (data_get) {
          var msg = data_get['msg']
          //alert(msg);
        }
      });

    }
  })

  // 儲存[玩家入金]頁面的資料
  $("#addValue1Save").on('click', function() {
    var player_id = $("#src_player_id").val();
    var amount = $("#amount2").val();
    var user_pwd = $("#user_pwd2").val();
    var desc = '入金';
    var addvalue_type = '8';
    var jewel_type = 2;
    // 檢查欄位是否有缺
    if (amount == '') {
      alert("請輸入金額!!");
    } else {
      // 金額格式檢查
        if(!/^[0-9]+$/.test(amount)) {
          alert("金額只能輸入數字!!");
        } else {
          if (user_pwd == '') {
            alert("請輸入密碼!!");
          } else {
            // call ajax 傳送資料
            var url = "/member/addvalue/";
            var token = $('input[name=csrfmiddlewaretoken]').val();    
            var para = {
              'csrfmiddlewaretoken':token,
              'player_id':player_id,
              'amount':amount,
              'desc':desc,
              'addvalue_type':addvalue_type,
              'jewel_type':jewel_type,
              'user_pwd':user_pwd};
        
            $.ajax({
              url: url, 
              data: para,
              type: 'POST',
              dataType: 'json',
              success: function(data_get){
                var msg = data_get['msg']
                var gold = '$ '+ data_get['new_gold']
                var star = '◈ '+ data_get['new_star']
                $("#gold").text(gold);
                $("#star").text(star);

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
  // 儲存[補幣]頁面的資料
  $("#addValueSave").on('click', function() {
    var player_id = $("#src_player_id").val();
    var amount = $("#amount").val();
    var desc = $("#desc").val();
    var checked = $('[name=typeOptions]:checked')
    var jewel_type = checked.val();
    var addvalue_type = '2';
    var user_pwd = $("#user_pwd3").val();

    // 檢查欄位是否有缺
    if (amount == '') {
      alert("請輸入金額!!");
    } else {
      // 金額格式檢查
        if(!/^[0-9]+$/.test(amount)) {
          alert("金額只能輸入數字!!");
        } else {
          if (desc == '') {
            alert("請輸入事由!!");
          } else {
            if (user_pwd == '') {
              alert("請輸入密碼!!");
            } else {
              // call ajax 傳送資料
              var url = "/member/addvalue/";
              var token = $('input[name=csrfmiddlewaretoken]').val();
              var para = {
                'csrfmiddlewaretoken':token,
                'player_id':player_id,
                'amount':amount,
                'desc':desc,
                'addvalue_type':addvalue_type,
                'jewel_type':jewel_type,
                'user_pwd':user_pwd};
          
              $.ajax({
                url: url, 
                data: para,
                type: 'POST',
                dataType: 'json',
                success: function(data_get){
                  var msg = data_get['msg']
                  var gold = '$ '+ data_get['new_gold']
                  var star = '◈ '+ data_get['new_star']
                  $("#gold").text(gold);
                  $("#star").text(star);                  
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
      }
  })

})

var $table = $('#table1')

$(function() {
  getPara();

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
    uniqueId: "seqno",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'seqno', title: 'seqno', visible: false}, 
              {field: 'id', title: 'id', visible: false}, 
              {field: 'start_time', title: 'start_time', visible: false}, 
              {field: 'desc', title: '#', class: 'bg-dark text-white', formatter: descFormatter}, 
              {field: 'player1_win_str', title: 'player1_win_str', visible: false}, 
              {field: 'player1_gold_flow', title: 'player1_gold_flow', visible: false}, 
              {field: 'player1_win_lost', title: 'player1_win_lost', visible: false}, 
              {field: 'player1', title: 'player1', formatter: player1Formatter}, 

              {field: 'player2_win_str', title: 'player2_win_str', visible: false}, 
              {field: 'player2_gold_flow', title: 'player2_gold_flow', visible: false}, 
              {field: 'player2_win_lost', title: 'player2_win_lost', visible: false}, 
              {field: 'player2', title: 'player2', formatter: player2Formatter}, 

              {field: 'player3_win_str', title: 'player3_win_str', visible: false}, 
              {field: 'player3_gold_flow', title: 'player3_gold_flow', visible: false}, 
              {field: 'player3_win_lost', title: 'player3_win_lost', visible: false}, 
              {field: 'player3', title: 'player3', formatter: player3Formatter}, 

              {field: 'player4_win_str', title: 'player4_win_str', visible: false}, 
              {field: 'player4_gold_flow', title: 'player4_gold_flow', visible: false}, 
              {field: 'player4_win_lost', title: 'player4_win_lost', visible: false}, 
              {field: 'player4', title: 'player4', formatter: player4Formatter}, 
              {field: 'corp_bonus', title: '抽水', formatter: bonusFormatter}] 
  })

  changeTableTitle();

  function descFormatter(value, row, index) {
    if (value == '總分' | value == '抽水') {
      return value;
    } else {
      return ['<span>' + value + '<br>'+ row.start_time + '</span>'].join('');
    }
  }

  function player1Formatter(value, row, index) {
    out_str = ''
    if (row.desc == '總分') {
      out_str = '遊戲總分：';
      if (row.player1_win_lost < 0) {
        out_str = out_str + '<span class="text-danger"> ' + row.player1_win_str +' </span>';
        out_str = out_str + '<br>金流異動：';
        out_str = out_str + '<span class="text-danger"> ' + row.player1_win_lost +'</span>';
      } else {
        out_str = out_str + '<span class="text-primary"> +' + row.player1_win_str +' </span>';
        out_str = out_str + '<br>金流異動：';
        out_str = out_str + '<span class="text-primary"> ' + row.player1_win_lost +'</span>';
      }      
    } else if (row.desc == '抽水') {
      return row.player1_win_str;
    } else {
      if (row.player1_win_lost < 0) {
        out_str = '<span class="text-danger"> ' + row.player1_win_str +' </span>';
        out_str = out_str + "<br>" + row.player1_gold_flow ;
        out_str = out_str + '<span class="text-danger"> ' + row.player1_win_lost +'</span>) ';
      } else {
        out_str = '<span class="text-primary"> ' + row.player1_win_str +' </span>';
        out_str = out_str + "<br>" + row.player1_gold_flow ;
        out_str = out_str + '<span class="text-primary"> ' + row.player1_win_lost +'</span>) ';
      }
    }
    return out_str
  }

  function player2Formatter(value, row, index) {
    out_str = ''
    if (row.desc == '總分') {
      out_str = '遊戲總分：';
      if (row.player2_win_lost < 0) {
        out_str = out_str + '<span class="text-danger"> ' + row.player2_win_str +' </span>';
        out_str = out_str + '<br>金流異動：';
        out_str = out_str + '<span class="text-danger"> ' + row.player2_win_lost +'</span>';
      } else {
        out_str = out_str + '<span class="text-primary"> +' + row.player2_win_str +' </span>';
        out_str = out_str + '<br>金流異動：';
        out_str = out_str + '<span class="text-primary"> ' + row.player2_win_lost +'</span>';
      }      
    } else if (row.desc == '抽水') {
      return row.player2_win_str;
    } else {
      if (row.player2_win_lost < 0) {
        out_str = '<span class="text-danger"> ' + row.player2_win_str +' </span>';
        out_str = out_str + "<br>" + row.player2_gold_flow ;
        out_str = out_str + '<span class="text-danger"> ' + row.player2_win_lost +'</span>) ';
      } else {
        out_str = '<span class="text-primary"> ' + row.player2_win_str +' </span>';
        out_str = out_str + "<br>" + row.player2_gold_flow ;
        out_str = out_str + '<span class="text-primary"> ' + row.player2_win_lost +'</span>) ';
      }
    }
    return out_str
  }

  function player3Formatter(value, row, index) {
    out_str = ''
    if (row.desc == '總分') {
      out_str = '遊戲總分：';
      if (row.player3_win_lost < 0) {
        out_str = out_str + '<span class="text-danger"> ' + row.player3_win_str +' </span>';
        out_str = out_str + '<br>金流異動：';
        out_str = out_str + '<span class="text-danger"> ' + row.player3_win_lost +'</span>';
      } else {
        out_str = out_str + '<span class="text-primary"> +' + row.player3_win_str +' </span>';
        out_str = out_str + '<br>金流異動：';
        out_str = out_str + '<span class="text-primary"> ' + row.player3_win_lost +'</span>';
      }      
    } else if (row.desc == '抽水') {
      return row.player3_win_str;
    } else {
      if (row.player3_win_lost < 0) {
        out_str = '<span class="text-danger"> ' + row.player3_win_str +' </span>';
        out_str = out_str + "<br>" + row.player3_gold_flow ;
        out_str = out_str + '<span class="text-danger"> ' + row.player3_win_lost +'</span>) ';
      } else {
        out_str = '<span class="text-primary"> ' + row.player3_win_str +' </span>';
        out_str = out_str + "<br>" + row.player3_gold_flow ;
        out_str = out_str + '<span class="text-primary"> ' + row.player3_win_lost +'</span>) ';
      }
    }
    return out_str
  }

  function player4Formatter(value, row, index) {
    out_str = ''
    if (row.desc == '總分') {
      out_str = '遊戲總分：';
      if (row.player4_win_lost < 0) {
        out_str = out_str + '<span class="text-danger"> ' + row.player4_win_str +' </span>';
        out_str = out_str + '<br>金流異動：';
        out_str = out_str + '<span class="text-danger"> ' + row.player4_win_lost +'</span>';
      } else {
        out_str = out_str + '<span class="text-primary"> +' + row.player4_win_str +' </span>';
        out_str = out_str + '<br>金流異動：';
        out_str = out_str + '<span class="text-primary"> ' + row.player4_win_lost +'</span>';
      }      
    } else if (row.desc == '抽水') {
      return row.player4_win_str;
    } else {
      if (row.player4_win_lost < 0) {
        out_str = '<span class="text-danger"> ' + row.player4_win_str +' </span>';
        out_str = out_str + "<br>" + row.player4_gold_flow ;
        out_str = out_str + '<span class="text-danger"> ' + row.player4_win_lost +'</span>) ';
      } else {
        out_str = '<span class="text-primary"> ' + row.player4_win_str +' </span>';
        out_str = out_str + "<br>" + row.player4_gold_flow ;
        out_str = out_str + '<span class="text-primary"> ' + row.player4_win_lost +'</span>) ';
      }
    }
    return out_str
  }

  function bonusFormatter(value, row, index) {
    return value
  }

  function getPara(){
    let url = new URL(location.href);
    let params = url.searchParams;
    var room_id = params.get("room_id");
    $("#room_id").val(room_id);
  }

  function changeTableTitle() {
    var player1 = $("#player_name1").val();
    var player2 = $("#player_name2").val();
    var player3 = $("#player_name3").val();
    var player4 = $("#player_name4").val();
    $table.bootstrapTable('updateColumnTitle', {field: 'player1', title: player1});
    $table.bootstrapTable('updateColumnTitle', {field: 'player2', title: player2});
    $table.bootstrapTable('updateColumnTitle', {field: 'player3', title: player3});
    $table.bootstrapTable('updateColumnTitle', {field: 'player4', title: player4});
  }
})

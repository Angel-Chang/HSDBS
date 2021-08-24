$(function() {
  getVipData(1);
  getVipData(2);
  getVipData(3);
  getVipData(4);
  getVipData(5);
  getVipData(6);

  $("#reload_1").on("click", function() {
    getVipData(1)
  })

  $("#reload_2").on("click", function() {
    getVipData(2)
  })

  $("#reload_3").on("click", function() {
    getVipData(3)
  })

  $("#reload_4").on("click", function() {
    getVipData(4)
  })
  
  $("#reload_5").on("click", function() {
    getVipData(5)
  })

  $("#reload_6").on("click", function() {
    getVipData(6)
  })

  $("#upper_layer_1").on("click", function() {
    getUpperVipData(1)
  })
  $("#upper_layer_2").on("click", function() {
    getUpperVipData(2)
  })
  $("#upper_layer_3").on("click", function() {
    getUpperVipData(3)
  })
  $("#upper_layer_4").on("click", function() {
    getUpperVipData(4)
  })
  $("#upper_layer_5").on("click", function() {
    getUpperVipData(5)
  })
  $("#upper_layer_6").on("click", function() {
    getUpperVipData(6)
  })
})

function getVipData(vip_type) {
  var para = {'vip_type': vip_type}
  var url = "/member/playervip"

  $.ajax({
    type: 'GET',
    url: url,
    data: para,
    dataType: 'json',
    success: function(data_get){
      var data = data_get['data'];
      var top_seat = data_get['top_seat']
      $("#topseat_"+vip_type).val(top_seat);
      $("#nowseat_"+vip_type).val(top_seat);
      $("#parent_seat_"+vip_type).val(-1);
      var player_id = data_get['user_id']
      $("#player_id").val(player_id);
      var fans_count = data_get['fans_count'];
      if (fans_count > 0) {
        $("#upper_layer_"+vip_type).show();
        $("#reload_"+vip_type).show();
      } else {
        $("#upper_layer_"+vip_type).hide();
        $("#reload_"+vip_type).hide();
      }
      var vip_type_count = data_get['vip_type_count'];
      document.getElementById("vip_type_count_"+vip_type).innerHTML= vip_type_count;
      var fans_count = data_get['fans_count'];
      document.getElementById("fans_count_"+vip_type).innerHTML= fans_count;
      var level10_count = data_get['level10_count'];
      document.getElementById("level10_count_"+vip_type).innerHTML= level10_count;
      var member_count = data_get['member_count'];
      document.getElementById("member_count_"+vip_type).innerHTML= member_count;
      var showlist = $("<ul id='org_" +vip_type +"' style='display:none'></ul>");
      showall(data, showlist, vip_type, player_id);
      $("#jOrgChart_"+vip_type).empty();
      $("#jOrgChart_"+vip_type).append(showlist);
      $("#org_"+vip_type).jOrgChart( {
        chartElement : '#jOrgChart_'+vip_type,//指定在某個dom生成jorgchart
        dragAndDrop : false//設置是否可拖動
      });

    },
    error: function () {
      alert('查詢異常，請通知工程師處理。')
    }
  })
}

function showall(menu_list, parent, vip_type, player) {
  $.each(menu_list, function(index, val) {
    var pid = val.pid
    if (pid==null)
      pid = val.id

    var picurl = picsrc + val.picurl
    if(val.childrens.length > 0){
      var li = $("<li></li>");
      li.append("<a href='javascript:void(0)'>"+val.text+"</a>").append("<ul></ul>").appendTo(parent);
      if(val.bind=='Y') {
        li.append("<a class='pic' href='javascript:void(0)' onclick=getOrgId(" + vip_type +","+val.id + ")><img src='"+picurl+"' width='75px' height='75px' style='border:5px blue outset;border-radius:50%;'/> " + val.id +"</a>").append("<ul></ul>").appendTo(parent);
      } else {
        li.append("<a class='pic' href='javascript:void(0)' onclick=getOrgId(" + vip_type +","+val.id + ")><img src='"+picurl+"' width='75px' height='75px' style='border-radius:50%;'/> " + val.id +"</a>").append("<ul></ul>").appendTo(parent);
      }
      //alert(li)
      //遞歸顯示
      showall(val.childrens, $(li).children().eq(1), vip_type, player);
    } else {
      var lil=$("<li></li>");
      lil.append("<a href='javascript:void(0)'>"+val.text+"</a>").appendTo(parent);
      if(val.bind=='Y') {
        lil.append("<a class='pic' href='javascript:void(0)' onclick=getOrgId(" + vip_type +","+val.id + ")><img src='"+picurl+"' width='75px' height='75px' style='border:5px blue outset;border-radius:50%;'/> " + val.id +"</a>");
      } else {
        lil.append("<a class='pic' href='javascript:void(0)' onclick=getOrgId(" + vip_type +","+val.id + ")><img src='"+picurl+"' width='75px' height='75px' style='border-radius:50%;'/> " + val.id +"</a>");
      }
    }
  });
}

// 點選組織圖的圖示重新再重載
function getOrgId(vip_type, seat) {
  var para = {'vip_type': vip_type,
              'seat': seat}
  var url = "/member/playervipseat"

  $.ajax({
    type: 'GET',
    url: url, 
    data: para,
    dataType: 'json',
    success: function(data_get){
      var data = data_get['data'];
      var now_seat = data_get['top_seat']
      $("#nowseat_"+vip_type).val(now_seat);
      var top_seat = $("#topseat_"+vip_type).val();
      if (top_seat == now_seat) {
        $("#parent_seat_"+vip_type).val(-1);
      } else {
        var pid_seat = data_get['pid_seat']
        if (pid_seat < top_seat) {
          $("#parent_seat_"+vip_type).val(-1);
        } else {
          $("#parent_seat_"+vip_type).val(pid_seat);
        }
      }

      var fans_count = data_get['fans_count'];
      if (fans_count > 0) {
        $("#upper_layer_"+vip_type).show();
        $("#reload_"+vip_type).show();
      } else {
        $("#upper_layer_"+vip_type).hide();
        $("#reload_"+vip_type).hide();
      }
      var vip_type_count = data_get['vip_type_count'];
      document.getElementById("vip_type_count_"+vip_type).innerHTML= vip_type_count;
      var fans_count = data_get['fans_count'];
      document.getElementById("fans_count_"+vip_type).innerHTML= fans_count;
      var level10_count = data_get['level10_count'];
      document.getElementById("level10_count_"+vip_type).innerHTML= level10_count;
      var member_count = data_get['member_count'];
      document.getElementById("member_count_"+vip_type).innerHTML= member_count;
      var showlist = $("<ul id='org_" +vip_type +"' style='display:none'></ul>");
      showall(data, showlist, vip_type, player_id);
      $("#jOrgChart_"+vip_type).empty();
      $("#jOrgChart_"+vip_type).append(showlist);
      $("#org_"+vip_type).jOrgChart( {
        chartElement : '#jOrgChart_'+vip_type,//指定在某個dom生成jorgchart
        dragAndDrop : false//設置是否可拖動
      });
    },
    error: function () {
      alert('查詢異常，請通知工程師處理。')
    }
  })
}

function getUpperVipData(vip_type) {
  var seat = $("#parent_seat_"+vip_type).val();
  if (seat != -1) {
    getOrgId(vip_type, seat);
  }
}

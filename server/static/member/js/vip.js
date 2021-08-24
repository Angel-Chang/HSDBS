$(function() {
  $("#upper_layer").hide();
  $("#reload").hide();

  $("#btnQuery").on("click", function() {
    getVipData();
  })

})

$("#reload").on("click", function() {
  getVipData();
})

$("#upper_layer").on("click", function() {
  var vip_type = $("#now_viptype").val();
  var player = $("#now_player_id").val();
  var seat = $("#parent_seat").val();
  if (seat != -1) {
    getOrgId(vip_type, player, seat);
  }   
})

function getVipData() {
  var player_id = $("#player_id").val();
  var vip_type = $("#vip_type").val();
  if (player_id == '') {
    alert('請輸入玩家ID！')
  } else {
    if(!/^[0-9]+$/.test(player_id)) {
      alert('玩家ID格式錯誤，請重新輸入！')
    } else  {
      var para = {'player_id': player_id,
                  'vip_type': vip_type}
      var url = "/member/vip"

      $.ajax({
        type: 'GET',
        url: url, 
        data: para,
        dataType: 'json',
        success: function(data_get){
          var data = data_get['data'];
          $("#now_viptype").val(vip_type);
          $("#now_player_id").val(player_id);
          var top_seat = data_get['top_seat']
          $("#top_seat").val(top_seat);
          $("#now_seat").val(top_seat);
          $("#parent_seat").val(-1);
          var fans_count = data_get['fans_count'];
          if (fans_count > 0) {
            $("#upper_layer").show();
            $("#reload").show();
          } else {
            $("#upper_layer").hide();
            $("#reload").hide();
          }
          var vip_type_count = data_get['vip_type_count'];
          document.getElementById("vip_type_count").innerHTML= vip_type_count;
          var fans_count = data_get['fans_count'];
          document.getElementById("fans_count").innerHTML= fans_count;
          var level10_count = data_get['level10_count'];
          document.getElementById("level10_count").innerHTML= level10_count;
          var member_count = data_get['member_count'];
          document.getElementById("member_count").innerHTML= member_count;
          var showlist = $("<ul id='org' style='display:none'></ul>");
          showall(data, showlist, vip_type, player_id);
          $("#jOrgChart").empty();
          $("#jOrgChart").append(showlist);
          $("#org").jOrgChart( {
            chartElement : '#jOrgChart',//指定在某個dom生成jorgchart
            dragAndDrop : false//設置是否可拖動
          });

        },
        error: function () {
          alert('查詢異常，請通知工程師處理。')
        }
      })
    }
  }

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
        li.append("<a class='pic' href='javascript:void(0)' onclick=getOrgId(" + vip_type +","+player+","+val.id+ ")><img src='"+picurl+"' width='75px' height='75px' style='border:5px blue outset;border-radius:50%;'/> "+val.id+"</a>").append("<ul></ul>").appendTo(parent);
      } else {
        li.append("<a class='pic' href='javascript:void(0)' onclick=getOrgId(" + vip_type +","+player+","+val.id + ")><img src='"+picurl+"' width='75px' height='75px' style='border-radius:50%;'/> "+val.id+"</a>").append("<ul></ul>").appendTo(parent);
      }
      //遞歸顯示
      showall(val.childrens, $(li).children().eq(1), vip_type, player);
    } else {
      var lil=$("<li></li>");
      lil.append("<a href='javascript:void(0)'>"+val.text+"</a>").appendTo(parent); 
      if(val.bind=='Y') {
        lil.append("<a class='pic' href='javascript:void(0)' onclick=getOrgId(" + vip_type +","+player+","+val.id+ ")><img src='"+picurl+"' width='75px' height='75px' style='border:5px blue outset;border-radius:50%;'/> "+val.id+"</a>");
      } else {
        lil.append("<a class='pic' href='javascript:void(0)' onclick=getOrgId(" + vip_type +","+player+","+val.id+ ")><img src='"+picurl+"' width='75px' height='75px' style='border-radius:50%;'/> "+val.id+"</a>");
      }
    }
  });
}

// 點選組織圖的圖示重新再重載
function getOrgId(vip_type, player, seat) {
  var para = {'vip_type': vip_type,
              'player_id': player,
              'seat': seat}
  var url = "/member/vipseat"

  $.ajax({
    type: 'GET',
    url: url, 
    data: para,
    dataType: 'json',
    success: function(data_get){
      var data = data_get['data'];
      var now_seat = data_get['top_seat']
      $("#now_seat").val(now_seat);
      var top_seat = $("#top_seat").val();
      if (top_seat == now_seat) {
        $("#parent_seat").val(-1);
      } else {
        var pid_seat = data_get['pid_seat']
        if (pid_seat < top_seat) {
          $("#parent_seat").val(-1);
        } else {
          $("#parent_seat").val(pid_seat);
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
      document.getElementById("vip_type_count").innerHTML= vip_type_count;
      var fans_count = data_get['fans_count'];
      document.getElementById("fans_count").innerHTML= fans_count;
      var level10_count = data_get['level10_count'];
      document.getElementById("level10_count").innerHTML= level10_count;
      var member_count = data_get['member_count'];
      document.getElementById("member_count").innerHTML= member_count;
      
      var showlist = $("<ul id='org' style='display:none'></ul>");
      showall(data, showlist, vip_type, player);
      $("#jOrgChart").empty();
      $("#jOrgChart").append(showlist);
      $("#org").jOrgChart( {
        chartElement : '#jOrgChart',//指定在某個dom生成jorgchart
        dragAndDrop : false//設置是否可拖動
      });

    },
    error: function () {
      alert('查詢異常，請通知工程師處理。')
    }
  })

}

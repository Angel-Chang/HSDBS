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
    uniqueId: "id",   //每一行的唯一标识，一般为主键列
    classes:"table table-hover table-sm table-bordered text-center table-striped",
    theadClasses: "thead-dark",
    columns: [{field: 'id', title: 'id', visible: false},
              {field: 'player_id', title: '玩家ID'}, 
              {field: 'wallet_addr', title: '錢包地址'}, 
              {field: 'amount', title: '金額'}, 
              {field: 'created_date', title: '日期'},
              {field: 'status', title: '狀態ID', visible: false},
              {field: 'status_name', title: '狀態', formatter: statusFormatter}]
  })

  function statusFormatter(value, row, index) {
    if (row.status == '2') {
      return [
        '<button type="button" class="update btn btn-sm btn-warning"' +
        'data-id=' + row.id ,
        ' ">' + value +'</button>'
      ].join('');
    } else {
      return value;
    }
  }  

  $('#table1 tbody').on('click','tr td .update', function() {
    var button = $(this);
    var idx = button.data('id');

    if (confirm('是否變更為已出金 ?')) {
      var url = "/member/update_player_order/";
      var token = $('input[name=csrfmiddlewaretoken]').val();
      var para = {'csrfmiddlewaretoken': token, 'pk':idx};

      $.ajax({
        url: url, 
        data: para,
        type: 'POST',
        dataType: 'json',
        success: function (data_get) {
          var rs1 = data_get['rs1'];
          $table.bootstrapTable('load',rs1);
          $table.bootstrapTable('refresh');
          alert('出金成功。')
        },
        error: function () {
          alert('資料更新發生異常，請通知工程師處理。')
        }
      }); 
    }
  });  
})

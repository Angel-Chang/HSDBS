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
    columns: [{field: 'id', title: 'ID'}, 
              {field: 'user_account', title: '帳號'}, 
              {field: 'user_password', title: '密碼', visible: false}, 
              {field: 'user_name', title: '名稱'}, 
              {field: 'phone_number', title: '手機號碼'}, 
              {field: 'last_login_date', title: '最後登入時間'}, 
              {field: 'level', title: '系統身份', visible: false}, 
              {field: 'level_name', title: '狀態'}, 
              {field: 'action', title: '設定', formatter: actionFormatter}]
  })

  function actionFormatter(value, row, index) {
    if (value == 'Y') {
      return [
        '<button type="button" class="update btn btn-sm btn-warning mr-2" ',
        'data-toggle="modal" data-target="#detail" data-title="更新管理員" ',
        'data-action="U" data-id=' + row.id , 
        ' ">修改</button>',
        '<button type="button" class="remove btn btn-sm btn-danger" ',
        'data-id=' + row.id , 
        ' ">刪除</button>'
      ].join('');
    } else {
      return '無修改權限';
    }

  }

  $("#btnQuery").on('click', function() {
    var args = $("#args").val();
    var para = {'args':args}
    var url = "/member/admin_list"

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

  //$('.remove').on('click', function() {
  $('#table1 tbody').on('click','tr td .remove', function() {
    var button = $(this);
    var idx = button.data('id');

    if (confirm('確定要刪除此管理員的資料嗎 ?')) {
      var url = "/member/delete_account/";
      var token = $('input[name=csrfmiddlewaretoken]').val();
      var para = {'csrfmiddlewaretoken': token, 'pk':idx};

      $.ajax({
        url: url, 
        data: para,
        type: 'post',
        dataType: 'json',
        success: function () {
          $table.bootstrapTable('removeByUniqueId', idx); 
          alert('資料刪除成功。')
        },
        error: function () {
          alert('資料刪除發生異常，請通知工程師處理。')
        }
      }); 
    }
  });

  $('#detail').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var title = button.data('title'); // Extract info from data-* attributes
    var modal = $(this);
    modal.find('.modal-title').text(title);
    var action = button.data('action');
    modal.find('#operate').val(action);

    if(action == 'C') {
      modal.find('.clear').val('');  
    }
    if(action == 'U') {
      // 取得那一行的資料
      var idx = button.data('id');
      var rowdata = $table.bootstrapTable('getRowByUniqueId', idx);
      var user_account = rowdata.user_account;
      var user_password = rowdata.user_password;
      var user_name = rowdata.user_name;
      var phone_number = rowdata.phone_number;
      var level = rowdata.level;

      modal.find('#uid').val(idx);
      modal.find('#user_account').val(user_account);
      modal.find('#user_password').val(user_password);
      modal.find('#user_name').val(user_name);
      modal.find('#phone_number').val(phone_number);
      modal.find('#level').val(level);
    }

    $('#detail').modal();
  })

  // 新增/更新管理員資訊
  $("#btnSave").on('click', function() {
    var action = $("#operate").val();
    var uid = $("#uid").val();
    var user_account = $("#user_account").val();
    var user_password = $("#user_password").val();
    var user_name = $("#user_name").val();
    var phone_number = $("#phone_number").val();
    var level = $("#level").val();
    // to do : 檢查欄位是否有缺
    var url = "/member/account/";

    var token = $('input[name=csrfmiddlewaretoken]').val();

    var para = {
      'csrfmiddlewaretoken':token,
      'action':action,
      'uid':uid,
      'user_account':user_account,
      'user_password':user_password,
      'user_name':user_name,
      'phone_number':phone_number,
      'level':level};

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
  })

})

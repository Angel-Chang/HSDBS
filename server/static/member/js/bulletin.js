$(document).ready(function() {

  $('#btnClear').on('click', function(e) {
    reset();
  });

  $('#btnSend').on('click', function(e) {
    // 檢查畫面上必輸值，是否都有輸入
    // receiver:1 玩家
    // receiver:2 所有玩家
    var receiver = $('input:radio[name=receiver]:checked').val();
    if(receiver == '1') {
      var receiver_list = $('#inputID').val();
      if (receiver_list == '') {
        alert("請輸入玩家ID!!");
      } else {
        // 檢查玩家ID格式
        receiver_list = receiver_list.replace(/\s*/g,"");
        check_list = receiver_list.replace(/,/g,"");
        // alert(check_list);
        if(!/^[0-9]+$/.test(check_list)) {
          alert("玩家ID格式不符!!");
        }
        var subject = $('#inputSubject').val();
        if (subject == '') {
          alert("請輸入主題!!");    
        } else {
          var message = $('#message').val();
          if (message == '') {
            alert("請輸入內容!!");    
          } else {
            // call ajax 傳送資料
            var url = "/member/sendmail/";
            var token = $('input[name=csrfmiddlewaretoken]').val();
            
            var para = {'csrfmiddlewaretoken': token, 
                        'receiver': receiver,
                        'receiver_list': receiver_list,
                        'subject': subject,
                        'message': message};

            $.ajax({
              url: url, 
              data: para,
              type: 'post',
              dataType: 'json',
              success: function (data_get) {
                var send_mail_count = data_get['send_mail_count'];
                alert('發送公告完成。共 ' + send_mail_count + ' 個玩家')
              },
              error: function () {
                alert('發送公告功能異常，請通知工程師處理。')
              }
            });               
          }
        }
      }
    }
  });

  function reset() {
    $('input:radio[name=receiver]:eq(0)').prop('checked', true);
    $('.clear').val('');      
  }
});
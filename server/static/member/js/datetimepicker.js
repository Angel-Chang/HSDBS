
$(document).ready(function() {
  var today = new Date();
  today.setHours(0,0,0);
  $('#startTime1').datetimepicker({
     format:"YYYY-MM-DD HH:mm:ss",
     locale: 'zh-tw'
  });

  today.setHours(23,59,59);
  $('#endTime1').datetimepicker({
     format:"YYYY-MM-DD HH:mm:ss",
     locale: 'zh-tw'
  });

} );
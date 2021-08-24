
$(document).ready(function() {
  var today = new Date();
  $('#checkMonth').datetimepicker({
     format: "YYYY/MM",
     locale: 'zh-tw',
     defaultDate: today
  });
} );
$(function() {
    $(".hasdetails").click(function() {
      $(this).next().slideToggle('slow');
    }).next().hide();
});
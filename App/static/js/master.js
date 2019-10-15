function show_error_notification(){
  notification = $('.notification')

  notification.removeClass('hidden');
  notification.removeClass('fadeOut');
  notification.addClass('fadeIn');

  setTimeout(function(){
    notification.removeClass('fadeIn');
    notification.addClass('fadeOut');
  }, 2000)

}

function get_points(){
  $('.loading').removeClass('hidden')
  $.ajax({
    url: '/',
    type: 'post',
    data: {
      'url': $('#cu__input').val()
    },
    success: function(response){
      $('#main__section__wrapper').html(response)
      $('.loading').addClass('hidden')
    },
    error: function(){
      show_error_notification()
    }
  })
}

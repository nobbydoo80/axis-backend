/* This is for all local mods */
(function($){

  /* Taken directly from Django https://docs.djangoproject.com/en/dev/ref/contrib/csrf/ */
  function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = jQuery.trim(cookies[i]);
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) == (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');

  /* Taken directly from Django https://docs.djangoproject.com/en/dev/ref/contrib/csrf/ */
function setupAjaxPostCSRF() {
  var csrftoken = getCookie('csrftoken');
      function csrfSafeMethod(method) {
          // these HTTP methods do not require CSRF protection
          return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
      }
      $.ajaxSetup({
          crossDomain: false, // obviates need for sameOrigin test
          beforeSend: function(xhr, settings) {
              if (!csrfSafeMethod(settings.type)) {
                  xhr.setRequestHeader("X-CSRFToken", csrftoken);
              }
          }
      });
  }

function setupAjaxLogin() {
  // login submit
  $('#login-form').submit(function(evt){
    evt.preventDefault();

    var url = $(this).attr('action'),
      username = $('#id_username').val(),
      password = $('#id_password').val();
    function showError(error) {
      $('#login-error').removeClass('hidden').fadeOut('fast', function(){
        $(this).text(error).fadeIn('fast');
      });
    }
    $.ajax({
      url: url,
      type: 'POST',
      data: {'username': username, 'password': password},
      error: function(response){
        showError("Sorry, there was a network problem. Please try again.");
      },
      success: function(response){
        response = JSON.parse(response);
        if (response.status) {
          window.location.replace("/");
        } else {
          showError("Sorry, there was a problem with your username or password");
        }
      }
    })

  })
}
});

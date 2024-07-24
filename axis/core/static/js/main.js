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

	// doc ready
	$(function(){

		setupAjaxPostCSRF();
		setupAjaxLogin();

        //This is the defaults for bootstrap-datepicker.
        $.extend($.fn.datepicker.defaults, {format: 'mm/dd/yyyy', todayBtn: true, todayHighlight: true});

        // This is used for the formset
        if($.fn.formset !== undefined && $.fn.formset.defaults !== undefined ){
            $.fn.formset.defaults = {
                addText: 'Add another',          // Text for the add link
                deleteText: 'Remove',            // Text for the delete link
                addCssClass: 'add-row',          // CSS class applied to the add link
                deleteCssClass: 'delete-row',    // CSS class applied to the delete link
                prefix: 'form',                  // The form prefix for your django formset
                formTemplate: null,              // The jQuery selection cloned to generate new form instances
                formCssClass: 'dynamic-form',    // CSS class applied to each form in a formset
                extraClasses: [],                // Additional CSS classes, which will be applied to each form in turn
                added: null,                     // Function called each time a new form is added
                removed: null                    // Function called each time a form is deleted
            };
        }
    });

})(jQuery)

// http://brack3t.com/ajax-and-django-views.html
function apply_form_field_error(fieldname, error) {
    var input = $("#id_" + fieldname),
        container = $("#div_id_" + fieldname),
        error_msg = $("<span />").addClass("help-block ajax-error").text(error[0]);

    container.addClass("has-error");
    error_msg.insertAfter(input);
}
function clear_form_field_errors(form) {
    $(".ajax-error", $(form)).remove();
    $(".error", $(form)).removeClass("error");
}

function getUrlParameters() {
    var pairs = window.location.search.substring(1).split(/[&?]/);
    var res = {}, i, pair;
    for (i = 0; i < pairs.length; i++) {
        pair = pairs[i].split('=');
        if (pair[1])
            res[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1]);
    }
    return res;
}

// Activates a select2 at runtime.
// "field_id" is the ajax value the django-select2 uses to identify the field globally.
// "options", if given, is the set of select2 instantiation options.  Sane defaults are used if
// no customizations are required.
function activate_deferred_select2(input, field_id, options, userGetValText) {
    var input_id = input.attr('id');
    var default_options = {
        'allowClear': true,
        'initSelection': django_select2.onInit,
        'multiple': false,
        'escapeMarkup': function(m) { return m; }, // allows HTML to appear in results
        'minimumInputLength': 1,
        'minimumResultsForSearch': 6,
        'closeOnSelect': false,
        'ajax': {
            'dataType': 'json',
            'quietMillis': 100,
            'url': '/fields/auto.json',
            'data': django_select2.runInContextHelper(django_select2.get_url_params, input_id),
            'results': django_select2.runInContextHelper(django_select2.process_results, input_id)
        },
        'placeholder': 'Type to search'
    }
    options = $.extend({}, default_options, options);
    userGetValText = userGetValText || null;

    input.data('field_id', field_id);
    input.change(django_select2.onValChange).data('userGetValText', userGetValText);
    input.select2(options);
}

var axis = {
    bind_auto_tab_activation: function(){
        // Auto-activate bootstrap tabs where a matching url hash targets one.
        // http://stackoverflow.com/a/10787789/194999
        var hash = document.location.hash;
        if (hash) {
            $('.nav-tabs a[href="'+hash+'"]').tab('show');
        }
    },

    setValidatorDefaults: function(){
        if (jQuery.validator) {
            jQuery.validator.setDefaults({
                success: function(element) {
                    $(element).closest('.form-group').addClass('has-success').text();
                },
                highlight: function(element) {
                    $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
                },
                unhighlight: function(element) {
                    $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
                },
                errorElement: 'span',
                errorClass: 'help-block',
                errorPlacement: function(error, element) {
                    if(element.parent('.input-group').length) {
                        error.insertAfter(element.parent());
                    } else {
                        error.insertAfter(element);
                    }
                }
            });
            jQuery.validator.addMethod("alphanumeric", function(value, element) {
                return this.optional(element) || /^[a-zA-Z0-9_]+$/.test(value);
            }, "Field must contain only letters or numbers.");
            jQuery.validator.addMethod("phoneUS", function(phone_number, element) {
                phone_number = phone_number.replace(/\s+/g, "");
                return this.optional(element) || phone_number.length == 12 &&
                    phone_number.match(/^([2-9]\d{2}-[2-9]\d{2}-\d{4})$/);
            }, "Please specify a valid phone number - XXX-XXX-XXXX");
        }
    },

    start_tooltips: function(){
        axis.initialize_tooltips($('[id^="hint"]'));

        $('body').tooltip({
            selector: '[data-toggle=tooltip]'
        }).popover({
            selector: '[data-toggle=popover]'
        });
        $('body').on('mouseenter', '[data-toggle="tooltip_trigger"]', function(){
            $(this).closest('.form-group').find('[data-toggle="tooltip"]').tooltip('show')
        }).on('mouseleave', '[data-toggle="tooltip_trigger"]', function(){
            $(this).closest('.form-group').find('[data-toggle="tooltip"]').tooltip('hide')
        });
    },

    initialize_tooltips: function(hints){
        hints.each(function(){
            var hint = $(this);
            var hint_text = hint.text();
            var form_group = hint.closest('.form-group');
            var trigger_type = 'focus';
            if(hint.siblings(":checkbox").length > 0){
                tooltip_icon_element = form_group.find('label')
                // have to add .pull-left to checkboxes so tooltip shows up next to label
                tooltip_element =  hint.parent().addClass('pull-left')
                trigger_type = 'hover'
            } else {
                if(form_group.find('.select2-container').length) trigger_type = 'hover';
                tooltip_icon_element = form_group.find('.control-label')
                tooltip_element =  hint.parent().children(':first')
            }
            tooltip_icon_element.append('<i class="text-muted fa fa-info-circle" data-toggle="tooltip_trigger"></i>');
            tooltip_element.attr({
                'data-trigger': trigger_type,
                'data-placement': 'right',
                'data-toggle': 'tooltip',
                'title': hint_text
            })
            hint.remove();
        });
    }
}

$(function(){
    axis.bind_auto_tab_activation();
    axis.setValidatorDefaults();
    axis.start_tooltips();

    var template_clear_button = $('<a href="#" class="clear-search"><i class="icon-remove-circle icon-large fa fa-times-circle-o fa-lg"></i></a>');

    $(document)
    .on('preInit.dt', function(e, settings){
        var api = new $.fn.dataTable.Api(settings);
        var wrapper = $(settings.nTableWrapper);
        var search_input = wrapper.find('.dataTables_filter input');
        var length_select = wrapper.find('.dataTables_length select');
        var export_buttons = wrapper.find('.dt-buttons a.btn');
        var table_info = wrapper.find('.dataTables_info');

        var clear_button = template_clear_button.clone().click(function(){
            api.search('').draw();
        });
        search_input.after(clear_button).after(' ');

        search_input.attr('placeholder', 'Filter');
        search_input.addClass('form-control input-sm');
        length_select.addClass('form-control input-sm');
        export_buttons.addClass('btn-sm');
        table_info.addClass('text-center');
    })
    .on('init.dt', function(e, settings){
        var wrapper = $(settings.nTableWrapper);
        var pagination = wrapper.find('.pagination');
        pagination.addClass('pagination-sm');
    });

    /**
     * Django adds a special input that you have to check when you want to fully remove a file
     * from a form. Jasny, not being meant to be used this way, has no clue about this extra input.
     * On fileinput clear, we need to check that remove box ourselves.
     */
    $(document).on('clear.bs.fileinput', function(e){
        $(e.target).find('[id$="clear_id"]').prop('checked', true);
    })
});

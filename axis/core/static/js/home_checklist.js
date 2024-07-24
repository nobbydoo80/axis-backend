$(function(){
  // variables
    var row_class = '.panel-question'; // top level question element
    var active_row;
    var pending_requests = 0;
    var answers = [];  // list of input IDs modified by the changer.
    var allowed_keys = [46, 8, 27, 35, 36, 37, 38, 39, 40, 190, 110]; // delete, backspace, escape, end, home, left, up, right, down, period, decimal point


  // templates
    var loading_indicator = $('<i class="icon-spinner icon-spin icon-large"></i>');
    var submitted_indicator = $('<label class="" title="This answer has been submitted."><span class="icon-stack"> <i class="icon-circle icon-stack-base"></i> <i class="icon-ok icon-white"></i> </span></label>');
    var submitting_notification = $('<span class="busy_submitting muted">Please wait for <span id="pending_quantity"></span> pending answers to finish submitting.</span>');
    var required_field = $('<span class="asteriskField">*</span>');
    var validation_notification = $('<span class="text-warning"></span>');


    // Basic components for workflow
    var form = $('#axis_form');
    var submit_button = form.find('button[type="submit"]');
    var form_submitting_notification = $(".submitting-notification").hide();
    form_submitting_notification.html(submitting_notification.clone());
    var pending_quantity_display = form_submitting_notification.find('#pending_quantity');
    var progress_bar = $(".progress-bar-success");
    var progress_bar_optional = $(".progress-bar-info");
    var retraction_modal = $("#retraction_modal");


  // initialize on page load
	// set the progress bar width
	update_questions_progress('answer', false, 0);  // no-op for getting the UI updated

    // Disabler for readonly mode
    disable_inputs(form.find('.noedit'));

    // highlight already answered questions
    $("input:radio").each(function(){
        var toggleColor = $(this).data('is-failure') ? 'btn-danger' : 'btn-success';
        $(this).closest('.btn').toggleClass(toggleColor+' active', $(this).is(':checked'));
    });

    // crispy textareas are giant
    $('textarea').each(function(){
        $(this).attr('style', '').attr('rows', 3);
    });

    // Start datepickers
    $(row_class+'.question-type-date .answer input').datepicker();

    // Configure inline formsets
    $(row_class).each(function(){
        var row = $(this);
        var row_id = row.data('id');
        row.find('.photos-table-row').formset({
           prefix: row_id + '_photos',
           addText: 'Add another',
           deleteText: 'Remove'
        });
        row.find('.documents-table-row').formset({
           prefix: row_id + '_documents',
           addText: 'Add another',
           deleteText: 'Remove'
        });
    });


  // Functions
    function disable_interactive(row) {
        // Sets a flag that causes the click handlers to ignore this row
        row.attr('data-disabled', "disabled");
        disable_inputs(row);
    }

    function enable_interactive(row) {
        // Sets a flag that causes the click handlers to examine this row
        console.log("making interactive again", row);
        row.removeAttr('data-disabled');
        row.removeClass('noedit');
        enable_inputs(row);
        row.find('.answered-by').remove();
        row.find('.delete').remove();
    }

    function disable_inputs(row) {
        var inputs = row.find('input:not([type=hidden]), textarea, button, select');
        inputs.attr('disabled', 'disabled').parent().addClass("disabled");
        row.find('.answer-unit').addClass('text-muted');
    }

    function enable_inputs(row) {
        var inputs = row.find('input:not([type=hidden]), textarea, button, select');
        inputs.removeAttr('disabled').parent().removeClass("disabled");
    }

    function add_request() {
        pending_requests += 1;
        pending_quantity_display.text(pending_requests);
        submit_button.attr('disabled', 'disabled');
        form_submitting_notification.slideDown('fast');
        progress_bar.parent().addClass('active progress-striped');
    }

    function clear_request() {
        pending_requests -= 1;
        pending_quantity_display.text(pending_requests);
        if (pending_requests == 0) {
            submit_button.removeAttr('disabled');
            form_submitting_notification.slideUp('fast');
            progress_bar.parent().removeClass('active progress-striped');
        }
    }

    function update_questions_progress(operator, optional, quantity){
		quantity = (quantity == null ? 1 : quantity);
		var val = quantity * (operator == 'answer' ? -1 : 1);
        if (optional) {
			remaining_optional_questions += val;
            progress_bar_optional.width((remaining_optional_questions/total_questions)*100 + '%');
            $("#optional_questions").text(remaining_optional_questions);
		} else {
            remaining_questions += val;
            progress_bar.width(((total_questions-remaining_questions-remaining_optional_questions)/total_questions)*100 + '%');
            $("#remaining_questions").text(remaining_questions);
        }
		var answered_optional_questions = optional_questions - remaining_optional_questions;
    }

    function prepare_row_for_submission(row) {
        // Returns the serialized data for a row and disables it from further interaction.
        // The disabling in this function is more severe than in the "disable_inputs", where simple
        // "disabled" attributes are assigned.
        row = $(row);

        // Calculate this before things get disabled
        var serialized_data = [row.find('input, textarea').serialize(), "id="+row.attr('data-id')];

        row.find('.answer .status').prepend(loading_indicator.clone());
        disable_interactive(row);
        row.find('.text-warning').remove();
        return serialized_data;
    }

    function display_errors(row, errors) {
        if (errors.answer) {
			var notification = validation_notification.clone();
			notification.text(errors.answer.answer);
			row.find('.status').prepend(notification);
			notification.slideDown();
        }
        if (errors.photo) {
            row.find('.photos').addClass("error");
        }
        if (errors.documents) {
            row.find('.documents').addClass("error");
        }
    }


  // Checks
    function has_file_field_completed(elements) {
        // Returns true if any file fields have a value
        return $(elements).toArray().reduce(function(a, b){
            return $(a).val() || $(b).val();
        });
    }

    function is_valid_row(row) {
        // Allows a row to pass or fail validation for background submission.

        // Remove rows missing their main answer
        var answer_wrapper = row.find('.panel-heading .answer');
        var is_valid = true;
        if (row.is('.question-type-multiple-choice')) {
            if (answer_wrapper.find('input:checked').length === 0) {
                is_valid = false;
            } else {
                var selected_input = row.find('input:checked');
                var has_document = has_file_field_completed('.documents input[type=file]');
                var document_required = selected_input.data('document-required');
                var has_photo = has_file_field_completed('.photos input[type=file]');
                var photo_required = selected_input.data('photo-required');
                var has_comment = row.find('textarea').val();
                var comment_required = selected_input.data('comment-required');

                console.log(selected_input, document_required, has_document, photo_required, has_photo, comment_required, has_comment);
                is_valid = (!document_required || has_document) && (!photo_required || has_photo) && (!comment_required || has_comment);
            }
        } else {
            var input = answer_wrapper.find('input:not([type=hidden])');
            if (input && input.val() === "") {
                is_valid = false;
            }
        }

        // Remove rows using a file field (we can't submit them over simple string ajax data)
        row.find('input[type=file]').each(function(){
            if ($(this).val() !== "") {
                is_valid = false;
            }
        });

        return is_valid;
    }


  // Listeners
    // Global hide-answered button
    $('#hide_answered').on('click', function(e) {
        e.preventDefault();
        if ($(this).text() === "Hide Answered") {
            $(this).text("Show Answered");
            $(".noedit").slideUp();
        } else {
            $(this).text("Hide Answered");
            $(".noedit").slideDown();
        }
    });

    $('#hide_optional').on('click', function(e){
        e.preventDefault();
        if($(this).text() == "Hide Optional"){
            $(this).text("Show Optional");
            $('.optional').slideUp();
        } else {
            $(this).text("Hide Optional");
            $('.optional').slideDown();
        }
    });

    // highlight radio button answer dependant on failing answer status
    $('body').on('change', 'input:radio', function(){
        var el = $(this);
        // if false, someone clicked on an already selected answer and
        // Bootstrap has unchecked it underneath, reset to checked and proceed.
        if(!this.checked) this.checked = true;

        // get required attributes for selected answer
        var document = el.data('document-required');
        var photo = el.data('photo-required');
        var comment = el.data('comment-required');
        var panel_collapse = el.closest('.panel').find('.panel-collapse');
        var required_box = el.closest('.panel').find('.requirements-box');
        el.closest('.panel-heading').find(".inline-requirements, .icon-comment-alt, .icon-picture, .icon-file-text").addClass('hidden');
        required_box.addClass('hidden').find('.icon-comment-alt, .icon-picture, .icon-file-text').parent().addClass('hidden');
        if(document || photo || comment){
            el.closest('.panel-heading').find('.inline-requirements').removeClass('hidden');
            required_box.removeClass('hidden');
            // show panel and add required marks to each element
            panel_collapse.collapse('show');
            if(comment){
                panel_collapse
                        .find('textarea')
                        .attr('placeholder', 'Comment Required...')
                        .closest('.form-group').find('label')
                        .append(required_field.clone());
                panel_collapse.prev().find('.icon-comment-alt').removeClass('hidden');
                required_box.find('.icon-comment-alt').parent().removeClass('hidden');
            }
            if(photo){
                panel_collapse.find('.photos-label').append(required_field.clone());
                panel_collapse.prev().find('.icon-picture').removeClass('hidden');
                required_box.find('.icon-picture').parent().removeClass('hidden');
            }
            if(document){
                panel_collapse.find('.documents-label').append(required_field.clone());
                panel_collapse.prev().find('.icon-file-text').removeClass('hidden');
                required_box.find('.icon-file-text').parent().removeClass('hidden');
            }
        } else {
            // if other answer is selected, remove required marks
            panel_collapse
                    .find('textarea')
                    .attr('placeholder', 'Comment...')
                    .closest('.form-group').find('.asteriskField')
                    .remove();
            panel_collapse.find('.photos-label').remove('.asteriskField');
            panel_collapse.find('.documents-label').remove('.asteriskField');
        }
        // loop through each btn in group and set color
        $(this).closest('.btn-group').children().each(function(){
            var self = $(this);
            var toggleColor = self.find('input').data('is-failure') ? 'btn-danger' : 'btn-success';
            self.toggleClass(toggleColor, self.find('input').is(':checked'));
        });
    });

    // Prevent anything but numbers from being typed in number fields
    $('body').on('keydown', '.question-type-float .answer input, .question-type-integer .answer input', function(e){
        if(allowed_keys.indexOf(e.keyCode) != -1){
            return;
        }
        else {
            // Ensure that it is a number and stop the keypress if not
            if (event.shiftKey || (event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105 )) {
                event.preventDefault();
            }
        }
    });

    // Mass answer changer
    $("#multi_choice_change").change(function() {
        var value = $(this).find("option:selected").val();
        console.log("Changed to " + value);
        //First unselect anything which was already changed
        $.each(answers, function (index){
            // console.log(this);
            console.log("Resetting", this);
            $(this).prop('checked', false);
        });
        $('input:radio:not(:checked):not(:disabled)[autofill=True][value*="' + value + '"]').each(
            function () {
                console.log("Looking at ", $(this).attr('id'));
                $(this).attr('checked', true).trigger('click');
                answers.push($(this).attr('id'));
            }
        );

        // Start batch submission
        // Map each modified answer to its row for the submission handler to use.
        var rows = $.map(answers, function(element_id){
            return $(element_id).closest('.row');
        });
        form.trigger('background-submit', $(rows));
    });


  // Handlers
    // Ajax submission
    // This works by allowing a user to fill out as much of a question as possible before actually
    // generating the ajax submission.  It's extremely likely that binding to an input's "blur"
    // event would cause a lot of trouble behind the scenes, for answers that require comments,
    // files, etc.
    form.bind('background-submit', function(event, rows){
        // Actual submission trigger, which posts all of the elements in the ``rows`` collection.

        var valid_rows = [];
        rows.each(function(){
            var row = $(this);

            if (is_valid_row(row)) {
                valid_rows.push(row);
            } else {
                console.log("Not submitting incomplete row", this);
            }
        });
        console.debug("Valid rows:", valid_rows.length, valid_rows);

        if (valid_rows.length) {
            // Gather the targeted form data for serialization
            var data = [form.find('input[name=csrfmiddlewaretoken]').serialize()];
            data = data.concat($.map(valid_rows, prepare_row_for_submission));
            add_request();

            // Uncomment if you don't want answers to be submitted
            // return;

            // Submit in background
            $.ajax({
                'type': "POST",
                'url': window.location.href,
                'data': data.join("&"),
                'dataType': 'json',
                'success': function(response, status, xhr){
                    clear_request();
                    console.log("Response raw status:", status);
                    if (status !== "success") {
                        // TODO: Handle this somehow
                        return;
                    }

                    if (response.results) {
                        $.each(response.results, function(question_id, data){
                            var row = $(row_class+'[data-id='+question_id+']');
                            row.find('.multiple-choice-identifier').text('');
                            row.find('.icon-spin').replaceWith(submitted_indicator.clone());
                            row.addClass('noedit');
                            console.log("Results for #%s:", question_id, data);

                            row.find('td *').unbind('click.axis');
                            update_questions_progress('answer', row.is('.optional'));
                        });
                    } else {
                        // Form validation error
                        $.each(response.errors, function(question_id, errors){
                            var row = $(row_class+'[data-id='+question_id+']');
                            row.find('.icon-spin').remove();
                            console.log("Errors for #%s:", question_id, errors);
                            enable_interactive(row);
                            display_errors(row, errors);
                        });
                    }
                },
                'error': function(xhr, status, error){
                    clear_request();
                    console.log(xhr, status, error);
                }
            });
        }
    });

    $(".delete").on('click', function(e){
        e.preventDefault();
        var panel_id = $(this).closest('.panel').data('id');
        var panel_question = $(this).closest('.panel-heading').find('.accordion-toggle').text().trim();
        retraction_modal.find('.modal-body').text(panel_question);
        retraction_modal.data('href', $(this).attr('href'));
        retraction_modal.data('panel', panel_id);
        retraction_modal.modal('show');
    });
    $('#retract_answer').on('click', function(){
        retraction_modal.modal('hide');
        var url = retraction_modal.data('href');
        var panel_id = retraction_modal.data('panel');

        console.log("you are now retracting this answer", panel_id);
        $.ajax({
            'type': "POST",
            'url': url,
            'data': {'retrieve_question': window.location.href+'?id='+panel_id}
        }).done(function(data){
            data = $(data).find('[data-id='+panel_id+']').eq(0);
            $('[data-id='+panel_id+']').replaceWith(data);
            update_questions_progress('retract', data.is('.optional'));
        })
    });

    // Bind clicks for background submissions
    form.on('click', row_class+':not(.noedit) *', function(){
        // This is pretty broadly bound, but captures clicks into elements in a row, including
        // labels, inputs, and the <a> togglers.
        var row = $(this);
        if (!row.is(row_class)) {
            row = row.closest(row_class);
        }
        if (row.is('.active')) {
            return;
        }

        // Release old active row for ajax submission
        if (active_row) {
            form.trigger('background-submit', [active_row]);
        }

        // New row is active
        row.addClass('active panel-info').siblings().filter('.active').removeClass('active panel-info');
        active_row = row;
    });

    // Submission of form
    form.submit(function(){
        // let them know we're doing something and disable submit button
        form_submitting_notification
            .html('Submitting, Please wait... ')
            .append(loading_indicator.clone())
            .slideDown('fast');
        submit_button.attr('disabled', 'disabled');

        // Ask the server to only consider items that haven't been ajax'd over the line.
        form.find('input[name="id"]').remove();
        form.find(row_class+':not([data-disabled]):not(.noedit)').each(function(){
            form.append($('<input type="hidden" name="id" />').val($(this).attr('data-id')));
        });

        // Turn off the click handlers so that things don't get crazy while the submission is going.
        form.find(row_class).attr('data-disabled', "disabled");

        return true;
    });
});

$(function(){
    // variables ===================================================================================
    var row_class = '.panel-question'; // top level question element
    var active_row;
    var pending_requests = 0;
    var answers = [];  // list of input IDs modified by the changer.
    var allowed_keys = [
        46, 8, 27, 35, 36, 9,  // delete, backspace, escape, end, home, tab
        37, 38, 39, 40, 190, 110  // left, up, right, down, period, decimal point
    ];


    // templates ===================================================================================
    var loading_indicator = $('<i class="icon-spinner icon-spin icon-large fa fa-spinner fa-spin fa-lg"></i>&nbsp;');
    var submitted_indicator = $('<label class="" title="This answer has been submitted."><i class="icon-stack fa fa-check-circle-o"></i></label>');
    var submitting_notification = $('<span class="busy_submitting muted">Please wait for <span id="pending_quantity"></span> pending answers to finish submitting.</span>');
    var required_field = $('<span class="asteriskField">*</span>');
    var validation_notification = $('<li class="list-group-item list-group-item-danger"></li>');
    var question_row = Handlebars.compile($('#question_row').html());


    // Basic components for workflow ===============================================================
    var form = $('#axis_form');
    var submit_button = form.find('button[type="submit"]');
    var home_detail_button = $("[href='"+cancel_url+"']");
    var form_submitting_notification = $(".submitting-notification").hide();
    form_submitting_notification.html(submitting_notification.clone());
    var pending_quantity_display = form_submitting_notification.find('#pending_quantity');
    var progress_bar = $(".progress-bar-success");
    var progress_bar_optional = $(".progress-bar-info");
    var retraction_modal = $("#retraction_modal");
    var required_questions_holder = $('#required_questions_holder');
    var optional_questions_holder = $('#optional_questions_holder');
    var answered_questions_holder = $('#answered_questions_holder');

    // initialize on page load =====================================================================
    // set the progress bar width
    update_questions_progress('answer', false, 0);  // no-op for getting the UI updated
    update_questions_progress('answer', true, 0);

    var promise = $.ajax({
        url: build_url_string(),
        success: function(data){
            window.a = data;
            initialize_data(data);
        }
    });

    promise.done(function(){
        if(!required_ef.length){
            $("[href=#required_questions_holder]").parent().addClass('disabled');
            $('#required_questions_spinner').hide();
        } else {
            console.time('required questions render');
            _each(required_ef, render_handlebars_row, required_questions_holder, 5, function(){
                console.timeEnd('required questions render');
            });
            $('#required_questions_spinner').hide();
        }

        if(!optional_ef.length){
            $("[href=#optional_questions_holder]").parent().addClass('disabled');
            $('#optional_questions_spinner').hide();
        } else {
            console.time('optional questions render');
            _each(optional_ef, render_handlebars_row, optional_questions_holder, 5, function(){
                console.timeEnd('optional questions render');
            });
            $('#optional_questions_spinner').hide();
        }

        if(!answered_ef.length){
            $('#answered_questions_spinner').hide();
        } else {
            console.log("ANSWERED: " + answered_ef.length);
            console.time('answered questions render');
            _each(answered_ef, render_handlebars_row, answered_questions_holder, 5, function(){
                console.timeEnd('answered questions render');
            });
            $('#answered_questions_spinner').hide();
        }

    });


    // Functions ===================================================================================
    function _each(arr, fn, holder, limit, callback){
        var count = 0,
            len = arr.length;

        function run(){
            var d = limit;
            while(d-- && count < len){
                fn(arr[count], holder, count++);
            }
            if(len > count){
                setTimeout(run, 200);
            } else {
                if(typeof callback === 'function'){
                    callback();
                }
            }
        }
        run();
    }

    function render_handlebars_row(item, holder, index){
        var rendered = $(question_row(item));
        $(holder).append(rendered);
        initialize_row(rendered);
    }

    function initialize_row(row){
        // init the formsets
        initialize_formset($(row));
        // size down the textarea for comments
        $(row).find('textarea').attr('style', '').attr('rows', 3);
        //color already answered questions
        $(row).find('input:radio').each(function(){
            var toggleColor = $(this).data('is-failure') ? 'btn-danger' : 'btn-success';
            toggleColor = $(this).data('display-as-failure') ? 'btn-danger' : toggleColor;
            $(this).closest('.btn').toggleClass(toggleColor+' active', $(this).is(':checked'));
        });
        // disable already answered questions
        disable_inputs(form.find('.noedit'));
        // initialize datepickers
        if($(row).hasClass('question-type-date')){
            $(row).find('.answer input').datepicker();
        }
    }

    function initialize_formset(row){
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
    }

    function disable_interactive(row){
        row.attr('data-disabled', 'disabled');
        disable_inputs(row);
    }

    function disable_inputs(row) {
        var inputs = row.find('input:not([type=hidden]), textarea, button, select');
        inputs.attr('disabled', 'disabled').parent().addClass("disabled");
        row.find('.answer-unit').addClass('text-muted');
    }

    function add_request() {
        pending_requests += 1;
        pending_quantity_display.text(pending_requests);
        submit_button.attr('disabled', 'disabled');
        home_detail_button.attr('disabled', 'disabled');
        form_submitting_notification.show();
        progress_bar.parent().addClass('active progress-striped');
    }

    function clear_request() {
        pending_requests -= 1;
        pending_quantity_display.text(pending_requests);
        if (pending_requests == 0) {
            submit_button.removeAttr('disabled');
            home_detail_button.removeAttr('disabled');
            form_submitting_notification.hide()
            progress_bar.parent().removeClass('active progress-striped');
        }
    }

    function update_questions_progress(operator, optional, quantity){
        quantity = (quantity == null ? 1 : quantity);
        var val = quantity * (operator == 'answer' ? -1 : 1);
        if (optional){
            remaining_optional_questions += val;
            progress_bar_optional.width(((optional_questions-remaining_optional_questions)/optional_questions) * 100 + "%");
            $('.remaining_optional').text(remaining_optional_questions);
        } else {
            remaining_questions += val;
            progress_bar.width(((required_questions-remaining_questions)/required_questions) * 100 + "%");
            $('.remaining_required').text(remaining_questions);
        }
    }

    function prepare_row_for_submission(row){
        row = $(row);

        row.find('.answer .status').prepend(loading_indicator.clone());
        row.find('.text-warning').remove();

        var question_id = row.data('id');
        var images = $("[name^="+question_id+"_photos][name$=raw]");
        var documents = $("[name^="+question_id+"_documents][name$=raw]");
        var answer = '';
        var comment = $("#id_"+question_id+"-comment").val();
        var image_set = [];
        var document_set = [];

        if(row.hasClass('question-type-multiple-choice')){
            answer = $("[id^=id_"+question_id+"-answer]:checked").val();
        } else {
            answer = $("[id^=id_"+question_id+"-answer]").val();
        }

        images.each(function(i, e){
            var photo_raw = $(e).val();
            var filename = $(e).siblings('[class$=filename]').val()
            if(photo_raw){
                image_set.push({
                    'photo_raw': photo_raw,
                    'photo_raw_name': filename
                });
            }
        });
        documents.each(function(i, e){
            var document_raw = $(e).val();
            var filename = $(e).siblings('[class$=filename]').val()
            if(document_raw){
                document_set.push({
                    'document_raw': document_raw,
                    'document_raw_name': filename
                });
            }
        });

        var data = {
            'home': object_id,
            'question': question_id,
            'user': user_id,
            'answer': answer,
            'comment': comment
        };

        if(image_set.length) data['answerimage_set'] = image_set;
        if(document_set.length) data['answerdocument_set'] = document_set;

        return data;
    }

    function display_errors(row, errors) {
        row.addClass('panel-error');
        if (errors.answer) {
            var notification = validation_notification.clone();
            notification.text(errors.answer.answer);
            row.find('.answer-error').prepend(notification);
            notification.slideDown();
        }
        if (errors.photo) {
            var notification = validation_notification.clone();
            notification.html(errors.photo.join('<br/>'));
            row.find('.photo-error').removeClass("hidden").find('.list-group').append(notification);
        }
        if (errors.documents) {
            var notification = validation_notification.clone();
            notification.html(errors.documents.join('<br/>'));
            row.find('.document-error').removeClass("hidden").find('.list-group').append(notification);
        }
    }

    function hide_required_marks(panel){
        panel
                .find('textarea')
                .attr('placeholder', 'Comment...')
                .closest('.form-group').find('.asteriskField')
                .remove();
        panel.find('.photos-label').find('.asteriskField').remove();
        panel.find('.documents-label').find('.asteriskField').remove();
    }

    // Checks ======================================================================================
    function has_file_field_completed(elements) {
        // Returns true if any file fields have a value
        var arr = $(elements).toArray();
        for(var i= 0, j=arr.length; i<j; i++){
            if($(arr[i]).val()) return true;
        }
        return false;
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
        if(typeof(window.FileReader) == 'undefined'){
            if(is_valid){
                home_detail_button.attr('disabled', 'disabled');
            }
            row.find('input[type=file]').each(function(){
                if ($(this).val() !== "") {
                    is_valid = false;
                }
            });
        }

        return is_valid;
    }


    // Listeners ===================================================================================
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
            $(this).text("Show Optional");
            $('.optional').slideDown();
        }
    });

    // highlight radio button answer dependant on failing answer status
    form.on('change', 'input:radio', function(){
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
        el.closest('.panel-heading').find(".inline-requirements, .fa.fa-comment-o, .fa.fa-picture.o, .fa.fa-file-text").addClass('hidden');
        required_box.addClass('hidden').find('.fa.fa-comment-o, .fa.fa-picture.o, .fa.fa-file-text').parent().addClass('hidden');
        hide_required_marks(panel_collapse);
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
                panel_collapse.prev().find('.fa.fa-comment-o').removeClass('hidden');
                required_box.find('.fa.fa-comment-o').parent().removeClass('hidden');
            }
            if(photo){
                panel_collapse.find('.photos-label').append(required_field.clone());
                panel_collapse.prev().find('.fa.fa-picture-o').removeClass('hidden');
                required_box.find('.fa.fa-picture.o').parent().removeClass('hidden');
            }
            if(document){
                panel_collapse.find('.documents-label').append(required_field.clone());
                panel_collapse.prev().find('.fa.fa-file-text').removeClass('hidden');
                required_box.find('.fa.fa-file-text').parent().removeClass('hidden');
            }
        }
        // loop through each btn in group and set color
        $(this).closest('.btn-group').children().each(function(){
            var self = $(this);
            var toggleColor = self.find('input').data('is-failure') ? 'btn-danger' : 'btn-success';
            toggleColor = self.find('input').data('display-as-failure') ? 'btn-danger' : toggleColor;
            self.toggleClass(toggleColor, self.find('input').is(':checked'));
        });
    });

    // Prevent anything but numbers from being typed in number fields
    form.on('keydown', '.question-type-float .answer input, .question-type-integer .answer input', function(e){
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
    $("#multi_choice_change").on('change', function() {
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

    $('.nav-tabs').on('click', '.disabled', function(e){
        e.stopImmediatePropagation();
    });

    // Handlers ====================================================================================
    // Ajax submission
    // This works by allowing a user to fill out as much of a question as possible before actually
    // generating the ajax submission.  It's extremely likely that binding to an input's "blur"
    // event would cause a lot of trouble behind the scenes, for answers that require comments,
    // files, etc.
    form.bind('background-submit', function(event, rows, submitAsync){
        // Actual submission trigger, which posts all of the elements in the ``rows`` collection.
        var valid_rows = [];
        rows.each(function(){
            var row = $(this);
            if(is_valid_row(row)){
                valid_rows.push(row);
            } else {
                console.log("Not submitting incomplete row", this);
            }
        });
        console.log("Submitting %i valid rows", valid_rows.length);

        $.each(valid_rows, function(index, element){
            var row = $(element);
            var question_id = row.data('id');
            row.find('.panel-collapse.in').collapse('hide');

            var data = JSON.stringify(prepare_row_for_submission(row));

            add_request();

            $.ajax({
                method: "POST",
                url: build_url_string()+question_id+"/answer/",
                data: data,
                async: submitAsync,
                contentType: 'application/json',
                success: function(response, status, xhr){
                    console.log('Response raw status:', status);
                    if(status !== 'success'){
                        // TODO: Handle this somehow
                        return;
                    }

                    clear_request();
                    response = init_object(response);
                    var rendered = $(question_row(response));
                    $("[data-id="+question_id+"]").replaceWith(rendered);
                    initialize_row(rendered);
                    update_questions_progress('answer', rendered.is('.optional'));
                },
                error: function(xhr, status, error){
                    var row = $("[data-id="+question_id+"]");

                    var notification = "";
                    if(xhr.responseJSON && 'non_field_errors' in xhr.responseJSON){
                        notification = validation_notification.clone();
                        notification.text(xhr.responseJSON.non_field_errors.join(", "));
                    }
                    row.find(".answer .status").html(notification);
                    console.log(xhr, status, error);
                    display_errors(row, xhr.responseJSON);
                    clear_request();
                }
            })
        });
    });

    form.on('click', '.delete', function(e){
        e.preventDefault();
        var panel_id = $(this).closest('.panel').data('id');
        var panel_question = $(this).closest('.panel-heading').find('.accordion-toggle').text().trim();
        retraction_modal.find('.modal-body').text(panel_question);
        retraction_modal.data('href', $(this).attr('href'));
        retraction_modal.data('panel', panel_id);
        retraction_modal.modal('show');
    });

    form.on('change.bs.fileinput', function(evt){
        /**
         * FIXME: temporary!
         * Jasny fileupload stops propogation of all events.
         * We can't catch the original change event on the file input.
         * Issue is submitted with jasny.
         * https://github.com/jasny/bootstrap/issues/343
         */
        var el = $(evt.target).find('input[type=file]');
        if (el[0] === undefined) {
            // erratic triggering of event without a target.
            return;
        }
        var files = el[0].files;

        for(var i = 0, f; f = files[i]; i++){
            var file_name = f.name;
            var reader = new FileReader();

            reader.onload = function(name, file){
                console.groupCollapsed('file');
                console.log('name', name);
                console.log('file', file);
                console.groupEnd('file');

                var lookup = el.attr('id');

                var raw = file.target.result;
                var extension = name.split('.').pop();
                if(raw.indexOf(':;') > -1){
                    raw = raw.replace(':;', ':application/' + extension + ';');
                } else if(raw.indexOf('octet-stream') > -1 && extension == 'blg'){
                    raw = raw.replace('octet-stream', extension);
                }

                $("#"+lookup+"_raw").val(raw);
                $("#"+lookup+"_raw_name").val(name);

            }.bind(this, file_name);

            reader.readAsDataURL(f);
        }
    });

    $('#retract_answer').on('click', function(){
        retraction_modal.modal('hide');
        var url = retraction_modal.data('href');
        var panel_id = retraction_modal.data('panel');

        console.log("you are now retracting this answer", panel_id);
        $.ajax({
            'type': "DELETE",
            'url': url,
            success: function(response, status, xhr){
                if(status !== 'success'){
                    // TODO: Handle this somehow
                    return ;
                }
                response = init_object(response);
                var rendered = $(question_row(response));
                $("[data-id="+panel_id+"]").replaceWith(rendered);
                update_questions_progress('retract', rendered.is('.optional'));
                initialize_row(rendered);
            },
            error: function(data){
                console.log("got back an error");
                window.a = data;
            }
        });
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
            form.trigger('background-submit', [active_row, true]);
        }

        // New row is active
        row.addClass('active panel-info').siblings().filter('.active').removeClass('active panel-info');
        active_row = row;
    });

    // Submission of form
    form.submit(function(){
        // background submit.
        form.trigger('background-submit', [active_row, false]);

        // let them know we're doing something and disable submit button
        submit_button.prepend(loading_indicator.clone());
        form_submitting_notification
            .html('Submitting, Please wait... ')
            .show();
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

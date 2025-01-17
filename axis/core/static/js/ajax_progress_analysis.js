function api_get_multiple(endpoint, id_list, row_callback, callback) {
    var results = [];
    var xhr = $.ajax(endpoint);
    xhr.done(function(data){
        for (var i in id_list) {
            var item = data['object_list'][id_list[i]];
            (row_callback || function(){})(i, id_list[i], item);
            var result = {};
            result[id_list[i]] = item
            results.push(result);
        }
        (callback || function(){})(results);
    });
    return xhr;
}

// Returns an anonymous function usable as a row_callback to the api_get_multiple function
function get_progress_report_row_callback(containers) {
    var templates = {
        'item': $('<li><span class="requirement" /></li>'),
        'incomplete': $('<i class="icon-check-empty fa fa-square-o" />'),
        'complete': $('<i class="icon-check-sign fa fa-check-square" />'),
        'message': $('<div class="message"><i class="icon-info-sign fa fa-info-circle text-danger" /><span /></div>'),
        'progress_bar': $('<div class="progress"><div class="progress-bar progress-bar-success"></div></div>'),
        'show_completed_steps': $('<div><a href="#" class="show-completed-steps text-muted"></a></div>'),
        'certify_button': $('<a class="btn btn-primary btn-xs">Certify home</a>')
    }
    return function(i, id, progress){
        var report = $('<ul class="requirements" />');
        var has_completed_steps = false;
        for (var j in progress['requirements']) {
            // Fetch the result object for this program.
            // Available: name, status, data, message
            var result = progress['requirements'][j];

            var test_name = Object.keys(result)[0];
            result = result[test_name];

            var item = templates['item'].clone();
            item.find('.requirement').text(result.name);
            item.attr('data-requirement', test_name);
            if (result.message) {
                var message = templates['message'].clone();
                message.find('span').text(result.message)
                if (!result.status && result.url) {
                    // Wrap the message in <a> for a link to the page where they can fix it
                    message = $('<a href="'+result.url+'" />').append(message);
                }
                item.append(message);
            }
            if (result.status == true) {
                item.addClass('complete text-muted').prepend(templates['complete'].clone());
                has_completed_steps = true;
            } else {
                item.prepend(templates['incomplete'].clone());
            }
            report.append(item);
        }
        if (has_completed_steps) {
            var show_link = templates['show_completed_steps'].clone();
            var completed = progress['completed_requirements'];
            var base_msg = " " + completed + " completed requirement"+(completed == 1 ? "" : "s");
            var button = show_link.find('a');
            button.on('click', function(){
                button.closest('ul').find('.complete').slideToggle('fast');
                button.toggleClass('revealed');
                button.text((button.is('.revealed') ? 'Hide' : 'Show') + base_msg);
                return false;
            }).text("Show" + base_msg);
            report.append(show_link);
        }

        var container = containers.eq(i).empty();
        // Add visual progress indicator
        var progress_bar = templates['progress_bar'].clone();
        progress_bar.find('.progress-bar').css('width', ''+progress.completion+'%');
        container.append(progress_bar);

        // For multi-program homes, this will add progress bars to the summary tab
        var summary_cell = container.closest('.panel-group').children('.panel').eq(0).find('.program-completion-progress');
        summary_cell.empty().append(progress_bar.clone());

        // Append report items
        container.append(report);

        // Activate the "certify" button if passing status is met
        if (progress['status']) {
            var certify_wrapper = container.closest('.panel').find('.certify_button');
            var certify_url = certify_wrapper.attr('data-url');
            certify_wrapper.empty().append(templates['certify_button'].clone().attr('href', certify_url));
        }
    }
}

$(function(){
    $('.eto-calculations-output').each(function() {
        var wrapper = $(this);
        var output = wrapper.closest('.row').find('.eto-calculations-output-data');
        var error_data = wrapper.closest('.row').find('.eto-calculations-errors');
        var input_form = wrapper.closest('.row').find('.eto-calculations-input');

        xhr = $.get(wrapper.attr('data-url'));
        xhr.success(function (data, status, xhr) {
            wrapper.find('.eto-calculations-progress-indicator').remove();
            populate_calculations_table(data, wrapper);
            $(output).slideDown('fast');

            var button_str = '<div class="btn-group pull-right"><button type="button" ' +
                'class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">' +
                'Full report <span class="caret"></span></button>' +
                '<ul class="dropdown-menu text-left"><li';

            var showview = output.attr('data-showview');

            if (typeof showview !== 'undefined' && showview !== false) {
                if ( showview == 0 ){ button_str += ' class="hidden '}}
            button_str += '><a class="eto-view-full-report" href="#">View</a></li>' +
                '<li><a href="'+data.eps_report_url+'">EPS Download</a></li></ul></div>';

            var button_group = $(button_str);
            button_group.find('.eto-view-full-report').on('click', function(){
                input_form.submit();
                return false;
            });

            if (typeof data['is_locked'] !== 'undefined' && data['is_locked'] !== false){
                head_txt = 'Home as Built &nbsp; <i class="fa fa-lock" data-toggle="tooltip" title="As reported to ETO"></i>';
                output.find('thead tr th').html(head_txt)
            }
            output.find('thead tr th').append(button_group);
        });
        xhr.fail(function(data) {
            var errors = data.responseJSON['errors'];

            ul_ = "<strong>Energy Performance Score cannot yet be calculated.<br />The following ";
            ul_ += "information items are missing or not valid for the program:</strong><br /><ul>";
            $.each(errors, function( index, value ) {
                ul_ += "<li>" + value + "</li>";
            });
            ul_ += "</ul>";
            error_data.html(ul_);
            console.log(ul_);
            wrapper.find('.eto-calculations-progress-indicator').remove();
            $(error_data).slideDown('fast');
        });
    });

    function populate_calculations_table(data, output) {
        output.find('tr[data-name]').each(function(){
            var tr = $(this);
            var name = tr.attr('data-name');
            var value = data[name];
            var cell = tr.find('td.value');
            var precision = parseInt(cell.attr('data-precision'));
            if (cell.text().indexOf('$') != -1) {
                if (value) {
                    value = Math.round(value * Math.pow(10, precision)) / Math.pow(10, precision);
                    value = "$" + value.toFixed(precision);
                } else {
                    value = "$0.00";
                }
            } else {
                if (cell.is('[data-percentage]')) {
                    value = '' + Math.round(value * 100 * Math.pow(10, precision)) / Math.pow(10, precision) + '%';
                } else {
                    value = Math.round(value * Math.pow(10, precision)) / Math.pow(10, precision);
                }
            }
            cell.text(value);
        });
    }
});

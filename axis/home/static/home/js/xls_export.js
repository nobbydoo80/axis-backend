/**
 * Created by michaeljeffrey on 8/12/15.
 */

var STAT_LIMIT = 4000;

$(function(){
    var export_fields = $("#export_fields"),
        export_rows_defaults = {};

    export_fields.on('change', '.btn', toggleFieldColor);
    export_fields.on('change', 'input', syncLocalStorage);
    $("#reset_defaults").on('click', resetDefaults);


    // ==================================== //
    // GET EXPORT FIELDS                    //
    // ==================================== //
    $.ajax({
        url: '/api/v2/home/status/report/export_fields/',
        success: function(data){
            var cleaned_html = $($.parseHTML($.trim(data))).filter(function(index, element){
                return element.nodeName != '#text';
            });
            export_fields.append(cleaned_html);
            init_export_fields();
            export_fields.find('input:radio').closest('.btn').on('click', enableRadioInputDeselection);
        }
    });

    // ==================================== //
    // INIT EXPORT FIELDS                   //
    // ==================================== //
    function init_export_fields(){
        // Set our defaults
        export_rows_defaults = _mapSerializedArray(export_fields.find('input:checked').serializeArray());
        // If we haven't stored anything then set the classes up
        if (!('home_status_export_fields' in localStorage)) {
            export_fields.find('input:radio:checked, input:checkbox:checked').each(function () {
                $(this).closest('.btn').addClass('btn-success active');
            })
            return
        }

        export_fields.find('input:checked').attr('checked', false);

        var reset_data = JSON.parse(localStorage.getItem('home_status_export_fields'));
        setFieldsToProvidedData(reset_data);
    }

    // ==================================== //
    // EVENT LISTENERS                      //
    // ==================================== //
    function resetDefaults(e){
        e.preventDefault();
        export_fields.find('input:radio:checked, input:checkbox:checked')
        .prop('checked', false)
        .closest('.btn')
        .removeClass('btn-success active');

        setFieldsToProvidedData(export_rows_defaults);
    }
    function toggleFieldColor(){
        var el = $(this);

        if(el.hasClass('radio')){
            el.closest('.btn-group-nested').children().each(toggleFieldClasses);
        } else {
            toggleFieldClasses(null, el);
        }
    }
    function enableRadioInputDeselection(){
        var el = $(this),
            input = el.find('input:radio'),
            isChecked = input.is(':checked');

        if(isChecked){
            setTimeout(function(){
                //el.removeClass('active');
                input.prop('checked', false).trigger('change');
            }, 0)
        }
    }

    // ==================================== //
    // HELPERS                              //
    // ==================================== //
    function toggleFieldClasses(_, element){
        // Adds color when buttons are clicked.
        var el = $(element);
        var isChecked = el.find('input').is(':checked');

        setTimeout(function(){
            // Some listener somewhere unsets active after we set it.
            // So we gotta come to the party a little late to avoid
            // the butt heads.
            el.toggleClass('btn-success active', isChecked);
        }, 0);
    }
    function syncLocalStorage(){
        var data = export_fields.find('input').serializeArray();

        data = _mapSerializedArray(data);

        localStorage.setItem('home_status_export_fields', JSON.stringify(data));
    }
    function setFieldsToProvidedData(data){
        for(var key in data){
            var field = $("[name='"+key+"']");

            if(field.is(':radio')){
                field = $("[name='"+key+"'][value='"+data[key]+"']");
            }

            field.closest('.btn').trigger('click');
        }
    }
    function _mapSerializedArray(arr){
        return _.chain(arr).indexBy('name').mapValues('value').value();
    }
});

datatableview.finalizeOptions = (function(){
    // Add XLS export specific datatable options without removing the
    // pages datatable options.
    var hsr_finalizeOptions = datatableview.finalizeOptions;

    return function _confirm_datatable_options(datatable, options){
        options = hsr_finalizeOptions(datatable, options);
        options.fnDrawCallback = function(oSettings){
            var allowed = oSettings.fnRecordsDisplay() > STAT_LIMIT;
            $("#export_button").attr('disabled', allowed);
            $("#count_note").toggle(allowed);
        };
        return options
    }
})();

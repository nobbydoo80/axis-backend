/**
 * Created by michaeljeffrey on 8/11/15.
 */

$(function(){
    var dateFields = $("#id_activity_start, #id_activity_stop, #id_paid_date_start, #id_paid_date_stop, #id_program_activity_start, #id_program_activity_stop, #id_home_created_date_start, #id_home_created_date_end"),
        showDatesButton = $("#show_dates_href"),
        certificationOnly = $("#id_certification_only"),
      stateFields = $("#id_state"),
        filterSearchInput = $('#id_search_bar'),
        dataTableSearchInput = $(".dataTables_filter input");

    $("form").on('change', reloadDatatable);

    // ================================= //
    //  Date Fields                      //
    // ================================= //
    dateFields
        .on('change', preventDateFieldEvent)
        .datepicker()
        .closest('#date_ranges')
        // Show the date fields if they are prefilled with dates
        .toggle(dateFields.val() != '');

    showDatesButton.on('click', toggleDateFields);

    // ================================= //
    //  Certification/State Fields       //
    // ================================= //
    /**
     * When filtering by a state, certification date should be false.
     * Clicking the certification date checkbox, set all state filters to default value.
     */
    certificationOnly.on('change', unsetStateSelects);
    stateFields.on('change', uncheckCertificationOnly);

    // ================================= //
    //  Certification/State Fields       //
    // ================================= //
    filterSearchInput.val(dataTableSearchInput.val());
    dataTableSearchInput.on('keyup', function(){
        filterSearchInput.val($(this).val());
    });

    // Submit handlers
    $('form').find('input,button').filter('[type="submit"]').click(function(){
        var button = $(this);
        var action_url = button.attr('data-action');
        button.closest('form').attr('action', action_url);
    });

    // ================================= //
    // Event Handlers                    //
    // ================================= //
    function preventDateFieldEvent(e){
        var el = $(this),
            prev_date = el.data('prev_selected_date'),
            curr_date = el.val();

        if(prev_date == curr_date){
            e.preventDefault();
            e.stopImmediatePropagation();
        } else {
            el.data('prev_selected_date', curr_date);
        }
    }
    function toggleDateFields(e){
        e.preventDefault();
        var visible = dateFields.is(':visible'),
            empty = dateFields.val() == '';

        dateFields.closest('#date_ranges').toggle(!(visible && empty));
    }
    function uncheckCertificationOnly(e){
        certificationOnly.prop('checked', false);
    }
    function unsetStateSelects(e){
        if($(this).is(':checked')){
            stateFields.val('');
        }
        if(dateFields.val() == ''){
            alert('Please select a date to filter certification by.');
        }
    }
    function reloadDatatable(e){
        // Don't trigger a datatable reload on checkbox and radio changes.
        var el = $(e.target);

        if(!el.is(':checkbox, :radio')){
            $(".datatable").dataTable().fnDraw();
        }
    }
});

datatableview.autoInitialize = true;
datatableview.finalizeOptions = (function(){
    var super_finalizeOptions = datatableview.finalizeOptions;

    return function _confirm_datatable_options(datatable, options){
        options = super_finalizeOptions(datatable, options);
        options.ajax.data = function(data){
            data.builder_id = $('#id_builder').val();
            data.provider_id = $('#id_provider').val();
            data.rater_id = $('#id_rater').val();
            data.utility_id = $('#id_utility').val();
            data.hvac_id = $('#id_hvac').val();
            data.architect_id = $('#id_architect').val();
            data.developer_id = $('#id_developer').val();
            data.communityowner_id = $('#id_communityowner').val();
            data.qa_id = $('#id_qa').val();
            data.eep_id = $('#id_eep').val();
            data.general_id = $('#id_general').val();
            data.rater_of_record_id = $('#id_rater_of_record').val();
            data.subdivision_id = $('#id_subdivision').val();
            data.eep_program_id = $('#id_eep_program').val();
            data.state = $('#id_state').val();
            data.ipp_state = $('#id_ipp_state').val();
            data.qatype = $('#id_qatype').val();
            data.qastatus = $('#id_qastatus').val();
            data.qaobservation = $('#id_qaobservation').val();
            data.metro_id = $('#id_metro').val();
            data.city_id = $('#id_city').val();
            data.us_state = $('#id_us_state').val();
            data.eto_region = $('#id_eto_region').val();
            data.rating_type = $('#id_rating_type').val();
            data.activity_type = $('#id_activity_type').val();
            data.activity_start = $('#id_activity_start').val();
            data.activity_stop = $('#id_activity_stop').val();
            data.home_created_date_start = $('#id_home_created_date_start').val();
            data.home_created_date_end = $('#id_home_created_date_end').val();
            data.certification_only = $('#id_certification_only').is(':checked');
            data.program_activity_start = $('#id_program_activity_start').val();
            data.program_activity_stop = $('#id_program_activity_stop').val();
            data.heat_source = $('#id_heat_source').val();
            data.meets_or_beats = $("#id_meets_or_beats").val();
            data.remrate_flavor = $("#id_remrate_flavor").val();
            data.paid_date_start = $('#id_paid_date_start').val();
            data.paid_date_stop = $('#id_paid_date_stop').val();
            data.exclude_ids = $("#id_exclude_ids").val();
            data.task_type_id = $("#id_task_type").val();
            data.task_assignee = $("#id_task_assignee").val();
            data.qa_designee = $("#id_qa_designee").val();
        }
        return options
    }
})();

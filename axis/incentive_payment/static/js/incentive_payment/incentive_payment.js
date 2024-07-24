// TODO: Errors are not showing in Error modal.
// TODO: Reverting stats. All at once, or one at a time?
// TODO: Annotating Stats, all at once, or one at a time?
// TODO: Make sure all the rest of the transitions work.


/*
 * POST APS MEETING:
 * TODO: Per Builder payment forecast (check with steve)
 *
 *
 * POSSIBLE OPTIONS:
 * OPTION: default active table
 * OPTION: refresh tables?
 * OPTION: refresh table time...
 * OPTION: propagate filters through table
 * OPTION: Options to refresh tables automatically (what will this effect?)
 */

/*
 * Incentive Payment Page.
 *
 * Currently there are four actions one can perform.
 * Actions are defined in control_center.html in the actions array.
 *
 * Each Action is directly related to a Button Object where all of the functionality lies.
 * A Button Object has:
 *  form
 *  datatable
 *
 * When something is submitted that makes a progress Bar Object.
 * A progress Bar Object has:
 *  number of items to submit
 *  handlers for success, info, and error
 *  pointer to Button Object submission was generated from
 *
 * Submitting is handled by the Button, and responded by the Bar.
 */

//-------------------------------- HELPERS ---------------------------------------------------------
function get_annotation(unserialized){
    /**
    * helper function for getting an annotation from a form.
    * Only to be called as 'get_annotation.call(this)' from a form submission setup function.
    * */
    var annotation;
    var comment = this.form.find("#id_comment");
    if(comment.length){
        if(unserialized) return comment.val();
        annotation = comment.serialize();
        annotation = annotation.replace('comment', 'annotation');
    } else {
        annotation = this.form.find("#id_annotation");
        if(unserialized) return annotation.val();
        annotation = annotation.serialize();
    }

    return annotation;
}
function is_table_expired(table, storage_string){
    table = JSON.parse(table);
    var today = new Date();
    if(today > new Date(table.expire) || typeof(table) == 'string'){
        console.log('removing this entry', storage_string);

        localStorage.removeItem(storage_string);
        return false;
    }
    return true;
}
function update_filter_by_counter(){
    var count_el = $('#filtered_results_count');
    var text_el = $('#filtered_by');
    var count = 0;
    var text = [];
    for(var i = 0; i < check_count_of_tables.length; i++){
        count += buttons[check_count_of_tables[i]].counter_value;
    }
    for(var i = 0; i < check_count_of_filters.length; i++){
        var temp = $(check_count_of_filters[i] + " :selected");
        if(temp.val()){
            text.push(temp.text());
        }
    }
    count_el.closest('div').toggle(!!text.length);
    count_el.text(count);
    text_el.text(text.join(' and '));
}
function update_table_by_filter(me){
    // loop through the tables that are not the current table and update them with the new filter options applied

    function _reload(view){
        return function __reload(){
            buttons[view].update_table();
        }
    }
    var count = 1;
    for(var view in buttons){
        if(buttons[view] != me){
            setTimeout(_reload(view), 1000*count);
            count++;
        }
    }
}
function lazy_load_tables(){
    // init button if it is not ready, and has not already tried to be initialized
    for(var button in buttons){
        if(!buttons[button].ready && !buttons[button].init_called){
            buttons[button].init();
        }
    }
}
function get_meter_set_column_position(){
    /**
    * return the position of the Meter Set column.
    * */
    var element = CURRENT_TABLE.datatable_holder.find('thead th').filter(function(index){
       return $(this).text().toLowerCase() === 'meter set';
    });

    return CURRENT_TABLE.datatable_holder.find('thead th').index(element);
}
function get_meter_set_dates(){
    /**
    * return an object of {dates, ids, builder_agreements} for items exceeding builder agreements.
    * */
    var position = get_meter_set_column_position();
    var dates = [];
    CURRENT_TABLE.datatable_holder.find('tbody tr').each(function(index, element){
        var el = $(element);
        var ba_id = parseInt($(el.find('td')[0]).find('input:checked').attr('data-builder-agreement-id'));

        if(CURRENT_TABLE.builder_agreements_exceeded.indexOf(ba_id) != -1){
            // builder agreement is being exceeded

            var text = $(el.find('td')[position]).text();
            var select_id = el.attr('id');
            dates.push({'date': new Date(text), 'id': select_id, 'builder_agreement': ba_id})
        }
    });
    return dates;
}
function unselect_checkboxes(e){
    /**
    * Sort the list of dates and uncheck dates in order.
    * Unselect newest first.
    * */
    e.preventDefault();
    CURRENT_TABLE.datatable_holder.find(".checkall").prop('checked', false);
    var dates = get_meter_set_dates();
    dates.sort(function(a, b){
        if(a.date > b.date) return -1;
        if(a.date < b.date) return 1;
        return 0
    });


    for(var i = 0; i < dates.length; i++){
        if(CURRENT_TABLE.builder_agreements_exceeded.length){
            var obj = dates[i];
            console.log('unchecking', obj.id);
            $("tr#"+obj.id).find('input').prop('checked', false).trigger('change');
        }
    }
}
function reload_form_from_refresh_button(e){
        /*
        * Made for 'Approved for Payment'.
        * The page is loaded with the builders that are available in the table.
        * As stats are progressed through the system. more builders may be made available.
        * This prevents the user from having to reload the page.
        * */
    if (CURRENT_TABLE.title !== 'Approved For Payment') {
        return;
    }
    if (e !== undefined) {
        e.preventDefault();
    }
    console.log("Refreshing customer dropdown for Approved For Payment");
    CURRENT_TABLE.form_holder.html("<h4><i class='fa fa-spin fa-spinner'></i> Reloading Form</h4>");
    CURRENT_TABLE.get_form();
}

//-------------------------------- SUBMISSION SETUPS -----------------------------------------------
function annotation_submission_setup(progress_bar){
    var data = [];
    var submit = this.get_submit_type();
    var annotation = get_annotation.call(this);
    for(var i = 0; i < this.selected.length; i++){
        data.push([
            this.csrf,
            annotation,
            'stats='+this.selected[i],
            'progress='+progress_bar,
            'submit='+submit
        ]);
    }
    return data;

}
function revert_submission_setup(progress_bar){
    var data = [];
    var submit = this.get_submit_type();
    var annotation = get_annotation.call(this);
    for(var i = 0; i < this.selected.length; i++){
        data.push([
            this.csrf,
            annotation,
            'stats='+this.selected[i],
            'progress='+progress_bar,
            'submit='+submit
        ])
    }

    var confirmation = confirm("Are you sure you want to revert the selected homes to Received?");
    return confirmation ? data : false
}
function create_incentive_submission_setup(progress_bar){
    var data = [];
    var submit = this.get_submit_type();
    var customer = this.form.find('#id_customer').serialize();
    var check_req_date = this.form.find('#id_check_requested_date').serialize();
    var annotation = get_annotation.call(this);
    var stats = [];
    for (var i in this.selected) {
        stats.push('stats=' + this.selected[i]);
    }
    data.push([
        this.csrf,
        customer,
        check_req_date,
        annotation,
        stats.join('&'),
        'progress='+progress_bar,
        'submit='+submit
    ]);

    return data;
}
function advance_state_submission_setup(progress_bar){
    var data = [];
    var submit = this.get_submit_type();
    var new_state = this.form.find('#id_new_state').serialize();
    var annotation = get_annotation.call(this);
    for(var i = 0; i < this.selected.length; i++){
        data.push([
            this.csrf,
            new_state,
            annotation,
            'stats='+this.selected[i],
            'progress='+progress_bar,
            'number='+i,
            'submit='+submit
        ])
    }
    return data;
}

//-------------------------------- SUBMISSION VALIDATORS -------------------------------------------
function validate_create_incentive_form(checkbox){
    // return false anywhere in this function if you want to stop propagation
    checkbox = $(checkbox);

    // don't need to process the checkall checkbox
    if(checkbox.hasClass('checkall')) return;

    this.set_submit_button_text();
    return true;
}
function validate_advance_state_form(){
    // needs a new state OR an annotation to be defined before being submitted.
    var new_state = this.form.find("#id_new_state").val().trim();
    var annotation = this.form.find("#id_annotation").val().trim();
    return Boolean(new_state || annotation);
}

//-------------------------------- VALIDATORS ------------------------------------------------------
function state_change_handler(){
    /**
    * Called when state changes in query form.
    * Reinstates new_states defaults, then removes the unacceptable ones.
    */
    var selected_state = $('#id_state').find('option:selected').val();
    if(this.form){
        if(this.form.find('#id_new_state').length != 0){
            new_state = this.form.find('#id_new_state');
            new_state.empty().append(this.select_defaults);
            invalid_states[selected_state].forEach(function(invalid_state, i){
                new_state.find('option[value="'+invalid_state+'"]').remove();
            });
            new_state.val('');
        } else {
            console.log("changing out state options does not apply here...")
        }
    }
    console.log('-- Changed State : ', selected_state, ' --');
}

//-------------------------------- GLOBAL VARS -----------------------------------------------------
var CURRENT_TABLE = 0;
var buttons = {};
var progress_bars = [];
var toggle = false;
var new_state = null;
var skeleton_expiration = 1; //number of days to keep table skeletons in localstorage
var new_state_defaults = null;
var clear_filters_on_table_reload = true;
var check_count_of_tables = [ 'pending', 'received', 'required', 'approved'];
var check_count_of_filters = [ '#id_builder', '#id_provider', '#id_eep_program', '#id_subdivision', '#id_activity_start', '#id_activity_stop'];
var invalid_states = {
        'start': [
            'start',
            'ipp_failed',
            'ipp_failed_restart',
            'ipp_payment_automatic_requirements',
            'payment_pending',
            'complete'
        ],
        'ipp_failed_restart': [
            'ipp_failed_restart',
            'ipp_payment_automatic_requirements',
            'payment_pending',
            'complete'
        ],
        'ipp_payment_failed_requirements': [
            'start',
            'ipp_payment_requirements',
            'ipp_payment_automatic_requirements',
            'payment_pending',
            'complete',
            'ipp_payment_failed_requirements'
        ],
        'ipp_payment_automatic_requirements': [
            'ipp_payment_requirements',
            'ipp_payment_automatic_requirements',
            'payment_pending',
            'complete',
            'ipp_payment_failed_requirements',
            'ipp_failed_restart'
        ],
        'payment_pending': [
            'start',
            'ipp_payment_requirements',
            'ipp_payment_automatic_requirements',
            'payment_pending',
            'complete',
            'ipp_payment_failed_requirements',
            'ipp_failed_restart'
        ],
        'complete': [
            'start',
            'ipp_payment_requirements',
            'ipp_payment_automatic_requirements',
            'payment_pending',
            'complete',
            'ipp_payment_failed_requirements',
            'ipp_failed_restart'
        ]
    };


$(function () {


    //-------------------------------- OBJECTS ---------------------------------
    function Button(options){
        // for internal use
        this.form_suffix = options.form_suffix || '_form';
        this.table_suffix = options.table_suffix || '_table';
        this.skeleton_suffix = options.skeleton_suffix || '_skeleton';
        this.counter_element = options.counter_element || false;
        this.filter_form_name = options.filter_form_name || '#query_form';

        // DOM elements
        this.el = $(options.element);
        this.parent_element = options.parent_element ? $(options.parent_element) : false;
        this.form_holder = $(options.element + this.form_suffix);
        this.datatable_holder = $(options.element + this.table_suffix);
        this.filter_form_holder = $(this.filter_form_name);
        this.results_counter = this.counter_element ? $(this.counter_element) : this.el.find('.counter');
        this.results_counter = $(this.counter_element);

        // regular variables
        this.init_called = false;  // in the process of being initialized
        this.ready = false;  // datatable and form are loaded
        this.datatable_loaded = false;  // flag for after datatable data is loaded
        this.form_loaded = false;  // flag for after form data is loaded
        this.active = options.active || false;  // which view is active
        this.text = options.text;
        this.title = options.title;
        this.filter_state = options.filter_state || '';
        this.form_url = options.form_url || '';
        this.datatable_url = options.datatable_url;
        this.submit_validator_string = options.submit_validator_string || false;
        this.state_change_handler_string = options.state_change_handler_string || false;
        this.submit_handler_string = options.submit_handler_string || false;
        this.counter_value = 0;
        this.select_all_toggle = false;
        this.local_storage_string = this.datatable_holder.attr('id')+"_"+window.user_id+"_"+this.datatable_url + this.skeleton_suffix;
        this.validate_on_checkbox = options.validate_on_checkbox || false;
        this.dependent_tables = options.dependent || false;
        this.propagate_filter_changes = options.propagate_filter_changes || true;
        this.disallow_filter_by = options.disallow_filter_by || [];
        this.filter_form_fields = this.get_filter_form_fields();
        this.filterable = options.filterable || true;
        this.builder_agreements_exceeded = [];

        console.log(this.title, this.disallow_filter_by);

        if(this.active){
            this.el.addClass('btn-primary')
        }

        // get from form ajax
        this.form = null;
        this.csrf = null;
        this.form_fields = [];
        this.submit_url = null;
        this.submit_button = null;
        this.select_defaults = null;

        // get from datatable ajax
        this.datatable_skeleton = localStorage.getItem(this.local_storage_string);
        this.initialized_datatable = null;

        // add on usage
        this.progress_bars = [];
        this.selected = [];

        // Listeners
        this.el.on('click', function(e){
            e.preventDefault();
            if(this.active){
                this.update_table();
            } else {
                this.show_datatable();
                this.active = true;
                $('.btn-block').removeClass('btn-primary');
                $('.btn-block li').removeClass('active');
                if(this.parent_element){
                    this.parent_element.addClass('btn-primary');
                    this.el.parent().addClass('active')
                }
                this.el.addClass('btn-primary');
            }
        }.bind(this));

        this.set_element_title();

    }
    Button.prototype = {
        /*
        * Some functions use the 'me' variable.
        * Inside jQuery Ajax calls, 'this' refers to the ajax call object,
        *    while 'self' refers to the window object.
        * Something else was needed to refer to the object at hand. Hence 'me'.
        * When making a method that has to use 'me', declare at the top and use for all
        *   'this' references.
        */
        // GENERAL METHODS
        init: function(){
            this.init_called = true;
            this.get_form();
            this.get_datatable();
            if(this.active){
                this.activate_form();
                this.datatable_holder.show();
            }
        },
        check_ready_status: function(){
            // checking for initialized datatable because first Button will not have datatable_skeleton
            if(this.datatable_loaded && this.form_loaded){
                this.ready = true;
                if(this.parent_element) this.parent_element.attr('disabled', false);
                this.el.attr('disabled', false);
                $('#table_loading').hide();
                lazy_load_tables();
            }
        },
        set_element_title: function(){
            this.el.find('.title').text(this.title);
        },
        // FORM METHODS
        _form_success: function(data){
            /*
            * If form success handler is called from within $.ajax(), must be called as
            * this._form_success.bind(this)
            * */
            this.form = $(data);
            this._initialize_form();
            this.form_holder.html(this.form);
            this.form_holder.find('select').trigger('change');
            this.form_loaded = true;
            this.check_ready_status();
        },
        _initialize_form: function(){
            this.submit_url = this.form.attr('action');
            this.csrf = this.form.find('input[name="csrfmiddlewaretoken"]').serialize();
            this.submit_button = this.form.find('input[type="submit"]');

            this._set_form_listeners();
            this._set_form_display_attributes();

            this.select_defaults = this.form.find('.select').children();
            if(this.state_change_handler_string) this.state_change_handler();

            this.form.find('.dateinput').datepicker({dateFormat: 'yyyy-mm-dd'});

        },
        _set_form_display_attributes: function(){
            this.form.find('#id_annotation, #id_comment').attr('rows', 2);
            this.form.find('#div_id_stats').hide();
        },
        _get_form_fields: function(){
            return this.form.find('.controls').children().toArray();
        },
        _set_form_listeners: function(){
            this.form_fields = this._get_form_fields();
            var me = this;
            me.form_fields.forEach(function(el, i){
                $(el).on('change', function(){
                    me.set_submit_button_text();
                    if(me.submit_validator_string){
                        me.submit_validator();
                    }
                })
            });
            me.form.on('click', 'input:submit', function(){
                $(this).addClass('clicked_submit')
            });
            me.form.on('submit', function(e){
                e.preventDefault();
                if(me.submit_validator_string){
                    if(me.submit_validator()){
                        me.submit_form()
                    } else {
                        console.log("something went wrong.")
                    }
                } else {
                    console.log('assuming everything is okay');
                    me.submit_form()
                }
            });
        },
        get_form: function(){
            var me = this;
            if(me.form_url){
                $.ajax({
                    type: 'GET',
                    url: me.form_url,
                    success: me._form_success.bind(this)
                })
            } else {
                me.form_loaded = true;
            }
        },
        get_filter_form_fields: function(){
            var temp = {};
            this.filter_form_holder.find('.form-control').each(function(index, value){
                temp[$(value).attr('id')] = $(value);
            });
            return temp;
        },
        get_clicked_submit_button: function(){
            return this.form.find('.clicked_submit') || '';
        },
        get_submit_type: function(){
            return this.get_clicked_submit_button().val().toLowerCase();
        },
        get_form_submission_setup_handler: function(){
            /*
            * If the submit button pressed is "Update" stick with the regular supplied handler.
            * If the submit button is 'annotate' or 'revert' return a different one.
            * */
            var submit = this.get_submit_type();
            var validators = {
                'update': window[this.submit_handler_string],
                'annotate': annotation_submission_setup,
                'revert': revert_submission_setup
            };
            return validators[submit].bind(this);
        },
        submission_handler: function(progress_bar){
            return this.get_form_submission_setup_handler()(progress_bar)
        },
        get_state_change_handler: function(){
            return window[this.state_change_handler_string].bind(this);
        },
        state_change_handler: function(){
            return this.get_state_change_handler()();
        },
        get_submit_validator: function(){
            return window[this.submit_validator_string].bind(this);
        },
        submit_validator: function(args){
            return this.get_submit_validator().call(this, args);
        },
        set_submit_button_text: function(){
            // called from show_hide_form and _set_form_listeners
            var val = this.form.find("#id_new_state, #id_customer").val();
          // var exceeding = this.builder_agreements_exceeded.length !== 0;
          var text = val ? "Update" : "Annotate";
            this.form.find('input:submit[value="Update"], input:submit[value="Annotate"]').val(text);

            // Hide the revert button if in annotation mode
//            this.form.find("input:submit[value='Revert']").toggle(text !== "Annotate");
        },
        hide_form: function(){
            // hide the part of the form controlled by the status of selected
            this.form_holder.find('.hide-form').slideUp();
        },
        show_form: function(){
            // show the part of the form controlled by the status of selected
            this.form_holder.find('.hide-form').slideDown();
        },
        show_hide_form: function(){
            if(this.form){
                $('#datatable_holder').removeClass('col-md-12').addClass('col-md-9');
                $('#form_holder').show('slow');
                if (this.selected.length == 0) {
                    $('#instructions').slideDown();
                    this.hide_form();
                } else {
                    $('#instructions').slideUp();
                    this.show_form();
                    this.set_submit_button_text();
                }
            } else if(this.form_url == '' && !this.filterable) {
                $('#form_holder').hide('slow');
                $('#datatable_holder').removeClass('col-md-9').addClass('col-md-12');
            }
        },
        activate_form: function(){
            // show the part of the form controlled by what table is in view
            this.form_holder.slideDown();
            $.each(this.filter_form_fields, function(index, element){
                $(element).closest('.form-group').toggle(!($.inArray($(element).attr('id'), this.disallow_filter_by) > -1))
            }.bind(this));
            var s = $('#id_state');
            s.val(this.filter_state);
            s.attr('disabled', !!this.filter_state);
            if(this.state_change_handler_string) this.state_change_handler();
            this.show_hide_form();
        },
        deactivate_form: function(){
            // hide the part of the form controlled by what table is in view
            this.form_holder.slideUp();
            this.hide_form();
        },
        pre_submit: function(){
            /* called if anything general needs to be done before submitting. */
            // TODO: make sure this cancels the submission.
            // TODO: make sure this only gets triggered on update, and not annotate or revert.
            // TODO: Double check if we want a message still, or just let the server kick back an error.
            var submit = this.get_submit_type();

            this.form.find('.clicked_submit').attr('disabled', 'disabled')
            if(submit == 'update' && this.builder_agreement_exceeded) {
                alert("The number of homes paid on this agreement has been reached.");
                return false;
            }
        },
        post_submit: function(){
            /* called if anything general needs to be done after submitting. */
            this.form.find('#id_annotation, #id_comment').val('');
            this.form.find('#id_new_state').val('');
            var me = this;
            setTimeout(function(){
                me.form.find('.clicked_submit').removeClass('clicked_submit').removeAttr('disabled')
            }, 500);
        },
        submit_form: function(){
            var me = this;
            this.pre_submit();

            var for_submission = this.submission_handler(progress_bar);
            if(!for_submission){
                // in the case Revert is hit, and they cancel the action. Don't submit.
                console.log("Revert was Cancelled");
                return false;
            }

            var bar = new Bar(this.selected.length, progress_bars.length, this);
            progress_bars.push(bar);
            this.progress_bars.push(bar);

            bar._total_questions = for_submission.length;

            var total_questions = for_submission.length;

            for(var k = 0; k < total_questions; k++){
                $.ajax({
                    type: 'POST',
                    url: me.submit_url,
                    data: for_submission[k].join('&'),
                    dataType: 'json',
                    success: function(response, status, xhr){
                        if(response.success){
                            console.log('success');
                            bar.success(response.success);
                        }
                        if(response.info){
                            console.log('info');
                            bar.info(response.info);
                        }
                        if(response.error){
                            console.log('error');
                            bar.error(response.error);
                        }
                    },
                    error: function(response, status, error){
                        console.log('ERROR');
                        console.log(response, status, error);
                        bar.error(response)
                    }
                });
            }
            this.post_submit();
        },
        show_warning: function(message){
            this.form.find(".messages").html(message).show();
        },
        hide_warning: function(){
            this.form.find(".messages").html('').hide();
        },
        // DATATABLE METHODS
        get_datatable_options: function(){
            var me = this;
            var state = me.filter_state;
            var options = {ajax: {}};
            options.ajax.data = function (data) {
                data.builder_id = $('#id_builder').val();
                data.provider_id = $('#id_provider').val();
                data.subdivision_id = $('#id_subdivision').val();
                data.eep_program_id = $('#id_eep_program').val();
                data.activity_start = $('#id_activity_start').val();
                data.activity_stop = $('#id_activity_stop').val();
                data.state = state;
            };
            options.fnDrawCallback = function(oSettings){
                me.datatable_loaded = true;
                me.update_counter(oSettings.fnRecordsTotal());
                me.check_ready_status();
                update_filter_by_counter();
            };
            return options;
        },
        get_datatable: function(){
            var me = this;
            if(me.datatable_holder.find('.datatable').length){

                me.initialized_datatable = me.datatable_holder.find('.datatable').dataTable();
                me.initialized_datatable.find('[data-name="select"]')
                    .unbind('click')
                    .html('Select All<br><input class="checkall" type="checkbox">');

            } else {

                if(me.datatable_skeleton && is_table_expired(me.datatable_skeleton, me.local_storage_string)){

                    me.datatable_skeleton = JSON.parse(me.datatable_skeleton).skeleton;
                    me.datatable_holder.html(me.datatable_skeleton);
                    me.initialized_datatable = datatableview.initialize(
                        me.datatable_holder.find('.datatable'), me.get_datatable_options());
                    me.initialized_datatable.find('[data-name="select"]')
                    .unbind('click')
                    .html('Select All<br><input class="checkall" type="checkbox">');

                    me.check_ready_status();

                } else {

                    $.ajax({
                        type: 'GET',
                        url: me.datatable_url,
                        dataType: 'json',
                        success: function(data){
                            me.datatable_skeleton = data;
                            // initialize right mheh
                            me.datatable_holder.html(me.datatable_skeleton);
                            me.initialized_datatable = datatableview.initialize($(me.datatable_holder).find('.datatable'), me.get_datatable_options());
                            me.initialized_datatable.find('[data-name="select"]')
                                .unbind('click')
                                .html('Select All<br><input class="checkall" type="checkbox">');

                            var store_time = new Date();
                            store_time.setDate(store_time.getDate() + skeleton_expiration);
                            var store = {
                                expire: store_time,
                                skeleton: me.datatable_skeleton
                            };

                            localStorage.setItem(me.local_storage_string, JSON.stringify(store));

                            // check to see if the datatable and form are ready
                            me.check_ready_status();

                        }
                    });
                }
            }
        },
        update_counter: function(value){
            this.counter_value = value;
            this.results_counter.text(value)
        },
        uncheck_all: function(){
            // uncheck all the checkboxes when a uses navigates away from it.
            this.initialized_datatable.find(':checkbox:checked').each(function(){
                $(this).prop('checked', false).change();
            });
            this.select_all_toggle = false;
            this.datatable_holder.find('.checkall').prop('checked', false);

        },
        hide_datatable: function(){
            this.active = false;
            this.deactivate_form();
            $(this.datatable_holder).slideUp('slow');
            this.uncheck_all();
        },
        show_datatable: function(){
            CURRENT_TABLE.hide_datatable();
            this.active = true;
            $(this.datatable_holder).slideDown();
            this.activate_form();
            CURRENT_TABLE = this;
            reload_form_from_refresh_button();
            console.log(CURRENT_TABLE.selected, 'from show_datatable')
        },
        update_table: function(){
            // This method gets called from Bar.complete_text() and query_form listener
            while(this.selected.length){
                this.initialized_datatable
                    .find('[data-id="'+this.selected[0]+'"]')
                    .attr('checked', false)
                    .change();
            }
            if(this == CURRENT_TABLE){
                this.show_hide_form();
                if(this.propagate_filter_changes){
                    update_table_by_filter(this)
                }
            }

            if(this.form && this.form.find("#id_customer")){
                this.form.find("#id_customer").val(query_form.find("#id_builder").val());
            }

            this.initialized_datatable.DataTable().draw();
            this.select_all_toggle = false;
            this.datatable_holder.find('.checkall').prop('checked', false);
        },
        update_dependent_tables: function(){
            // This method gets called from Bar.complete_text()
            if(this.dependent_tables && this == CURRENT_TABLE){
                for(var view in this.dependent_tables){
                    buttons[this.dependent_tables[view]].update_table();
                }
            }
        },
    };

    var ProgressBarMixin = {
        init_progress_bar: function(){
            var p_bar = progress_bar.clone().attr('id', this._id);
            window.b = p_bar;
            p_bar.prepend(processing.clone(), close_button.clone());
            p_bar.find('.progress')
                .append(progress_success.clone(), progress_error.clone(), progress_info.clone());

            $('#processing').append(p_bar)
        },
        init_modal: function(){
            // make the modal and grab some pieces of it.
            this.modal = modal.clone().attr('id', this._modal_id);
            this.modal_body = this.modal.find('.modal-body');
            this.set_modal_title();
            this.set_panel_footers();

            $('#modal_wrapper').append(this.modal);
            this.modal.on('click', '.undo', function(e){
                this.undo_transition();
            }.bind(this));
        },
        set_modal_title: function(){
            if(this.button.title == 'Approved For Payment'){
                if(this.submit_type == 'update'){
                    text = "Incentive Distribution Created.";
                } else if(this.submit_type == 'annotate'){
                    text = "Annotation added."
                } else {
                    text = "State reverted to 'Received'."
                }
            } else {
                var text = "";
                var new_state = this.button.form.find("#id_new_state :selected");
                if(new_state.val()){
                    text += $("#query_form").find('#id_state :selected').text();
                    text += ' -> ';
                    text += new_state.text();
                } else {
                    text += "Annotation Added";
                }
            }
            this.modal.find('.modal-title').text(text);
        },
        set_panel_footers: function(text){
            if(!this.footer_set){
                if(!text){
                    text = get_annotation.call(this.button, true);
                }
                if(text){
                    text = "Annotation: <i>" + text + "</i>";
                    this.modal.find('.panel-footer').show().html(text);
                }
                this.footer_set = true;
            }
        },
        set_heading_text_for_panel: function(panel, text){
            this.modal_body.find('.panel-'+panel+' .panel-heading').text(text)
        },
        append_modal_text: function(target, text){
            this.modal_body.find('.panel-'+target).show().find('.panel-body').append($('<p></p>').html(text));
        },
        allow_undo: function(){
            this.modal.find('.undo').show();
        },
        progress_text: function(){
            var text = this._total_complete + " out of " + this._total_questions + " complete.";
            this.info_text.text(text);
        },
        complete_text: function(){
            // all the queries are done, now is time to refresh the table
            this.button.update_table();
//            this.button.update_dependent_tables();
            var text = this._total_questions + " items processed. ";
            this.info_text.html(text).append(this.modal_button)
        },
        success: function(response){
                console.log(response);
                this._success++;
                this._success_progress.width((this._success/this._total_questions)*100 + "%");

                if('annotation' in response) this.set_panel_footers(response.annotation);
                if('url' in response) this.append_modal_text('success', response.url);

                if('builder_breakdown' in response){
                    this.append_modal_text('success', builder_agreement_info_template(response.builder_breakdown))
                }

                if('undo' in response){
                    this.can_undo = true;
                    this.undo_state = response.undo.old_state;
                    this.undo_stats.push(response.id);
                    this.allow_undo();
                }

                this.total();
        },
        info: function(response){
            if(this._info == 0) this.set_heading_text_for_panel('info', response.message);
            this._info++;
            this._info_progress.width((this._info/this._total_questions)*100 + "%");
            if('annotation' in response) this.set_panel_footers(response.annotation);
            this.append_modal_text('info', response.url);
            this.total();
        },
        error: function(response){
            this._error++;
            this._error_progress.width((this._error/this._total_questions)*100 + "%");
            var error_string = '';
            var error_strings = [];

            for(var error in response){
                if(error == '__all__') continue;
                error_strings.push(error + ": " + response[error]);
            }
            if(error_strings.length){
                error_string = error_strings.join('<br/>');
            }

            if('__all__' in response){
                error_string += response['__all__'].join('<br/>')
            }
            if($.inArray(error_string, this.messages.error) == -1){
                if(error_string){
                    this.append_modal_text('danger', error_string);
                } else {
                    this.append_modal_text('danger', response.url);
                }
                this.messages.error.push(error_string)
            }
            this.total();
        },
        total: function(){
            this._total_complete = this._success + this._error + this._info;
            if(this._total_complete == this._total_questions){
                this.complete_text();
                this.bar.find('.progress').removeClass('active progress-striped');
            } else {
                this.progress_text();
            }
        },
        kill: function(){
            this.bar.fadeOut();
        },
        undo_transition: function(){
            var undo_button = this.modal.find('.undo');
            undo_button.popover({
                html: true,
                title: 'Undo State Transition',
                content: '<textarea class="textarea form-control" cols="40" rows="2" id="undo_reason" placeholder="Reason for revert..."></textarea>\n<div class="modal-footer">\n    <button class="btn btn-default undo-close" data-dismiss="modal">Cancel</button>\n    <button class="btn btn-primary undo-submit" data-dismiss=\'modal\'>Submit</button>\n</div>',
                placement: 'top'
            });
            undo_button.popover('show');

            $(".undo-close").on('click', function(){
                undo_button.popover('destroy');
            });
            $(".undo-submit").on('click', function(){

                var submit = 'submit=undo';
                var stats = 'stats='+this.undo_stats.join('&stats=');
                var old_state = 'old_state='+this.undo_state;
                var annotation = 'annotation='+$("#undo_reason").val();

                var bar = new UndoBar(this);
                progress_bars.push(bar);
                bar._total_questions = 1;

                $.ajax({
                    type: 'POST',
                    url: this.button.submit_url,
                    data: [submit, stats, old_state, annotation].join('&'),
                    dataType: 'json',
                    success: function(response, status, xhr){
                        if(response.success){
                            console.log('undo success');
                            bar.success(response.success);
                        }
                        if(response.info){
                            console.log('undo info');
                            bar.info(response.info);
                        }
                        if(response.error){
                            console.log('undo error');
                            bar.error(response.error);
                        }
                    },
                    error: function(response, status, error){
                        console.log('UNDO ERROR');
                        console.log(response, status, error);
                        bar.error(response);
                    }
                });
                undo_button.popover('destroy');
                undo_button.addClass('disabled').attr('disabled', true);
            }.bind(this));
        }
    };

    function UndoBar(bar){
        this.bar = bar;
        this.button = bar.button;
        this._id = 'progress_' + progress_bars.length;
        this._modal_id = this._id+'_modal';
        this.modal = null;
        this.modal_body = null;
        this.submit_type = 'undo';
        this.init_progress_bar();
        this.init_modal();

        this.bar = $('#'+this._id);
        this.info_text = this.bar.find('.info-text');
        this.modal_button = modal_button.clone().attr('data-target', '#'+this._modal_id);

        this._success_progress = this.bar.find('.progress-bar-success');
        this._error_progress = this.bar.find('.progress-bar-error');
        this._info_progress = this.bar.find('.progress-bar-info');
        this._total_questions = 1;
        this._total_complete = 0;
        this._success = 0;
        this._error = 0;
        this._info = 0;

        this.messages = { success: [], info: [], error: [] };

        this.footer_set = false;

        this.bar.on('click', '.close', function(e){
            this.kill()
        }.bind(this));
    }
    UndoBar.prototype = Object.create(ProgressBarMixin);
    UndoBar.prototype.set_modal_title = function(){
        this.modal.find('.modal-title').text("Undo Transition to Corrections Required");
    };
    UndoBar.prototype.set_panel_footers = function(text){
        if(text){
            text = 'Annotation: <i>' + text + '</i>';
            this.modal.find('.panel-footer').show().html(text);
        }
    };

    function Bar(total_questions, index, button){
        this.button = button;
        this._id = 'progress_'+index;
        this._modal_id = this._id+'_modal';
        this.modal = null;  // gets set in init_modal
        this.modal_body = null;  // gets set in init_modal
        this.submit_type = !!button ? button.get_submit_type() : 'undo';
        this.init_progress_bar();
        this.init_modal();

        this.bar = $('#'+this._id);
        this.info_text = this.bar.find('.info-text');
        this.modal_button = modal_button.clone().attr('data-target', '#'+this._modal_id);
        this._success_progress = this.bar.find('.progress-bar-success');
        this._error_progress = this.bar.find('.progress-bar-error');
        this._info_progress = this.bar.find('.progress-bar-info');
        this._total_questions = total_questions;
        this._total_complete = 0;
        this._success = 0;
        this._error = 0;
        this._info = 0;

        this.can_undo = false;
        this.undo_state = null;
        this.undo_stats = [];

        this.messages = { success: [], info: [], error: [] };

        // flags
        this.footer_set = false;

        // Listeners
        this.bar.on('click', '.close', function(e){
            this.kill();
        }.bind(this));
    }
    Bar.prototype = Object.create(ProgressBarMixin);

    //-------------------------------- INITIALIZE OBJECTS ---------------------------------
    for(var view in actions){
        var temp = new Button(actions[view]);
        if(temp.active){
            CURRENT_TABLE = temp;
            temp.init();
        }
        buttons[view] = temp
    }

    //start datepickers
    $('#id_activity_start, #id_activity_stop').datepicker();

    // Grab some elements
    var state = $('select#id_state');
    // Default state to disabled because of default first table
    state.attr('disabled', true);
    var state_initial = state.find('option:selected').val();
    var selected_form = $('#selected_form');
    var query_form = $('#query_form');

    //---------------------------- TEMPLATES ---------------------------------
    var processing = $("<span class='info-text'>Processing...</span>");
    var close_button = $("<button type='button' class='close' data-dismiss='modal' aria-hidden='true'>&times;</button>");
    var progress_bar = $("<div id='progress'><div class='progress progress-striped active'></div></div");
    var progress_success = $("<div class='progress-bar progress-bar-success' role='progressbar' aria-valuemin='0' aria-valuemax='100' style='width:0%;'></div>");
    var progress_info = $("<div class='progress-bar progress-bar-info' role='progressbar' aria-valuemin='0' aria-valuemax='100' style='width:0%;'></div>");
    var progress_error = $("<div class='progress-bar progress-bar-error' role='progressbar' aria-valuemin='0' aria-valuemax='100' style='width:0%;'></div>");
    var modal_button = $('<button class="btn btn-default btn-xs" data-toggle="modal" data-target="#myModal"> View Info </button>');
    var modal = $('<div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true"> \
                        <div class="modal-dialog"> \
                            <div class="modal-content"> \
                                <div class="modal-header"> \
                                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button> \
                                    <h4 class="modal-title" id="myModalLabel">Modal title</h4> \
                                </div> \
                                <div class="modal-body"> \
                                    <div class="panel panel-success" style="display:none;"> \
                                        <div class="panel-heading">Successful</div> \
                                        <div class="panel-body"></div> \
                                        <div class="panel-footer" style="display:none;"></div> \
                                    </div> \
                                    <div class="panel panel-info" style="display:none;"> \
                                        <div class="panel-heading"></div> \
                                        <div class="panel-body"></div> \
                                        <div class="panel-footer" style="display:none;"></div> \
                                    </div> \
                                    <div class="panel panel-warning" style="display:none;"> \
                                        <div class="panel-heading"></div> \
                                        <div class="panel-body"></div> \
                                        <div class="panel-footer" style="display:none;"></div> \
                                    </div> \
                                    <div class="panel panel-danger" style="display:none;"> \
                                        <div class="panel-heading">Error</div> \
                                        <div class="panel-body"></div> \
                                        <div class="panel-footer" style="display:none;"></div> \
                                    </div> \
                                </div> \
                                <div class="modal-footer"> \
                                    <button style="display:none;" type="button" class="btn btn-info undo" >Undo</button> \
                                    <!--<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>--> \
                                    <button type="button" class="btn btn-primary" data-dismiss="modal">Close</button> \
                                </div> \
                            </div> \
                        </div> \
                   </div> \
    ');


    //---------------------------- GLOBAL EVENT LISTENERS ---------------------------------
    //Check all checkboxes
    $('#datatable_holder').on('click', '.checkall', function (e) {

        e.stopPropagation();
        if(CURRENT_TABLE.validate_on_checkbox){
            var continue_running = CURRENT_TABLE.submit_validator($(this));
            // stop running if the submit validator returns a false value
            if(continue_running == false) return continue_running;
        }
        CURRENT_TABLE.select_all_toggle = $(this).is(':checked');
        var count = 0;

        CURRENT_TABLE.initialized_datatable.find(':checkbox:not(.checkall)').each(function(){
            var el = $(this);
            if(CURRENT_TABLE.select_all_toggle){
                if(!el.is(':checked')){
                    el.prop('checked', true).trigger('change');
                }
            } else {
                if(el.is(':checked')){
                    el.prop('checked', false).trigger('change');
                }
            }
        });
    });
    // Individual checkboxes
    $('#datatable_holder').on('change', 'table tbody :checkbox', function () {
        if(CURRENT_TABLE.validate_on_checkbox){
            var continue_running = CURRENT_TABLE.submit_validator($(this));
            // stop running if the submit validator returns a false value
            if(continue_running == false) return continue_running;
        }

        var row = $(this).closest('tr');
        var iId = $(row).attr('id');
        var is_in_array = (-1 != $.inArray(iId, CURRENT_TABLE.selected));

        if($(this).is(":checked")){
            if (!is_in_array) {
                CURRENT_TABLE.selected.push(iId);
            }
        } else {
            CURRENT_TABLE.selected = $.grep(CURRENT_TABLE.selected, function(value){
                return value != iId;
            })
        }

        CURRENT_TABLE.form_holder.find('#id_stats').val(CURRENT_TABLE.selected);
        console.log('Current table selected: ', CURRENT_TABLE.title, CURRENT_TABLE.selected);
        CURRENT_TABLE.show_hide_form();
    });

    // Reload the table on filter change
    // Uncheck everything and hide form
    query_form.on('change', function () {
        CURRENT_TABLE.update_table();
    });

    // Listener for add form
    // Filter the table by customer/builder
    // Hide only the submitting part of the form, keep the customer filter
    query_form.on('change', '#id_builder', function(){
        if($('#id_customer').length){
            $('#id_customer').val($(this).val());
        }
    });
    selected_form.on('change', '#id_customer', function(){
        $('#id_builder').val($(this).val()).trigger('change');
    });

    // Listener for showing and hiding Filter options
    $('#toggle_filter').on('click', function (e) {
        if ($(this).text() == 'hide') {
            query_form.slideUp();
            $(this).text('show');
        } else {
            query_form.slideDown();
            $(this).text('hide');
        }
        e.preventDefault();
    }); // END toggle filter listener

    // Listener for clearing filters
    $('#clear_filter').on('click', function(e){
        query_form.find('.form-control:not(#id_state)').each(function(index, element){
            console.log('clearing the filters');
            $(element).val('');
        });
        CURRENT_TABLE.update_table();
    });

    $('body').on('click', '#unselect_checkboxes', unselect_checkboxes);
    $('body').on('click', '.reload_form', reload_form_from_refresh_button);
//    $('body').on('click', 'th', function(e){
//        CURRENT_TABLE.initialized_datatable.find('input:checkbox').each(function(index, element){
//            var el = $(element);
//            if(el.is(":checked")){
//                el.prop('checked', false).trigger('change');
//            }
//        })
//    })
}); // END on ready

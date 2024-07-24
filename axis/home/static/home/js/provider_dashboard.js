/**
 * Created by michaeljeffrey on 8/10/15.
 */

// FEATURES
var FEATURES = {
    certification: {
        active: true
    },
    qa: {
        active: !!window._qa_active || false,
        addNote: true
    },
    notes: {
        active: true
    },
    projecttracker: {
        active: true
    }
};

$(function () {
    var MODE = 'certification',
        MODES = {
            certification: Certification(),
            qa: QA(),
            notes: HomeNotes(),
            projecttracker: ProjectTracker()
        };

    var templates = {
        icons: {
            spinner: _getIcon('fa-spin fa-spinner'),
        }
    };

    var datatable = $(".datatable"),
        resultModal = $("#result-modal"),
        transactionModal = $("#transaction-modal"),
        tabButtons = $("button[data-toggle='tab']"),
        modeInput = $('#mode');

    datatable.on('change', 'tbody :checkbox', checkboxChangeHandler);
    tabButtons.on('click', tabChangeHandler);
    resultModal.on('show.bs.modal', resultModalHandler);
    transactionModal.on('show.bs.modal', showTransactionModalHandler);
    transactionModal.on('hide.bs.modal', hideTransactionModalHandler);

    function resetCheckboxes() {
        datatable.find('.datatable :checkbox:checked').prop('checked', false);
        $('.no-items-selected').toggle(true);
        $('.items-selected').toggle(false);
    }

    function refreshSelectionLabels() {
        // Update labels with counts
        var numItems = datatable.find('tbody :checkbox:checked').length;
        var hasItems = (numItems > 0);
        $('.no-items-selected').toggle(!hasItems);
        $('.items-selected').toggle(hasItems);
        $('.checked-item-counter').text(numItems);
    }

    // Handlers
    function resultModalHandler(event) {
        var button = $(event.relatedTarget || event.target),
            modal = $(this),
            transaction = button.data('transaction');

        modal.find('.modal-title').html(transaction.title);
        modal.find('.modal-body').html(new Transaction(transaction));
    }

    function showTransactionModalHandler(event) {
        // Guard against datepickers triggering the modal handler.
        if ($(event.target).hasClass('dateinput')) return;

        var checked = datatable.find('tbody :checkbox:checked');

        // Make sure they've selected homes.
        if (!checked.length) {
            event.preventDefault();
            alert('Please select some homes.');
            return;
        }

        var currentModeObj = getMode(),
            transaction = getTransactionObj(),
            modal = $(this),
            render = getUpdateUI(modal.find('.modal-body .target'), transaction);

        // Clean data -- transaction is modified in place
        checked.each(cleanData(transaction, render));

        render();

        modal.find('.modal-title').html(transaction.title);
        modal.find('.primary-action').html(transaction.button);
        currentModeObj.showModal(modal);

        var clickHandler = getPrimaryActionHandler(currentModeObj, transaction, modal, checked, render);
        modal.find('.primary-action').on('click', clickHandler);
    }

    function hideTransactionModalHandler(event) {
        // Guard against datepickers triggering the modal hanlder.
        if ($(event.target).hasClass('dateinput')) return;

        var currentModeObj = getMode(),
            modal = $(this);

        // Turn off the click handlers and enable the button for next time.
        modal.find('.primary-action').attr('disabled', false).off('click');

        currentModeObj.hideModal(modal);
    }

    function checkboxChangeHandler(event) {
        var currentModeObj = getMode();

        if (modeIsActive() && currentModeObj.hasOwnProperty('checkboxHandler')) {
            var promise = currentModeObj.checkboxHandler.call(this, event);
            if (promise !== undefined) {
                promise.then(function () {
                    refreshSelectionLabels();
                });
            } else {
                refreshSelectionLabels();
            }
        } else {
            refreshSelectionLabels();
        }

    }

    function tabChangeHandler(event) {
        try {
            MODE = event.target.innerText.toLowerCase();
        } catch (e) {
            // Firefox doesn't have an `innerText`
            MODE = event.target.textContent.toLowerCase();
        }

        var currentModeObj = getMode();
        modeInput.val(MODE);

        if (currentModeObj.hasOwnProperty('tabChangeHandler')) {
            currentModeObj.tabChangeHandler.call(this, event);
        }

        resetCheckboxes();
    }

    function getPrimaryActionHandler(currentModeObj, transaction, modal, checked, render) {
        return function primaryActionHandler() {
            if (!modeIsActive()) return;

            if (currentModeObj.hasOwnProperty('canContinue')) {
                if (!currentModeObj.canContinue(modal)) {
                    return;
                }
            }

            // Disable the button so they can't click it again.
            $(this).attr('disabled', true);

            $(this).prepend(templates.icons.spinner.clone());

            var transactionCompleteFn = _.after(checked.length, function () {
                datatable.dataTable().fnDraw();
                transaction.complete = true;
                modal.find('.form-group').remove();
                modal.find('.fa-spinner').remove();
                updateQuickLinkCounts();
            });
            var progressBar = new AsyncProgressBar(checked.length, '.progress-bar-target');

            progressBar.container.find('.progress')
                .attr('data-target', '#result-modal')
                .attr('data-toggle', 'modal')
                .data('transaction', transaction)
                .addClass(transaction.type + '-results');

            currentModeObj.modifyTransaction(transaction, modal);
            var itemHandler = currentModeObj.getItemHandler(transaction, transactionCompleteFn, render, progressBar);

            transaction.homes.reduce(function (promise, item) {
                return promise.then(function () {
                    var value = itemHandler(item);
                    if (!(value instanceof Promise)) {
                        value = Promise.resolve(value);
                    }
                    return value;
                });
            }, Promise.resolve());

            resetCheckboxes();
        }
    }

    function updateQuickLinkCounts() {
        $(".quick-link .badge").html(templates.icons.spinner.clone());
        $.ajax({
            method: 'GET',
            url: '/api/v2/quick_links/',
            data: {
                'view': 'provider_dashboard'
            },
            success: function (data) {
                _.each(data, function (quick_link) {
                    var el = $("#quick_link_" + quick_link.slug);
                    el.find('.badge').html(quick_link.count);

                    _.each(quick_link.filters, function (filter) {
                        el.find('.filter[data-name="' + filter.name + '"]').attr('data-value', filter.value);
                    });
                });
            },
            error: function (data) {
                console.log(data)
            }
        });
    }

    // Helpers
    function getUpdateUI(target, state) {
        return function updateUI() {
            target.html(new Transaction(state));
        }
    }

    function cleanData(transaction, renderFn) {
        return function _cleanData() {
            var el = $(this),
                id = el.closest('tr').attr('id'),
                homeName = el.parent().siblings().first().html(),
                programName = $(el.parent().siblings().get(2)).html();

            // Get hte program if it already exists.
            var program = _.findWhere(transaction.programs, {name: programName});

            // Make a new entry if the program did not exist.
            if (!program) {
                program = {name: programName, homes: []};
                transaction.programs.push(program);

                var url = '/api/v2' + $(programName).attr('href') + 'note/';
                $.ajax({
                    url: url,
                    cache: true,
                    success: function (data) {
                        if (data.length > 1) {
                            program.footer = data;
                            renderFn()
                        }
                    }
                })
            }

            // push a reference of the home into the program and master home list.
            var homeObj = {id: id, name: homeName, result: null, data: null, el: el};
            transaction.homes.push(homeObj);
            program.homes.push(homeObj);
        }
    }

    function modeIsActive() {
        return FEATURES[MODE].active;
    }

    function getMode() {
        return MODES[MODE];
    }

    function getTransactionObj() {
        return _.clone(getMode().transactionObj, true);
    }

    function _getIcon(classes) {
        return $("<i>").addClass('fa fa-fw').addClass(classes);
    }

    // ======================================== //
    // REGULAR LISTENERS                        //
    // ======================================== //
    var snapshot = $(".list-group.snapshot");

    // Collapse listener
    $("#toggle-snapshot").on('click', function (e) {
        e.preventDefault();
        var el = $(this),
            text = el.text(),
            showText = 'Show Stats',
            hideText = 'Hide Stats';

        if (text == showText) {
            snapshot.slideDown();
            el.text(hideText);
        } else {
            snapshot.slideUp();
            el.text(showText);
        }
    });

    // Filter Listener
    snapshot.on('click', '.list-group-item', function (e) {
        e.preventDefault();
        $("#query_form").find('input:visible, select:visible, #id_exclude_ids').val('');
        $(".select2-container select").val('').trigger('change');

        let quickLinkId = $(this).attr('id');

        if (quickLinkId === 'quick_link_qa-correction-required' ||
            quickLinkId === 'quick_link_qa-correction-received') {
            $('#id_state').val('');
        } else {
            $('#id_state option[value="certification_pending"]').prop('selected', true);
        }

        $(this).find('.filter').each(function (e) {
            var el = $(this),
                name = el.attr('data-name'),
                value = el.attr('data-value');

            var target = $("#id_" + name);

            if (target.length == 0) {
                // check if an extra '_id' is making jquery return nothing.
                target = $("#id_" + name.replace('_id', ''));
            }

            if (target.hasClass('select2multiplewidget')) {
                if (value.indexOf('[') > -1) {
                    value = JSON.parse(value);
                }
                target.select2('val', value);
            } else {
                target.val(value);
            }
        });
        // apply the filters.
        $("#query_form").trigger('change');

        $("form").one('change', function () {
            snapshot.find('.active').removeClass('active');
        });
        $(this).addClass('active');
    });

    // Clear Filters
    $("#clear-filters").on('click', function (e) {
        e.preventDefault();
        $("a.list-group-item").removeClass('active');
        $("#query_form").find('input:visible, select:visible').val('');
        $(".select2-container").select2('val', '');
        $('#id_state option[value="certification_pending"]').prop('selected', true);
        datatable.dataTable().fnDraw();
    });
});

var CheckBox = (function () {
    var wrapper = $("<div>").addClass('checkbox form-group'),
        label = $("<label>"),
        checkbox = $("<input type='checkbox'/>").attr('checked', 'checked');

    function CheckBox(options) {
        this.options = options;
        this.render();
        return this.el;
    }

    CheckBox.prototype.render = function render() {
        var _label = label.clone().append(checkbox.clone(), this.getText());

        this.el = wrapper.clone().append(_label);
    };
    // FIXME: This is specific to Notes
    CheckBox.prototype.getText = function getText() {
        return "Is public";
    };
    return CheckBox;
})();
var TextArea = (function () {
    var textarea = $("<textarea>").addClass('form-control').attr('placeholder', 'Note...');

    function TextArea(options) {
        this.options = options;
        this.render();
        return this.el;
    }

    TextArea.prototype.render = function render() {
        var group = div('form-group'),
            label = div('control-label', 'label').text(this.options.label),
            inputWrapper = div('controls'),
            input = textarea.clone();

        this.el = group.append(label, inputWrapper.append(input));
    };

    function div(classes, el) {
        el = !!el ? "<" + el + ">" : '<div>';
        return $(el).addClass(classes);
    }

    return TextArea;
})();
var DatePickerInput = (function () {
    /**
     * <div class='form-group'>
     *     <label class='control-label'>Certification Date</label>
     *     <div class='controls'>
     *          <div class='input-group date'>
     *              <input type='text' value='todays date'/>
     *              <div class='input-group-addon'><i class='fa fa-calendar'></i></div>
     *          </div>
     *     </div>
     *  </div>
     * @type {*|jQuery}
     */

    var formGroup = div('form-group'),
        label = div('control-label', 'label').text('Certification Date'),
        inputWrapper = div('controls'),
        inputGroup = div('input-group date'),
        datePickerButton = div('input-group-addon').append(div('fa fa-calendar', 'i')),
        datePickerInput = $("<input type='text' />")
            .addClass('dateinput form-control')
            .attr('placeholder', 'Certification Date...')
            .attr('data-provide', 'datepicker')
            .attr('data-date-format', 'm/d/yyyy')
            .attr('data-date-today-btn', false)
            .attr('data-date-autoclose', true)
            .val(moment().format('M/D/YYYY'));


    function DatePickerInput(options) {
        this.options = options;
        this.render();
        return this.el;
    }

    DatePickerInput.prototype.render = function render() {
        this.el = div('row').append(
            div('col-md-6').append(
                formGroup.clone().append(
                    this.getLabel(),
                    this.getInput()
                )
            )
        );
    };
    DatePickerInput.prototype.getLabel = function getLabel() {
        return label.clone();
    };
    DatePickerInput.prototype.getInput = function getInput() {
        return inputWrapper.clone().append(
            inputGroup.clone().append(
                datePickerInput.clone(),
                datePickerButton.clone()
            )
        );
    };

    function div(classes, el) {
        el = !!el ? "<" + el + ">" : '<div>';
        return $(el).addClass(classes);
    }

    return DatePickerInput;
})();
var Transaction = (function () {
    var wrapper = $("<div>");

    function Transaction(options) {
        this.options = options;
        this.render();
        return this.el;
    }

    Transaction.prototype.render = function render() {
        this.el = wrapper.clone();
        this.el.append(this.getPrograms());
        if (this.options.hasOwnProperty('extraText')) {
            this.el.append(this.getExtraText());
        }
    };
    Transaction.prototype.getPrograms = function getPrograms() {
        return this.options.programs.map(function (program) {
            return new Program(program);
        });
    };
    Transaction.prototype.getExtraText = function getExtraText() {
        if (this.options.complete) {
            return this.options.extraText();
        }
    };

    function div(classes, el) {
        el = !!el ? "<" + el + ">" : '<div>';
        return $(el).addClass(classes);
    }

    return Transaction;
})();
var Program = (function () {
    var panel = {
        wrapper: div('panel panel-default'),
        heading: div('panel-heading'),
        title: div('panel-title', 'h5'),
        body: div('list-group', 'ul'),
        footer: div('panel-footer')
    };

    function Program(options) {
        this.options = options;
        this.render();
        return this.el;
    }

    Program.prototype.render = function render() {
        this.el = panel.wrapper.clone();
        this.el.append(this.getHeader());
        this.el.append(this.getHomes());
        this.el.append(this.getFooter());
    };
    Program.prototype.getHeader = function getHeader() {
        return panel.heading.clone().html(panel.title.clone().html(this.options.name));
    };
    Program.prototype.getHomes = function getHomes() {
        var html = this.options.homes.map(function (home) {
            return new Home(home);
        });
        return panel.body.clone().html(html);
    };
    Program.prototype.getFooter = function getFooter() {
        if (this.options.footer) {
            return panel.footer.clone().html(this.options.footer);
        }
    };

    function div(classes, el) {
        el = !!el ? "<" + el + ">" : '<div>';
        return $(el).addClass(classes);
    }

    return Program;
})();
var Home = (function () {
    var successClass = 'list-group-item-success',
        errorClass = 'list-group-item-danger',
        li = $("<li>").addClass('list-group-item'),
        heading = $("<h5>").addClass('list-goup-item-heading'),
        body = $("<p>").addClass('list-group-item-text');

    function Home(options) {
        this.options = options;
        this.render();
        return this.el;
    }

    Home.prototype.render = function render() {
        this.el = li.clone();
        this.el.attr('data-id', this.options.id);
        this.el.html(this.getText());
        this.el.addClass(this.getClass());
    };
    Home.prototype.getText = function getText() {
        return [this.getHeading(), this.getBody()];
    };
    Home.prototype.getClass = function getClass() {
        var status = this.options.result;
        return status == 'success' ? successClass : status == 'error' ? errorClass : '';
    };

    Home.prototype.getHeading = function getHeading() {
        return heading.clone().html(this.options.name);
    };
    Home.prototype.getBody = function getBody() {
        return body.clone().html(this.options.data || 'Pending...');
    };
    return Home;
})();

var Certification = (function () {
    var datatable = $(".datatable"),
        MessagingService = angular.element($('[ng-app]')).injector().get('MessagingService');

    var templates = {
        icons: {
            spinner: _getIcon('fa-spin fa-spinner'),
        },
        cannotCertify: $("<span>Cannot be Certified. <span class='popover-target btn btn-xs btn-default'>Why Not?</span></span>"),
    };
    var urls = {
        certify: function (id) {
            return '/api/v2/homestatus/' + id + '/certify/';
        },
        check: function (id) {
            return '/api/v2/homestatus/' + id + '/can_certify/';
        }
    };
    var messageOptions = {
        html: true,
        level: 'error',
        title: 'Error',
        content: null
    };
    var transactionObj = {
        programs: [],
        homes: [],
        complete: false,
        certificationDate: null,
        title: 'Certification',
        button: 'Certify',
        type: 'certification',
        extraText: function () {
            return "Certification Date: " + this.certificationDate;
        }
    };

    return {
        showModal: showModal,
        hideModal: hideModal,
        canContinue: canContinue,
        modifyTransaction: modifyTransaction,
        getItemHandler: getCertifyHandler,

        checkboxHandler: checkboxHandler,
        tabChangeHandler: tabChangeHandler,
        transactionObj: transactionObj
    };

    function showModal(modal) {
        var datepicker = new DatePickerInput();

        modal.find('.modal-body').append(datepicker);
    }

    function hideModal(modal) {
        modal.find('.form-group').remove();
    }

    function canContinue(modal) {
        if (!modal.find('.dateinput').val()) {
            alert('Please select a Certification Date.');
            return false;
        }
        return true;
    }

    function modifyTransaction(transaction, modal) {
        transaction.certificationDate = modal.find('.dateinput').val();
    }

    function checkboxHandler() {
        /**
         * When a checkbox is changed, we want to determine if it can be certified or not.
         * Because of the nature of checking the eligibility of an item, we wait until
         * the user click the checkbox to see if they can move forward.
         * Hopefully this step can be removed in the future.
         */
        // pop out early if they're unchecking the box
        if (!this.checked || $(this).find('.fa-spinner').length > 0) {
            return;
        }

        var checkbox = $(this),
            td = checkbox.parent(),
            row = checkbox.closest('tr'),
            id = row.attr('id'),
            spinner = templates.icons.spinner.clone();

        checkbox.hide();
        td.append(spinner);

        return $.ajax({
            url: urls.check(id),
            success: function () {
                checkbox.show()
            },
            error: errorHandler,
            complete: function () {
                spinner.remove();
            }
        });

        function errorHandler(data) {
            var popover = templates.cannotCertify.clone();
            row.addClass('warning');
            td.html(popover);

            // Trigger the messages
            messageOptions['content'] = data.responseJSON.join('<br/>');
            popover.find('.popover-target').popover(messageOptions);
            MessagingService.introduceExternalMessage(messageOptions);
        }
    }

    function tabChangeHandler() {
        // change qastatus to '-----' and cause table draw.
        $('#id_state').val('certification_pending').trigger('change').removeAttr('disabled');
        $("#id_qastatus").val('').trigger('change');  // QA Addable
    }

    // Helpers
    function getCertifyHandler(transaction, refreshTableFn, renderFn, progressBar) {
        return function certify(home) {
            var handlers = getAjaxHandlers(home, progressBar);

            return $.ajax({
                url: urls.certify(home.id),
                data: {bypass_check: true, certification_date: transaction.certificationDate},
                success: handlers.success,
                error: handlers.error,
                complete: function () {
                    refreshTableFn();
                    renderFn();
                }
            });
        }
    }

    function getAjaxHandlers(home, progressBar) {
        return {
            success: function (data) {
                var data = data.data;
                progressBar.success();
                home.result = 'success';
                home.data = data.length == 0 ? 'Successfully Certified' : data;
            },
            error: function (data) {
                progressBar.error();
                home.result = 'error';
                home.data = data.responseText;
            }
        }
    }

    function _getIcon(classes) {
        return $("<i>").addClass('fa fa-fw').addClass(classes);
    }
});

var QA = (function () {
    var datatable = $(".datatable");

    var urls = {
        add: function (id) {
            return '/api/v2/homestatus/' + id + '/add_program_review_qa/';
        }
    };

    var transactionObj = {
        programs: [],
        homes: [],
        complete: false,
        note: null,
        title: 'Program Review',
        button: 'Add Review',
        type: 'qa',
        extraText: function () {
            if (this.note) {
                return 'Note: ' + this.note;
            } else {
                return '';
            }
        }
    };

    return {
        showModal: showModal,
        hideModal: hideModal,
        modifyTransaction: modifyTransaction,
        getItemHandler: getQAHandler,

        tabChangeHandler: tabChangeHandler,
        transactionObj: transactionObj
    };

    function showModal(modal) {
        if (FEATURES.qa.addNote) {
            var textarea = new TextArea({'label': 'QA Note'});

            modal.find('.modal-body').append(textarea);
        }
    }

    function hideModal(modal) {
        modal.find('.form-group').remove();
    }

    // function canContinue(modal){}
    function modifyTransaction(transaction, modal) {
        if (FEATURES.qa.addNote) {
            transaction.note = modal.find('textarea').val();
        }
    }

    // function checkboxHandler(){}
    function tabChangeHandler(event) {
        // change qastatus to "Not Complete", state to empty and cause table draw.
        $('#id_state').removeAttr('disabled');
        $('#id_state').val('');
        $("#id_qastatus").val(-1).trigger('change');
    }

    // helpers
    function getQAHandler(transaction, refreshTableFn, renderFn, progressBar) {
        return function itemQA(item) {
            var handlers = getAjaxHandlers(item, progressBar);

            var options = {
                url: urls.add(item.id),
                success: handlers.success,
                error: handlers.error,
                complete: function () {
                    refreshTableFn();
                    renderFn();
                }
            };

            if (FEATURES.qa.addNote) {
                options['data'] = {note: transaction.note};
            }

            $.ajax(options);
        }
    }

    function getAjaxHandlers(item, progressBar) {
        return {
            success: function _success(data) {
                progressBar.success();
                item.result = 'success';
                item.data = data.message;
            },
            error: function _error(data) {
                progressBar.error();
                item.result = 'error';
                item.data = data.responseText;
            }
        }
    }
});

var HomeNotes = (function () {
    var datatable = $(".datatable");

    var urls = {
        add: '/api/v2/eepprogramhomestatus/annotations/'
    };
    var transactionObj = {
        programs: [],
        homes: [],
        complete: false,
        note: null,
        title: 'Home Notes',
        button: 'Add Note',
        type: 'notes',
        extraText: function () {
            return 'Note: ' + this.note;
        }
    };

    return {
        showModal: showModal,
        hideModal: hideModal,
        canContinue: canContinue,
        tabChangeHandler: tabChangeHandler,
        modifyTransaction: modifyTransaction,
        getItemHandler: getNoteHandler,

        transactionObj: transactionObj
    };

    function showModal(modal) {
        var textarea = new TextArea({'label': 'Home Note'});
        var checkbox = new CheckBox();

        modal.find('.modal-body').append($("<hr/>"), checkbox, textarea);
    }

    function hideModal(modal) {
        modal.find('.form-group, hr').remove();
    }

    function canContinue(modal) {
        if (!modal.find('textarea').val()) {
            alert('Must provide a note.');
            return false;
        }
        return true;
    }

    function modifyTransaction(transaction, modal) {
        transaction.note = modal.find('textarea').val();
        transaction.is_public = modal.find(':checkbox').is(':checked');
    }

    // function checkboxHandler(){}
    function tabChangeHandler() {
        $('#id_state').removeAttr('disabled');
    }

    // helpers
    function getNoteHandler(transaction, refreshTableFn, renderFn, progressBar) {
        return function itemNote(item) {
            var handlers = getAjaxHandlers(item, progressBar);

            $.ajax({
                url: urls.add + '?machinery=EEPProgramHomeStatusAnnotationsMachinery_note',
                method: 'POST',
                data: {
                    content: transaction.note,
                    //content_type: 75,
                    is_public: transaction.is_public,
                    object_id: item.id,
                    type: 'note'
                },
                success: handlers.success,
                error: handlers.error,
                complete: function () {
                    refreshTableFn();
                    renderFn();
                }
            });
        }
    }

    function getAjaxHandlers(item, progressBar) {
        return {
            success: function _success(data) {
                progressBar.success();
                item.result = 'success';
                item.data = 'Note Added';
            },
            error: function _error(data) {
                progressBar.error();
                item.result = 'error';
                item.data = data;
            }
        }
    }
});

var ProjectTracker = (function () {
    let datatable = $(".datatable")
    MessagingService = angular.element($('[ng-app]')).injector().get('MessagingService');

    let templates = {
        icons: {
            spinner: _getIcon('fa-spin fa-spinner'),
        },
        cannotSubmit: $("<span>Cannot be submitted. <span class='popover-target btn btn-xs btn-default'>Why Not?</span></span>"),
    };
    let urls = {
        taskSubmit: function (id) {
            return '/api/v3/project-tracker/' + id + '/submit/';
        },
        taskStatus: function (id, uuids) {
            return '/api/v3/project-tracker/' + id + '/status/?task_ids=' + uuids.join(",");
        }
    };
    let labels = {
        requesting: 'Acknowledging...',
        waiting: 'Waiting...',
        processing: 'Submitting...',
        complete: 'Finishing...'
    }
    let messageOptions = {
        html: true,
        level: 'error',
        title: 'Error',
        content: null
    };
    var transactionObj = {
        programs: [],
        homes: [],
        complete: false,
        title: 'Submit to ProjectTracker',
        button: 'Submit',
        type: 'projecttracker',
        extraText: function () {
            return '';
        }
    };

    return {
        showModal: showModal,
        hideModal: hideModal,
        canContinue: canContinue,
        modifyTransaction: modifyTransaction,
        getItemHandler: getSubmitHandler,
        checkboxHandler: checkboxHandler,
        tabChangeHandler: tabChangeHandler,

        transactionObj: transactionObj
    };

    function showModal(modal) {
    }

    function hideModal(modal) {
        modal.find('.form-group, hr').remove();
    }

    function canContinue(modal) {
        return true;
    }

    function modifyTransaction(transaction, modal) {
    }

    function checkboxHandler() {
        /**
         * When a checkbox is changed, we want to determine if it can be submitted or not.
         */
        // pop out early if they're unchecking the box
        if (!this.checked) {
            return;
        }

        var checkbox = $(this),
            td = checkbox.parent(),
            row = checkbox.closest('tr'),
            id = row.attr('id'),
            spinner = templates.icons.spinner.clone();

        checkbox.hide();
        td.append(spinner);

        var dt_rowData = td.closest('table').DataTable().row(row).data().DT_RowData;
        if (dt_rowData.projecttracker_submit_available) {
            checkbox.show();
        } else {
            var popover = templates.cannotSubmit.clone();
            row.addClass('warning');
            td.html(popover);

            // Trigger the messages
            messageOptions['content'] = "This home is not ready for submission or has been submitted already.";
            popover.find('.popover-target').popover(messageOptions);
            MessagingService.introduceExternalMessage(messageOptions);
        }
        spinner.remove();
    }

    function tabChangeHandler() {
        $('#id_state').val("complete").trigger('change').attr('disabled', 'disabled');
    }

    // helpers
    function getSubmitHandler(transaction, refreshTableFn, renderFn, progressBar) {
        return function submit(item) {
            var handlers = getAjaxHandlers(item, progressBar);

            async function refreshUntilComplete(uuids, resolve) {
                    // Only starts on an active phase of submission

                let duration;
                let startTime;
                let status = "PENDING";

                function sleep(ms) {
                    return new Promise(function (resolve) {
                        setTimeout(resolve, ms);
                    });
                }

                function _update(data) {  // ajax response handler
                    // console.log("UPDATE " + item.status + " " + JSON.stringify(data))
                    status = data.status;
                    if (status === "STARTING") {
                        if (startTime === null) {
                            startTime = new Date();
                        }
                    }
                    if (startTime !== null) {
                        duration = (new Date() - startTime);
                    }

                    if (status === 'SUCCESS') {
                        handlers.success(data, duration);
                    } else if (data.status === 'FAILURE') {
                        handlers.error(data, duration);
                    } else {
                        handlers.update(data, duration);
                    }

                    renderFn();
                }

                startTime = null;
                duration = null;
                renderFn();
                while (status !== "SUCCESS" && status !== "FAILURE") {
                    await sleep(2000);

                    $.ajax({
                        async: false,
                        url: urls.taskStatus(item.id, uuids),
                        method: 'GET',
                        success: _update,
                        error: _update
                    });
                }

                refreshTableFn();
                resolve();
            }

            function go(resolve) {
                $.ajax({
                    url: urls.taskSubmit(item.id),
                    method: 'POST',
                    success: function (taskResponse) {
                        console.log("Submit: " + JSON.stringify(taskResponse))
                        refreshUntilComplete(taskResponse.task_ids, resolve);
                    },
                    error: function (data) {
                        handlers.error(data);
                        refreshTableFn();
                        renderFn();
                        resolve();
                    }
                });
            }

            return new Promise(go);
        }
    }

    function getAjaxHandlers(item, progressBar) {
        function getDurationString(duration) {
            if (!duration) {
                return "";
            }
            var minutes = parseInt("" + (duration / 1000 / 60));
            var seconds = _.padLeft(parseInt("" + ((duration / 1000)) % 60), 2, '0');
            return " (~" + minutes + ":" + seconds + ")";
        }

        return {
            success: function _success(data, duration) {
                progressBar.success(item);
                item.result = data.status.toLowerCase();
                item.data = data.result + getDurationString(duration);
            },
            update: function _update(data, duration) {
                item.result = data.status.toLowerCase();
                item.data = data.status_display + getDurationString(duration);
            },
            error: function _error(data, duration) {
                progressBar.error(item);
                item.result = data.status.toLowerCase();
                item.data = data.result + getDurationString(duration);
            }
        }
    }

    function _getIcon(classes) {
        return $("<i>").addClass('fa fa-fw').addClass(classes);
    }
});

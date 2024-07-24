// We're explicitly requiring localStorage or nothing at all (no cookie fallback) in order to reduce
// client and support confusion over conditions where some browsers might require different
// cache-invalidating processes.
var datatables_state_scope_name = "Axis_DataTables_" + window.location.pathname + '_';
var use_datatables_localStorage = false;
try {
    use_datatables_localStorage = typeof window.localStorage !== "undefined";
} catch (e) {
    // Some configurations of IE present 'access denied' messages just for touching the localStorage
    // variable, even if it is available.  This 'catch' block should allow the disabling of
    // localStorage.
}

if (use_datatables_localStorage) {
    $.extend( $.fn.dataTable.defaults, {
        "stateSave": true,
        "stateSaveCallback": function (settings, data) {
            localStorage.setItem(datatables_state_scope_name + settings.sTableId, JSON.stringify(data));
        },
        "stateLoadCallback": function (settings) {
            var obj = JSON.parse(localStorage.getItem(datatables_state_scope_name + settings.sTableId));
			if (obj) {
				return obj;
			}
			return null;
        }
    });
}

$.extend($.fn.dataTable.defaults, {
    "bSort": true,
    "bProcessing": true,
    'sPaginationType':'simple_numbers',
    "iDisplayLength": 25,
    "searchDelay": 1000,
    "aLengthMenu": [
        [10, 25, 50, 100, 250, -1],
        [10, 25, 50, 100, 250, "All"]
    ]
});

$.fn.dataTableExt.sErrMode = 'throw';

$(function(){
    $(document).bind('clear.datatable', function(event, datatable){
        // Invalidate the state-saving mechanism's settings
        if (use_datatables_localStorage) {
            localStorage.removeItem(datatables_state_scope_name + datatable.fnSettings().sTableId);
        }
        datatable.fnSortNeutral();
    });
});

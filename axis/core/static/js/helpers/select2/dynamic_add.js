window.dynamic_get_or_create = dynamic_get_or_create;
window.process_results_and_inject_option = process_results_and_inject_option;

function dynamic_get_or_create(name_field_selector) {
    var field = $(name_field_selector || "#id_name");
    if (!field.is(":hidden")) {
        // This appears to be a text-based input, not a select2.  This likely means that the page is
        // an edit page, not a creation page.
        return;
    }
    var form = $("<form method='post'><input name='object' /><input name='go_to_detail' /></form>").hide();
    form.attr('action', field.attr('data-relationship-url'));
    form.append($('input[name=csrfmiddlewaretoken]').clone());

    field.change(function(event){
        var id = parseInt(event.val);
        if (event.type == "change" && id) {
            form.find('input[name=object]').val(id);
            form.appendTo('body');

            service = angular.element(field).injector().get('MessagingService')
            service.introduceExternalMessage({
                'title': 'Redirecting...',
                'content': "Please wait while we create an association...",
                'sticky_alert': true,
                'level': 'info',
                'sender': null
            })
            form.submit();
        }
    });
}

function process_results_and_inject_option(data, page, context) {
    // This is a modified version of django_select2.process_results

	var results;
	if (data.err && data.err.toLowerCase() === 'nil') {
        /*
        * When navigating away from select2 element, then coming back, select2 makes a new input.
        * Since we can't be sure in which order the inputs are returned, grab the value of all of them.
        * We can be sure that select2 clears the value of all old inputs.
        * */
        var term = $('.select2-drop-active .select2-input').map(function(i, element){
            return $(element).val();
        }).toArray();
        term = term.join('');
        if (data.results.length == 0) {
            data.results = [{'text': '(No matches)'}]
        }
		results = {
			'results': [
                {
                    'text': "Create new:",
                    'children': [{ 'id': term, 'text': term }]
                },
                {
                    'text': "Select from existing:",
    			    'children': data.results
                }
            ]
		};
		if (context) {
			results['context'] = context;
		}
		if (data.more === true || data.more === false) {
			results['more'] = data.more;
		}
	} else {
		results = {'results':[]};
	}
	if (results.results) {
		$(this).data('results', results.results);
	} else {
		$(this).removeData('results');
	}
	return results;
}

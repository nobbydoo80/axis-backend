function relationship_check(app_label, model, company_id, params, callback){
    // This will check to see if a relationship exists.  This works even on new objects.
    kwargs = $.extend({}, params);
    kwargs['app_label'] = app_label;
    kwargs['model'] = model;
    kwargs['relationship__company'] = company_id;
    kwargs['error_on_objects_exists_and_no_relation'] = true;
    ajax_req = $.ajax({
        url: "/api/v2/relationship/discover/",
        type: "GET",
        data: kwargs,
        success: function(data, textStatus, jqXHR) {
            typeof callback === 'function' && callback();
        },
        error: function(data, textStatus, jqXHR) {
            results = $.parseJSON(data.responseText)
            var info;
            var msg;
            if (results['object_exists'] && ! results['relationships_exists']){
                level = 'info';
                msg = results['create_string'];
            } else {
                level = 'error';
                msg = results['error'];
            }
            service = angular.element(field).injector().get('MessagingService')
            service.introduceExternalMessage({
                'title': level,
                'content': msg,
                'sticky_alert': true,
                'level': level,
                'sender': null
            })
            return false
        }
    });
}

/* Generic ExamineView implementation of sidebar ajax getter */
// Relies on pre-baked window.relationship_url with an id=0
function build_relationship_sidebar(event, regionObject){
    var object_id = regionObject.object.id;
    var relTable = $('#relations');
    var relationship_url = window.relationship_url.replace('0', object_id);
    $.getJSON(relationship_url, function(data) {
        relTable.empty();
        var arr = []
        for (var item in data) {
            var itemData = data[item];
            var dt = $('<dt/>').text(item);
            relTable.append(dt);
            for (idata in itemData) {
                var dd = $('<dd/>');
                dd.append(itemData[idata].href);
                var icons = $('<span class="icons"/>');
                if (itemData[idata].is_owned && itemData[idata].auto_add) {
                    icons.append($('<i class="fa fa-unlock-alt" data-toggle="tooltip" title="Company auto accepted this relationship"></i>'));
                } else if(itemData[idata].is_owned){
                    icons.append($('<i class="fa fa-lock" data-toggle="tooltip" title="Company approved this relationship"></i>'));
                }
                icons.append($(data[item][idata].add_href));
                if (!itemData[idata].is_owned) {
                    icons.append($(data[item][idata].direct_href));
                }
                icons.append($(data[item][idata].delete_href));
                dd.prepend(icons);
                relTable.append(dd);
            }
        }
    });
}

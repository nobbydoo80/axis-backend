import angular from 'angular';
import { zendesk as settings } from './settings.js';
import UAParser from 'user-agent-parser';

const module_name = 'axis.zendesk';
export default module_name;

var module = angular.module(module_name, []);

module.factory('Zendesk', function($http, $q){
    var obj = {
        ticket_fields: []
    };

    init();

    return {
        all: () => $http.get(settings.urls.list),
        create: (data) => $http.post(settings.urls.create, data),
        data: obj
    };

    function init(){
        //getTicketFields().then((fields) => obj.ticket_fields.push.apply(obj.ticket_fields, fields));
    }

    function getTicketFields(){
        return $q((resolve, reject) => {
            let ticket_fields = sessionStorage.getItem(settings.keys.ticket_fields);
            if(ticket_fields !== null){
                resolve(JSON.parse(ticket_fields));
            } else {
                $http.get(settings.urls.ticket_fields).success(storeTicketFields(resolve)).error(reject);
            }
        });
    }
    function storeTicketFields(resolve){
        return function _storeTicketFields(data){
            data = data.ticket_fields;
            sessionStorage.setItem(settings.keys.ticket_fields, JSON.stringify(data));
            resolve(data);
        }
    }
});

module.controller('ZendeskController', function($scope, User, Zendesk, Impersonate){
    var ctrl = this;

    ctrl.processing = 0;
    ctrl.requester_name = '';
    ctrl.requester_email = '';
    ctrl.ticket_type = 'question';
    ctrl.ticket_priority = 'low';
    ctrl.submit = submit;
    ctrl.show = false;
    ctrl.ticket = null; // Where we store the response.
    ctrl.model = {'subject': '', 'description': ''};

    ctrl.type_options = [
        {'name': 'Question', 'value': 'question'},
        {'name': 'Incident', 'value': 'incident'},
        {'name': 'Problem', 'value': 'problem'},
        {'name': 'Task', 'value': 'task'}
    ];

    ctrl.priority_options = [
        {name: 'Low', value: 'low'},
        {name: 'Normal', value: 'normal'},
        {name: 'High', value: 'high'},
        {name: 'Urgent', value: 'urgent'}
    ];

    User.subscribe((user) => {
        ctrl.requester_name = `${user.first_name} ${user.last_name}`;
        ctrl.requester_email = user.email;
        ctrl.show = !!Impersonate.current_user && !Impersonate.is_impersonating;
    });

    function submit(){
        ctrl.processing = 1;
        return Zendesk.create(clean_data(ctrl.model)).then(submit_success, submit_error).finally(submit_finally);
    }

    function clean_data(model){
        var data = angular.copy(model);

        data.requester = {
            "name": ctrl.requester_name,
            "email": ctrl.requester_email
        };
        data.current_page = getCurrentPage();
        data.other_pages = getOtherPages();
        data.type = ctrl.ticket_type;
        data.priority = ctrl.ticket_priority;
        data.comment = {body: getCommentWithCustomFields(data)};
        // TODO: browser and browser version.
        delete data.description;

        return data;
    }

    function submit_success(data){
        ctrl.processing = 2;
        ctrl.ticket = data.data.ticket || data.data.request;
    }
    function submit_error(){
        ctrl.processing = 3;
    }
    function submit_finally(){
        setTimeout(() => {
            ctrl.processing = 0;
            $scope.$digest();
        }, 2000);
    }

    function getCommentWithCustomFields(data){
        var ua = new UAParser(navigator.userAgent).getResult();
        return `${data.description}

        ---
        Current Page:
        ${data.current_page}
        ---
        Other Pages:
        ${data.other_pages || 'None'}
        ---
        Browser:
        ${ua.browser.name} - ${ua.browser.version}
        ---
        OS:
        ${ua.os.name} - ${ua.os.version}
        `;
    }
    function getCurrentPage(){
        return window.location.href;
    }
    function getOtherPages(){
        let other_pages = JSON.parse(localStorage.getItem('zendesk_open_pages'));
        other_pages.splice(other_pages.indexOf(window.location.href), 1);

        return other_pages.join(', ');
    }
});

module.directive('zendesk', function(){
    return {
        controller: 'ZendeskController',
        controllerAs: 'zendesk',
        link: function(scope, element, attrs, ctrl){
            ctrl.is_open = false;
            ctrl.negate_is_open = () => ctrl.is_open = !ctrl.is_open;

            // init
            element.css('max-height', settings.widget.min_height);

            ctrl.toggle = () => {
                element.css('max-height', !ctrl.is_open ? settings.widget.max_height : settings.widget.min_height);
                toggle_is_open(!!ctrl.ticket);
            };

            function toggle_is_open(reset_fields=false){
                // if it's open, we wait until the next digest cycle to remove the panel body
                // so the animation has time to take place.
                if(ctrl.is_open){
                    setTimeout(() => {
                        ctrl.negate_is_open()

                        if(reset_fields){
                            ctrl.ticket = null;
                            ctrl.model = {'subject': '', 'description': ''};
                        }

                    }, 1);
                } else {
                    ctrl.negate_is_open();
                }
            }
        }
    }
});

$(function(){
    let original_href = window.location.href;
    let open_pages = JSON.parse(localStorage.getItem(settings.keys.open_pages)) || [];
    open_pages.push(original_href);
    try{
        localStorage.setItem(settings.keys.open_pages, JSON.stringify(open_pages));
    } catch(e){
        localStorage.removeItem(settings.keys.open_pages);
    }

    $(window).unload(function removePageFromStorage(){
        let open_pages = JSON.parse(localStorage.getItem(settings.keys.open_pages)) || [];
        open_pages.splice(open_pages.indexOf(original_href), 1);

        try{
            localStorage.setItem(settings.keys.open_pages, JSON.stringify(open_pages));
        } catch(e){
            localStorage.removeItem(settings.keys.open_pages);
        }
    });
});

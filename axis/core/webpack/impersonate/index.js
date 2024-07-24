import angular from 'angular';
import  typeahead from 'angular-ui-bootstrap';
import {impersonate as settings} from './settings.js';

const module_name = 'axis.impersonate';
export default module_name;

const RELOAD_ON_IMPERSONATE = true;

var module = angular.module(module_name, [typeahead]);

module.factory('Impersonate', function($q, $http, $interpolate, User){
    var obj = {
        current_user: null,
        super_user: null,
        is_impersonating: window.is_impersonate,
        all: () => $http.get(settings.urls.list),
        start: start,
        stop: stop
    };

    var _url = (url, id) => $interpolate(url)({id: id}),
        user_url = (id) => _url(settings.urls.detail, id),
        start_url = (id) => _url(settings.urls.impersonate_start, id),
        set_user = (data) => obj.current_user = data.data,
        set_super = (data) => obj.super_user = data.data,
        set_both = (data) => {set_user(data); set_super(data)};

    // init
    User.subscribe((user) => (obj.is_impersonating ? set_user : set_both)({data:user}));
    getSuperUser();

    return obj;

    function start(user){
        if(obj.is_impersonating){
            return _stop(false).then(() => _start(user)).then(User.getUser);
        } else {
            return _start(user).then(User.getUser);
        }
    }
    function stop(){
        return _stop().then(User.getUser);
    }

    function _start(user){
        addImpersonateCount(user.id);
        return $http.post(start_url(user.id)).then(function(data){
            obj.is_impersonating = true;
            window.user_id = user.id;
            if(RELOAD_ON_IMPERSONATE) window.location.reload(true);
            return data;
        });
    }
    function _stop(reloadPage=true){
        return $http.post(settings.urls.impersonate_stop).then(function(data){
            storeLatestImpersonate(User.user);
            obj.is_impersonating = false;
            window.user_id = window.impersonator_id;
            if(RELOAD_ON_IMPERSONATE && reloadPage) window.location.reload(true);
            return data;
        })
    }

    function getSuperUser(){
        if(obj.is_impersonating){
            $http.get(user_url(window.impersonator_id)).then(set_super);
        }
    }

    function addImpersonateCount(userId){
        var counts = JSON.parse(localStorage.getItem(settings.keys.counts)) || {};
        if(userId in counts){
            counts[userId]++;
        } else {
            counts[userId] = 1;
        }
        localStorage.setItem(settings.keys.counts, JSON.stringify(counts));
    }
    function storeLatestImpersonate(user){
        var latest = JSON.parse(localStorage.getItem(settings.keys.latest_impersonate)) || [];
        latest = _.reject(latest, user); // remove if already in list
        latest.unshift(user); // add to the front
        latest.splice(5, 1);  // trim list to 5 max
        localStorage.setItem(settings.keys.latest_impersonate, JSON.stringify(latest));
    }
});

module.controller('ImpersonateController', function(Impersonate, User){
    var ctrl = this;

    // variables
    ctrl.processing = false;
    ctrl.user = null;
    ctrl.users = [];

    // helpers
    ctrl.processing_start = () => ctrl.processing = true;
    ctrl.processing_stop = () => ctrl.processing = false;
    ctrl.user_null = () => ctrl.user = null;
    ctrl.is_impersonating = () => Impersonate.is_impersonating;
    ctrl.current_user = () => User.user;

    // hoisted
    ctrl.impersonate = impersonate;
    ctrl.stop = stop;

    // init
    Impersonate.all().then((users) => ctrl.users = users.data);

    function impersonate(user){
        if(typeof user === 'number'){
            user = _.indexBy(ctrl.users, 'id')[user];
        }
        ctrl.processing_start();
        Impersonate.start(user).then(ctrl.user_null).finally(ctrl.processing_stop);
    }
    function stop(){
        ctrl.processing_start();
        Impersonate.stop().finally(ctrl.processing_stop);
    }
});

module.directive('impersonate', function(User, $compile){
    return {
        controller: 'ImpersonateController',
        controllerAs: 'impersonate',
        link: function(scope, element, attrs, ctrl){
            User.subscribe(function(user){
                if(scope.impersonate.is_impersonating()){
                    setImpersonatePersist(user);
                }
                setUserProfileText(user);
                setPreviousImpersonateList();
            });
            //User.subscribe((user) => element.find('.user').text(get_current_user(user)));

            function setImpersonatePersist(user){
                $(".impersonate-persist").html(getImpersonatePersistText(user)).removeClass('hidden');
            }
            function setUserProfileText(user){
                element.find('.user').html(getUserProfileText(user));
            }
            function setPreviousImpersonateList(){
                element.find('.impersonation-list').html($compile(getPreviousImpersonateList())(scope));
            };
            function getPreviousImpersonateList(){
                var latest = JSON.parse(localStorage.getItem(settings.keys.latest_impersonate)) || [];
                if(!latest.length) return;

                return `
                    <h5>Previous Impersonations</h5>
                    <div class="list-group">
                        ${latest.map(user => `
                            <a class="list-group-item" ng-click="impersonate.impersonate(${user.id})">
                                ${getImpersonatePersistText(user)}
                            </a>
                        `).join('')}
                    </div>
                `
            }
            function getUserProfileText(user){
                return `
                    <h4>
                        <span class="text-muted">[${user.id}]</span>
                        ${user.first_name} ${user.last_name} ${userIsAdmin(user)}
                        - <small>${user.title}</small>
                    </h4>
                    <h5>
                        <span class="text-muted">[${user.company}]</span>
                        ${user.company_name} - <small>${user.company_type}</small>
                    </h5>
                `;
            }
            function userIsAdmin(user){
                if(user.is_company_admin){
                    return '<i class="fa fa-fw fa-user-secret"></i>';
                }
            }
            function getImpersonatePersistText(user){
                return `
                ${[user.first_name, user.last_name].join(' ')} (${user.username}) | ${user.company_name} (${user.company_type})
                `;
            }
        }
    }
});

module.directive('preventTypeaheadClose', function($document, $timeout){
    return {
        restrict: 'A',
        link: function(scope, element, attrs){
            $document.on('click', function(e){
                if(scope.impersonate.is_open){
                    if($(e.target).closest('a').hasClass('typeahead-item')){
                        e.stopImmediatePropagation();
                    }
                }
            });
            scope.$watch(function(){
                return scope.impersonate.is_open;
            }, function(newVal, oldVal){
                if (newVal && newVal !== oldVal){
                    // This fires before the DOM is redrawn.
                    // We need to wait until this field is focus-able.
                    $timeout(function(){
                        element.find('input.form-control').focus();
                    }, 0);
                }
            })
        }
    }
});

module.run(function($templateCache){
    $templateCache.put("template/typeahead/typeahead-impersonate-match.html",
        ` <a tabindex='-1' class='typeahead-item'>
            <span bind-html-unsafe="match.model.first_name | typeaheadHighlight:query"></span>
            <span bind-html-unsafe="match.model.last_name | typeaheadHighlight:query"></span>
            (<span bind-html-unsafe="match.model.username | typeaheadHighlight:query"></span>)
            <br>
            <span bind-html-unsafe="match.model.company_name | typeaheadHighlight:query"></span>
            <span bind-html-unsafe="match.model.company_type | typeaheadHighlight:query"></span>
        </a> `
    );
});

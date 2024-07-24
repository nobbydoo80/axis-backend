import angular from 'angular';
import dropdown from 'angular-ui-bootstrap';
import impersonate from '../impersonate/index.js';
import { USER_DETAIL, auth } from './settings'

const module_name = 'axis.authentication';

export default module_name;

var module = angular.module(module_name, [dropdown, impersonate]);

module.factory('Authentication', function($http){
    return {
        login: login
    };

    function login(username, password){
        return $http({
            url: auth.login,
            method: 'POST',
            data: $.param({username: username, password: password}),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
    }
});

module.controller('LoginController', function(Authentication){
    var ctrl = this;

    ctrl.dropdown_open = false;
    ctrl.spinner_displayed = false;

    ctrl.login = login;

    ctrl.login_success = () => window.location = '/';  // reload to root. Can't come from anywhere else.
    ctrl.login_error = (data) => ctrl.errors = data.data.errors;  // hand up the errors.

    function login(){
        // Submit is assumed to be out of the dropdown, and we can't get to the
        // event and stop it without also stopping the submit,
        // so we just mark the dropdown as still open explicity.
        ctrl.dropdown_open = true;
        ctrl.spinner_displayed = true;
        return Authentication.login(ctrl.username, ctrl.password).then(ctrl.login_success, ctrl.login_error);
    }
});

module.directive('login', function () {
    return {
        controller: 'LoginController',
        controllerAs: 'login'
    }
});
module.directive('preventClose', function(){
    return {
        restrict: 'A',
        link: function(scope, element){
            element.on('click', function(e){
                e.stopPropagation();
            });
        }
    }
});

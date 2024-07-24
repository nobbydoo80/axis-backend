import angular from 'angular';
import auth from '../../webpack/auth/index.js';
import { urls } from '../../webpack/imports/settings.js';
import zendesk from '../../webpack/zendesk/index.js';

angular.module('axis', ['axis.messaging', 'axis.navigation', auth, zendesk].concat(window.axis_angular_dependencies))

.config(function($sceDelegateProvider, $interpolateProvider, $httpProvider){
    $sceDelegateProvider.resourceUrlWhitelist([
        'self',
        window.STATIC_URL + '**'
    ]);

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
})

.factory('User', function($interpolate, $http, $q){
    var user_detail_url = $interpolate(urls.user.detail);

    var data = {
        user: {},
        change_callbacks: []
    };
    // If there's no user_id, we're on the splash page waiting for the user to login.
    if(window.user_id !== null){
        getUser();
    }

    return {
        getUser: getUser,
        setUser: setUser,
        user: data.user,
        subscribe: (fn) => data.change_callbacks.push(fn)
    };

    function setUser(user){
        console.log('setting user', user.username);
        angular.extend(data.user, user);
        _.map(data.change_callbacks, (callback) => callback(data.user));
    }

    function getUser(){
        var url = user_detail_url({id: window.user_id});
        return $http.get(url).then((response) => {
            setUser(response.data);
            return response.data;
        });
    }
})
.directive('copyToClipboard', function () {
    return {
        restrict: 'A',
        scope: {
          copyToClipboard: "="
        },
        link: function (scope, elem, attrs) {
            elem.click(function () {
                if (attrs.copyToClipboard) {
                    var $temp_input = $("<input>");
                    $("body").append($temp_input);
                    $temp_input.val(attrs.copyToClipboard).select();
                    document.execCommand("copy");
                    $temp_input.remove();
                }
            });
        }
    };
})
.directive('axisAutoLink', function($rootScope){
    return {
        restrict: 'A',
        link: function(scope, element, attrs){

            // use setTimeout to get outside the regular angular flow.
            let href = attrs['href'];
            element.on('click', function(e){
                if(e.which > 1 || e.shiftKey || e.altKey || e.metaKey || e.ctrlKey || e.target.target === '_blank'){
                    /**
                     * // Wrote this if statement with an empty block because it's easier
                     * // to understand, and leaves a place for a nice comment :D.
                     * The user is attempting a special click on a menu item,
                     * we don't want to ruin that in any way,
                     * we can assume the browser is doing something special
                     * like opening the link in a new window, and we don't
                     * have to get outside of angular for that.
                     *
                     * Or the user has clicked on a link that is saying it wants
                     * to open in its own window, and we don't need to do anything.
                     */
                } else {
                    setTimeout(function(){
                        window.location = href;
                    }, 100);
                }
            });

            // remove active class from menu items
            if(!angular.isUndefined($rootScope.examineApp)){
                if(attrs['href'].toLowerCase().indexOf('add') > -1){
                    var unwatch;
                    unwatch = scope.$watch(function(){
                        return $rootScope.examineApp.creating;
                    }, function(newVal, oldVal){
                        // Covers switching to false, and starting with false.
                        if(newVal === false){
                            unwatch();
                        }
                        // Was creating, now we're not.
                        if(oldVal === true && newVal === false){
                            element.parent().removeClass('active');
                        }
                    });
                }
            }
        }
    }
});


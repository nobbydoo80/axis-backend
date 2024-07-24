/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.services.TabService')
.factory('TabService', function($rootScope, $log, $state, RuntimeStates){
    var tabs = {},
        firstState = 'replace',
        abstract = {
                abstract: true,
                url: '/tabs'
            };

    $rootScope.$on('$stateChangeStart', stateChangeStart);
    return {
        go: go,
        addTab: addTab,
        tabs: tabs,
        updateDisableListener: updateDisableListener
    };

    // GETTERS
    function getEndpointName(endpoint){
        if(!endpoint) throw new Error('Endpoint must be provided.');
        var temp = endpoint.split('.'),
        parent = temp[0],
        name = temp[1];
        return name;
    }
    function getFirstAvailableState(){
        var states = $state.get();
        var toState;

        for(var i = 0; i < states.length; i++){
            var s = states[i];
            if(!s.abstract && s.name.length > 0){
                try{
                    if(!tabs[s.name.split('.').pop()].disabled){
                        toState = s.name;
                        break;
                    }
                } catch(e){}
            }

        }
        if(!toState) toState = 'index';
        return toState;
    }

    // ACTIONS
    function stateChangeStart(event, toState, toParams, fromState, fromParams){
        // Checking for an intersection allows nested urls to keep the tab their in open.
        var intersection = _.intersection(toState.name.split('.'), fromState.name.split('.'));
        if(intersection.length){
            // only match for things that aren't just tabs.
            if(intersection.indexOf('tabs') == -1){
                return;
            }
        }
        var toTab = tabs[getEndpointName(toState.name)];

        angular.forEach(tabs, function(obj, key){
            obj.active = false;
        });

        // protects against switching to home_statuses that aren't
        // registered as tabs
        if(angular.isDefined(toTab)) toTab.active = true;
    }
    function addTab(endpoint, disabled){
        var name = getEndpointName(endpoint);
        $log.debug('endpoint', endpoint, 'current', $state.current.name, 'disabled', disabled);

        if(!Object.keys(tabs).length){
            RuntimeStates.addState('tabs', abstract);
        }

        tabs[name] = {
            active: $state.current.name == endpoint,
            disabled: !!disabled
        };

        RuntimeStates.addState(endpoint, {
            url: '/' + name,
            template: ''
        })
    }
    function updateDisableListener(endpoint, value){
        $log.debug('tab', endpoint, 'is', value ? 'disabled' : 'enabled');
        var name = getEndpointName(endpoint);
        tabs[name].disabled = value;
    }
    function go(endpoint){
        try{
            if(!tabs[getEndpointName(endpoint)].disabled){
                $rootScope.$broadcast('TabService.go', endpoint);
                $state.go(endpoint, {}, {location:firstState});
                firstState = true;
            } else {
                throw endpoint + ' is disabled';
            }
        } catch(e){
            $state.go(getFirstAvailableState());
        }
    }
});

/**
 * Created by mjeffrey on 12/31/14.
 */

angular.module('axis.services.Actions')
.factory('Actions', function($rootScope, $log, $http, $modal, $q, $interpolate, $timeout, RegionService, Modal, HttpQueue){
    /**
     * Provides the ability to add arbitrary amounts of pre and post method callbacks.
     *
     * NOTE: providing a string to 'addPreMethod' or 'addPostMethod'
     *       will search the Action methods before erroring.
     * NOTE: Action methods must return a promise. And resolves are expected to be
     *       the regionObject.
     *
     * @Example Adding a geocode that calls save when it's done.
     *
     *      function geocode(args...){
     *          //...
     *      }
     *
     *      Actions.addMethod('geocode', geocode);
     *      Actions.addPostMethod('geocode', 'save');
     */

    var fnMustBeStringOrFn = 'A function or string of a function must be passed to addPreMethod.';

    var preMethods = {};
    var postMethods = {};
    var methods = {
        edit: methodEdit,
        save: methodSave,
        saveAll: methodSaveAll,
        cancel: methodCancel,
        exit: methodExit,
        destroy: methodDestroy,
        saveAndReload: methodSaveAndReload,
        delete: methodDelete,
        reload: methodReload,
        validate: methodValidate,
        editRelated: methodEditRelated
    };
    var utils = {
        formatUrl: formatUrl,
        deepExtend: deepExtend,
        updateRegionObject: updateRegionObject,
        resolveDependencies: _resolveDependencies
    };

    addPreMethod('save', 'validate');

    return {
        addPreMethodToType: addPreMethodToType,
        addPostMethodToType: addPostMethodToType,
        addPreMethod: addPreMethod,
        addPostMethod: addPostMethod,
        addMethod: addMethod,
        getPreMethods: getPreMethods,
        getPostMethods: getPostMethods,
        getMethod: getMethod,
        hasMethod: hasMethod,
        callMethod: function(methodName, obj, then){
            return callMethod(methodName, obj, then)
                    .catch(errorHandler(methodName.instruction || methodName, obj));
        },
        methods: methods,
        utils: utils
    };

    // API
    function addPreMethodToType(methodName, typeName, fn){
        fn = getMethodFromString(fn);
        if(angular.isArray(typeName)){
            angular.forEach(typeName, function(name){
                addPreMethodToType(methodName, name, fn);
            })
        } else {
            _addPreMethod(methodName, typeName, fn);
        }
    }
    function addPostMethodToType(methodName, typeName, fn){
        fn = getMethodFromString(fn);
        if(angular.isArray(typeName)){
            angular.forEach(typeName, function(name){
                addPostMethodToType(methodName, name, fn);
            })
        } else {
            _addPostMethod(methodName, typeName, fn);
        }
    }
    function addPreMethod(methodName, fn){
        fn = getMethodFromString(fn);
        _addPreMethod(methodName, 'global',  fn);
    }
    function addPostMethod(methodName, fn){
        fn = getMethodFromString(fn);
        _addPostMethod(methodName, 'global', fn);
    }
    function addMethod(methodName, method, overwrite){
        if(angular.isDefined(methods[methodName]) && !overwrite){
            $log.error('Method', methodName, 'already exists. ' +
                    'To overwrite this method pass \'true\' as the last argument.' +
                    'Otherwise, choose a different method name.')
        } else {
            methods[methodName] = method;
            $log.debug('set', methodName);
        }
    }

    function getPreMethods(methodName, typeName){
        /**
         * Wrapper for pre methods
         * @param methodName
         * @param typeName
         * @returns {callable}
         */
        var regionKey = getMethodKey(methodName, typeName),
            globalKey = getMethodKey(methodName, 'global'),
            fns = (preMethods[regionKey] || []).concat(preMethods[globalKey] || []);
        return getPrePostMethodsCallback(fns);
    }
    function getPostMethods(methodName, typeName){
        /**
         * Wrapper for post methods
         * @param methodName
         * @param typeName
         * @returns {callable}
         */
        var regionKey = getMethodKey(methodName, typeName),
            globalKey = getMethodKey(methodName, 'global'),
            fns = (postMethods[regionKey] || []).concat(postMethods[globalKey] || []);
        return getPrePostMethodsCallback(fns);
    }
    function getMethod(methodName, data){
        /**
         * we only allow one method for main actions.
         * So we can comfortably call the method without putting it in a chain.
         */
        return function(regionObject){
            return callMethodAndExtendObject(methods[methodName], regionObject, data);
        }
    }
    function hasMethod(methodName){
        return !!methods[methodName];
    }
    function callMethod(methodName, regionObject, then){
        var action;
        if(angular.isObject(methodName)){
            action = methodName;
            methodName = methodName.instruction;
        }

        if(hasMethod(methodName)){
            $log.debug('Calling method', methodName, regionObject.type_name);

            regionObject.controller.addProcessingStatus(methodName);
            var typeName = regionObject.type_name;

            return resolveDependencies(regionObject, (methodName == 'save'))
                .then(createModal(action))
                .then(getPreMethods(methodName, typeName))
                .then(getMethod(methodName, action))
                .then(getPostMethods(methodName, typeName))
                .finally(function(){
                    $timeout(function(){
                        (then || angular.identity)();
                        regionObject.controller.clearProcessingStatus(methodName);
                    });
                });
        } else {
            var msg = methodName + ' does not exist as an Action.';
            $log.error(msg);
            return $q.reject(msg);
        }
    }

    // DEFAULT METHODS
    function methodReload(regionObject){
        return utils.resolveDependencies(regionObject).then(function(rObject){
            var url = formatUrl(regionObject.parentRegionSet.region_endpoint_pattern, rObject.object);
            return HttpQueue.addObjectRequest(url);
        }).then(function(freshObject){
            return utils.deepExtend(regionObject, freshObject);
        });
    }
    function methodDelete(regionObject){

        var delete_url = regionObject.delete_endpoint || regionObject.object_endpoint,
            modal = {
                templateUrl: regionObject.delete_confirmation_template_url,
                dataUrl: regionObject.relatedobjects_endpoint
            },
            options = {
                url: delete_url,
                method: 'DELETE'
            };

        return $q(function _methodDelete(resolve, reject){
            Modal({modal: modal}, regionObject).then(function(){
                // modal success
                $http(options).success(function(data){
                    // http success
                    $log.info('Deleted', regionObject.type_name);
                    regionObject.controller.removeRegion(regionObject);
                    RegionService.removeRegion(regionObject);
                    resolve(regionObject);
                    // reload to list view for primaryRegions
                    if(regionObject.parentRegionSet.isPrimaryRegion){
                        $timeout(function(){
                            window.location.replace(data.url || data.data.url);
                        }, 100);
                    }
                }).error(function(data, status){
                    // http error
                    regionObject.controller.error(arguments);
                    reject(status.toString());
                });
            }, function(){
                // modal cancelled
                reject('modal cancelled');
            });
        });
    }
    function methodSaveAndReload(regionObject){
        // ...
        return $q(function(resolve, reject){
            reject('not implemented yet');
        });
    }
    function methodDestroy(regionObject){
        return $q(function _methodDestroy(resolve){
            regionObject.controller.removeRegion(regionObject);
            RegionService.removeRegion(regionObject);
            resolve(regionObject);
        });
    }
    function methodCancel(regionObject){
        regionObject.controller.reset();
        return callMethod('exit', regionObject);
    }
    function methodExit(regionObject){
        regionObject.controller.activeState = 'default';
        return $q.when(regionObject);
    }
    function methodSaveAll(regionObject){
        var queue = regionObject.controller.handleAction(regionObject.commit_instruction);
        var triggeredChildren = [];

        var filteredRegionObjects = RegionService.helpers.regions.filter(function(otherRegionObject){
            return otherRegionObject.commit_instruction !== null;
        });

        // Flag regions as pending
        angular.forEach(filteredRegionObjects, function(otherRegionObject){
            if (regionObject != otherRegionObject) {
                otherRegionObject.controller.addProcessingStatus("waiting");
            }
        });

        // Process regions
        angular.forEach(filteredRegionObjects, function(otherRegionObject){
            if(regionObject != otherRegionObject && triggeredChildren.indexOf(otherRegionObject) == -1){
                if (otherRegionObject.passive_machinery === true) {
                    return;
                }
                triggeredChildren.push.apply(triggeredChildren, otherRegionObject.controller.children);

                queue = queue.then(function(res){
                    $log.debug("Issuing", otherRegionObject.commit_instruction, "to", otherRegionObject.type_name, otherRegionObject);

                    return otherRegionObject.controller.handleAction(otherRegionObject.commit_instruction).then(function(){
                        otherRegionObject.controller.clearProcessingStatus("waiting");
                        return res;
                    }, function(){
                        otherRegionObject.controller.clearProcessingStatus("waiting");
                        return res;
                    });
                });
            }
        });
        return queue.finally(function(){
            filteredRegionObjects.map(function(otherRegionObject){
                otherRegionObject.controller.clearProcessingStatus('waiting');
            });
        });
    }
    function methodSave(regionObject){
        var method = regionObject.object.id ? 'PATCH' : 'POST';
        var url = method == 'PATCH' ? regionObject.object_endpoint_pattern : regionObject.object_endpoint;
        url = formatUrl(url, regionObject.object);

        angular.forEach(regionObject.object, function(value, key){
            if(angular.isObject(value) && !angular.isArray(value)){
                regionObject.object[key] = value.id;
            }
        });

        return $q(function _methodSave(resolve, reject){
            $http({
                url: url,
                method: method,
                data: regionObject.object
            }).success(function(data){
                updateRegionObject(regionObject, data);

                regionObject.controller.success();
                resolve(regionObject);
            }).error(function(data, status){
                if(status === 500){
                    data = 'System error occurred. \n We apologize for the interruption and have already been notified.'
                }
                regionObject.controller.error(data);
                reject(status.toString());
            })
        });
    }
    function methodEdit(regionObject){
        regionObject.controller.activeState = 'edit';
        return $q.when(regionObject);
    }
    function methodValidate(regionObject){
        var typeName = regionObject.type_name;
        return $q.when(regionObject)
            .then(getPreMethods('validate', typeName))
            .then(getPostMethods('validate', typeName))
            .then(function(){
                return regionObject;
            });
    }
    function methodEditRelated(regionObject, action){
        function getExtraDataMethod(url, initialData){
            // create callable closure around the extra data url.
            return function(){
                var items = $q.defer();
                $http.get(url).success(function(data){
                    return items.resolve(angular.extend(initialData || {}, data));
                });
                return items.promise;
            }
        }

        var extraDataGetter = null;
        if (action.dataUrl === undefined) {
            extraDataGetter = function(){ return action.extraData };
        } else {
            extraDataGetter = getExtraDataMethod(action.dataUrl, action.extraData);
        }

        var resolves = {
            regionObject: function(){ return regionObject },
            extraData: extraDataGetter,
            saveUrl: function(){ return action.saveUrl }
        }
        var modal = $modal.open({
            templateUrl: action.templateUrl,
            resolve: resolves,
            controller: 'EditRelatedModalController',
            controllerAs: 'vm',
            size: 'lg'
        });

        return modal.result.then(function(){
            return methodReload(regionObject);
        });
    }

    // UTILS
    function getMethodKey(methodName, typeName){
        return ['_fn', methodName, typeName].join('_');
    }
    function getMethodFromString(fn){
        if(typeof fn == 'string' && angular.isDefined(methods[fn])){
            fn = methods[fn];
        }
        if(typeof fn !== 'function'){
            throw new Error(fnMustBeStringOrFn);
        }
        return fn;
    }
    function formatUrl(endpoint, context, typeName){
        var startSymbol = $interpolate.startSymbol(),
            endSymbol = $interpolate.endSymbol(),
            regex = /__(\w+)__/g,
            replaceStr = startSymbol + '$1' + endSymbol;

        if(typeName){
            var obj = { endpoint: endpoint, context: context};
            return getPreMethods('formatUrl', typeName)(obj)
            .then(function(obj){
                obj['endpoint'] = $interpolate(obj.endpoint.replace(regex, replaceStr))(obj.context);
                return obj
            })
            .then(getPostMethods('formatUrl', typeName))
            .then(function(obj){
                return obj.endpoint;
            });
        }

        return $interpolate(endpoint.replace(regex, replaceStr))(context)
    }
    function deepExtend(destination, data){
        // Try a merge of top-level entries.  updateRegionObject is not a recursive deep merge, but many
        // of our top-level keys are Object-type.
        var specialCases = ['controller', 'parentRegionObject', 'parentRegionSet'];
        for(var k in data){
            if(!data.hasOwnProperty(k) || specialCases.indexOf(k) > -1) continue;
            var original_v = destination[k];
            var v = data[k];
            if(angular.isArray(original_v) && !angular.equals(original_v, v)){
                original_v.length = 0; // lol, this actually works
                original_v.push.apply(original_v, v);
            } else if(angular.isObject(original_v)){
                angular.extend(original_v, v);
            } else {
                destination[k] = v;
            }
        }
        return destination;
    }
    function updateRegionObject(regionObject, data){
        deepExtend(regionObject, data);
        regionObject._masterForm = angular.copy(regionObject.object);
    }
    function _resolveDependencies(regionObject, rejectFail){
        /**
         * Look into the object and try to grab things it needs from other Regions.
         * Non forceful resolve but can choose to reject on fail
         *
         * @param regionObject
         * @param forceful
         * @returns {promise}
         */

        return $q(function __resolveDependencies(resolve, reject){
            if(!RegionService.helpers.hasDependencies(regionObject)){
                resolve(regionObject);
            } else {
                try{
                    updateRegionObject(regionObject.object, RegionService.helpers.fetchRegionDependencies(regionObject));
                    resolve(regionObject);
                } catch(e) {
                    rejectFail ? reject(e) : resolve(regionObject);
                }
            }
        });
    }
    function callMethodAndExtendObject(fn, regionObject, data){
        /**
         * Can't be positive that the function we're running is a promise.
         * Wrap it and expect the result to be an object that we want to extend
         * the regionObject by.
         *
         * @param fn
         * @param regionObject
         * @returns {!Promise.<RESULT>|*}
         */
        return $q.when(fn(regionObject, data)).then(function(result){
            updateRegionObject(regionObject, result);
            return regionObject;
        });
    }

    // HELPERS
    function _addPreMethod(methodName, typeName, fn){
        var key = getMethodKey(methodName, typeName);
        if(!angular.isDefined(preMethods[key])){
            preMethods[key] = [];
        }
        preMethods[key].push(fn);
    }
    function _addPostMethod(methodName, typeName, fn){
        var key = getMethodKey(methodName, typeName);
        if(!angular.isDefined(postMethods[key])){
            postMethods[key] = [];
        }
        postMethods[key].push(fn);
    }
    function _getPrePostMethodsCallback(methods){
        /**
         * creates a callback chain where all the functions aren't called until the previous returns.
         *
         * @param {array} methods
         * @returns {promise}
         */
        return function promiseChainer(regionObject){
            var queue = $q.when(regionObject);
            angular.forEach(methods, function(fn, i){
                queue = queue.then(function(res){
                    return callMethodAndExtendObject(fn, regionObject).then(function(){
                        return res;
                    });
                });
            });
            return queue;
        }
    }
    function resolveDependencies(regionObject, forceful){
        /**
         * Look into the object and try to grab things it needs from other Regions.
         * If it can't find them and we really need them, attempt a save on the region
         * that we believe contains the data we need.
         *
         * @param regionObject
         * @param forceful
         * @returns {promise}
         */
        var deferred = $q.defer();

        utils.resolveDependencies(regionObject, forceful)
        .then(function(rObject){
            deferred.resolve(rObject);
        }, function(error){
            // error
            // NOTE: this will only get run if forceful is true.
            var depsRegion = RegionService.getRegionFromTypeName(error.regionName);
            callMethod(depsRegion.commit_instruction, depsRegion).then(utils.resolveDependencies, deferred.reject);
        });

        return deferred.promise;
    }

    // RETURNS PROMISE CALLBACKS
    function getPrePostMethodsCallback(methods){
        /**
         * check if there are any methods to be called.
         * If not, return a function that just returns the regionObject.
         *
         * @param {array} methods
         * @returns {*} (promise chain | identity)
         */
        return angular.isDefined(methods) ? _getPrePostMethodsCallback(methods) : angular.identity;
    }
    function createModal(action){
        /**
         * If the action calls to be gated by a modal,
         * this returns a function that will do that when the action chain gets there.
         *
         * @param regionObject
         * @returns {*}
         */
        function _createModal(regionObject){
            return Modal(action, regionObject);
        }

        var useModal = angular.isDefined(action) && angular.isDefined(action.modal) && action.modal !== null;
        return useModal ? _createModal : angular.identity;
    }
    function errorHandler(methodName, regionObject){
        //var err = new ActionException(methodName, regionObject);
        return function(cause){
            return $q.reject(cause);
        }
    }
})

.controller('EditRelatedModalController', function($http, $scope, $modalInstance, saveUrl, regionObject, extraData){
    var vm = this;
    $scope.regionObject = vm.regionObject = regionObject;
    $scope.extraData = vm.extraData = extraData;
    vm.ok = function(){
        var method = (extraData.id ? 'patch' : 'post');
        $http[method](saveUrl, regionObject.object).then(function(response){
            $modalInstance.close(vm.regionObject);
        });
    };
    vm.cancel = function(){
        $modalInstance.dismiss('cancel');
    };
})

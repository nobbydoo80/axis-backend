describe('Controller: RegionController', function(){

    // injected
    var httpReal, $http, $rootScope, $timeout, $controller, $q, Actions, HomeOptions, RegionObjects;
    // used
    var regionObject, controller, scope;

    // httpReal makes it so we can make actual XHR requests.
    beforeEach(module('httpReal', 'axis.region.region', 'fixtureData'));
    // get all the deps
    beforeEach(inject(function(_httpReal_, _$http_, _$rootScope_, _$timeout_, _$controller_, _$q_, _Actions_, _HomeOptions_, _RegionObjects_){
        httpReal = _httpReal_;
        $http = _$http_;
        $rootScope = _$rootScope_;
        $timeout = _$timeout_;
        $controller = _$controller_;
        $q = _$q_;
        Actions = _Actions_;
        HomeOptions = _HomeOptions_;
        RegionObjects = _RegionObjects_;
        if(RegionObjects.length) regionObject = RegionObjects[0];
    }));
    // This should only run once. To minimize api requests
    beforeEach(function(){
        if(!regionObject){
            $rootScope.$apply(function(){
                $http.get(HomeOptions.endpoints[0]).success(function(data){
                    RegionObjects.push(data);
                    regionObject = data;
                });
            });
            waitsFor(function(){
                return !!regionObject;
            }, 3000);
        }
    });

    // Give the scope a fresh regionObject and options
    // make a fresh controller.
    beforeEach(function(){
        getNewScope();
        getNewController();
    });

    function getNewScope(){
        scope = $rootScope.$new();
        scope.regionObject = angular.copy(regionObject);
        scope.options = angular.copy(HomeOptions);
        scope.regionSet = {};

        scope.regionObject.parentRegionSet = {processing: false};
    }
    function getNewController(){
        controller = $controller('RegionController', {
            $rootScope: $rootScope,
            $scope: scope,
            $q: $q,
            Actions: Actions
        })
    }

    it('should exist', function(){
        expect(!!controller).toBe(true);
    });
    it('should have default flags set', function(){
        expect(controller.children).toEqual([]);
        expect(controller.axisFields).toEqual({});
        expect(controller.activeState).toBeDefined();
    });
    it('should grab the activeState from the regionObject', function(){
        getNewScope();
        var activeState = 'testing';
        scope.regionObject.default_instruction = activeState;
        getNewController();

        expect(controller.activeState).toEqual(activeState);
    });
    it('should set activeState to default if regionObject doesnt have a default state', function(){
        getNewScope();
        if(scope.regionObject.default_instruction) delete scope.regionObject.default_instruction;
        getNewController();

        expect(controller.activeState).toEqual('default');
    });

    // init
    it('should add additional scope to the controller form the regionObject', function(){
        getNewScope();
        scope.regionObject.additionalScope = {};
        var testString = 'this is a test string';
        scope.regionObject.additionalScope.test = testString;
        getNewController();

        expect(controller.test).toEqual(testString);
    });
    // initRegionObject
    it('should add the necessary attributes to the regionObject', function(){
        expect(scope.regionObject.errors).toBeDefined();
        expect(scope.regionObject.controller).toBeDefined();
        expect(scope.regionObject._masterForm).toBeDefined();
        expect(scope.regionObject.object_endpoint_pattern).toBeDefined();

        expect(scope.regionObject.controller).toBe(controller);
        expect(scope.regionObject._masterForm).toEqual(scope.regionObject.object);
        expect(scope.regionObject.object_endpoint_pattern).toEqual(scope.options.object_endpoint_pattern);
    });
    it('should make a _masterForm from the regionObject', function(){
        expect(scope.regionObject._masterForm).toBeDefined();
        expect(scope.regionObject._masterForm).toEqual(scope.regionObject.object);
        scope.regionObject.object.type_name = 'testing';
        expect(scope.regionObject._masterForm).not.toEqual(scope.regionObject.object);
    });
    // reset
    it('should reset the regions object to its original form', function(){
        expect(scope.regionObject._masterForm).toBeDefined();
        expect(scope.regionObject.object).toEqual(scope.regionObject._masterForm);
        scope.regionObject.object.id = 'not an ID';
        expect(scope.regionObject.object).not.toEqual(scope.regionObject._masterForm);
        controller.reset();
        expect(scope.regionObject.object).toEqual(scope.regionObject._masterForm);
    });
    // success
    describe('success method', function(){
        beforeEach(function(){
            var regionSet = jasmine.createSpyObj('regionSet', ['regionSuccess']);
            scope.regionSet = regionSet;
            scope.timedClass = angular.noop;
            spyOn(scope, 'timedClass');
        });
        it('should clear the errors on success', function(){
            expect(scope.regionObject.errors).toEqual({});
            scope.regionObject.errors['test'] = 'some errors';
            expect(scope.regionObject.errors).not.toEqual({});
            controller.success();
            expect(scope.regionObject.errors).toEqual({});
        });
        it('should forward the success message to the regionSet and add success class', function(){
            var message = 'Awesome success';
            controller.success(message);
            expect(scope.timedClass).toHaveBeenCalledWith('success');
            expect(scope.regionSet.regionSuccess).toHaveBeenCalledWith(message);
        });
    });
    // error
    describe('error method', function(){
        beforeEach(function(){
            var regionSet = jasmine.createSpyObj('regionSet', ['regionError']);
            scope.regionSet = regionSet;
            scope.timedClass = angular.noop;
            spyOn(scope, 'timedClass');

            expect(scope.regionObject.errors).toEqual({});
        });
        it('should put errors on the regionObject', function(){
            var errors = {
                field_one: 'this is required',
                test: 'test'
            };
            controller.error(errors);
            expect(scope.regionObject.errors).toEqual(errors);
        });
        it('should turn strings into object under non_field_errors', function(){
            var message = 'Something happened';
            controller.error(message);
            expect(scope.regionObject.errors).toEqual({non_field_errors: [message]});
        });
        it('should an array into object under non_field_errors', function(){
            var message = ["Something happened"];
            controller.error(message);
            expect(scope.regionObject.errors).toEqual({non_field_errors: message});
        });
        it('should move __all__ errors to non_field_errors', function(){
            var messages = ['this is an error', 'and another error'];
            var errors = { __all__: messages};
            controller.error(errors);
            expect(scope.regionObject.errors).toEqual({non_field_errors: messages})
        });
        it('should forward errors to regionSet and add error class', function(){
            var messages = ['this is an error', 'and another error'];
            var errors = { __all__: messages};
            controller.error(errors);
            expect(scope.timedClass).toHaveBeenCalledWith('error');
            expect(scope.regionSet.regionError).toHaveBeenCalledWith({non_field_errors: messages});
        });
    });
    // handleAction
    describe('handleAction', function(){
        it('should call a save action for all registered children', function(){
            var calls = {};
            var fakeEdit = function(){return true};
            spyOn(Actions, 'callMethod').andCallFake(function(methodName){
                // track calls to callMethod.
                if(methodName.instruction) methodName = methodName.instruction;
                calls[methodName] ? calls[methodName]++ : calls[methodName] = 1;

                return $q.when({});
            });
            // make a save action
            var action = {is_mode: false, instruction: scope.regionObject.commit_instruction};
            // add children to attempt to save
            controller.children.push({id: '1', commit_instruction: 'save', controller: {editing: fakeEdit}});
            controller.children.push({id: '2', commit_instruction: 'save', controller: {editing: fakeEdit}});

            // test
            controller.handleAction(action);
            expect(calls[scope.regionObject.commit_instruction]).toEqual(1);
            expect(calls.exit).toBeUndefined();
            $rootScope.$apply();
            expect(calls.save).toEqual(2);
            expect(calls.exit).toEqual(3);
        });
        it('should not save a child region that does not have a commit instruction', function(){
            var calls = {};
            spyOn(Actions, 'callMethod').andCallFake(function(methodName){
                // track calls to callMethod.
                if(methodName.instruction) methodName = methodName.instruction;
                calls[methodName] ? calls[methodName]++ : calls[methodName] = 1;

                return $q.when({});
            });
            // make a save action
            var action = {is_mode: false, instruction: 'save'};
            // add children to attempt to save
            controller.children.push({id: '1'});
            controller.children.push({id: '2'});

            // test
            controller.handleAction(action);
            expect(calls.save).toEqual(1);
            expect(calls.exit).toBeUndefined();
            $rootScope.$apply();
            expect(calls.save).toEqual(1);
            expect(calls.exit).toBeUndefined();  // only come out of edit mode when save instruction is sent
        });
        it('should not exit a region if the instruction was not a save', function(){
            var calls = {};
            spyOn(Actions, 'callMethod').andCallFake(function(methodName){
                // track calls to callMethod.
                if(methodName.instruction) methodName = methodName.instruction;
                calls[methodName] ? calls[methodName]++ : calls[methodName] = 1;

                return $q.when({});
            });
            // make a save action
            var action = {is_mode: false, instruction: 'floof'};

            // test
            controller.handleAction(action);
            expect(calls.floof).toEqual(1);
            expect(calls.exit).toBeUndefined();
            $rootScope.$apply();
            expect(calls.floof).toEqual(1);
            expect(calls.exit).toBeUndefined();
        });
    });
    // reloadRegionListener
    describe('reloadListener', function(){
        beforeEach(function(){
            spyOn(Actions, 'callMethod');
            scope.regionSet = {processing: false};
        });

        it('should call a reload', function(){
            $rootScope.$broadcast('reloadRegions', 'firingType');
            expect(Actions.callMethod).toHaveBeenCalledWith('reload', scope.regionObject);
        });
        it('should not call a reload if fired by a region of the same type', function(){
            $rootScope.$broadcast('reloadRegions', scope.regionObject.type_name);
            expect(Actions.callMethod).not.toHaveBeenCalled();
        });
        it('should not call reload if the region is processing', function(){
            scope.regionSet.processing = true;
            $rootScope.$broadcast('reloadRegions', 'firingType');
            expect(Actions.callMethod).not.toHaveBeenCalled();
        });
    });
    it('should determine editing status correctly', function(){
        expect(controller.editing()).toEqual(false);
        controller.activeState = 'edit';
        expect(controller.editing()).toEqual(true);
    });
});

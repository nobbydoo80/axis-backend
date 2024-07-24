describe('Controller: SingleRegionController', function(){

    // injected
    var $controller, $rootScope, $timeout, $compile, RegionService, UrlService, HomeOptions, $http, $log, HttpQueue, Actions, RegionObjects;
    // used
    var controller, scope, regionObject;

    beforeEach(module('httpReal', 'axis.region.singleRegion', 'fixtureData', 'axis.services.Actions', 'axis.services.HttpQueue'));
    beforeEach(inject(function(_$controller_, _$rootScope_, _$timeout_, _$compile_, _RegionService_, _UrlService_, _HomeOptions_, _$http_, _$log_, _HttpQueue_, _Actions_, _RegionObjects_){
        $controller =_$controller_;
        $rootScope =_$rootScope_;
        $timeout =_$timeout_;
        $compile =_$compile_;
        RegionService =_RegionService_;
        UrlService =_UrlService_;
        HomeOptions = _HomeOptions_;
        $http = _$http_;
        $log = _$log_;
        HttpQueue = _HttpQueue_;
        Actions = _Actions_;
        RegionObjects = _RegionObjects_;
        if(RegionObjects.length) regionObject = RegionObjects[0];
    }));
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
    beforeEach(function(){
        newScope();
        newController();
    });
    function newScope(){
        scope = $rootScope.$new();
        scope.options = angular.copy(HomeOptions);
    }
    function newController(){
        controller = $controller('SingleRegionController', {
            $rootScope: $rootScope,
            $scope: scope,
            $timeout: $timeout,
            $compile: $compile,
            RegionService: RegionService,
            UrlService: UrlService,
            HttpQueue: HttpQueue,
            Actions: Actions
        });
    }

    it('should exist', function(){
        expect(!!controller).toBe(true);
    });
    it('should start with correct defaults', function(){
        expect(controller.regionsErrors).toEqual({});
        expect(controller.processing).toEqual(false);
        expect(controller.showLoader).toEqual(true);
        expect(controller.eventPrefix).toEqual('SingleRegionLoaded:');
        expect(controller.parentRegionObject).toEqual();
        expect(controller.isFormTemplateLoaded).toEqual(false);
        expect(controller.isDetailTemplateLoaded).toEqual(false);
        expect(controller.heading.destination).toEqual(null);
        expect(controller.heading.element).toEqual(null);
        expect(controller.heading.scope).toEqual(null);
        expect(scope.isPrimaryRegion).toEqual(false);
    });

    // setRegion
    describe('setRegion', function(){
        it('should set the controller region_template_url', function(){
            expect(controller.region_template_url).toBeUndefined();
            var regionTemplateUrl = 'test value';
            regionObject.region_template_url = regionTemplateUrl;
            controller.setRegion(regionObject);
            expect(controller.region_template_url).toBeDefined();
            expect(controller.region_template_url).toEqual(regionTemplateUrl);
        });
        it('should register the regionObject', function(){
            spyOn(RegionService, 'addRegion');
            expect(RegionService.addRegion).not.toHaveBeenCalled();
            controller.setRegion(regionObject);
            expect(RegionService.addRegion).toHaveBeenCalled();
        });
        it('should say there was a piece of the puzzle loaded', function(){
            // pieceLoaded() is an internal method, we can know its been called
            // by watching for the event it emits when everything is done loading.

            // mock region being done
            controller.isFormTemplateLoaded = true;

            spyOn($rootScope, '$broadcast').andCallThrough();
            expect($rootScope.$broadcast).not.toHaveBeenCalled();

            controller.setRegion(regionObject);
            // checking for undefined in the element because we're not testing with a directive.
            expect($rootScope.$broadcast).not.toHaveBeenCalledWith(controller.event, scope.regionObject, undefined);
            $timeout.flush();
            expect($rootScope.$broadcast).toHaveBeenCalledWith(controller.event, scope.regionObject, undefined)
        });
        it('should add the parentRegionObject from the controller', function(){
            controller.parentRegionObject = {test: 'one'};

            controller.setRegion({});
            expect(scope.regionObject.parentRegionObject).toBeDefined();
            expect(scope.regionObject.parentRegionObject).toEqual(controller.parentRegionObject);
        });
    });
    // setHeadingDestination
    describe('setHeadingDestination', function(){
        it('should not set the element if nothing is sent', function(){
            expect(controller.heading.destination).toEqual(null);
            controller.setHeadingDestination();
            expect(controller.heading.destination).toEqual(null);
        });
        it('should not set the element if a blank array is set', function(){
            expect(controller.heading.destination).toEqual(null);
            var el = angular.element();
            controller.setHeadingDestination(el);
            expect(controller.heading.destination).toEqual(null);
        });
        it('should not set the element if its not an element', function(){
            expect(controller.heading.destination).toEqual(null);
            var el = angular.element('<div></div>');
            controller.setHeadingDestination(el);
            expect(controller.heading.destination).toEqual(el);
        });
    });
    // setHeadingElement
    describe('setHeadingElement', function(){
        it('should not set the element if nothing is sent', function(){
            expect(controller.heading.element).toEqual(null);
            controller.setHeadingElement();
            expect(controller.heading.element).toEqual(null);
        });
        it('should not set the element if a blank array is set', function(){
            expect(controller.heading.element).toEqual(null);
            var el = angular.element();
            controller.setHeadingElement(el);
            expect(controller.heading.element).toEqual(null);
        });
        it('should not set the element if its not an element', function(){
            expect(controller.heading.element).toEqual(null);
            var el = angular.element('<div></div>');
            controller.setHeadingElement(el);
            expect(controller.heading.element).toEqual(el);
        });
    });
    // setHeadingScope
    describe('setHeadingScope', function(){
        it('should not set the scope if its an empty object or nothing', function(){
            expect(controller.heading.scope).toEqual(null);
            controller.setHeadingScope();
            expect(controller.heading.scope).toEqual(null);
            controller.setHeadingScope({});
            expect(controller.heading.scope).toEqual(null);
        });
        it('should set the scope to a scope object', function(){
            expect(controller.heading.scope).toEqual(null);
            var scope = $rootScope.$new();
            controller.setHeadingScope(scope);
            expect(controller.heading.scope).toEqual(scope);
        });
        it('should not be able to be overwritten by nothing or null', function(){
            expect(controller.heading.scope).toEqual(null);
            var scope = $rootScope.$new();
            controller.setHeadingScope(scope);
            expect(controller.heading.scope).toEqual(scope);
            controller.setHeadingScope();
            expect(controller.heading.scope).toEqual(scope);
            controller.setHeadingScope({});
            expect(controller.heading.scope).toEqual(scope);
        })
    });
    // compileHeading
    describe('compileHeading', function(){
        it('should fill the heading destination with the registered element and scope', function(){
            var el = angular.element('<div>this is a message. {{ test }}</div>');
            var dest = angular.element('<h1></h1>');
            var sco = $rootScope.$new();
            sco.test = 'testing';
            var result = 'this is a message. testing';

            expect(controller.heading.destination).toBe(null);
            expect(controller.heading.element).toBe(null);
            expect(controller.heading.scope).toBe(null);
            controller.setHeadingDestination(dest);
            controller.setHeadingElement(el);
            controller.setHeadingScope(sco);
            expect(controller.heading.destination).not.toBe(null);
            expect(controller.heading.element).not.toBe(null);
            expect(controller.heading.scope).not.toBe(null);

            expect(!!controller.heading.destination.html()).toEqual(false);
            controller.compileHeading();
            $rootScope.$digest();
            expect(!!controller.heading.destination.html()).toEqual(true);
            expect(controller.heading.destination.html()).toContain(result);
        });
    });
    // primaryRegionWatcher
    describe('primaryRegionWatcher', function(){
        it('should setup a watcher', function(){
            spyOn(scope, '$watch');
            expect(scope.$watch).not.toHaveBeenCalled();
            controller.primaryRegionWatcher();
            expect(scope.$watch).toHaveBeenCalled();
        });
        it('should not try to change the url if it started with a good value', function(){
            spyOn(UrlService, 'setUpdatedLink');

            expect(!!regionObject.object.id).toBe(true);
            controller.setRegion(regionObject);

            expect(UrlService.setUpdatedLink).not.toHaveBeenCalled();

            controller.primaryRegionWatcher('id');
            expect(UrlService.setUpdatedLink).not.toHaveBeenCalled();

            scope.$digest();
            expect(UrlService.setUpdatedLink).not.toHaveBeenCalled();

            scope.regionObject.object.id = 12;
            expect(UrlService.setUpdatedLink).not.toHaveBeenCalled();

            scope.$digest();
            expect(UrlService.setUpdatedLink).not.toHaveBeenCalled();
        });
        it('should change the url but not flip an attr if none was given', function(){
            $rootScope.nested = {watchedAttr: false};
            regionObject.object.id = null;
            controller.setRegion(regionObject);
            controller.primaryRegionWatcher('id');
            spyOn(UrlService, 'setUpdatedLink');

            expect(UrlService.setUpdatedLink).not.toHaveBeenCalled();

            scope.$apply();
            expect($rootScope.nested.watchedAttr).toBe(false);
            expect(UrlService.setUpdatedLink).not.toHaveBeenCalled();

            scope.regionObject.object.id = 12;
            scope.$apply();
            expect($rootScope.nested.watchedAttr).toBe(false);
            expect(UrlService.setUpdatedLink).toHaveBeenCalledWith('/'+controller.type_name+'/'+scope.regionObject.object.id+'/');

            scope.flipWatchedAttr();
            expect($rootScope.nested.watchedAttr).toBe(false);

        });
        describe('already setup', function(){
            beforeEach(function(){
                $rootScope.nested = {watchedAttr: false};
                $rootScope.nested.watchedAttr = false;
                regionObject.object.id = null;
                controller.setRegion(regionObject);
                controller.primaryRegionWatcher('id', 'nested.watchedAttr');

                spyOn(UrlService, 'setUpdatedLink');
            });
            it('should try to change the url', function(){

                expect(UrlService.setUpdatedLink).not.toHaveBeenCalled();

                scope.$digest();
                expect($rootScope.nested.watchedAttr).toBe(false);
                expect(UrlService.setUpdatedLink).not.toHaveBeenCalled();

                scope.regionObject.object.id = 12;
                scope.$digest();
                expect(UrlService.setUpdatedLink).toHaveBeenCalledWith('/'+controller.type_name+'/'+scope.regionObject.object.id+'/');
            });
            it('should flip the attr it was given', function(){
                expect($rootScope.nested.watchedAttr).toBe(false);
                scope.$digest();
                expect($rootScope.nested.watchedAttr).toBe(false);
                scope.regionObject.object.id = 12;
                scope.$digest();
                expect($rootScope.nested.watchedAttr).toBe(false);
                $timeout.flush();
                expect($rootScope.nested.watchedAttr).toBe(true);
            });
        });
    });
    // regionSuccess
    it('should broadcast a success event', function(){
        controller.setRegion(regionObject);
        spyOn($rootScope, '$broadcast');

        expect($rootScope.$broadcast).not.toHaveBeenCalled();
        controller.regionSuccess();
        expect($rootScope.$broadcast).toHaveBeenCalledWith(controller.event+':success', scope.regionObject, undefined);
    });
    // regionError
    describe('regionError', function(){
        beforeEach(function(){
            expect(controller.regionsErrors).toEqual({});
        });
        it('should unpack the errors into regionsErrors and all keys should point to arrays', function(){
            var one = 'error string one';
            var two = 'error string two';
            var three = ['array', 'of', 'error', 'strings'];
            var errors = {
                one: one,
                two: two,
                three: three
            };
            controller.regionError(errors);
            expect(controller.regionsErrors).toEqual({one: [one], two: [two], three: three});
        });
        it('should not allow for duplicate errors with the same key', function(){
            var one = ['string', 'thing', 'string'];
            var two = ['one', 'two'];
            var three = 'three';

            controller.regionError({one: one, two: two, three: three});
            expect(controller.regionsErrors).toEqual({one: ['string', 'thing'], two: ['one', 'two'], three: [three]});
            one.push('ahem');
            controller.regionError({one: one, three: three});
            expect(controller.regionsErrors).toEqual({one: ['string', 'thing', 'ahem'], two: ['one', 'two'], three: [three]});
        });
        it('should do nothing if something besides an object is passed', function(){
            var error = 'this is an error';

            expect(controller.regionsErrors).toEqual({});
            controller.regionError(error);
            expect(controller.regionsErrors).toEqual({});
        });
    });
    describe('template loading', function(){
        beforeEach(function(){
            controller.setRegion(regionObject);
            spyOn($rootScope, '$broadcast').andCallThrough();
        });
        // detailTemplateLoaded
        it('should flip the variable and broadcast an event', function(){
            expect(controller.isDetailTemplateLoaded).toBe(false);
            scope.detailTemplateLoaded();
            expect(controller.isDetailTemplateLoaded).toBe(true);
            expect($rootScope.$broadcast).not.toHaveBeenCalled();
            $timeout.flush();
            expect($rootScope.$broadcast).toHaveBeenCalledWith(controller.event+':detailTemplateLoaded', scope.regionObject, undefined);
        });
        // formTemplateLoaded
        it('should flip the variable and broadcast an event', function(){
            expect(controller.isFormTemplateLoaded).toBe(false);
            scope.formTemplateLoaded();
            expect(controller.isFormTemplateLoaded).toBe(true);
            expect($rootScope.$broadcast).not.toHaveBeenCalled();
            $timeout.flush();
            expect($rootScope.$broadcast).toHaveBeenCalledWith(controller.event+':formTemplateLoaded', scope.regionObject, undefined);
        });
    });
    describe('isDoneLoading', function(){
        beforeEach(function(){
            controller.setRegion(regionObject);
        });
        it('return false if only the regionObject is loaded', function(){
            expect(controller.isFormTemplateLoaded).toBe(false);
            expect(controller.isDetailTemplateLoaded).toBe(false);
            expect(controller.isDoneLoading()).toBe(false);
        });
        it('should return true when the form template is loaded', function(){
            expect(controller.isFormTemplateLoaded).toBe(false);
            expect(controller.isDetailTemplateLoaded).toBe(false);
            expect(controller.isDoneLoading()).toBe(false);
            controller.isFormTemplateLoaded = true;
            expect(controller.isDoneLoading()).toBe(true);
        });
        it('should return true when the detail template is loaded', function(){
            expect(controller.isFormTemplateLoaded).toBe(false);
            expect(controller.isDetailTemplateLoaded).toBe(false);
            expect(controller.isDoneLoading()).toBe(false);
            controller.isDetailTemplateLoaded = true;
            expect(controller.isDoneLoading()).toBe(true);
        });
        it('should always return true after initial load is complete', function(){
            expect(controller.isFormTemplateLoaded).toBe(false);
            expect(controller.isDetailTemplateLoaded).toBe(false);
            expect(controller.isDoneLoading()).toBe(false);
            controller.isFormTemplateLoaded = true;
            expect(controller.isDoneLoading()).toBe(true);
            controller.isFormTemplateLoaded = false;
            expect(controller.isDoneLoading()).toBe(true);
        });
    });
    describe('errorCheck', function(){
        beforeEach(function(){
            spyOn($log, 'warn');
            newScope();
        });
        it('should warn if visible fields is defined on both scope and options', function(){
            scope.visibleFields = scope.options.visible_fields;

            expect(newController).not.toThrow();
            expect($log.warn).toHaveBeenCalled();
        });
        it('should warn if visible fields is NOT defined on either scope or options', function(){
            delete scope.options.visible_fields;

            expect(newController).not.toThrow();
            expect($log.warn).toHaveBeenCalled();
        });
    });
    describe('getRegionObject', function(){
        beforeEach(function(){
            spyOn(HttpQueue, 'addObjectRequest').andCallFake(function(){
                return regionObject;
            });
            newScope();
            scope.options.endpoints = ['fallback'];
            scope.options.region_endpoint_pattern = '/__test__/';
            delete scope.options.object;
        });
        // TODO: should resole from a parent region that gets registered
        //it('should format the url correctly', function(){
        //    scope.options.object = {test: 'something'};
        //    newController();
        //    expect(HttpQueue.addObjectRequest).not.toHaveBeenCalled();
        //    scope.$digest();
        //    expect(HttpQueue.addObjectRequest).toHaveBeenCalledWith('/something/');
        //});
        it('should use the endpoints array if the pattern url cannot be resolved', function(){
            newController();
            expect(HttpQueue.addObjectRequest).not.toHaveBeenCalled();
            scope.$digest();
            expect(HttpQueue.addObjectRequest).toHaveBeenCalledWith('fallback');
        });
    });
});

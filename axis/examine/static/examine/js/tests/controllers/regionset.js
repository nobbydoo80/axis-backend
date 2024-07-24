/**
 * Created by mjeffrey on 10/20/14.
 */

describe('Controller: RegionSetController', function(){

    // injected
    var httpReal, $rootScope, $timeout, $compile, $log, HttpQueue, RegionService, HomeOptions, $controller;
    // used
    var controller, scope;

    beforeEach(module('httpReal', 'axis.region.regionSet', 'fixtureData'));
    beforeEach(inject(function(_httpReal_, _$rootScope_, _$timeout_, _$compile_, _$log_, _HttpQueue_, _RegionService_, _HomeOptions_, _$controller_){
        httpReal = _httpReal_;
        $rootScope = _$rootScope_;
        $timeout = _$timeout_;
        $compile = _$compile_;
        $log = _$log_;
        HttpQueue = _HttpQueue_;
        RegionService = _RegionService_;
        HomeOptions = _HomeOptions_;
        $controller = _$controller_;
    }));
    beforeEach(function(){
        newScope();
        newController();
    });
    function newScope(){
        scope = $rootScope.$new();
        HomeOptions.new_region_url = 'string';
        scope.options = angular.copy(HomeOptions);
    }
    function newController(){
        controller = $controller('RegionSetController', {
            $rootScope: $rootScope,
            $scope: scope,
            $timeout: $timeout,
            $compile: $compile,
            $log: $log,
            HttpQueue: HttpQueue,
            RegionService: RegionService
        });
    }

    it('should exist', function(){
        expect(!!controller).toBe(true);
    });
    it('should start with correct defaults', function(){
        expect(controller.regions).toEqual([]);
        expect(controller.processing).toEqual(false);
        expect(controller.regionsErrors).toEqual({});
        expect(controller.initialLoad).toEqual(false);
        expect(controller.eventPrefix).toEqual('RegionSetLoaded:');
        expect(controller.detailTemplatesCount).toEqual(0);
        expect(controller.formTemplatesCount).toEqual(0);
        expect(controller.event).toBe('RegionSetLoaded:home');
    });
    it('should have all the options on the controller', function(){
        var keys = Object.keys(HomeOptions);
        for(var i = 0; i < keys.length; i++){
            var key = keys[i];
            expect(controller[key]).toBeDefined();
            expect(controller[key]).toEqual(HomeOptions[key]);
        }
    });

    // addRegion
    describe('addRegion', function(){
        beforeEach(function(){
            spyOn(RegionService, 'addRegion').andCallFake(angular.identity);
        });
        it('should push a region into the list', function(){
            expect(controller.regions.length).toBe(0);
            controller.addRegion({});
            expect(controller.regions.length).toBe(1);
            controller.addRegion({});
            expect(controller.regions.length).toBe(2);
        });
        it('should get the region dependencies from options', function(){
            var deps = controller.region_dependencies;
            controller.addRegion({});

            var region = controller.regions[0];
            expect(region.region_dependencies).toEqual(deps);
        });
        it('should add the regionSet controller to each region as parentRegionController', function(){
            controller.addRegion({});
            var region = controller.regions[0];
            expect(region.parentRegionController).toBe(controller);
        });
        it('should add the parentRegionObject to each region', function(){
            controller.parentRegionObject = {test:'one'};

            controller.addRegion({});
            var region = controller.regions[0];
            expect(region.parentRegionObject).toBeDefined();
            expect(region.parentRegionObject).toEqual(controller.parentRegionObject);
        });
    });
    // removeRegion
    it('should remove a region', function(){
        controller.addRegion({id: 'one'});
        controller.addRegion({id: 'two'});
        controller.addRegion({id: 'three'});

        var one = controller.regions[0],
            two = controller.regions[1],
            three = controller.regions[2];

        expect(controller.regions.length).toBe(3);
        controller.removeRegion(two);
        expect(controller.regions.length).toBe(2);
        expect(controller.regions).toEqual([one, three]);
    });
    // fetchNewRegion
    describe('fetchNewRegion', function(){
        beforeEach(inject(function($q){
            spyOn(HttpQueue, 'addObjectRequest').andCallFake(function(){
                var deferred = $q.defer();
                deferred.resolve({});
                return deferred.promise;
            });
        }));
        it('should flip processing to true, then to false when it comes back', function(){
            expect(controller.processing).toBe(false);
            controller.fetchNewRegion();
            expect(controller.processing).toBe(true);
            $rootScope.$digest();
            expect(controller.processing).toBe(false);
        });
        it('should add the fetched region to the list', function(){
            spyOn(controller, 'addRegion');

            expect(controller.addRegion).not.toHaveBeenCalled();
            controller.fetchNewRegion();
            expect(controller.addRegion).not.toHaveBeenCalled();
            $rootScope.$digest();
            expect(controller.addRegion).toHaveBeenCalled();
        });
    });
    // regionSuccess
    it('should broadcast a success event', function(){
        spyOn($rootScope, '$broadcast');

        expect($rootScope.$broadcast).not.toHaveBeenCalled();
        controller.regionSuccess();
        expect($rootScope.$broadcast).toHaveBeenCalledWith(controller.event+':success', controller.regions, undefined);
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
                two: [two],
                three: three
            };
            controller.regionError(errors);
            expect(controller.regionsErrors).toEqual({one: [one], two: [two], three: three});
        });
        it('should now allow for duplicate errors with the same key', function(){
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
            spyOn($rootScope, '$broadcast').andCallThrough();
        });
        // detailTemplateLoaded
        it('should increment the number of templates loaded and fire an event', function(){
            var region = {id: 'one'},
                element = angular.element('<div></div>');

            expect(controller.detailTemplatesCount).toBe(0);
            scope.detailTemplateLoaded(region, element);
            expect(controller.detailTemplatesCount).toBe(1);
            expect($rootScope.$broadcast).not.toHaveBeenCalled();
            $timeout.flush();
            expect($rootScope.$broadcast).toHaveBeenCalledWith(controller.event+':detailTemplateLoaded', region, element);
        });
        // formTemplateLoaded
        it('should increment the number of templates loaded and fire an event', function(){
            var region = {id: 'one'},
                element = angular.element('<div></div>');

            expect(controller.formTemplatesCount).toBe(0);
            scope.formTemplateLoaded(region, element);
            expect(controller.formTemplatesCount).toBe(1);
            expect($rootScope.$broadcast).not.toHaveBeenCalled();
            $timeout.flush();
            expect($rootScope.$broadcast).toHaveBeenCalledWith(controller.event+':formTemplateLoaded', region, element);
        });
    });

    // init
    // initRegionObject
    // errorCheck
    // pieceLoaded
    it('should broadcast an event when a region and template are loaded', function(){
        // pieceLoaded() is an internal method, we can know its been called
        // by watching for teh event it broadcasts when everything is done loading.

        spyOn($rootScope, '$broadcast').andCallThrough();
        spyOn(RegionService, 'addRegion').andCallFake(angular.identity);
        expect($rootScope.$broadcast).not.toHaveBeenCalled();

        controller.addRegion({});
        expect($rootScope.$broadcast).not.toHaveBeenCalled();

        scope.detailTemplateLoaded();
        expect($rootScope.$broadcast).not.toHaveBeenCalled();
        $timeout.flush();
        expect($rootScope.$broadcast).toHaveBeenCalledWith(controller.event, controller.regions, undefined);
    });
    // isDoneLoading
    describe('isDoneLoading', function(){
        it('should return true if there is nothing to load', function(){
            scope.options.endpoints = [];
            newController();
            expect(controller.isDoneLoading()).toBe(true);
        });
        it('should return false if there is stuff to load', function(){
            scope.options.endpoints = ['one', 'two'];
            newController();
            expect(controller.isDoneLoading()).toBe(false);
        });
        it('should return true when either detail or form becomes fully loaded', function(){
            scope.options.endpoints = ['one', 'two', 'three'];
            newController();

            expect(controller.isDoneLoading()).toBe(false);
            controller.regions.push.apply(controller.regions, [1, 2, 3]);
            expect(controller.isDoneLoading()).toBe(false);
            controller.detailTemplatesCount = 3;
            expect(controller.isDoneLoading()).toBe(true);
        });
        it('should always return true after initial load is complete', function(){
            scope.options.endpoints = ['one', 'two', 'three'];
            newController();

            expect(controller.isDoneLoading()).toBe(false);
            controller.regions.push.apply(controller.regions, [1, 2, 3]);
            controller.detailTemplatesCount = 3;
            expect(controller.isDoneLoading()).toBe(true);
            controller.regions = [];
            controller.detailTemplatesCount = 0;
            expect(controller.isDoneLoading()).toBe(true);
        });
    });
    describe('errorCheck', function(){
        beforeEach(function(){
            spyOn($log, 'warn');
            newScope();
        });
        it('should thrown an errors if there are no endpoints key in the options', function(){
            delete scope.options.endpoints;

            expect(newController).toThrow();
        });
        it('should warn if there is no new_region_url key', function(){
            delete scope.options.new_region_url;

            expect(newController).not.toThrow();
            expect($log.warn).toHaveBeenCalled();
        });
        it('should warn if visibleFields was defined on scope AND options', function(){
            scope.visibleFields = scope.options.visible_fields;
            expect(newController).not.toThrow();
            expect($log.warn).toHaveBeenCalled();
        });
        it('should warn if there are no visibleFields defined on scope AND options', function(){
            delete scope.options.visible_fields;
            expect(newController).not.toThrow();
            expect($log.warn).toHaveBeenCalled();
        });
    });
    // TODO: getRegions
    //it('should send a request for each endpoint provided', inject(function($q){
    //    var one = {id: 'one'};
    //    var two = {id: 'two'};
    //    var three = {id: 'three'};
    //    var objs = [three, two, one];
    //    var endpoints = ['one', 'two','three'];
    //
    //    spyOn(HttpQueue, 'addObjectRequest').andCallFake(function(){
    //        var deferred = $q.defer();
    //        deferred.resolve(objs.pop());
    //        return deferred.promise;
    //    });
    //
    //    scope.options.endpoints = endpoints;
    //
    //    expect(HttpQueue.addObjectRequest).not.toHaveBeenCalled();
    //
    //    newController();
    //    spyOn(controller, 'addRegion').andCallThrough();
    //
    //    expect(HttpQueue.addObjectRequest).toHaveBeenCalled();
    //    expect(HttpQueue.addObjectRequest.callCount).toBe(3);
    //
    //    expect(controller.regions.length).toEqual(0);
    //    scope.$apply();
    //    expect(controller.regions.length).toEqual(3);
    //}));
});

describe('Directive: SingleRegion', function(){

    // injected
    var $rootScope, $compile, HomeOptions;
    // used
    var scope, element, singleRegionString;


    beforeEach(module('axis.region.singleRegion', 'fixtureData', 'templates', 'httpReal'));
    beforeEach(inject(function(_$rootScope_, _$compile_, _HomeOptions_){
        $rootScope = _$rootScope_;
        $compile = _$compile_;
        HomeOptions = _HomeOptions_;
    }));
    beforeEach(function(){
        singleRegionString = "<axis-single-region options='options'></axis-single-region>";
        newScope();
        newElement();
    });
    function newScope(){
        scope = $rootScope.$new();
        scope.options = HomeOptions;
        scope.options.endpoints = [];
    }
    function newElement(){
        element = $compile(singleRegionString)(scope);
        scope.$apply();
    }

    it('should exist', function(){
        expect(!!element).toBe(true);
    });

    it('should put the element on the controller', function(){
        var controller = element.controller('axisSingleRegion');
        expect(controller.hasOwnProperty('$element')).toBe(true);
    });

    it('should not setup the primary region watcher if there is no primary region attribute', function(){
        scope = element.isolateScope();
        expect(scope.isPrimaryRegion).toEqual(false);
    });
    it('should setup the primary region watcher if there is a primary region attribute', function(){
        singleRegionString = angular.element(singleRegionString);
        singleRegionString.attr('primary-region', 'id');
        scope.$root.creating = true;

        newElement();
        var isoScope = element.isolateScope();
        expect(isoScope.regionSet.isPrimaryRegion).toBe(true);
    });
    it('should put skipChildRegistration on the scope', function(){
        singleRegionString = angular.element(singleRegionString);
        singleRegionString.attr('skip-child-registration', 'true');

        newElement();
        var isoScope = element.isolateScope();
        expect(isoScope.skipChildRegistration).toBeDefined();
        expect(isoScope.skipChildRegistration).toBe(true);
    });
});

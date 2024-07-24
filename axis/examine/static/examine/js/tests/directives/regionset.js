describe('Directive: RegionSet', function(){

    // injected
    var $rootScope, $compile, HomeOptions;
    // used
    var scope, element;

    var regionSetString = "<axis-region-set options='options'></axis-region-set>";
    var regionSetNonFieldErrors = "<region-set-non-field-errors></region-set-non-field-errors>";

    beforeEach(module('axis.region.regionSet', 'fixtureData', 'bracketInterpolator'));
    beforeEach(inject(function(_$rootScope_, _$compile_, _HomeOptions_){
        $rootScope = _$rootScope_;
        $compile = _$compile_;
        HomeOptions = _HomeOptions_;
    }));
    beforeEach(function(){
        scope = $rootScope.$new();
        scope.options = HomeOptions;
        scope.options.endpoints = [];  // so it doesn't try to make any requests

        element = $compile(regionSetString)(scope);
        scope.$apply();
    });

    it('should exist', function(){
        expect(!!element).toBe(true);
    });
    it('should put the element on the controller', function(){
        var controller = element.controller('axisRegionSet');
        expect(controller.hasOwnProperty('$element')).toBe(true);
    });
    describe('regionSetNonFieldErrors', function(){
        it('should display the errors form the region set', function(){
            var scope = element.isolateScope();
            scope.regionSet.regionsErrors = {non_field_errors: ['one', 'two', 'three', 'longer error message']};

            var errElement = angular.element(regionSetNonFieldErrors);

            element.append(errElement);

            $compile(errElement)(scope);
            $rootScope.$apply();

            var html = element.html();

            expect(html).toContain('one');
            expect(html).toContain('two');
            expect(html).toContain('three');
            expect(html).toContain('longer error message');
        });
    });

});

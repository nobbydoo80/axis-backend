describe('Directive: Region', function(){

    // injected
    var $rootScope, $compile, $http, HomeOptions, RegionObjects;
    // used
    var element, scope, regionObject;

    var axisRegionString = "<axis-region></axis-region>";
    var axisSingleRegionString = "<axis-single-region options='options'> </axis-single-region>";
    var axisRegionSetString = "<axis-region-set> </axis-region-set>";

    beforeEach(module('httpReal', 'axis.region.region', 'axis.region.singleRegion', 'fixtureData'));
    beforeEach(inject(function(_$rootScope_, _$compile_, _$http_, _HomeOptions_, _RegionObjects_){
        $rootScope = _$rootScope_;
        $compile = _$compile_;
        $http = _$http_;
        HomeOptions = _HomeOptions_;
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
            }, 3000)
        }
    });
    beforeEach(function(){
        newScope();
        newElement();
    });
    function newScope(){
        scope = $rootScope.$new();
        scope.options = HomeOptions;
        scope.regionObject = regionObject;
        scope.regionSet = {};
    }
    function newElement(){
        element = $compile(axisRegionString)(scope);
        scope.$digest();
    }

    it('should exist', function(){
        expect(!!element).toBe(true);
    });

    it('should put the element and parentRegionSet onto the regionObject', function(){
        // checking for existance of key because it may be set to 'undefined'
        expect(scope.regionObject.hasOwnProperty('$element')).toBe(true);
        expect(scope.regionObject.hasOwnProperty('parentRegionSet')).toBe(true);
    });
    it('should put the type_name on the element', function(){
        expect(element.attr('type-name')).toEqual(scope.regionObject.type_name);
    });

    it('should set the scope for a transcluded heading and try to compile it', function(){
        var parentElement = angular.element($compile(axisSingleRegionString)(scope));
        var parentController = parentElement.controller('axisSingleRegion');
        spyOn(parentController, 'setHeadingScope').andCallThrough();
        spyOn(parentController, 'compileHeading').andCallThrough();

        var region = angular.element(axisRegionString);
        parentElement.append(region);
        $compile(region)(scope);

        expect(parentController.setHeadingScope).toHaveBeenCalled();
        expect(parentController.compileHeading).toHaveBeenCalled();
    });
    it('should add class to element for set seconds and remove it', inject(function($timeout){
        var testClass = 'testClass';
        scope = element.scope();
        expect(element.hasClass(testClass)).toBe(false);
        scope.timedClass(testClass);
        expect(element.hasClass(testClass)).toBe(true);
        $timeout.flush();
        expect(element.hasClass(testClass)).toBe(false);
    }));
    it('should register as a child if it has a parentRegionObject', inject(function(RegionService){
        spyOn(RegionService, 'registerChildRegion').andCallFake(angular.noop);
        scope.regionObject.parentRegionObject = {id: 'one'};

        $compile(axisRegionString)(scope);
        expect(RegionService.registerChildRegion).toHaveBeenCalledWith({id: 'one'}, scope.regionObject);
    }));
});

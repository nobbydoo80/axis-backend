describe('Directive: ActionStripSet', function(){

    // injected
    var $rootScope, $compile;
    // used
    var scope, element;

    var axisRegion = "<axis-region></axis-region>";
    var actionStripSet = "<action-strip-set></action-strip-set>";

    beforeEach(module('axis.region.region', 'axis.actionStrip.actionStripSet', 'templates'));
    beforeEach(inject(function(_$rootScope_, _$compile_){
        $rootScope = _$rootScope_;
        $compile = _$compile_;
    }));
    beforeEach(function(){
        newScope();
        newElement();
    });
    function newScope(){
        scope = $rootScope.$new();
        scope.regionObject = {};
        scope.options = {};
        scope.regionObject.actions = {one: ['one'], two: ['two']};
        scope.regionSet = {};
    }
    function newElement(){
        element = $compile(actionStripSet)(scope);
        scope.$digest();
    }

    it('should exist', function(){
        expect(!!element).toBe(true);
    });

    describe('regular action strip', function(){
        beforeEach(function(){
            // make an element with a parent.

            var p = $compile(axisRegion)(scope);
            var strip = angular.element(actionStripSet);
            p.append(strip);
            $compile(strip)(scope);

            element = p;
        });
        it('should get the actions from the parent scope', function(){
            scope.$digest();

            var stripScope = element.find('action-strip-set').scope();
            expect(stripScope.actionsObject).toEqual(scope.regionObject.actions);

            expect(element.find('action-strip').length).toBe(2);
        });
    });
    describe('single instance strip', function(){
        beforeEach(function(){
            var p = $compile(axisRegion)(scope);
            var strip = angular.element(actionStripSet);
            strip.attr('single-instance', 'one');
            p.append(strip);
            $compile(strip)(scope);

            element = p;
        });
        it('should only grab a reference to the key given', function(){
            scope.$digest();

            var stripScope = element.find('action-strip-set').scope();
            expect(stripScope.actionsObject.one).toBeDefined();
            expect(stripScope.actionsObject.one).toEqual(scope.regionObject.actions.one);
            scope.regionObject.actions.one.push('something');
            expect(stripScope.actionsObject.one).toEqual(scope.regionObject.actions.one);

            expect(element.find('action-strip').length).toBe(1);

        });
    });

});

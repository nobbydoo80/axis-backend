describe('Directive: ActionStrip', function(){

    // injected
    var $rootScope, $compile;
    // used
    var scope, element;

    var actionStripString = '<action-strip></action-strip>';

    beforeEach(module('axis.actionStrip.actionStrip'));
    beforeEach(inject(function(_$rootScope_, _$compile_){
        $rootScope = _$rootScope_;
        $compile = _$compile_;
    }));
    beforeEach(function(){
        scope = $rootScope.$new();

        element = $compile(actionStripString)(scope);
        scope.$apply();
    });

    it('should exist', function(){
        expect(!!element).toBe(true);
    });
});

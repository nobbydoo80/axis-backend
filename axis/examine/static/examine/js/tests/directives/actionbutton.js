describe('Directive: ActionButton', function(){

    // injected
    var $rootScope, $compile;
    // used
    var scope, element;

    var actionButtonString = '<action-button></action-button>';

    beforeEach(module('axis.actionStrip.actionButton'));
    beforeEach(inject(function(_$rootScope_, _$compile_){
        $rootScope = _$rootScope_;
        $compile = _$compile_;
    }));
    beforeEach(function(){
        scope = $rootScope.$new();

        element = $compile(actionButtonString)(scope);
        scope.$apply();
    });

    it('should exist', function(){
        expect(!!element).toBe(true);
    });
});

describe('Controller: ActionStripSetController', function(){

    // injected
    var $controller;
    // used
    var controller;

    beforeEach(module('axis.actionStrip.actionStripSet'));
    beforeEach(inject(function(_$controller_){
        $controller = _$controller_;
    }));
    beforeEach(function(){
        controller = $controller('ActionStripSetController', {});
    });

    it('should exist', function(){
        expect(!!controller).toBe(true);
    });
    it('should start with correct defaults', function(){
        expect(controller.singleInstance).toBe(false);
        expect(controller.actionsAttribute).toBe(false);
    });
});

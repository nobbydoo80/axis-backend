describe('Controller: ActionStripController', function(){

    // injected
    var $controller;
    // used
    var controller;

    beforeEach(module('axis.actionStrip.actionStrip'));
    beforeEach(inject(function(_$controller_){
        $controller = _$controller_
    }));
    beforeEach(function(){
        controller = $controller('ActionStripController', {});
    });

    it('should exist', function(){
        expect(!!controller).toBe(true);
    });
});

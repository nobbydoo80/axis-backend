/**
 * Created by mjeffrey on 12/26/14.
 */

describe('Service: Modal', function(){

    // injected
    var $rootScope, $httpBackend, $injector, $controller;
    // used
    var Modal, controller, $modalInstance;

    beforeEach(module('axis.services.Modal', 'templates'));
    beforeEach(inject(function(_$rootScope_, _Modal_, _$httpBackend_, _$injector_){
        $rootScope = _$rootScope_;
        Modal = _Modal_;
        $httpBackend = _$httpBackend_;
        $injector = _$injector_;
        $controller = $injector.get('$controller');
    }));
    beforeEach(function(){
        $httpBackend.expectGET('template.html').respond('a template');
        $modalInstance = jasmine.createSpyObj('$modalInstance', ['close', 'dismiss']);
        controller = $controller('ModalFactoryController', {
            $scope: $rootScope.$new(),
            $modalInstance: $modalInstance,
            regionObject: {},
            extraData: {}
        });
    });

    it('should exist', function(){
        expect(!!Modal).toBe(true);
        expect(!!controller).toBe(true);
    });
    it('should have the right initial data on the controller', function(){
        expect(controller.regionObject).toBeDefined();
        expect(controller.extraData).toBeDefined();
        expect(controller.ok).toBeDefined();
        expect(controller.cancel).toBeDefined();
    });
    it('should close and dismiss the modal as expected', function(){
        expect($modalInstance.close).not.toHaveBeenCalled();
        expect($modalInstance.dismiss).not.toHaveBeenCalled();

        controller.ok();

        expect($modalInstance.close).toHaveBeenCalledWith({});
        expect($modalInstance.dismiss).not.toHaveBeenCalled();

        controller.cancel();

        expect($modalInstance.close).toHaveBeenCalledWith({});
        expect($modalInstance.dismiss).toHaveBeenCalled();
    });
    it('should place wanted extra data on extraData', function(){
        var $httpBackend = $injector.get('$httpBackend');
        $httpBackend.expectGET('/get/extra/data/').respond({one: 'one', two: 'two', three: 'three'});

        var action = {modal: {templateUrl: 'template.html', dataUrl: '/get/extra/data/'}};
        var modal = Modal(action);
        $rootScope.$apply();
        $httpBackend.flush();
    });
    it('should make a modal and return the result', function(){
        var action = {modal: {templateUrl: 'template.html'}};
        var modal = Modal(action);
        $rootScope.$apply();
    });
});

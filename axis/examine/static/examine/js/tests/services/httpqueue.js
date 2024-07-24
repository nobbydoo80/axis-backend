describe('Service: HttpQueue', function(){

    // injected
    var $rootScope, $httpBackend, $http;
    // used
    var HttpQueue;

    beforeEach(module('axis.services.HttpQueue'));
    beforeEach(inject(function(_$rootScope_, _HttpQueue_, _$httpBackend_, _$http_){
        $rootScope = _$rootScope_;
        HttpQueue = _HttpQueue_;
        $httpBackend = _$httpBackend_;
        $http = _$http_;
    }));

    it('should exist', function(){
        expect(!!HttpQueue).toBe(true);
    });

    it('should call template requests immediately', function(){
        $httpBackend.whenGET(/.*/).respond({});
        spyOn($http, 'get').andCallThrough();

        expect($http.get.callCount).toBe(0);
        HttpQueue.addTemplateRequest('one');
        expect($http.get.callCount).toBe(1);
        HttpQueue.addTemplateRequest('two');
        HttpQueue.addTemplateRequest('three');
        expect($http.get.callCount).toBe(3);
        HttpQueue.addTemplateRequest('four');
        HttpQueue.addTemplateRequest('five');
        HttpQueue.addTemplateRequest('six');
        expect($http.get.callCount).toBe(6);

        $rootScope.$apply();
    });
    it('should add object requests to the queue', function(){
        $httpBackend.whenGET(/.*/).respond({});
        spyOn($http, 'get').andCallThrough();

        expect($http.get.callCount).toBe(0);
        HttpQueue.addObjectRequest('one');  // should be called immediately.
        expect($http.get.callCount).toBe(1);
        HttpQueue.addObjectRequest('two');  // should be queued
        expect($http.get.callCount).toBe(1);
        HttpQueue.addObjectRequest('three');  // also queued
        expect($http.get.callCount).toBe(1);
        $httpBackend.flush();  // run the rest of them
        expect($http.get.callCount).toBe(3);
    });
    it('should reject a promise', function(){
        $httpBackend.whenGET(/.*/).respond(400, {});
        var mock ={resolve: angular.noop, reject: angular.noop};

        spyOn(mock, 'resolve');
        spyOn(mock, 'reject');
        spyOn($http, 'get').andCallThrough();

        HttpQueue.addObjectRequest('one').then(mock.resolve, mock.reject);

        expect($http.get).toHaveBeenCalled();
        expect(mock.resolve).not.toHaveBeenCalled();
        expect(mock.reject).not.toHaveBeenCalled();

        $httpBackend.flush();
        expect($http.get).toHaveBeenCalled();
        expect(mock.resolve).not.toHaveBeenCalled();
        expect(mock.reject).toHaveBeenCalled();
    });

});

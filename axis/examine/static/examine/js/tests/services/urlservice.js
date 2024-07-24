describe('Service: UrlService', function(){

    // injected
    var $rootScope, $location, $state, $injector, TabService;
    // used
    var UrlService;

    beforeEach(module('axis.services.UrlService', 'axis.services.TabService'));
    beforeEach(inject(function(_$rootScope_, _$location_, _$state_, _$injector_, _TabService_){
        $rootScope = _$rootScope_;
        $location = _$location_;
        $state = _$state_;
        $injector = _$injector_;
        TabService = _TabService_;
    }));

    it('should exist', function(){
        UrlService = $injector.get('UrlService');
        expect(!!UrlService).toBe(true);
    });

    it('should set the new updated location.pathname', function(){
        spyOn(String.prototype, 'replace').andCallThrough();

        $location.pathname = 'subdivision/add';
        UrlService = $injector.get('UrlService');
        TabService.addTab('tabs.homes');
        $state.go('tabs.homes');
        $rootScope.$apply();
        UrlService.setUpdatedLink('homes/123');
        $rootScope.$apply();
        expect(String.prototype.replace).toHaveBeenCalledWith('subdivision/add', 'homes/123');

    });
    it('should go to index if there is no current state', function(){
        UrlService = $injector.get('UrlService');
        spyOn($state, 'go');

        UrlService.setUpdatedLink('homes/123');
        expect($state.go).toHaveBeenCalledWith('index');
    });
});

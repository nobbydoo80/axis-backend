describe('Service: TabService', function(){

    // injected
    var $rootScope, $state, $injector;
    // used
    var TabService;

    beforeEach(module('axis.services.TabService'));
    beforeEach(inject(function(_$rootScope_, _TabService_, _$state_, _$injector_){
        $rootScope = _$rootScope_;
        TabService = _TabService_;
        $state = _$state_;
        $injector = _$injector_;
    }));

    it('should exist', function(){
        expect(!!TabService).toBe(true);
    });
    it('should get the tabs', function(){
        expect(TabService.tabs).toEqual([]);
    });

    describe('addTab', function(){
        it('should add tab as a possible state', function(){
            expect($state.get().length).toBe(1);  // have to allow for the index state it starts with
            TabService.addTab('tabs.homes');
            expect($state.get().length).toBe(3);  // have to allow for the abstract tabs state
        });
        it('should give each tab the correct defaults', function(){
            var one = 'tabs.homes';
            TabService.addTab(one);
            var state = $state.get().pop();
            expect(state.name).toEqual(one);
            var homes = TabService.tabs['homes'];
            expect(homes.active).toBe(false);
            expect(homes.disabled).toBe(false);

            var two = 'tabs.documents';
            TabService.addTab(two, true);
            state = $state.get().pop();
            expect(state.name).toEqual(two);
            var documents = TabService.tabs['documents'];
            expect(documents.active).toBe(false);
            expect(documents.disabled).toBe(true);
        });
        it('should throw if trying to add a tab with no name', function(){
            expect(TabService.addTab).toThrow();
        })
    });
    describe('go', function(){
        beforeEach(function(){
            TabService.addTab('tabs.homes');
            expect($state.current.name).not.toEqual('tabs.homes');
        });
        it('should route to a tab', function(){
            TabService.go('tabs.homes');
            $rootScope.$apply();
            expect($state.current.name).toEqual('tabs.homes');
        });
        it('should go to the first available state if a state is disabled', function(){
            TabService.addTab('tabs.documents', true);
            TabService.go('tabs.documents');
            $rootScope.$apply();
            expect($state.current.name).toEqual('tabs.homes');
        });
        it('should go to index if all states are disabled', function(){
            var RuntimeStates = $injector.get('RuntimeStates'),
                tabs = TabService.tabs;
            RuntimeStates.addState('index', {url: '/index', template: ''});

            TabService.go('tabs.homes');
            $rootScope.$apply();
            expect($state.current.name).toEqual('tabs.homes');

            angular.forEach(tabs, function(obj, key){
                obj.disabled = true;
            });

            TabService.go('tabs.homes');
            $rootScope.$apply();
            expect($state.current.name).toEqual('index');
        });
        it('should go to a non disabled tab', function(){
            TabService.addTab('tabs.one', true);
            TabService.addTab('tabs.two', false);
            TabService.addTab('tabs.three', true);
            TabService.updateDisableListener('tabs.homes', true);

            TabService.go('tabs.three');
            $rootScope.$apply();
            expect($state.current.name).toEqual('tabs.two');

        });
        it('should go to the first available state if trying to go to a tab that is not registered', function(){
            TabService.go('tabs.documents');
            $rootScope.$apply();
            expect($state.current.name).toEqual('tabs.homes');
        });
        it('should deactivate previous tab on subsequent change', function(){
            var tabs = TabService.tabs;
            TabService.addTab('tabs.documents', false);

            $rootScope.$apply();
            expect(tabs['homes'].active).toBe(false);

            $rootScope.$apply();
            TabService.go('tabs.homes');
            expect(tabs['homes'].active).toBe(true);

            $rootScope.$apply();
            TabService.go('tabs.documents');
            expect(tabs['homes'].active).toBe(false);
        });
        it('should deactivate all tabs if going to a non tab state', function(){
            var RuntimeStates = $injector.get('RuntimeStates');
            RuntimeStates.addState('index', {url: '/index', template: ''});

            var tabs = TabService.tabs;
            TabService.addTab('tabs.documents', false);
            TabService.addTab('tabs.another', false);

            TabService.go('tabs.homes');
            $rootScope.$apply();
            expect(tabs['homes'].active).toBe(true);

            $state.go('index');

            angular.forEach(tabs, function(obj, key){
                expect(obj.active).toBe(false);
            })
        });
    });
    describe('updateDisabledListener', function(){
        beforeEach(function(){
            TabService.addTab('tabs.homes');
            expect($state.current.name).not.toEqual('tabs.homes');
        });
        it('should change the tabs status to the new value', function(){
            var tabs = TabService.tabs;
            expect(tabs['homes'].disabled).toBe(false);
            TabService.updateDisableListener('tabs.homes', true);
            expect(tabs['homes'].disabled).toBe(true);
            TabService.updateDisableListener('tabs.homes', false);
            expect(tabs['homes'].disabled).toBe(false);
        });
    });
});

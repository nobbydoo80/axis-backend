/**
 * Created by mjeffrey on 10/20/14.
 */

describe('Controller: ExamineView', function(){

    // injected
    var $rootScope, $state, ExamineSettings, TabService, RegionService, $controller, FieldFixture;
    // used
    var controller, scope, initialDependencies;

    beforeEach(module('examineApp', 'fixtureData'));
    beforeEach(inject(function(_$rootScope_, _$state_, _ExamineSettings_, _TabService_, _RegionService_, _$controller_, _FieldFixture_){
        $rootScope = _$rootScope_;
        $state = _$state_;
        ExamineSettings = _ExamineSettings_;
        TabService = _TabService_;
        RegionService = _RegionService_;
        $controller = _$controller_;
        FieldFixture = _FieldFixture_;
    }));
    beforeEach(function(){
        newScope();
        newController();
        initialDependencies = ['ui.bootstrap', 'ui.router', 'ui.select', 'axis.filters', 'axis.services', 'axis.fields', 'axis.region', 'axis.actionStrip'];
    });
    function newScope(){
        scope = $rootScope.$new();
    }
    function newController(){
        controller = $controller('ExamineViewController', {
            $rootScope: $rootScope,
            $state: $state,
            $scope: scope,
            ExamineSettings: ExamineSettings,
            TabService: TabService,
            RegionService: RegionService
        });
    }

    it('should exist', function(){
        expect(!!controller).toBe(true);
    });
    it('should have the correct initial dependencies', function(){
        expect(getDependencies()).toEqual(initialDependencies);
    });
    it('should inject any dependencies declared', function(){
        var extraDeps = ['one', 'two', 'three'];
        initialDependencies.push.apply(initialDependencies, extraDeps);
        expect(getDependencies(extraDeps)).toEqual(initialDependencies);
    });
    it('should make the $state available on rootScope', function(){
        expect($rootScope.$state).toBe($state);
    });
    it('should grab the tabs object', function(){
        newController();

        expect(controller.tabsActive).toBeDefined();
        expect(scope.tabsActive).toBeDefined();
        expect(controller.tabsActive).toBe(TabService.tabs);
        expect(scope.tabsActive).toBe(TabService.tabs);
    });
    it('should get the pageRegions from ExamineSettings', function(){
        expect(scope.pageRegions).toBe(ExamineSettings.regions_endpoints);
        expect(controller.pageRegions).toBe(ExamineSettings.regions_endpoints);
    });
    it('should determine if a field is truly a hidden field', function(){
        expect(scope.isHiddenField(FieldFixture.AutoHeavySelect2Widget)).toBe(false);
        expect(scope.isHiddenField(FieldFixture.TextInput)).toBe(false);
        expect(scope.isHiddenField(FieldFixture.CheckBoxInput)).toBe(false);
        expect(scope.isHiddenField(FieldFixture.Select2Widget)).toBe(false);
        expect(scope.isHiddenField(FieldFixture.HiddenInput)).toBe(true);
    });
});

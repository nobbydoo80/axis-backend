describe('Service: RegionService', function(){

    // injected
    var $rootScope;
    // used
    var RegionService;

    beforeEach(module('axis.services.RegionService', 'bracketInterpolator'));
    beforeEach(inject(function(_$rootScope_, _RegionService_){
        $rootScope = _$rootScope_;
        RegionService = _RegionService_;
    }));

    it('should exist', function(){
        expect(!!RegionService).toBe(true);
        expect(RegionService.helpers.regions).toEqual([]);
        expect(RegionService.helpers.regionsMap).toEqual({});
    });

    it('should add a region', function(){
        expect(RegionService.helpers.regions.length).toBe(0);
        RegionService.addRegion({});
        expect(RegionService.helpers.regions.length).toBe(1);
        RegionService.addRegion({});
        expect(RegionService.helpers.regions.length).toBe(2);
    });
    it('should remove a region', function(){
        var one = {id: 'one'};
        var two = {id: 'two'};
        RegionService.addRegion(one);
        RegionService.addRegion(two);

        expect(RegionService.helpers.regions.length).toBe(2);
        RegionService.removeRegion(two);
        expect(RegionService.helpers.regions.length).toBe(1);
        RegionService.removeRegion(one);
        expect(RegionService.helpers.regions.length).toBe(0);
    });
    it('should determine if a region has dependencies', function(){
        var one = {};
        var two = {region_dependencies: {}};
        var three = {region_dependencies: {home: [{serialize_as: 'id', dep: 'something'}]}};
        RegionService.addRegion(one);
        RegionService.addRegion(two);
        RegionService.addRegion(three);

        expect(RegionService.helpers.hasDependencies(one)).toBe(false);
        expect(RegionService.helpers.hasDependencies(two)).toBe(false);
        expect(RegionService.helpers.hasDependencies(three)).toBe(true);
    });
    it('should get a region by region object', function(){
        var one = {key: 'something'};
        RegionService.addRegion(one);
        var gotten = RegionService.getRegion(one);
        expect(gotten).toBe(one);
    });
    it('should get a region by type_name', function(){
        var one = {type_name: 'one'};
        var two = {type_name: 'two'};

        RegionService.addRegion(one);
        RegionService.addRegion(two);

        var gottenOne = RegionService.getRegionFromTypeName(one.type_name);
        var gottenTwo = RegionService.getRegionFromTypeName(two.type_name);

        expect(gottenOne).toBe(one);
        expect(gottenTwo).toBe(two);
    });
    it('should add regions to a list', function(){
        var one = {type_name: 'one', id: 1};
        var two = {type_name: 'two', id: 2};
        var three = {type_name: 'one', id: 3};

        RegionService.addRegion(one);
        RegionService.addRegion(two);
        RegionService.addRegion(three);

        var gottenOne = RegionService.getRegionFromTypeName(one.type_name);

        expect(gottenOne).toEqual([one, three]);
    });

    it('should register a child with a parent', function(){
        var parent = {controller: {children: []}};
        var child = {id: 'child'};

        RegionService.registerChildRegion(parent, child);

        expect(parent.controller.children).toEqual([child]);
    });
    it('should register a child with a parent by type name', function(){
        var parent = {type_name: 'home', controller: {children: []}};
        var child = {id: 'child'};

        RegionService.addRegion(parent);
        RegionService.registerChildRegionByTypeName('home', child);
        expect(parent.controller.children).toEqual([child]);
    });
    it('should return a single region value', function(){
        var region = {type_name: 'home', object: {test: 'this is a message'}};
        RegionService.addRegion(region);
        var val = RegionService.helpers.getRegionValue('home', 'test');
        expect(val).toEqual(region.object.test);
    });
    it('should throw an error if a region does not have an object on it', function(){
        var region = {type_name: 'home'};
        RegionService.addRegion(region);

        function go(){
            RegionService.helpers.getRegionValue('home', 'id');
        }

        expect(go).toThrow();
    });
    it('should throw an error when trying to get a value that does not exist', function(){
        var region = {type_name: 'home', object: {test: 'this is a message'}};
        RegionService.addRegion(region);

        function go(){
            RegionService.helpers.getRegionValue('home', 'id');
        }

        expect(go).toThrow();
    });
    it('should give the correct error message when it errors', function(){
        var message = "'id' is undefined for 'home'";
        RegionService.addRegion({type_name: 'home', object: {}});
        try{
            RegionService.helpers.getRegionValue('home', 'id');
        }catch(e){
            expect(e.getMessage()).toEqual(message);
        }
    });
    describe('fetch region dependencies', function(){
        var home, main;
        beforeEach(function(){
            main = {
                type_name: 'home_status',
                region_dependencies: {
                    home: [
                        {
                            field_name: 'id',
                            serialize_as: 'home'
                        }
                    ]
                },
                object: {}
            };
            home = {
                type_name: 'home',
                object: {id: 1234},
            };
        });
        it('should grab dependencies from the parent if there is one', function(){
            main.parentRegionSet = {parentRegionObject: home};

            var deps = RegionService.helpers.fetchRegionDependencies(main);
            expect(deps.home).toEqual(home.object.id);
        });
        it('should grab a regions dependencies', function(){
            RegionService.addRegion(home);

            var deps = RegionService.helpers.fetchRegionDependencies(main);
            expect(deps.home).toEqual(home.object.id);
        });
    });

    xit('should get a list of region dependencies');  // TODO: make as a method on the regionObject itself
    xit('should get a list of regions type_names holding another regions dependecies');
    xit('should resolve a regions dependencies from parent RegionObject');  // TODO: make as a method on the reigonObject itself
    xit('should resolve a regions dependencies');  // for regions that don't have a parent.

    xit('should error if a region defined as a dependency does not exist');
    xit('should error if a region defined as a dependency does not have the needed key');

    // maybes
    xit('should get a list of regions by type_name');
    xit('should get a specific value from a region');
});

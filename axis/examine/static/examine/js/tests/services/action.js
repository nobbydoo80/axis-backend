describe('Service: Actions', function(){

    // injected
    var $rootScope, $log, $injector, $httpBackend, $q, $controller;
    // used
    var Actions, regionObject, callMethod, ActionUtils, ActionMethods, $window;

    beforeEach(function(){
        angular.mock.module('axis.services', function($provide){
            var window = {
                location: {
                    replace: jasmine.createSpy(),
                    pathname: '/subdivision/123/',
                    hash: '/something'
                }
            };
            $provide.value("$window", window);
        })
    });
    beforeEach(module('axis.services.Actions', 'axis.region.region'));
    beforeEach(inject(function(_$rootScope_, _$log_, _$injector_){
        $rootScope = _$rootScope_;
        $log = _$log_;
        $injector = _$injector_;
        $httpBackend = $injector.get('$httpBackend');
        $q = $injector.get('$q');
        $controller = $injector.get('$controller');
        Actions = $injector.get('Actions');
        ActionMethods = Actions.methods;
        ActionUtils = Actions.utils;
        $window = {location: {pathname: jasmine.createSpy()}};
    }));
    beforeEach(function(){
        var $scope = $rootScope.$new();
        regionObject = {
            type_name: 'test',
            parentRegionSet: {
                processing: false
            }
        };
        $scope.regionObject = regionObject;
        $scope.options = {};
        $scope.regionSet = {};
        controller = newController($scope)
        regionObject.controller = controller;
    });

    function newController($scope){
        var controller = $controller('RegionController', {
            $rootScope: $rootScope,
            $scope: $scope,
            $q: $q,
            Actions: Actions
        });
        regionObject.controller = controller;
        return controller;
    }

    it('should exist', function(){
        expect(!!Actions).toBe(true);
    });

    describe('callMethod', function(){
        var testMethod;
        beforeEach(function(){
            testMethod = jasmine.createSpy('testMethod');
            spyOn($log, 'error');
            expect($log.error).not.toHaveBeenCalled();
            Actions.addMethod('test', testMethod);
        });
        it('should error whe trying to call a method that does not exist', function(){
            var checked = false;
            var result = Actions.callMethod('nononono', regionObject).then(function(){
                expect(true).toBe(false);
            }, function(){
                checked = true;
            });
            $rootScope.$apply();
            expect(checked).toBe(true);
            expect($log.error).toHaveBeenCalled();
        });
        it('should return a promise when calling a method', function(){
            var result = Actions.callMethod('save', regionObject);
            expect(result.then).toBeDefined();
        });
        it('should call a pre method if one exists', function(){
            var preMethod = jasmine.createSpy('preMethod');
            Actions.addPreMethod('test', preMethod);
            Actions.callMethod('test', regionObject);
            expect(preMethod).not.toHaveBeenCalled();
            $rootScope.$apply();
            expect(preMethod).toHaveBeenCalled();
        });
        it('should call a post method if one exists', function(){
            var postMethod = jasmine.createSpy('postMethod');
            Actions.addPostMethod('test', postMethod);
            Actions.callMethod('test', regionObject);
            expect(postMethod).not.toHaveBeenCalled();
            $rootScope.$apply();
            expect(postMethod).toHaveBeenCalled();
        });
        it('should take an action object', function(){
            var action = {instruction: 'test'};
            expect(testMethod).not.toHaveBeenCalled();
            Actions.callMethod(action, regionObject);
            $rootScope.$apply();
            expect(testMethod).toHaveBeenCalled();
            expect(testMethod.callCount).toBe(1);
        });
        it('should attempt to resolve dependencies twice if the action is a save', function(){
            var RegionService = $injector.get('RegionService');
            regionObject.region_dependencies = {
                home: [
                    {
                        field_name: 'id',
                        serialize_as: 'home'
                    }
                ]
            };
            var home = {
                type_name: 'home',
                commit_instruction: 'save',
                controller: {
                    addProcessingStatus: jasmine.createSpy('addProcessingStatus')
                },
                object: {}
            };
            RegionService.addRegion(home);
            spyOn(Actions.utils, 'resolveDependencies').andCallThrough();
            var count = 0;
            spyOn(ActionMethods, 'save').andCallFake(function(){
                return $q(function(resolve, reject){
                    if(count == 2){
                        resolve(regionObject);
                    } else {
                        home.object.id = 123;
                        resolve(home);
                    }
                    ++count;
                });
            });

            expect(Actions.utils.resolveDependencies.callCount).toBe(0);
            Actions.callMethod('save', regionObject);
            expect(Actions.utils.resolveDependencies.callCount).toBe(1);
            $rootScope.$apply();
            // first: from regionObject
            // second: from home
            // third: from home second attempt
            expect(Actions.utils.resolveDependencies.callCount).toBe(3);
        });
        it('should call the modal service if the action says it should', function(){
            var $modal = $injector.get('$modal');
            spyOn($modal, 'open').andCallFake(function(){
                return {
                    result: jasmine.createSpy('result')
                }
            });

            var action = {instruction: 'test', modal: true};
            Actions.callMethod(action, regionObject);

            $rootScope.$apply();

            expect($modal.open).toHaveBeenCalled();
        });
        it('should bubble errors', function(){
            var checked = false;
            spyOn(Array.prototype, 'join').andCallThrough();
            testMethod.andCallFake(function(){
                return $q.reject(new Error('test'));
            });

            Actions.callMethod('test', regionObject).then(function(){
                expect(false).toBe(true);
            }, function(data){
                expect(data.message).toEqual('test');
                checked = true;
            });
            $rootScope.$apply();
            expect(checked).toBe(true);
        });
    });
    describe('Actions', function(){
        describe('addMethod', function(){
            beforeEach(function(){
                spyOn($log, 'error');
            });
            it('should error when trying to add a method with a name that already exists', function(){
                Actions.addMethod('save');
                expect($log.error).toHaveBeenCalled();
            });
            it('should add a callable method', inject(function(){
                var testMethod = jasmine.createSpy('testMethod');
                Actions.callMethod('test', regionObject);
                expect($log.error).toHaveBeenCalled();
                Actions.addMethod('test', testMethod);
                Actions.callMethod('test', regionObject);
                expect(testMethod).not.toHaveBeenCalled();
                $rootScope.$apply();  // trigger the promises to resolve.
                expect(testMethod).toHaveBeenCalled();
            }));
            it('should not overwrite an added method', function(){
                var testMethodOne = jasmine.createSpy('testMethodOne');
                var testMethodTwo = jasmine.createSpy('testMethodTwo');

                Actions.addMethod('test', testMethodOne);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethodOne).toHaveBeenCalled();
                expect(testMethodOne.callCount).toBe(1);
                expect(testMethodTwo).not.toHaveBeenCalled();

                Actions.addMethod('test', testMethodTwo);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethodOne).toHaveBeenCalled();
                expect(testMethodOne.callCount).toBe(2);
                expect(testMethodTwo).not.toHaveBeenCalled();
            });
            it('should overwrite existing method if overwrite flag is true', function(){
                var testMethodOne = jasmine.createSpy('testMethodOne');
                var testMethodTwo = jasmine.createSpy('testMethodTwo');

                Actions.addMethod('test', testMethodOne);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethodOne).toHaveBeenCalled();
                expect(testMethodOne.callCount).toBe(1);
                expect(testMethodTwo).not.toHaveBeenCalled();
                expect(testMethodTwo.callCount).toBe(0);

                Actions.addMethod('test', testMethodTwo, true);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethodOne).toHaveBeenCalled();
                expect(testMethodOne.callCount).toBe(1);
                expect(testMethodTwo).toHaveBeenCalled();
                expect(testMethodTwo.callCount).toBe(1);

            });
        });
        describe('addPreMethod', function(){
            var testMethod;
            beforeEach(function(){
                testMethod = jasmine.createSpy('testMethod');
                spyOn($log, 'error');
                expect($log.error).not.toHaveBeenCalled();
                Actions.addMethod('test', testMethod);
            });
            it('should error when trying to add a pre method that does not exist', function(){
                function go(){
                    Actions.addPreMethod('test', 'nonon');
                }
                expect(go).toThrow();
            });
            it('should error when trying to add a pre method and a function is not passed', function(){
                function go(){
                    Actions.addPreMethod('test');
                }
                expect(go).toThrow();
            });
            it('should add a pre method', function(){
                var testPreMethod = jasmine.createSpy('testPreMethod');

                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethod.callCount).toBe(1);
                expect(testPreMethod.callCount).toBe(0);

                Actions.addPreMethod('test', testPreMethod);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethod.callCount).toBe(2);
                expect(testPreMethod.callCount).toBe(1);
            });
            it('should add a pre method from the method list', function(){
                var testMethodTwo = jasmine.createSpy('testMethodTwo');

                Actions.addMethod('testMethodTwo', testMethodTwo);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethod.callCount).toBe(1);
                expect(testMethodTwo.callCount).toBe(0);

                Actions.addPreMethod('test', 'testMethodTwo');
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testMethod.callCount).toBe(2);
                expect(testMethodTwo.callCount).toBe(1);
            });
            it('should add multiple pre methods', function(){
                var preMethodOne = jasmine.createSpy('preMethodOne');
                var preMethodTwo = jasmine.createSpy('preMethodTwo');
                function back(a){return $q.when(a)}
                preMethodOne.andCallFake(back);
                preMethodTwo.andCallFake(back);

                Actions.addPreMethod('test', preMethodOne);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(preMethodOne.callCount).toBe(1);
                expect(preMethodTwo.callCount).toBe(0);

                Actions.addPreMethod('test', preMethodTwo);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(preMethodOne.callCount).toBe(2);
                expect(preMethodTwo.callCount).toBe(1);
            });
            it('should add a pre method to a specific type', function(){
                var testHomeMethod = jasmine.createSpy('testHomeMethod');
                var testTestMethod = jasmine.createSpy('testTestMethod');

                Actions.addPreMethodToType('test', 'home', testHomeMethod);
                Actions.addPreMethodToType('test', 'test', testTestMethod);

                expect(testHomeMethod.callCount).toBe(0);
                expect(testTestMethod.callCount).toBe(0);

                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testHomeMethod.callCount).toBe(0);
                expect(testTestMethod.callCount).toBe(1);
            });
            it('should add a post method to a specific type', function(){
                var testHomeMethod = jasmine.createSpy('testHomeMethod');
                var testTestMethod = jasmine.createSpy('testTestMethod');

                Actions.addPostMethodToType('test', 'home', testHomeMethod);
                Actions.addPostMethodToType('test', 'test', testTestMethod);

                expect(testHomeMethod.callCount).toBe(0);
                expect(testTestMethod.callCount).toBe(0);

                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testHomeMethod.callCount).toBe(0);
                expect(testTestMethod.callCount).toBe(1);
            });
            it('should call a type specific pre method and global pre method', function(){
                var testHomeMethod = jasmine.createSpy('testHomeMethod');
                var testTestMethod = jasmine.createSpy('testTestMethod');
                var testGlobalMethod = jasmine.createSpy('testGlobalMethod');

                Actions.addPreMethodToType('test', 'home', testHomeMethod);
                Actions.addPreMethodToType('test', 'test', testTestMethod);
                Actions.addPreMethod('test', testGlobalMethod);

                expect(testHomeMethod.callCount).toBe(0);
                expect(testTestMethod.callCount).toBe(0);
                expect(testGlobalMethod.callCount).toBe(0);

                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testHomeMethod.callCount).toBe(0);
                expect(testTestMethod.callCount).toBe(1);
                expect(testGlobalMethod.callCount).toBe(1);
            });
            it('should call a type specific post method and global post method', function(){
                var testHomeMethod = jasmine.createSpy('testHomeMethod');
                var testTestMethod = jasmine.createSpy('testTestMethod');
                var testGlobalMethod = jasmine.createSpy('testGlobalMethod');

                Actions.addPostMethodToType('test', 'home', testHomeMethod);
                Actions.addPostMethodToType('test', 'test', testTestMethod);
                Actions.addPostMethod('test', testGlobalMethod);

                expect(testHomeMethod.callCount).toBe(0);
                expect(testTestMethod.callCount).toBe(0);
                expect(testGlobalMethod.callCount).toBe(0);

                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testHomeMethod.callCount).toBe(0);
                expect(testTestMethod.callCount).toBe(1);
                expect(testGlobalMethod.callCount).toBe(1);
            });
            it('should add a pre method to each type_name if provided in a list', function(){
                var testUberMethod = jasmine.createSpy('testUberMethod');

                Actions.addPreMethodToType('test', ['one', 'two', 'three'], testUberMethod);

                expect(testUberMethod.callCount).toBe(0);

                regionObject.type_name = controller.type_name = 'one';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(1);

                regionObject.type_name = controller.type_name = 'home';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(1);

                regionObject.type_name = controller.type_name = 'two';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(2);

                regionObject.type_name = controller.type_name = 'test';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(2);

                regionObject.type_name = controller.type_name = 'three';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(3);
            });
            it('should add a post method to each type_name if provided in a list', function(){
                var testUberMethod = jasmine.createSpy('testUberMethod');

                Actions.addPostMethodToType('test', ['one', 'two', 'three'], testUberMethod);

                expect(testUberMethod.callCount).toBe(0);

                regionObject.type_name = controller.type_name = 'one';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(1);

                regionObject.type_name = controller.type_name = 'home';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(1);

                regionObject.type_name = controller.type_name = 'two';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(2);

                regionObject.type_name = controller.type_name = 'test';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(2);

                regionObject.type_name = controller.type_name = 'three';
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testUberMethod.callCount).toBe(3);
            });
        });
        describe('addPostMethod', function(){
            var testMethod;
            beforeEach(function(){
                testMethod = jasmine.createSpy('testMethod');
                spyOn($log, 'error');
                expect($log.error).not.toHaveBeenCalled();
                Actions.addMethod('test', testMethod);
            });
            it('should error when trying to add a post method that does not exist', function(){
                function go(){
                    Actions.addPostMethod('test', 'nonon');
                }
                expect(go).toThrow();
            });
            it('should error when trying to add a post method and a function is not passed', function(){
                function go(){
                    Actions.addPostMethod('test');
                }
                expect(go).toThrow();
            });
            it('should add a post method', function(){
                var testPostMethod = jasmine.createSpy('testPostMethod');

                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethod.callCount).toBe(1);
                expect(testPostMethod.callCount).toBe(0);

                Actions.addPostMethod('test', testPostMethod);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethod.callCount).toBe(2);
                expect(testPostMethod.callCount).toBe(1);
            });
            it('should add a post method from the method list', function(){
                var testMethodTwo = jasmine.createSpy('testMethodTwo');

                Actions.addMethod('testMethodTwo', testMethodTwo);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(testMethod.callCount).toBe(1);
                expect(testMethodTwo.callCount).toBe(0);

                Actions.addPostMethod('test', 'testMethodTwo');
                Actions.callMethod('test', regionObject);
                $rootScope.$apply();
                expect(testMethod.callCount).toBe(2);
                expect(testMethodTwo.callCount).toBe(1);
            });
            it('should add multiple post methods', function(){
                var postMethodOne = jasmine.createSpy('postMethodOne');
                var postMethodTwo = jasmine.createSpy('postMethodTwo');
                function back(a){return $q.when(a)}
                postMethodOne.andCallFake(back);
                postMethodTwo.andCallFake(back);

                Actions.addPostMethod('test', postMethodOne);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(postMethodOne.callCount).toBe(1);
                expect(postMethodTwo.callCount).toBe(0);

                Actions.addPostMethod('test', postMethodTwo);
                Actions.callMethod('test', regionObject);

                $rootScope.$apply();
                expect(postMethodOne.callCount).toBe(2);
                expect(postMethodTwo.callCount).toBe(1);
            });
        });
    });
    describe('ActionUtils', function(){
        it('should format a url', function(){
            var result = '/home/123/';
            var input = '/home/__id__/';
            var context = {id: 123};
            expect(Actions.utils.formatUrl(input, context)).toEqual(result);
        });
        describe('deepExtend', function(){
            it('should extend arrays by overwriting', function(){
                var a = {one: ['one', 'two', 'three']};
                var b = {one: ['four', 'five', 'six']};
                var result = {one: ['four', 'five', 'six']};
                Actions.utils.deepExtend(a, b);
                expect(a).toEqual(result);
            });
            it('should skip over special keys', function(){
                var skipThese = ['controller', 'parentRegionObject', 'parentRegionSet'];
                var a = {};
                var b = {controller: 'one', parentRegionObject: 'two', parentRegionSet: 'three'};
                Actions.utils.deepExtend(a, b);
                angular.forEach(skipThese, function(key){
                    expect(a[key]).toBeUndefined();
                });
            });
            it('should regular extend objects', function(){
                var deepOne = {one: 'aaa', two: ['bbb']};
                var deepTwo = {one: 'ccc', two: ['ddd']};
                var one = {test: deepOne};
                var two = {test: deepTwo};

                Actions.utils.deepExtend(one, two);
                expect(one.test).toEqual(angular.extend(deepOne, deepTwo));
            });
            it('should replace regular keys', function(){
                var one = {one: 'one'};
                var two = {one: 'two'};
                Actions.utils.deepExtend(one, two);
                expect(one.one).toEqual('two');
            });
        });
        it('should call deep extend and make a new _masterForm', function(){
            var regionObject = {object: {one: 'one'}};
            var data = {object: {two: 'two'}, test: 'something'};

            expect(regionObject._masterForm).toBeUndefined();
            Actions.utils.updateRegionObject(regionObject, data);
            expect(regionObject._masterForm).toBeDefined();
            expect(regionObject._masterForm).toEqual(regionObject.object);
        });
        describe('resolveDependencies', function(){
            var checked;
            beforeEach(function(){
                checked = false;
            });
            it('should resolve right away if there are none', function(){
                Actions.utils.resolveDependencies(regionObject).then(function(rObject){
                    expect(rObject).toEqual(regionObject);
                    checked = true
                }, function(){
                    expect(false).toBe(true);  // make sure this never gets run
                });
                $rootScope.$apply();
                expect(checked).toBe(true);
            });
            it('should resolve dependencies', function(){
                var RegionService = $injector.get('RegionService');
                var home = {
                    type_name: 'home',
                    object: {id: 123}
                };
                regionObject.object = {};
                regionObject.region_dependencies = {

                    home: [
                        {
                            field_name: 'id',
                            serialize_as: 'home'
                        }
                    ]
                };

                RegionService.addRegion(home);

                expect(regionObject.object.home).toBeUndefined();
                Actions.utils.resolveDependencies(regionObject).then(function(rObject){
                    checked = true;
                    expect(regionObject.object.home).toBeDefined();
                    expect(regionObject.object.home).toBe(123);
                }, function(){
                    expect(false).toBe(true);
                });

                $rootScope.$apply();
                expect(checked).toBe(true);
            });
            it('should resolve if it can not find dependencies', function(){
                regionObject.region_dependencies = {
                    home: [
                        {
                            field_name: 'id',
                            serialize_as: 'home'
                        }
                    ]
                };
                Actions.utils.resolveDependencies(regionObject).then(function(rObject){
                    checked = true;
                    expect(rObject).toEqual(regionObject);
                }, function(){
                    expect(false).toBe(true);
                });

                $rootScope.$apply();
                expect(checked).toBe(true);
            });
            it('should reject if it can not find dependencies and we need them', function(){
                regionObject.region_dependencies = {
                    home: [
                        {
                            field_name: 'id',
                            serialize_as: 'home'
                        }
                    ]
                };

                Actions.utils.resolveDependencies(regionObject, true).then(function(){
                    expect(false).toBe(true);  // make sure this never gets run
                }, function(){
                    checked = true;
                });

                $rootScope.$apply();
                expect(checked).toBe(true);
            });
        });
    });
    describe('ActionMethods', function(){
        describe('methodReload', function(){
            var HttpQueue;
            beforeEach(function(){
                HttpQueue = $injector.get('HttpQueue');
                spyOn(HttpQueue, 'addObjectRequest').andCallFake(function(){
                    return $q.when(regionObject);
                });
                spyOn(ActionUtils, 'resolveDependencies').andCallThrough();
                spyOn(ActionUtils, 'deepExtend').andCallThrough();
                regionObject.parentRegionSet.region_endpoint_pattern = '/home/__id__/';
            });
            it('should return a promise', function(){
                var result = ActionMethods.reload(regionObject);
                expect(result.then).toBeDefined();
            });
            it('should resolve dependencies to fetch the correct url', function(){
                expect(Actions.utils.resolveDependencies).not.toHaveBeenCalled();
                ActionMethods.reload(regionObject);
                expect(Actions.utils.resolveDependencies).toHaveBeenCalled();
                expect(Actions.utils.resolveDependencies).toHaveBeenCalledWith(regionObject);
            });
            it('should add an object request', function(){
                expect(HttpQueue.addObjectRequest).not.toHaveBeenCalled();
                ActionMethods.reload(regionObject);
                $rootScope.$apply();
                expect(HttpQueue.addObjectRequest).toHaveBeenCalled();
                expect(HttpQueue.addObjectRequest).toHaveBeenCalledWith('/home//');  // nothing to format url with
            });
            it('should extend the region with what is returned', function(){
                expect(Actions.utils.deepExtend).not.toHaveBeenCalled();
                ActionMethods.reload(regionObject);
                expect(Actions.utils.deepExtend).not.toHaveBeenCalled();
                $rootScope.$apply();
                expect(Actions.utils.deepExtend).toHaveBeenCalled();
            });
        });
        describe('methodSave', function(){
            var errorString;
            beforeEach(function(){
                var data = {object: {test_key: 'test object value'}, test_key: 'test region value'};
                $httpBackend.whenPOST(/.*/).respond(200, data);
                $httpBackend.whenPATCH(/.*/).respond(200, data);
                controller.success = jasmine.createSpy('success');
                controller.error = jasmine.createSpy('error');
                regionObject.object = {};
                regionObject.object_endpoint_pattern = '/home/__id__/';
                regionObject.object_endpoint = '/home/123/';
                errorString = 'System error occurred. \n We apologize for the interruption and have already been notified.';
            });
            it('should return a promise', function(){
                var result = ActionMethods.save(regionObject);
                expect(result.then).toBeDefined();
            });
            it('should POST if there is no object.id', function(){
                $httpBackend.expectPOST(/.*/);

                ActionMethods.save(regionObject);
                $httpBackend.flush();
            });
            it('should PATCH if there is an object.id', function(){
                $httpBackend.expectPATCH(/.*/);

                regionObject.object.id = 123;
                ActionMethods.save(regionObject);
                $httpBackend.flush();
            });
            it('should put nested object ids on the object', function(){
                var one = 111;
                var two = 222;
                regionObject.object.one = {id: one};
                regionObject.object.two = {id: two};

                ActionMethods.save(regionObject);

                expect(regionObject.object.one).toEqual(one);
                expect(regionObject.object.two).toEqual(two);
            });
            it('should call validate beforehand', function(){
                var testPostValidateMethod = jasmine.createSpy('testPostValidateMethod');

                Actions.addPostMethod('validate', testPostValidateMethod);

                expect(testPostValidateMethod.callCount).toBe(0);

                Actions.callMethod('save', regionObject);

                $rootScope.$apply();
                expect(testPostValidateMethod.callCount).toBe(1);
            });
            it('should call all validate methods beforehand', function(){
                var one = jasmine.createSpy('one');
                var two = jasmine.createSpy('two');
                var three = jasmine.createSpy('three');

                Actions.addPostMethod('validate', one);
                Actions.addPostMethod('validate', two);
                Actions.addPostMethod('validate', three);

                expect(one.callCount).toBe(0);
                expect(two.callCount).toBe(0);
                expect(three.callCount).toBe(0);

                Actions.callMethod('save', regionObject);

                $rootScope.$apply();
                expect(one.callCount).toBe(1);
                expect(two.callCount).toBe(1);
                expect(three.callCount).toBe(1);
            });
            // success
            it('should update the regionObject on success', function(){
                $httpBackend.expectPOST(/.*/);

                ActionMethods.save(regionObject);
                expect(regionObject.object.test_key).toBeUndefined();
                expect(regionObject.test_key).toBeUndefined();

                $httpBackend.flush();
                expect(regionObject.object.test_key).toEqual('test object value');
                expect(regionObject.test_key).toEqual('test region value');
            });
            it('should call success on the controller', function(){
                $httpBackend.expectPOST(/.*/);

                ActionMethods.save(regionObject);
                expect(controller.success).not.toHaveBeenCalled();
                $httpBackend.flush();
                expect(controller.success).toHaveBeenCalled();
            });
            // error
            it('should give a generic error message for 500s to the controller', function(){
                $httpBackend.expectPOST(/.*/).respond(500, {});

                ActionMethods.save(regionObject);

                expect(controller.error).not.toHaveBeenCalled();
                $httpBackend.flush();
                expect(controller.error).toHaveBeenCalledWith(errorString);

            });
            it('should call error on the controller', function(){
                $httpBackend.expectPOST(/.*/).respond(400, {error: errorString});

                ActionMethods.save(regionObject);

                expect(controller.error).not.toHaveBeenCalled();
                $httpBackend.flush();
                expect(controller.error).toHaveBeenCalled();
                expect(controller.error).toHaveBeenCalledWith({error: errorString});
            });
        });
        describe('methodDelete', function(){
            var $modal;
            beforeEach(function(){
                $httpBackend.whenGET('').respond('<span>template</span>');
                $httpBackend.whenDELETE('/delete/').respond(200, {url: '/list_view/'});
                $httpBackend.whenDELETE('/fallback/').respond(200, '');
                controller.removeRegion = jasmine.createSpy('removeRegion');
                controller.error = jasmine.createSpy('error');
                regionObject.delete_confirmation_template_url = 'test.html';
                regionObject.relatedobjects_endpoint = '';
                regionObject.delete_endpoint = '/delete/';
                regionObject.object_endpoint = '/fallback/';
                $modal = $injector.get('$modal');
                spyOn($modal, 'open').andCallFake(function(){
                    return {
                        result: $q.when('something')
                    }
                });
            });
            it('should return a promise', function(){
                var result = ActionMethods.delete(regionObject);
                expect(result.then).toBeDefined();
            });
            it('should send a DELETE request', function(){
                $httpBackend.expectDELETE('/delete/');

                ActionMethods.delete(regionObject);
                $rootScope.$apply();
                $httpBackend.flush();
            });
            it('should fallback to the object endpoint if no delete_endpoint is provided', function(){
                $httpBackend.expectDELETE('/fallback/');

                delete regionObject.delete_endpoint;
                ActionMethods.delete(regionObject);
                $rootScope.$apply();
                $httpBackend.flush();
            });
            it('should launch a modal', function(){
                expect($modal.open).not.toHaveBeenCalled();
                ActionMethods.delete(regionObject);
                expect($modal.open).toHaveBeenCalled();
            });
            // success
            it('should remove a region on success', function(){
                var checked = false;
                expect(controller.removeRegion).not.toHaveBeenCalled();
                ActionMethods.delete(regionObject).then(function(data){
                    expect(data).toEqual(regionObject);
                    checked = true;
                }, function(){
                    expect(false).toBe(true);
                });
                expect(controller.removeRegion).not.toHaveBeenCalled();
                $rootScope.$apply();
                $httpBackend.flush();
                expect(controller.removeRegion).toHaveBeenCalled();
                expect(checked).toBe(true);
            });
            it('should redirect to a given url when a primary region is deleted', function(){
                var $timeout = $injector.get('$timeout'),
                    checked = false;

                spyOn(window.location, 'replace');

                regionObject.parentRegionSet = {isPrimaryRegion: true};
                ActionMethods.delete(regionObject).then(function(){
                    checked = true;
                }, function(){
                    expect(false).toBe(true);
                });

                $rootScope.$apply();
                $httpBackend.flush();
                $timeout.flush();
                expect(checked).toBe(true);
                expect(window.location.replace).toHaveBeenCalledWith('/list_view/');
            });
            // error
            it('should call error on the controller', function(){
                var checked = false;
                $httpBackend.expectDELETE('/delete/').respond(500, {});
                expect(controller.error).not.toHaveBeenCalled();
                ActionMethods.delete(regionObject).then(function(data){
                    expect(false).toBe(true);
                }, function(){
                    checked = true;
                });
                expect(controller.error).not.toHaveBeenCalled();
                $rootScope.$apply();
                $httpBackend.flush();
                expect(controller.error).toHaveBeenCalled();
                expect(checked).toBe(true);
            });
            it('should do nothing when the modal is cancelled', function(){
                var checked = false;
                $modal.open.andCallFake(function(){
                    return {
                        result: $q.reject()
                    }
                });
                ActionMethods.delete(regionObject).then(function(){
                    expect(false).toBe(true);
                }, function(e){
                    checked = true;
                    expect(e).toEqual('modal cancelled');
                });
                $rootScope.$apply();
                expect(checked).toBe(true);
            });
        });
        describe('methodDestroy', function(){
            var RegionService;
            beforeEach(function(){
                controller.removeRegion = jasmine.createSpy('removeRegion');
                RegionService = $injector.get('RegionService');
                spyOn(RegionService, 'removeRegion').andCallThrough();
            });
            it('should call removeRegion on the controller', function(){
                expect(controller.removeRegion).not.toHaveBeenCalled();
                ActionMethods.destroy(regionObject);
                expect(controller.removeRegion).toHaveBeenCalled();
            });
            it('should call removeRegion on the RegionService', function(){
                expect(RegionService.removeRegion).not.toHaveBeenCalled();
                ActionMethods.destroy(regionObject);
                expect(RegionService.removeRegion).toHaveBeenCalled();
            });
        });
        describe('methodCancel', function(){
            it('should call reset on the controller', function(){
                var checked = false;
                spyOn(controller, 'reset');

                expect(controller.reset).not.toHaveBeenCalled();
                ActionMethods.cancel(regionObject).then(function(){
                    checked = true;
                }, function(){
                    expect(false).toBe(true);
                });
                $rootScope.$apply();
                expect(controller.reset).toHaveBeenCalled();
                expect(checked).toBe(true);
            });
            it('should call exit', function(){
                var checked = false;
                spyOn(ActionMethods, 'exit');

                expect(ActionMethods.exit).not.toHaveBeenCalled();
                ActionMethods.cancel(regionObject).then(function(){
                    checked = true;
                }, function(){
                    expect(false).toBe(true);
                });
                $rootScope.$apply();
                expect(ActionMethods.exit).toHaveBeenCalled();
                expect(checked).toBe(true);
            })
        });
        describe('methodExit', function(){
            it('should put the active state back to default', function(){
                var checked = false;
                controller.activeState = 'edit';
                expect(controller.activeState).not.toEqual('default');
                ActionMethods.exit(regionObject).then(function(){
                    checked = true;
                }, function(){
                    expect(false).toBe(true);
                });
                $rootScope.$apply();
                expect(controller.activeState).toEqual('default');
                expect(checked).toBe(true);
            });
        });
        describe('methodEdit', function(){
            it('should put the active state to edit', function(){
                var checked = false;

                expect(controller.activeState).not.toEqual('edit');
                ActionMethods.edit(regionObject).then(function(){
                    checked = true;
                }, function(){
                    expect(false).toBe(true);
                });
                $rootScope.$apply();
                expect(controller.activeState).toEqual('edit');
                expect(checked).toBe(true);
            });
        });
        describe('methodSaveAndReload', function(){
            it('should throw a not implemented yet error', function(){
                var checked = false;
                ActionMethods.saveAndReload(regionObject).then(function(){
                    expect(false).toBe(true);
                }, function(error){
                    expect(error).toEqual('not implemented yet');
                    checked = true;
                });
                $rootScope.$apply();
                expect(checked).toBe(true);
            });
        });
        describe('methodSaveAll', function(){
            it('should callMethod for all regions registered', function(){
                // spies
                var testMethod = jasmine.createSpy('testMethod');
                testMethod.andCallFake(function(a){
                    return $q.when(a);
                });

                var calls = {};
                spyOn(Actions, 'callMethod').andCallFake(function(methodName){
                    // track calls to callMethod.
                    if(methodName.instruction) methodName = methodName.instruction;
                    calls[methodName] ? calls[methodName]++ : calls[methodName] = 1;

                    return $q.when({});
                });

                // make regions
                var RegionService = $injector.get('RegionService');
                var prevR, children = 0;
                regionObject.commit_instruction = 'test';
                for(var i = 1; i < 10; i++){
                    var r = angular.copy(regionObject),
                        $scope = $rootScope.$new();
                    r.object = {id: i};
                    r.type_name += i;
                    $scope.regionObject = r;
                    $scope.options = {};
                    $scope.regionSet = {};
                    r.controller = newController($scope);
                    spyOn(r.controller, 'editing').andReturn(true);

                    RegionService.addRegion(r);
                    // make some children
                    if(!(i%3) && prevR) RegionService.registerChildRegion(prevR, r);
                    prevR = r;
                }

                // last setup
                Actions.addMethod('test', testMethod);
                regionObject.object = {id: 0};

                // test
                expect(calls.test).toBeUndefined();
                expect(calls.exit).toBeUndefined();
                ActionMethods.saveAll(regionObject);
                expect(calls.test).toBe(1);  // get called immediately
                expect(calls.exit).toBeUndefined();  // waits for digest cycle.
                $rootScope.$apply();
                expect(calls.test).toBe(10);
                expect(calls.exit).toBe(10);
            });
        });
        describe('methodValidate', function(){
            it('should return the regionObject', function(){
                var checked = false;
                ActionMethods.validate(regionObject).then(function(){
                    checked = true;
                }, function(){
                    expect(false).toBe(true);
                });
                $rootScope.$apply();
                expect(checked).toBe(true);
            });
            it('should call all pre methods', function(){
                var checked = false;
                var one = jasmine.createSpy('one');
                var two = jasmine.createSpy('two');
                var three = jasmine.createSpy('three');

                Actions.addPreMethod('validate', one);
                Actions.addPreMethod('validate', two);
                Actions.addPreMethod('validate', three);

                expect(one.callCount).toBe(0);
                expect(two.callCount).toBe(0);
                expect(three.callCount).toBe(0);

                ActionMethods.validate(regionObject).then(function(){
                    checked = true;
                }, function(){
                    expect(false).toBe(true);
                });

                $rootScope.$apply();
                expect(checked).toBe(true);
                expect(one.callCount).toBe(1);
                expect(two.callCount).toBe(1);
                expect(three.callCount).toBe(1);
            });
            it('should call all post methods', function(){
                var one = jasmine.createSpy('one');
                var two = jasmine.createSpy('two');
                var three = jasmine.createSpy('three');

                Actions.addPostMethod('validate', one);
                Actions.addPostMethod('validate', two);
                Actions.addPostMethod('validate', three);

                expect(one.callCount).toBe(0);
                expect(two.callCount).toBe(0);
                expect(three.callCount).toBe(0);

                ActionMethods.validate(regionObject);

                $rootScope.$apply();
                expect(one.callCount).toBe(1);
                expect(two.callCount).toBe(1);
                expect(three.callCount).toBe(1);
            });
            it('should call all pre methods per type of region object', function(){
                var testOne = jasmine.createSpy('testOne');
                var testTwo = jasmine.createSpy('testTwo');
                var homeOne = jasmine.createSpy('homeOne');
                var homeTwo = jasmine.createSpy('homeTwo');

                Actions.addPreMethodToType('validate', 'test', testOne);
                Actions.addPreMethodToType('validate', 'test', testTwo);
                Actions.addPreMethodToType('validate', 'home', homeOne);
                Actions.addPreMethodToType('validate', 'home', homeTwo);

                expect(testOne.callCount).toBe(0);
                expect(testTwo.callCount).toBe(0);
                expect(homeOne.callCount).toBe(0);
                expect(homeTwo.callCount).toBe(0);

                ActionMethods.validate(regionObject);

                $rootScope.$apply();
                expect(testOne.callCount).toBe(1);
                expect(testTwo.callCount).toBe(1);
                expect(homeOne.callCount).toBe(0);
                expect(homeTwo.callCount).toBe(0);

                regionObject.type_name = 'home';
                ActionMethods.validate(regionObject);

                $rootScope.$apply();
                expect(testOne.callCount).toBe(1);
                expect(testTwo.callCount).toBe(1);
                expect(homeOne.callCount).toBe(1);
                expect(homeTwo.callCount).toBe(1);
            });
            it('should call all post methods per type of region object', function(){
                var testOne = jasmine.createSpy('testOne');
                var testTwo = jasmine.createSpy('testTwo');
                var homeOne = jasmine.createSpy('homeOne');
                var homeTwo = jasmine.createSpy('homeTwo');

                Actions.addPostMethodToType('validate', 'test', testOne);
                Actions.addPostMethodToType('validate', 'test', testTwo);
                Actions.addPostMethodToType('validate', 'home', homeOne);
                Actions.addPostMethodToType('validate', 'home', homeTwo);

                expect(testOne.callCount).toBe(0);
                expect(testTwo.callCount).toBe(0);
                expect(homeOne.callCount).toBe(0);
                expect(homeTwo.callCount).toBe(0);

                ActionMethods.validate(regionObject);

                $rootScope.$apply();
                expect(testOne.callCount).toBe(1);
                expect(testTwo.callCount).toBe(1);
                expect(homeOne.callCount).toBe(0);
                expect(homeTwo.callCount).toBe(0);

                regionObject.type_name = 'home';
                ActionMethods.validate(regionObject);

                $rootScope.$apply();
                expect(testOne.callCount).toBe(1);
                expect(testTwo.callCount).toBe(1);
                expect(homeOne.callCount).toBe(1);
                expect(homeTwo.callCount).toBe(1);
            });
        });
    });
});

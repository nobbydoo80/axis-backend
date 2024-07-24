/**
 * Created by mjeffrey on 8/26/14.
 */
describe('Controller: AppController', function(){
    var rootScope, controller, scope, $location, $timeout, $httpBackend, SampleSetProperties, LocationService;

    beforeEach(function(){
        inject(function($rootScope, $controller, _$location_, _$timeout_, _$httpBackend_, _SampleSetProperties_, _LocationService_){
            rootScope = $rootScope;
            scope = $rootScope.$new();
            $location = _$location_;
            $timeout = _$timeout_;
            $httpBackend = _$httpBackend_;
            controller = $controller('AppController', {
                $scope: scope,
                $location: $location
            });
            SampleSetProperties = _SampleSetProperties_;
            LocationService = _LocationService_;
        });
    });

    it('should exist', function(){
        expect(!!controller).toBe(true);
    });
    it('should not show help text by default', function(){
        expect(scope.showHelp).toBe(false);
    });
    it('should add samplesets to page grabbed from url', function(){
        spyOn(SampleSetProperties, 'addSampleSet').andCallThrough();
        $location.search('id', [1, 2, 3]);

        scope.init();

        expect(SampleSetProperties.addSampleSet).toHaveBeenCalled();
        expect(SampleSetProperties.addSampleSet.callCount).toBe(3);
    });

    describe('jquery api', function(){
        beforeEach(function(){
            this.testHomes = [
            {
                "eep_program": "APS ENERGY STAR V3",
                "name": "23642 Corona Ave",
                "metro": "Phoenix-Mesa-Glendale, AZ",
                "home_status_id": 2,
                "builder": "DR Horton",
                "is_test_home": true,
                "metro_id": 264,
                "builder_id": 34,
                "home_id": 2311,
                "eep_program_id": 5,
                "source_answers": {
                    "384": 34948,  "385": 34949,  "386": 34950,  "387": 34951,  "388": 34952,  "389": 34953,  "390": 34954,  "391": 34955,  "392": 34956,  "393": 34957,  "394": 34958,  "395": 34959,  "396": 34960,  "397": 34961,  "398": 34962,  "399": 34963,  "400": 34964,  "410": 34965,  "411": 34966,  "412": 34967,  "413": 34968,  "346": 34969,  "347": 34970,  "348": 34971,  "349": 34972,  "354": 34973,  "355": 34974,  "356": 34975,  "357": 34976,  "358": 34977,  "359": 34978,  "360": 34979,  "361": 34980,  "362": 34981,  "363": 34982,  "364": 34983,  "365": 34984,  "366": 34985,  "367": 34986,  "368": 34987,  "369": 34988,  "370": 34989,  "371": 34990,  "372": 34991,  "373": 34992,  "374": 34993,  "375": 34994,  "376": 34995,  "377": 34996,  "378": 34997,  "379": 34998,  "380": 34999,  "381": 35000,  "382": 35001,  "383": 35002
                },
                "subdivision_id": 68,
                "contributed_answers": {
                    "384": 34948,  "385": 34949,  "386": 34950,  "387": 34951,  "388": 34952,  "389": 34953,  "390": 34954,  "391": 34955,  "392": 34956,  "393": 34957,  "394": 34958,  "395": 34959,  "396": 34960,  "397": 34961,  "398": 34962,  "399": 34963,  "400": 34964,  "410": 34965,  "411": 34966,  "412": 34967,  "413": 34968,  "346": 34969,  "347": 34970,  "348": 34971,  "349": 34972,  "354": 34973,  "355": 34974,  "356": 34975,  "357": 34976,  "358": 34977,  "359": 34978,  "360": 34979,  "361": 34980,  "362": 34981,  "363": 34982,  "364": 34983,  "365": 34984,  "366": 34985,  "367": 34986,  "368": 34987,  "369": 34988,  "370": 34989,  "371": 34990,  "372": 34991,  "373": 34992,  "374": 34993,  "375": 34994,  "376": 34995,  "377": 34996,  "378": 34997,  "379": 34998,  "380": 34999,  "381": 35000,  "382": 35001,  "383": 35002
                },
                "subdivision": "Sonoran Vista",
                "detail_url": "/home/2311/",
                "id": 4226
            }
        ];
            this.sampledHomes = [
            {
                "eep_program": "APS ENERGY STAR V3",
                "name": "23683 Corona Ave",
                "metro": "Phoenix-Mesa-Glendale, AZ",
                "home_status_id": 3,
                "builder": "DR Horton",
                "is_test_home": false,
                "metro_id": 264,
                "builder_id": 34,
                "home_id": 2310,
                "eep_program_id": 5,
                "source_answers": { "384": null,  "385": null,  "386": null,  "387": null,  "388": null,  "389": null,  "390": null,  "391": null,  "392": null,  "393": null,  "394": null,  "395": null,  "396": null,  "397": null,  "398": null,  "399": null,  "400": null,  "410": null,  "411": null,  "412": null,  "413": null,  "346": null,  "347": null,  "348": null,  "349": null,  "354": null,  "355": null,  "356": null,  "357": null,  "358": null,  "359": null,  "360": null,  "361": null,  "362": null,  "363": null,  "364": null,  "365": null,  "366": null,  "367": null,  "368": null,  "369": null,  "370": null,  "371": null,  "372": null,  "373": null,  "374": null,  "375": null,  "376": null,  "377": null,  "378": null,  "379": null,  "380": null,  "381": null,  "382": null,  "383": null
                },
                "subdivision_id": 68,
                "contributed_answers": {
                    "384": null,  "385": null,  "386": null,  "387": null,  "388": null,  "389": null,  "390": null,  "391": null,  "392": null,  "393": null,  "394": null,  "395": null,  "396": null,  "397": null,  "398": null,  "399": null,  "400": null,  "410": null,  "411": null,  "412": null,  "413": null,  "346": null,  "347": null,  "348": null,  "349": null,  "354": null,  "355": null,  "356": null,  "357": null,  "358": null,  "359": null,  "360": null,  "361": null,  "362": null,  "363": null,  "364": null,  "365": null,  "366": null,  "367": null,  "368": null,  "369": null,  "370": null,  "371": null,  "372": null,  "373": null,  "374": null,  "375": null,  "376": null,  "377": null,  "378": null,  "379": null,  "380": null,  "381": null,  "382": null,  "383": null
                },
                "subdivision": "Sonoran Vista",
                "detail_url": "/home/2310/",
                "id": 4225
            },
            {
                "eep_program": "APS ENERGY STAR V3",
                "name": "23614 W Atlanta Ave",
                "metro": "Phoenix-Mesa-Glendale, AZ",
                "home_status_id": 4,
                "builder": "DR Horton",
                "is_test_home": false,
                "metro_id": 264,
                "builder_id": 34,
                "home_id": 2312,
                "eep_program_id": 5,
                "source_answers": {
                    "384": null,  "385": null,  "386": null,  "387": null,  "388": null,  "389": null,  "390": null,  "391": null,  "392": null,  "393": null,  "394": null,  "395": null,  "396": null,  "397": null,  "398": null,  "399": null,  "400": null,  "410": null,  "411": null,  "412": null,  "413": null,  "346": null,  "347": null,  "348": null,  "349": null,  "354": null,  "355": null,  "356": null,  "357": null,  "358": null,  "359": null,  "360": null,  "361": null,  "362": null,  "363": null,  "364": null,  "365": null,  "366": null,  "367": null,  "368": null,  "369": null,  "370": null,  "371": null,  "372": null,  "373": null,  "374": null,  "375": null,  "376": null,  "377": null,  "378": null,  "379": null,  "380": null,  "381": null,  "382": null,  "383": null
                },
                "subdivision_id": 68,
                "contributed_answers": {
                    "384": null,  "385": null,  "386": null,  "387": null,  "388": null,  "389": null,  "390": null,  "391": null,  "392": null,  "393": null,  "394": null,  "395": null,  "396": null,  "397": null,  "398": null,  "399": null,  "400": null,  "410": null,  "411": null,  "412": null,  "413": null,  "346": null,  "347": null,  "348": null,  "349": null,  "354": null,  "355": null,  "356": null,  "357": null,  "358": null,  "359": null,  "360": null,  "361": null,  "362": null,  "363": null,  "364": null,  "365": null,  "366": null,  "367": null,  "368": null,  "369": null,  "370": null,  "371": null,  "372": null,  "373": null,  "374": null,  "375": null,  "376": null,  "377": null,  "378": null,  "379": null,  "380": null,  "381": null,  "382": null,  "383": null
                },
                "subdivision": "Sonoran Vista",
                "detail_url": "/home/2312/",
                "id": 4227
            },
            {
                "eep_program": "APS ENERGY STAR V3",
                "name": "5033 S 236th Dr",
                "metro": "Phoenix-Mesa-Glendale, AZ",
                "home_status_id": 5,
                "builder": "DR Horton",
                "is_test_home": false,
                "metro_id": 264,
                "builder_id": 34,
                "home_id": 2313,
                "eep_program_id": 5,
                "source_answers": {
                    "384": null,  "385": null,  "386": null,  "387": null,  "388": null,  "389": null,  "390": null,  "391": null,  "392": null,  "393": null,  "394": null,  "395": null,  "396": null,  "397": null,  "398": null,  "399": null,  "400": null,  "410": null,  "411": null,  "412": null,  "413": null,  "346": null,  "347": null,  "348": null,  "349": null,  "354": null,  "355": null,  "356": null,  "357": null,  "358": null,  "359": null,  "360": null,  "361": null,  "362": null,  "363": null,  "364": null,  "365": null,  "366": null,  "367": null,  "368": null,  "369": null,  "370": null,  "371": null,  "372": null,  "373": null,  "374": null,  "375": null,  "376": null,  "377": null,  "378": null,  "379": null,  "380": null,  "381": null,  "382": null,  "383": null
                },
                "subdivision_id": 68,
                "contributed_answers": {
                    "384": null,  "385": null,  "386": null,  "387": null,  "388": null,  "389": null,  "390": null,  "391": null,  "392": null,  "393": null,  "394": null,  "395": null,  "396": null,  "397": null,  "398": null,  "399": null,  "400": null,  "410": null,  "411": null,  "412": null,  "413": null,  "346": null,  "347": null,  "348": null,  "349": null,  "354": null,  "355": null,  "356": null,  "357": null,  "358": null,  "359": null,  "360": null,  "361": null,  "362": null,  "363": null,  "364": null,  "365": null,  "366": null,  "367": null,  "368": null,  "369": null,  "370": null,  "371": null,  "372": null,  "373": null,  "374": null,  "375": null,  "376": null,  "377": null,  "378": null,  "379": null,  "380": null,  "381": null,  "382": null,  "383": null
                },
                "subdivision": "Sonoran Vista",
                "detail_url": "/home/2313/",
                "id": 4228
            }
        ];
            this.mockSampleSet = {
                "id": 1,
                "name": "965ea40b-2f43-484d-b2a6-e40c2c3f2662",
                "alt_name": "32120810_e2",
                "test_homes": this.testHomes,
                "sampled_homes": this.sampledHomes,
                "builder_id": 34,
                "builder_name": "DR Horton"
            };
            var uuids = ['1234', '2345', '3456', '4567', '5678'];
            $httpBackend.whenGET('/api/v2/sampleset/uuid/').respond(function(method, url, data){
                return [200, {uuid: uuids.pop()}, {}]
            });
            $httpBackend.whenGET('/api/v2/sampleset/1/summary/').respond(this.mockSampleSet);
        });
        it('should start and stop dragging', function(){
            expect(scope.ssProperties.isDragging).toBe(false);
            scope.startDragging();
            $timeout.flush();
            expect(scope.ssProperties.isDragging).toBe(true);
            scope.cancelDragging();
            $timeout.flush();
            expect(scope.ssProperties.isDragging).toBe(false);
        });
        it('should make a sampleset with a home', function(){
            $httpBackend.whenGET('/api/v2/homestatus/1/question_summary/').respond({
                name: '123 North West Street',
                home_status_id: 1
            });

            expect(scope.viewingSampleSets.length).toBe(0);
            scope.makeSampleSetWithHome(1);
            $httpBackend.flush();
            expect(scope.viewingSampleSets.length).toBe(1);
        });
        it('should remove home from old sample set if used to create new sample set', function(){
            $httpBackend.whenGET('/api/v2/homestatus/10/question_summary/').respond({
                name: 'remove this home',
                home_status_id: 10,
                is_test_home: true,
                questions: {}
            });

            expect(scope.viewingSampleSets.length).toBe(0);

            scope.makeSampleSetWithHome(10);
            $httpBackend.flush();

            var ssOne = scope.viewingSampleSets[0];
            expect(ssOne.test_homes.length).toBe(1);

            expect(scope.ssProperties.viewingSampleSets.length).toBe(1);

            scope.makeSampleSetWithHome(10, ssOne.name);
            $httpBackend.flush();
            scope.$apply();
            expect(scope.ssProperties.viewingSampleSets.length).toBe(2);

            var ssTwo = scope.viewingSampleSets[1];

            expect(ssTwo.test_homes.length).toBe(1);
            expect(ssOne.test_homes.length).toBe(0);
        });
        it('should make an empty sample set', function(){
            scope.makeEmptySampleSet();
            $httpBackend.flush();
            expect(SampleSetProperties.getObject().viewingSampleSets.length).toBe(1);
        });
        it('should add a sample set from the server', function(){
            spyOn(SampleSetProperties, 'addSampleSet').andCallThrough();
            spyOn(LocationService, 'addId').andCallThrough();

            scope.addSampleSet(1);
            $httpBackend.flush();

            expect(SampleSetProperties.getObject().viewingSampleSets.length).toBe(1);
            expect(SampleSetProperties.addSampleSet).toHaveBeenCalled();
            expect(LocationService.addId).toHaveBeenCalled();
            expect(LocationService.getSampleSetIds()).toEqual(['1'])
        });
        it('should remove a sample set', function(){
            scope.makeEmptySampleSet();
            $httpBackend.flush();
            expect(SampleSetProperties.getObject().viewingSampleSets.length).toBe(1);
            var ss = SampleSetProperties.getObject().viewingSampleSets[0];
            scope.removeSampleSet(ss, false);
            expect(SampleSetProperties.getObject().viewingSampleSets.length).toBe(0);
        });
        it('should remove a home', function(){
            scope.addSampleSet(1);
            $httpBackend.flush();
            var ss = SampleSetProperties.getObject().viewingSampleSets[0];

            spyOn(SampleSetProperties, 'removeHome').andCallThrough();
            var len = ss.test_homes.length;
            var home_status_id = ss.test_homes[0].home_status_id;

            scope.removeHome(ss.test_homes[0], ss.name);

            expect(ss.test_homes.length).toBe(len-1);
            expect(SampleSetProperties.removeHome).toHaveBeenCalledWith(home_status_id, ss.name, true);
        });
        it('should prompt a user before removing a changed sampleset', function(){
            spyOn(window, 'confirm').andCallFake(function(){
                return true;
            });

            scope.makeEmptySampleSet();
            $httpBackend.flush();
            expect(SampleSetProperties.getObject().viewingSampleSets.length).toBe(1);
            var ss = SampleSetProperties.getObject().viewingSampleSets[0];
            scope.removeSampleSet(ss, true);
            expect(window.confirm).toHaveBeenCalled();
            expect(SampleSetProperties.getObject().viewingSampleSets.length).toBe(0);

        });
        it('should broadcast an openAccordion event if the sampleset is already on the page', function(){
            spyOn(rootScope, '$broadcast').andCallThrough();
            scope.addSampleSet(1);
            $httpBackend.flush();
            expect(SampleSetProperties.getObject().viewingSampleSets.length).toBe(1);

            scope.addSampleSet(1);
            expect(rootScope.$broadcast).toHaveBeenCalledWith('openAccordion', 1);
        });
    });

});

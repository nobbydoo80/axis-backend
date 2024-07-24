/**
 * Created by mjeffrey on 8/26/14.
 */

describe('Service: SampleSetProperties', function(){
    var SampleSetProperties, HomeProperties, $httpBackend, scope;

    beforeEach(function(){
        // instantiate service
        inject(function($rootScope, _SampleSetProperties_, _HomeProperties_, _$httpBackend_){
            scope = $rootScope.$new();
            SampleSetProperties = _SampleSetProperties_;
            HomeProperties = _HomeProperties_;
            $httpBackend = _$httpBackend_
        });
        this.mockTestHome = {
            "metro_id": 264,
            "builder_id": 1,
            "is_test_home": true,
            "source_answers": { "384": 193440, "385": 193441, "386": 193442, "387": 193443, "388": 193444, "389": 193445, "390": 193446, "391": 193447, "392": 193448, "393": 193449, "394": 193450, "395": 193451, "396": 193452, "397": 193453, "398": 193454, "399": 193455, "400": 193456, "410": 193457, "411": 193458, "412": 193459, "413": 193460, "346": 193461, "347": 193462, "348": 193463, "349": 193464, "354": 193465, "355": 193466, "356": 193467, "357": 193468, "358": 193469, "359": 193470, "360": 193471, "361": 193472, "362": 193473, "363": 193474, "364": 193475, "365": 193476, "366": 193477, "367": 193478, "368": 193479, "369": 193480, "370": 193481, "371": 193482, "372": 193483, "373": 193484, "374": 193485, "375": 193486, "376": 193487, "377": 193488, "378": 193489, "379": 193490, "380": 193491, "381": 193492, "382": 193493, "383": 193494 },
            "detail_url": "/home/1/",
            "eep_program": "APS ENERGY STAR V3",
            "subdivision": "Madison Place",
            "name": "5550 N 16th St",
            "metro": "Phoenix-Mesa-Glendale, AZ",
            "home_status_id": 1,
            "builder": "Meritage Homes of Arizona, Inc.",
            "eep_program_id": 5,
            "subdivision_id": 259,
            "contributed_answers": { "384": 193440, "385": 193441, "386": 193442, "387": 193443, "388": 193444, "389": 193445, "390": 193446, "391": 193447, "392": 193448, "393": 193449, "394": 193450, "395": 193451, "396": 193452, "397": 193453, "398": 193454, "399": 193455, "400": 193456, "410": 193457, "411": 193458, "412": 193459, "413": 193460, "346": 193461, "347": 193462, "348": 193463, "349": 193464, "354": 193465, "355": 193466, "356": 193467, "357": 193468, "358": 193469, "359": 193470, "360": 193471, "361": 193472, "362": 193473, "363": 193474, "364": 193475, "365": 193476, "366": 193477, "367": 193478, "368": 193479, "369": 193480, "370": 193481, "371": 193482, "372": 193483, "373": 193484, "374": 193485, "375": 193486, "376": 193487, "377": 193488, "378": 193489, "379": 193490, "380": 193491, "381": 193492, "382": 193493, "383": 193494 }
        };
        this.mockSampledHome = {
            "metro_id": 264,
            "builder_id": 2,
            "is_test_home": false,
            "source_answers": {},
            "detail_url": "/home/1/",
            "eep_program": "APS ENERGY STAR V3",
            "subdivision": "Madison Place",
            "name": "5550 N 16th St",
            "metro": "Phoenix-Mesa-Glendale, AZ",
            "home_status_id": 12,
            "builder": "Meritage Homes of Arizona, Inc.",
            "eep_program_id": 5,
            "subdivision_id": 259,
            "contributed_answers": { "384": 193440, "385": 193441, "386": 193442, "387": 193443, "388": 193444, "389": 193445, "390": 193446, "391": 193447, "392": 193448, "393": 193449, "394": 193450, "395": 193451, "396": 193452, "397": 193453, "398": 193454, "399": 193455, "400": 193456, "410": 193457, "411": 193458, "412": 193459, "413": 193460, "346": 193461, "347": 193462, "348": 193463, "349": 193464, "354": 193465, "355": 193466, "356": 193467, "357": 193468, "358": 193469, "359": 193470, "360": 193471, "361": 193472, "362": 193473, "363": 193474, "364": 193475, "365": 193476, "366": 193477, "367": 193478, "368": 193479, "369": 193480, "370": 193481, "371": 193482, "372": 193483, "373": 193484, "374": 193485, "375": 193486, "376": 193487, "377": 193488, "378": 193489, "379": 193490, "380": 193491, "381": 193492, "382": 193493, "383": 193494 }
        };
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

        this.uuid = 'unique-string';
        this.viewingSS = SampleSetProperties.getObject().viewingSampleSets;
        $httpBackend.whenGET('/api/v2/sampleset/uuid/').respond({uuid: this.uuid});
        $httpBackend.whenGET('/api/v2/sampleset/1/summary/').respond(this.mockSampleSet);
        $httpBackend.whenGET('/api/v2/homestatus/1/question_summary/').respond(this.mockTestHome);
        $httpBackend.whenGET('/api/v2/homestatus/12/question_summary/').respond(this.mockSampledHome);
    });

    afterEach(function(){
        $httpBackend.verifyNoOutstandingRequest();
        $httpBackend.verifyNoOutstandingExpectation();
    });

    it('should exist', function(){
        expect(!!SampleSetProperties).toBe(true);
        var a = SampleSetProperties.getObject();
        expect(a.isDragging).toBeDefined();
        expect(a.viewingSampleSets).toBeDefined();
        expect(a.availableTestAnswers).toBeDefined();
    });

    describe('Sample Set Operations', function(){

        it('should add a sample set to viewingSamplesets', function(){
            expect(this.viewingSS.length).toBe(0);
            SampleSetProperties.addSampleSet(1);
            $httpBackend.flush();
            expect(this.viewingSS.length).toBe(1);
            expect(this.viewingSS[0]).toEqual(this.mockSampleSet);
        });
        it('should not add the same sample set more than once', function(){
            expect(this.viewingSS.length).toBe(0);

            SampleSetProperties.addSampleSet(1);
            $httpBackend.flush();
            expect(this.viewingSS.length).toBe(1);
            expect(this.viewingSS[0]).toEqual(this.mockSampleSet);

            SampleSetProperties.addSampleSet(1);
            $httpBackend.flush();
            expect(this.viewingSS.length).toBe(1);
            expect(this.viewingSS[0]).toEqual(this.mockSampleSet);
        });
        it('should add an empty sample set', function(){
            expect(this.viewingSS.length).toBe(0);

            SampleSetProperties.addBlankSampleSet();
            $httpBackend.flush();

            expect(this.viewingSS.length).toBe(1);

            var ss = this.viewingSS[0];

            expect(ss.name).toEqual(this.uuid);
            expect(ss.id).not.toBeDefined();
            expect(ss.alt_name).toEqual('');
            expect(ss.test_homes.length).toBe(0);
            expect(ss.sampled_homes.length).toBe(0);
        });
        it('should remove a sample set with an id', function(){
            SampleSetProperties.addBlankSampleSet();
            $httpBackend.flush();

            expect(this.viewingSS.length).toBe(1);
            this.viewingSS[0]['id'] = 1;

            SampleSetProperties.removeSampleSet(1);

            expect(this.viewingSS.length).toBe(0);
        });
        it('should remove a sample set with a uuid', function(){
            SampleSetProperties.addBlankSampleSet();
            $httpBackend.flush();

            expect(this.viewingSS.length).toBe(1);

            SampleSetProperties.removeSampleSet(this.uuid);
            expect(this.viewingSS.length).toBe(0);
        });
        it('should move cached homes to removed when sample set is removed', function(){
            expect(this.viewingSS.length).toBe(0);
            SampleSetProperties.addSampleSet(1);
            $httpBackend.flush();
            expect(this.viewingSS.length).toBe(1);

            var num_of_homes = this.testHomes.length + this.sampledHomes.length;
            expect(HomeProperties.getCachedHomesIds().length).toBe(num_of_homes);

            SampleSetProperties.removeSampleSet(1);
            expect(this.viewingSS.length).toBe(0);

            expect(HomeProperties.getCachedHomesIds().length).toBe(0);
        })
    });

    describe('home moving', function(){
        describe('blank sample sets', function(){
            beforeEach(function(){
                // add a default blank sampleset.
                expect(this.viewingSS.length).toBe(0);
                SampleSetProperties.addBlankSampleSet();
                $httpBackend.flush();
                expect(this.viewingSS.length).toBe(1);
            });

            it('should add a test home to an existing sample Set', function(){
                var ss = this.viewingSS[0];
                expect(ss.test_homes.length).toBe(0);
                expect(ss.sampled_homes.length).toBe(0);

                SampleSetProperties.addHome(this.mockTestHome.home_status_id, ss.name);
                $httpBackend.flush();

                expect(ss.test_homes.length).toBe(1);
                expect(ss.sampled_homes.length).toBe(0);
            });
            it('should add a sample home to an existing sample set', function(){
                var ss = this.viewingSS[0];
                expect(ss.test_homes.length).toBe(0);
                expect(ss.sampled_homes.length).toBe(0);

                SampleSetProperties.addHome(this.mockSampledHome.home_status_id, ss.name);
                $httpBackend.flush();

                expect(ss.test_homes.length).toBe(0);
                expect(ss.sampled_homes.length).toBe(1);
            });
            it('should not add the same test home to a sample set', function(){
                var ss = this.viewingSS[0];
                expect(ss.test_homes.length).toBe(0);
                expect(ss.sampled_homes.length).toBe(0);

                SampleSetProperties.addHome(this.mockTestHome.home_status_id, ss.name);
                $httpBackend.flush();

                expect(ss.test_homes.length).toBe(1);
                expect(ss.sampled_homes.length).toBe(0);

                var added = SampleSetProperties.addHome(this.mockTestHome.home_status_id, ss.name);
                expect($httpBackend.flush).toThrow();

                expect(added).toBeTruthy();
                expect(ss.test_homes.length).toBe(1);
                expect(ss.sampled_homes.length).toBe(0);
            });
            it('should not add the same sampled home to a sample set', function(){
                var ss = this.viewingSS[0];
                expect(ss.test_homes.length).toBe(0);
                expect(ss.sampled_homes.length).toBe(0);

                SampleSetProperties.addHome(this.mockSampledHome.home_status_id, ss.name);
                $httpBackend.flush();

                expect(ss.test_homes.length).toBe(0);
                expect(ss.sampled_homes.length).toBe(1);

                SampleSetProperties.addHome(this.mockSampledHome.home_status_id, ss.name);
                expect($httpBackend.flush).toThrow();

                expect(ss.test_homes.length).toBe(0);
                expect(ss.sampled_homes.length).toBe(1);
            });
        });
        describe('used sample sets', function(){
            beforeEach(function(){
                expect(this.viewingSS.length).toBe(0);
                SampleSetProperties.addSampleSet(1);
                $httpBackend.flush();
                expect(this.viewingSS.length).toBe(1);
            });
            it('should remove a home from an existing sample set', function(){
                var ss = this.viewingSS[0];
                expect(!!ss).toBe(true);

                var testHomeLength = this.testHomes.length;
                var sampledHomeLength = this.sampledHomes.length;

                expect(ss.test_homes.length).toBe(testHomeLength);
                expect(ss.sampled_homes.length).toBe(sampledHomeLength);

                var removed = SampleSetProperties.removeHome(this.testHomes[0].home_status_id, ss.name);

                expect(removed).toBe(true);

                expect(ss.test_homes.length).toBe(testHomeLength-1);
                expect(ss.sampled_homes.length).toBe(sampledHomeLength);

                SampleSetProperties.removeHome(this.sampledHomes[0].home_status_id, ss.name);

                expect(ss.test_homes.length).toBe(testHomeLength-1);
                expect(ss.sampled_homes.length).toBe(sampledHomeLength-1);
            });
            it('should move a home between two sample sets', function(){
                SampleSetProperties.addBlankSampleSet();
                $httpBackend.flush();
                expect(this.viewingSS.length).toBe(2);


                var ssOne = this.viewingSS[0];
                var ssTwo = this.viewingSS[1];
                expect(ssOne).not.toEqual(ssTwo);
                expect(ssOne.test_homes.length).toBe(1);
                expect(ssTwo.test_homes.length).toBe(0);

                var home = ssOne.test_homes[0];

                var moved = SampleSetProperties.moveHome(home.home_status_id, ssOne.name, ssTwo.name)
                // Because the home is already cached by the sampleset the HomeAPI returns a
                // non-API backed promise. Need to call apply to trigger a digest cycle for it
                // to properly resolve.
                scope.$apply();

                expect(moved).toBeTruthy();
                expect(ssOne.test_homes.length).toBe(0);
                expect(ssTwo.test_homes.length).toBe(1);
            });
            it('should not remove a home from a sample set if it cannot add it to the new sample set', function(){
                var ss = this.viewingSS[0];
                expect(ss.test_homes.length).toBe(1);

                var home = ss.test_homes[0];
                var moved = SampleSetProperties.moveHome(home.home_status_id, ss.name, 'non-existent');

                expect(moved).toBeTruthy();
                moved.then(function(wasRemoved){
                    expect(wasRemoved).toBe(false);
                });
                expect(ss.test_homes.length).toBe(1);
                expect(ss.test_homes.indexOf(home)).not.toBe(-1);
            });
        });
    });

    describe('source answer accounting', function(){
        beforeEach(function(){
            this.answers = SampleSetProperties.getObject().availableTestAnswers;
            expect(this.answers).toEqual({});

            SampleSetProperties.addSampleSet(1);
            $httpBackend.flush();
            expect(this.viewingSS.length).toBe(1);

            this.ss = this.viewingSS[0];
            expect(this.answers).not.toEqual({});
            expect(this.answers[this.ss.name]).toBeDefined();
            expect(this.answers[this.ss.name].homes.length).toBe(this.ss.test_homes.length);
        });
        it('should add source answers when a home is loaded from the api.', function(){

            for(var i = 0; i < this.ss.test_homes.length; i++){
                var obj = this.ss.test_homes[i];
                for(var key in obj.source_answers){
                    expect(this.answers[this.ss.name].questions[key]).toBe(1);
                }
            }
        });
        it('should add a homes source answers and home id to the answer object when added to a sample set', function(){
            var mockTestHome = this.mockTestHome;
            var added = SampleSetProperties.addHome(mockTestHome.home_status_id, this.ss.name).then(function(wasAdded){
                expect(wasAdded).toBe(true);
            });
            $httpBackend.flush();

            expect(added).toBeTruthy();
            expect(this.ss.test_homes.length).toBe(2);
            expect(this.answers[this.ss.name].homes).toContain(String(mockTestHome.home_status_id));

            var contributedCounts = [];
            var answersHomeQuestions = [];

            // get the questions that have this.answers for ones already contributed.
            var answerKeys = Object.keys(this.answers[this.ss.name].questions);
            for(var i = 0; i < answerKeys.length; i++){
                var obj = answerKeys[i];
                if(this.answers[this.ss.name].questions[obj] && this.answers[this.ss.name].questions[obj] > 0){
                    contributedCounts.push(obj);
                }
            }

            // get the questions that have this.answers from the home
            var answerKeys = Object.keys(mockTestHome.source_answers);
            for(var i = 0; i < answerKeys.length; i++){
                var obj = answerKeys[i];
                if(this.answers[this.ss.name].questions[obj]){
                    answersHomeQuestions.push(obj);
                }
            }

            var questionsToCheck = answersHomeQuestions.filter(function(value){
                return contributedCounts.indexOf(value) > -1;
            });

            // make sure they were bumped up to 2.
            for(var i = 0; i < questionsToCheck.length; i++){
                var obj1 = questionsToCheck[i];
                expect(this.answers[this.ss.name].questions[obj1]).toBe(2);
            }


        });
        it('should remove a homes source answers and home id when removed from sampleset', function(){
            for(var i = 0; i < this.ss.test_homes.length; i++){
                var obj = this.ss.test_homes[i];
                for(var key in obj.source_answers){
                    expect(this.answers[this.ss.name].questions[key]).toBe(1);
                }
            }

            SampleSetProperties.removeHome(this.ss.test_homes[0].home_status_id, this.ss.name);
            for(var key in this.answers[this.ss.name].questions){
                expect(this.answers[this.ss.name].questions[key]).toBe(0)
            }

        });
        it('should not re-add a homes source answers to the answer object', function(){
            var home = this.ss.test_homes[0];

            var added = SampleSetProperties.addHome(home.home_status_id, 'test', this.ss.name);

            expect(added).toBeTruthy();
            added.then(function(wasAdded){
                expect(wasAdded).toBe(false);
            });
            expect(this.answers[this.ss.name].homes.length).toBe(1);
            expect(this.answers[this.ss.name].homes).toEqual(([String(this.ss.test_homes[0].home_status_id)]));
            for(var question_id in this.answers[this.ss.name].questions){
                var answer = this.answers[this.ss.name].questions[question_id];
                expect(answer).not.toBeGreaterThan(1);
            }
        });
        it('should return false if trying to remove a home that is not in a sampleset', function(){
            var testLength = this.ss.test_homes.length;
            var sampledLength = this.ss.sampled_homes.length;

            var removed = SampleSetProperties.removeHome(this.mockTestHome.home_status_id, this.ss.name);
            expect(removed).toBe(false);
            expect(this.ss.test_homes.length).toBe(testLength);
            expect(this.ss.sampled_homes.length).toBe(sampledLength);
        });
        it('should return a dict of sampleset ids with home status ids in them', function(){
            var obj = SampleSetProperties.getSampleSetHomeIds();

            for(var i = 0; i < this.viewingSS[0].test_homes.length; i++){
                var testHome = this.viewingSS[0].test_homes[i];
                expect(obj[testHome.home_status_id]).toBeDefined();
                expect(obj[testHome.home_status_id]).toBe(this.viewingSS[0].name);
            }
            for(var i = 0; i < this.viewingSS[0].sampled_homes.length; i++){
                var sampledHome = this.viewingSS[0].sampled_homes[i];
                expect(obj[sampledHome.home_status_id]).toBeDefined();
                expect(obj[sampledHome.home_status_id]).toBe(this.viewingSS[0].name);
            }
        });
    });

});

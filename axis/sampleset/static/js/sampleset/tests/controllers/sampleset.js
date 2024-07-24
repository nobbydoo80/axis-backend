/**
 * Created by mjeffrey on 9/2/14.
 */
describe('Controller: SampleSetController', function(){
    var rootScope, controller, scope, $location, $timeout, $httpBackend, SampleSetProperties, CustomEvents, SampleSetAPI;

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

        inject(function($rootScope, $controller, _$location_, _$timeout_, _$httpBackend_, _SampleSetProperties_, _CustomEvents_, _SampleSetAPI_){
            rootScope = $rootScope;
            scope = $rootScope.$new();
            $location = _$location_;
            $timeout = _$timeout_;
            $httpBackend = _$httpBackend_;
            scope['sampleSet'] = this.mockSampleSet;
            controller = $controller('SampleSetController', {
                $scope: scope,
                $location: $location
            });
            SampleSetProperties = _SampleSetProperties_;
            CustomEvents = _CustomEvents_;
            SampleSetAPI = _SampleSetAPI_;
        });

        $httpBackend.whenGET(/\/api\/v2\/*/).respond(this.mockSampleSet);
        $httpBackend.whenPUT(/\/api\/v2\/*/).respond({});
        $httpBackend.whenPOST(/\/api\/v2\/*/).respond({});
    });

    it('should exist', function(){
        expect(!!controller).toBe(true);
    });
    it('should start out with all flags false', function(){
        expect(scope.accordion.open).toEqual(false);
        expect(scope.accordion.currentClass).toEqual('');
        expect(scope.accordion.previousClass).toEqual('');

        expect(scope.notification.open).toEqual(false);
        expect(scope.notification.currentClass).toEqual('');
        expect(scope.notification.previousClass).toEqual('');

        expect(scope.flags.isCertifiable).toEqual(false);
        expect(scope.flags.showHomeDetail).toEqual(false);
        expect(scope.flags.changed).toEqual(false);
        expect(scope.flags.isProcessing).toEqual(false);
        expect(scope.flags.isDeleting).toEqual(false);

        expect(scope.messages).toEqual([]);
    });

    it('should try to analyze as soon as its loaded', function(){
        // check that init was called, and analyze was called
        spyOn(scope.api, 'analyze').andCallFake();
        scope.$apply();
        expect(scope.api.analyze).toHaveBeenCalled();
    });
    it('should call analyze when a home is added or removed to the sample set', function(){
        scope.$apply();
        spyOn(scope.api, 'analyze').andCallThrough();
        expect(scope.flags.changed).toBe(false);
        expect(scope.api.analyze.callCount).toBe(0);
        rootScope.$broadcast(scope.sampleSet.name+CustomEvents.suffixes.HOME_MOVE);
        expect(scope.flags.changed).toBe(true);
        expect(scope.api.analyze).toHaveBeenCalled();
        expect(scope.api.analyze.callCount).toBe(1);

    });
    it('should get the certify url as soon as its loaded', function(){
        scope.$apply();
        expect(scope.certifyUrl).not.toBeFalsy();
    });
    it('should grab the certified url from the sampled home unless there are none', function(){
        scope.getCertifyUrl();
        expect(scope.certifyUrl).toBe('/home/'+scope.sampleSet.sampled_homes[0].home_status_id+'/certify/');
        scope.sampleSet.sampled_homes = [];
        scope.getCertifyUrl();
        expect(scope.certifyUrl).toBe('/home/'+scope.sampleSet.test_homes[0].home_status_id+'/certify/');
    });
    it('should return the correct alert level for messages', function(){
        expect(scope.getAlertLevel('INFO')).toBe('info');
        expect(scope.getAlertLevel('WARNING')).toBe('warning');
        expect(scope.getAlertLevel('ERROR')).toBe('danger');
    });
    it('should open the accordion on even openAccordion and flash blue', function(){
        expect(scope.accordion.open).toBe(false);
        expect(scope.accordion.currentClass).toBe('');

        rootScope.$broadcast(CustomEvents.OPEN_ACCORDION, scope.sampleSet.id);
        scope.$digest();

        expect(scope.accordion.open).toBe(true);
        expect(scope.accordion.currentClass).toBe('panel-info');

        $timeout.flush();

        expect(scope.accordion.open).toBe(true);
        expect(scope.accordion.currentClass).toBe('');
    });

    describe("analyze", function(){
        it('should set isProcessing when called', function(){
            // get rid of initial analyze call
            $timeout.flush();

            expect(scope.flags.isProcessing).toBe(false);
            $timeout.flush();
            expect(scope.flags.isProcessing).toBe(true);
        });
        it('should cancel an analyze if called within 1 second', function(){
            spyOn($timeout, 'cancel').andCallThrough();
            expect($timeout.cancel.callCount).toBe(0);
            expect(scope.timedAnalyze).toBe(null);
            scope.api.analyze();
            expect(scope.timedAnalyze).not.toBe(null);
            var timer = scope.timedAnalyze;
            expect($timeout.cancel.callCount).toBe(0);
            scope.api.analyze();
            expect($timeout.cancel.callCount).toBe(1);
            expect(scope.timedAnalyze).not.toBe(timer);
        });
        it('analyze_success should set flags', function(){
            var new_builder = 'new builder name';
            var obj = {builder: new_builder, is_certifiable: true, is_metro_sampled: true};

            expect(scope.sampleSet.builder_name).not.toEqual(obj.builder);
            expect(scope.flags.isCertifiable).not.toBe(obj.is_certifiable);
            expect(scope.sampleSet.isMetroSampled).not.toBe(obj.is_metro_sampled);

            scope.api.analyze_success(obj);

            expect(scope.sampleSet.builder_name).toEqual(obj.builder);
            expect(scope.flags.isCertifiable).toBe(obj.is_certifiable);
            expect(scope.sampleSet.isMetroSampled).toBe(obj.is_metro_sampled);
        });
        it('should make the accordion and notification appropriate colors for messages returned', function(){
            var obj = {messages: [{level: 'INFO', message: 'test info message'}]},
                pblue = 'panel-info',
                pyellow = 'panel-warning',
                pred = 'panel-danger',
                nblue = 'label-info',
                nyellow = 'label-warning',
                nred = 'label-danger';

            expect(scope.accordion.currentClass).not.toBe(pblue);
            expect(scope.notification.currentClass).not.toBe(nblue);
            scope.api.analyze_success(obj);
            expect(scope.accordion.currentClass).toBe(pblue);
            expect(scope.notification.currentClass).toBe(nblue);

            obj.messages[0].level = 'WARNING';
            expect(scope.accordion.currentClass).not.toBe(pyellow);
            expect(scope.notification.currentClass).not.toBe(nyellow);
            scope.api.analyze_success(obj);
            expect(scope.accordion.currentClass).toBe(pyellow);
            expect(scope.notification.currentClass).toBe(nyellow);

            obj.messages[0].level = 'ERROR';
            expect(scope.accordion.currentClass).not.toBe(pred);
            expect(scope.notification.currentClass).not.toBe(nred);
            scope.api.analyze_success(obj);
            expect(scope.accordion.currentClass).toBe(pred);
            expect(scope.notification.currentClass).toBe(nred);
        });
        it('should make the accordion and notification red if an analyze call fails', function(){
            $httpBackend.expectGET(/\/api\/v2\/*/).respond(500, {});
            $timeout.flush();

            var pred = 'panel-danger';
            var nred = 'label-danger';

            expect(scope.accordion.currentClass).not.toBe(pred);
            expect(scope.notification.currentClass).not.toBe(nred);

            scope.api.analyze();
            $timeout.flush();
            $httpBackend.flush();

            expect(scope.accordion.currentClass).toBe(pred);
            expect(scope.notification.currentClass).toBe(nred);
        });
    });
    describe("commit", function(){
        it('should set isProcessing when called', function(){
            expect(scope.flags.isProcessing).toBe(false);
            scope.api.commit();
            expect(scope.flags.isProcessing).toBe(true);
            $httpBackend.flush();
            expect(scope.flags.isProcessing).toBe(false);
        });
        it('commit_success should set flags', function(){
            var obj = {sampleset: 42, eep_program: 'some new cool eep', is_certifiable: true};
            scope.flags.changed = true;

            expect(scope.sampleSet.id).not.toBe(obj.sampleset);
            expect(scope.sampleSet.eep_program).not.toBe(obj.eep_program);
            expect(scope.flags.isCertifiable).not.toBe(obj.is_certifiable);
            expect(scope.flags.changed).toBe(true);

            scope.api.commit_success(obj);

            expect(scope.sampleSet.id).toBe(obj.sampleset);
            expect(scope.sampleSet.eep_program).toBe(obj.eep_program);
            expect(scope.flags.isCertifiable).toBe(obj.is_certifiable);
            expect(scope.flags.changed).toBe(false);
        });
        it('should add the samplesets id to the url on first commit but not on subsequent commits', function(){

            // the Location Service uses an array even for 1 item and converts everything to strings.
            var obj = {sampleset: 42};

            expect($location.search().id).not.toBeDefined();
            scope.api.commit_success(obj);

            expect($location.search().id).toBeDefined();
            expect($location.search().id).toEqual([String(obj.sampleset)]);

            scope.api.commit_success(obj);

            expect($location.search().id).toBeDefined();
            expect($location.search().id).toEqual([String(obj.sampleset)]);
        });
        it('should turn the accordion green on success', function(){
            expect(scope.accordion.currentClass).toBe('');
            scope.api.commit_success({});
            expect(scope.accordion.currentClass).toBe('panel-success');
            $timeout.flush();
            expect(scope.accordion.currentClass).toBe('');
        });
        it('should turn the accordion red if the save was unsuccessful', function(){
            $httpBackend.expectPUT(/\/api\/v2\/*/).respond(500, {});
            expect(scope.accordion.currentClass).toBe('');
            scope.api.commit();
            $httpBackend.flush();
            expect(scope.accordion.currentClass).toBe('panel-danger');
        });
    });
    describe("advance", function(){
        it('should set isProcessing when called', function(){
            spyOn(window, 'confirm').andCallFake(function(){
                return true;
            });

            expect(scope.flags.isProcessing).toBe(false);
            scope.api.advance();
            expect(scope.flags.isProcessing).toBe(true);
            $httpBackend.flush();
            expect(scope.flags.isProcessing).toBe(false);
        });
        it('should turn the accordion green if the advance was successful', function(){
            expect(scope.accordion.currentClass).toBe('');
            scope.api.advance_success();
            expect(scope.accordion.currentClass).toBe('panel-success');
            $timeout.flush();
            expect(scope.accordion.currentClass).toBe('');
        });
        it('should turn the accordion red if the advance was unsuccessful', function(){
            $timeout.flush();
            $httpBackend.expectPOST(/\/api\/v2\/*/).respond(500, {});
            spyOn(window, 'confirm').andCallFake(function(){
                return true;
            });

            expect(scope.accordion.currentClass).toBe('');
            scope.api.advance();
            $httpBackend.flush();
            expect(scope.accordion.currentClass).toBe('panel-danger');
            $timeout.flush();
            expect(scope.accordion.currentClass).toBe('panel-danger');
        });
        it('should reload the sampleset after advancing', function(){
            spyOn(angular, 'extend').andCallThrough();
            spyOn(SampleSetProperties, 'addSampleSet').andCallThrough();
            scope.flags.isProcessing = true;

            scope.api.advance_finally();
            expect(scope.flags.isProcessing).toBe(false);
            expect(SampleSetProperties.addSampleSet).toHaveBeenCalled();
            expect(angular.extend).toHaveBeenCalled();
        });
        it('should not advance if the sampleset changed', function(){
            spyOn(window, 'alert');
            spyOn(SampleSetAPI, 'advance');
            scope.flags.changed = true;
            scope.api.advance();
            expect(SampleSetAPI.advance).not.toHaveBeenCalled();
            expect(window.alert).toHaveBeenCalled();
        });
        it('should prompt the user before advancing', function(){
            spyOn(window, 'confirm');
            scope.api.advance();
            expect(window.confirm).toHaveBeenCalled();
        })
    });
    describe("certify", function(){
        it('should open a new window', function(){
            scope.$apply();
            spyOn(window, 'open');
            scope.certify();
            expect(window.open).toHaveBeenCalledWith(scope.certifyUrl, '_blank');
        });
    });
});

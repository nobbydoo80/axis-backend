/**
 * Created by mjeffrey on 9/10/14.
 */

describe('Directive: droppable', function(){

    var $timeout, compile, rootScope, scope, SampleSetProperties;

    beforeEach(module('app'));

    beforeEach(inject(function(_$timeout_, $compile, $rootScope, _SampleSetProperties_){
        $timeout = _$timeout_;
        compile = $compile;
        rootScope = $rootScope;
        scope = $rootScope.$new();
        SampleSetProperties = _SampleSetProperties_;

        this.element = compile('<div droppable></div>')(scope);

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

        scope.sampleSet = this.mockSampleSet;
        scope.home = this.testHomes[0];
    }));

    beforeEach(function(){
        this.events = {
            dragover: document.createEvent('CustomEvent'),
            dragenter: document.createEvent('CustomEvent'),
            dragleave: document.createEvent('CustomEvent'),
            drop: document.createEvent('CustomEvent')
        };
        this.events.dragover.dataTransfer = jasmine.createSpy('dataTransfer');
        this.events.drop.dataTransfer = jasmine.createSpyObj('dataTransfer', ['getData']);

        this.events.dragover.initCustomEvent('dragover', false, false, false);
        this.events.dragenter.initCustomEvent('dragenter', false, false, false);
        this.events.dragleave.initCustomEvent('dragleave', false, false, false);
        this.events.drop.initCustomEvent('drop', false, false, false);

        this.over = function(){ this.element[0].dispatchEvent(this.events.dragover); }
        this.enter = function(){ this.element[0].dispatchEvent(this.events.dragenter); }
        this.leave = function(){ this.element[0].dispatchEvent(this.events.dragleave); }
        this.drop = function(){ this.element[0].dispatchEvent(this.events.drop); }
    });

    it('should add over class on dragover', function(){
        expect(this.element.hasClass('over')).toBe(false);
        this.over();
        expect(this.element.hasClass('over')).toBe(true);
    });
    it('should add over class on dragenter', function(){
        expect(this.element.hasClass('over')).toBe(false);
        this.enter();
        expect(this.element.hasClass('over')).toBe(true);
    });
    it('should remove over class on dragleave', function(){
        expect(this.element.hasClass('over')).toBe(false);
        this.over();
        expect(this.element.hasClass('over')).toBe(true);
        this.leave();
        expect(this.element.hasClass('over')).toBe(false);
    });
    it('should remove over class on drop', function(){
        expect(this.element.hasClass('over')).toBe(false);
        this.over();
        expect(this.element.hasClass('over')).toBe(true);
        this.drop();
        expect(this.element.hasClass('over')).toBe(false);
    });
    it('should make a blank sampleset if the event does not have a destination sample set', function(){
        // removing the sample set tells it that it wasn't dropped on a sampleset
        delete scope.sampleSet;
        spyOn(SampleSetProperties, 'addBlankSampleSetWithHome');

        expect(SampleSetProperties.addBlankSampleSetWithHome).not.toHaveBeenCalled();
        this.drop();
        expect(SampleSetProperties.addBlankSampleSetWithHome).toHaveBeenCalled();
    });
    it('should move a home into a sampleset if its dropped on one', function(){
        this.events.drop.dataTransfer.getData.andReturn(1);
        spyOn(SampleSetProperties, 'moveHome');

        expect(SampleSetProperties.moveHome).not.toHaveBeenCalled();
        this.drop();
        expect(SampleSetProperties.moveHome).toHaveBeenCalledWith(1, 1, scope.sampleSet.name);
    })
});

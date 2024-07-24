/**
 * Created by mjeffrey on 9/10/14.
 */

describe('Directive: QuestionTick', function(){
    var compile, rootScope, scope, QuestionProperties, CustomEvents;

    beforeEach(module('app'));

    beforeEach(inject(function($rootScope, $compile, _QuestionProperties_, _CustomEvents_){
        rootScope = $rootScope;
        scope = $rootScope.$new();
        compile = $compile;
        QuestionProperties = _QuestionProperties_;
        CustomEvents = _CustomEvents_;
    }));

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
                "failing_answers": {},
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
            "failing_answers": {},
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
            "failing_answers": {},
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
            "failing_answers": {},
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

    });
    describe('uses test home', function(){
        beforeEach(function(){
            scope.sampleSet = this.mockSampleSet;
            scope.home = this.testHomes[0];
            this.element = compile('<li display-home></li>')(scope);
            scope.$apply();
        });

        it('should add and remove hover class on mouse enter and leave', function(){
            var el = angular.element(this.element.find('span')[1]);
            expect(el.hasClass('hover')).toBe(false);
            el.triggerHandler('mouseenter');
            expect(el.hasClass('hover')).toBe(true);
            el.triggerHandler('mouseleave');
            expect(el.hasClass('hover')).toBe(false);
        });

        it('should set question as current viewing Question when mouse enter and unset when mouse leave', function(){
            var el = angular.element(this.element.find('span')[1]);
            spyOn(QuestionProperties, 'setCurrentQuestion').andCallThrough();

            expect(QuestionProperties.getObject().currentQuestion).toBe(null);
            var el_scope = angular.element(el).scope();
            el.triggerHandler('mouseenter');
            expect(QuestionProperties.getObject().currentQuestion).toBe(el_scope.question_id);
            el.triggerHandler('mouseleave');
            expect(QuestionProperties.getObject().currentQuestion).toBe(null);
        });

    });
    describe('use sampled home', function(){
        beforeEach(function(){
            spyOn(rootScope, '$on').andCallThrough();
            expect(rootScope.$on).not.toHaveBeenCalled();
            scope.sampleSet = this.mockSampleSet;
            scope.home = this.sampledHomes[1];
            this.element = compile('<li display-home></li>')(scope);
            scope.$apply();
        });
        it('should setup of a listener if the home is not a test home', function(){
            expect(rootScope.$on).toHaveBeenCalled();

            spyOn(scope, 'questionPopoverText').andCallThrough();
            expect(scope.questionPopoverText).not.toHaveBeenCalled();

            var name = scope.sampleSet.name + CustomEvents.suffixes.UPDATE_ANSWERS;
            rootScope.$broadcast(name);
            expect(scope.questionPopoverText).toHaveBeenCalled();
        });
    })
});

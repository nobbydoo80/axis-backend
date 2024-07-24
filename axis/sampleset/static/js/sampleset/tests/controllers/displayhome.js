/**
 * Created by mjeffrey on 9/2/14.
 */
describe('Controller: DisplayHomeController', function(){
    var rootScope, controller, scope, $location, $timeout, $httpBackend, SampleSetProperties, QuestionProperties;

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
                    "384": 34948, "385": null, "386": 34950, "387": 34951, "388": 34952, "389": 34953, "390": 34954, "391": 34955, "392": 34956, "393": null, "394": 34958, "395": 34959, "396": 34960, "397": 34961, "398": 34962, "399": 34963, "400": 34964, "410": 34965, "411": 34966, "412": 34967, "413": 34968, "346": 34969, "347": 34970, "348": 34971, "349": null, "354": null, "355": null, "356": 34975, "357": 34976, "358": 34977, "359": 34978, "360": 34979, "361": 34980, "362": 34981, "363": 34982, "364": 34983, "365": 34984, "366": 34985, "367": 34986, "368": 34987, "369": 34988, "370": 34989, "371": 34990, "372": 34991, "373": 34992, "374": 34993, "375": 34994, "376": 34995, "377": 34996, "378": 34997, "379": 34998, "380": 34999, "381": 35000, "382": 35001, "383": 35002
                },
                "subdivision_id": 68,
                "contributed_answers": {
                    "384": 34948, "385": 34949, "386": 34950, "387": 34951, "388": 34952, "389": 34953, "390": 34954, "391": 34955, "392": 34956, "393": 34957, "394": 34958, "395": 34959, "396": 34960, "397": 34961, "398": 34962, "399": 34963, "400": 34964, "410": 34965, "411": 34966, "412": 34967, "413": 34968, "346": 34969, "347": 34970, "348": 34971, "349": 34972, "354": 34973, "355": 34974, "356": 34975, "357": 34976, "358": 34977, "359": 34978, "360": 34979, "361": 34980, "362": 34981, "363": 34982, "364": 34983, "365": 34984, "366": 34985, "367": 34986, "368": 34987, "369": 34988, "370": 34989, "371": 34990, "372": 34991, "373": 34992, "374": 34993, "375": 34994, "376": 34995, "377": 34996, "378": 34997, "379": 34998, "380": 34999, "381": 35000, "382": 35001, "383": 35002
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
                "source_answers": { "384": null, "385": null, "386": null, "387": null, "388": null, "389": null, "390": null, "391": null, "392": null, "393": null, "394": null, "395": null, "396": null, "397": null, "398": null, "399": null, "400": null, "410": null, "411": null, "412": null, "413": null, "346": null, "347": null, "348": null, "349": null, "354": null, "355": null, "356": null, "357": null, "358": null, "359": null, "360": null, "361": null, "362": null, "363": null, "364": null, "365": null, "366": null, "367": null, "368": null, "369": null, "370": null, "371": null, "372": null, "373": null, "374": null, "375": null, "376": null, "377": null, "378": null, "379": null, "380": null, "381": null, "382": null, "383": null
                },
                "subdivision_id": 68,
                "contributed_answers": {
                    "384": null, "385": null, "386": null, "387": null, "388": null, "389": null, "390": null, "391": null, "392": null, "393": null, "394": null, "395": null, "396": null, "397": null, "398": null, "399": null, "400": null, "410": null, "411": null, "412": null, "413": null, "346": null, "347": null, "348": null, "349": null, "354": null, "355": null, "356": null, "357": null, "358": null, "359": null, "360": null, "361": null, "362": null, "363": null, "364": null, "365": null, "366": null, "367": null, "368": null, "369": null, "370": null, "371": null, "372": null, "373": null, "374": null, "375": null, "376": null, "377": null, "378": null, "379": null, "380": null, "381": null, "382": null, "383": null
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
                    "384": null, "385": null, "386": null, "387": null, "388": null, "389": null, "390": null, "391": null, "392": null, "393": null, "394": null, "395": null, "396": null, "397": null, "398": null, "399": null, "400": null, "410": null, "411": null, "412": null, "413": null, "346": null, "347": null, "348": null, "349": null, "354": null, "355": null, "356": null, "357": null, "358": null, "359": null, "360": null, "361": null, "362": null, "363": null, "364": null, "365": null, "366": null, "367": null, "368": null, "369": null, "370": null, "371": null, "372": null, "373": null, "374": null, "375": null, "376": null, "377": null, "378": null, "379": null, "380": null, "381": null, "382": null, "383": null
                },
                "subdivision_id": 68,
                "contributed_answers": {
                    "384": null, "385": null, "386": null, "387": null, "388": null, "389": null, "390": null, "391": null, "392": null, "393": null, "394": null, "395": null, "396": null, "397": null, "398": null, "399": null, "400": null, "410": null, "411": null, "412": null, "413": null, "346": null, "347": null, "348": null, "349": null, "354": null, "355": null, "356": null, "357": null, "358": null, "359": null, "360": null, "361": null, "362": null, "363": null, "364": null, "365": null, "366": null, "367": null, "368": null, "369": null, "370": null, "371": null, "372": null, "373": null, "374": null, "375": null, "376": null, "377": null, "378": null, "379": null, "380": null, "381": null, "382": null, "383": null
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
                    "384": null, "385": null, "386": null, "387": null, "388": null, "389": null, "390": null, "391": null, "392": null, "393": null, "394": null, "395": null, "396": null, "397": null, "398": null, "399": null, "400": null, "410": null, "411": null, "412": null, "413": null, "346": null, "347": null, "348": null, "349": null, "354": null, "355": null, "356": null, "357": null, "358": null, "359": null, "360": null, "361": null, "362": null, "363": null, "364": null, "365": null, "366": null, "367": null, "368": null, "369": null, "370": null, "371": null, "372": null, "373": null, "374": null, "375": null, "376": null, "377": null, "378": null, "379": null, "380": null, "381": null, "382": null, "383": null
                },
                "subdivision_id": 68,
                "contributed_answers": {
                    "384": null, "385": null, "386": null, "387": null, "388": null, "389": null, "390": null, "391": null, "392": null, "393": null, "394": null, "395": null, "396": null, "397": null, "398": null, "399": null, "400": null, "410": null, "411": null, "412": null, "413": null, "346": null, "347": null, "348": null, "349": null, "354": null, "355": null, "356": null, "357": null, "358": null, "359": null, "360": null, "361": null, "362": null, "363": null, "364": null, "365": null, "366": null, "367": null, "368": null, "369": null, "370": null, "371": null, "372": null, "373": null, "374": null, "375": null, "376": null, "377": null, "378": null, "379": null, "380": null, "381": null, "382": null, "383": null
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

        inject(function($rootScope, $controller, _$location_, _$timeout_, _$httpBackend_, _SampleSetProperties_, _QuestionProperties_){
            rootScope = $rootScope;
            scope = $rootScope.$new();
            $location = _$location_;
            $timeout = _$timeout_;
            $httpBackend = _$httpBackend_;
            scope['sampleSet'] = this.mockSampleSet;
            scope['home'] = this.sampledHomes[0];
            controller = $controller('DisplayHomeController', {
                $scope: scope,
                $location: $location
            });
            SampleSetProperties = _SampleSetProperties_;
            QuestionProperties = _QuestionProperties_;
        });
    });

    it('should exist', function(){
        expect(!!controller).toBe(true);
    });

    it('should make an object of questions with answers and types', function(){
        spyOn(QuestionProperties, 'cleanAnswers').andCallThrough();
        scope.$apply();
        expect(QuestionProperties.cleanAnswers).toHaveBeenCalled();
    });
    it('should return true from getting answer if test home has answer to contribute', function(){
        SampleSetProperties.addSourceAnswers(this.testHomes[0], scope.sampleSet.name);
        var question = {question_id: null, answer_id: null, type: 'contributed'};
        var questions = scope.availableTestAnswers[scope.sampleSet.name].questions;
        for(var q in  questions){
            if(questions[q]){
                question.question_id = q;
                break;
            }
        }
        expect(question.question_id).not.toBe(null);
        expect(scope.getGettingAnswer(question)).toBe(true);
    });
    it('should return false from getting answer if no test homes can contribute answers', function(){
        SampleSetProperties.addSourceAnswers(this.testHomes[0], scope.sampleSet.name);
        SampleSetProperties.removeSourceAnswers(this.testHomes[0], scope.sampleSet.name);
        var question = {question_id: null, answer_id: null, type: 'contributed'};
        var questions = scope.availableTestAnswers[scope.sampleSet.name].questions;
        for(var q in questions){
            if(!questions[q]){
                question.question_id = q;
                break;
            }
        }
        expect(question.question_id).not.toBe(null);
        expect(scope.getGettingAnswer(question)).toBe(false);
    });
    it('should return false if there are no test homes in the sample set', function(){
        expect(scope.getGettingAnswer({question_id: '348', answer_id: '1234', type: 'contributed'})).toBe(false);
        expect(scope.getGettingAnswer({question_id: '348', answer_id: false, type: 'contributed'})).toBe(false);
    });
    it('should return correct popover text for each type of question', function(){
        SampleSetProperties.addSourceAnswers(this.testHomes[0], scope.sampleSet.name);
        var unanswered_question = {question_id: '42', answer_id: '', type: 'contributed'},
            provided_questions = {question_id: '346', answer_id: '1234', type: 'source'},
            contributed_question = {question_id: '346', answer_id: '1234', type: 'contributed'},
            failing_questions = {question_id: '346', answer_id: '1234', type: 'failing'},
            receiving_question = {question_id: '346', answer_id: false, type: 'contributed'};

        expect(scope.questionPopoverText(unanswered_question)).toBe(scope.popoverText['unanswered']);
        expect(scope.questionPopoverText(provided_questions)).toBe(scope.popoverText['provided']);
        expect(scope.questionPopoverText(contributed_question)).toBe(scope.popoverText['contributed']);
        expect(scope.questionPopoverText(failing_questions)).toBe(scope.popoverText['failing']);
        expect(scope.questionPopoverText(receiving_question)).toBe(scope.popoverText['receiving']);
    });
});

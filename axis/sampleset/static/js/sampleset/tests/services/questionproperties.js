/**
 * Created by mjeffrey on 8/27/14.
 */
describe('Service: QuestionProperties', function(){
    var QuestionProperties;

    beforeEach(function(){
        inject(function(_QuestionProperties_){
            QuestionProperties = _QuestionProperties_;
        });

        this.props = QuestionProperties.getObject();
        this.testHome = {
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
                "384": 34948, "385": null, "386": 34950, "387": 34951, "388": 34952, "389": 34953, "390": 34954, "391": 34955, "392": 34956, "393": 34957, "394": 34958, "395": 34959, "396": 34960, "397": 34961, "398": null, "399": 34963, "400": 34964, "410": 34965, "411": 34966, "412": 34967, "413": 34968, "346": 34969, "347": 34970, "348": 34971, "349": 34972, "354": 34973, "355": 34974, "356": 34975, "357": 34976, "358": 34977, "359": 34978, "360": 34979, "361": 34980, "362": 34981, "363": 34982, "364": 34983, "365": 34984, "366": 34985, "367": 34986, "368": 34987, "369": 34988, "370": 34989, "371": null, "372": 34991, "373": null, "374": 34993, "375": 34994, "376": 34995, "377": 34996, "378": 34997, "379": 34998, "380": 34999, "381": null, "382": 35001, "383": 35002
            },
            "failing_answers": {
                "384": null, "385": 34949, "386": null, "387": null, "388": null, "389": null, "390": null, "391": null, "392": null, "393": null, "394": null, "395": null, "396": null, "397": null, "398": null, "399": null, "400": null, "410": null, "411": null, "412": null, "413": null, "346": null, "347": null, "348": null, "349": null, "354": null, "355": null, "356": null, "357": null, "358": null, "359": null, "360": null, "361": null, "362": null, "363": null, "364": null, "365": null, "366": null, "367": null, "368": null, "369": null, "370": null, "371": null, "372": null, "373": null, "374": null, "375": null, "376": null, "377": null, "378": null, "379": null, "380": null, "381": null, "382": null, "383": null

            },
            "subdivision_id": 68,
            "contributed_answers": {
                "384": 34948, "385": null, "386": 34950, "387": 34951, "388": 34952, "389": 34953, "390": 34954, "391": 34955, "392": 34956, "393": 34957, "394": 34958, "395": 34959, "396": 34960, "397": 34961, "398": 34962, "399": 34963, "400": 34964, "410": 34965, "411": 34966, "412": 34967, "413": 34968, "346": 34969, "347": 34970, "348": 34971, "349": 34972, "354": 34973, "355": 34974, "356": 34975, "357": 34976, "358": 34977, "359": 34978, "360": 34979, "361": 34980, "362": 34981, "363": 34982, "364": 34983, "365": 34984, "366": 34985, "367": 34986, "368": 34987, "369": 34988, "370": 34989, "371": 34990, "372": 34991, "373": 34992, "374": 34993, "375": 34994, "376": 34995, "377": 34996, "378": 34997, "379": 34998, "380": 34999, "381": 35000, "382": 35001, "383": 35002
            },
            "subdivision": "Sonoran Vista",
            "detail_url": "/home/2311/",
            "id": 4226
        };

    });

    it('should exist', function(){
        expect(!!QuestionProperties).toBe(true);
    });
    it('should start out with everything null', function(){
        expect(this.props.currentQuestion).toBe(null);
        expect(this.props.viewingQuestions.length).toBe(0);
    });
    it('should set current question', function(){
        expect(this.props.currentQuestion).toBe(null);
        QuestionProperties.setCurrentQuestion(100);
        expect(this.props.currentQuestion).toBe(100);
        QuestionProperties.setCurrentQuestion(null);
        expect(this.props.currentQuestion).toBe(null);
    });
    it('should add viewing questions', function(){
        expect(this.props.viewingQuestions.length).toBe(0);
        QuestionProperties.addViewingQuestions(100);
        expect(this.props.viewingQuestions.length).toBe(1);
    });
    it('should not add the same question twice', function(){
        expect(this.props.viewingQuestions.length).toBe(0);
        QuestionProperties.addViewingQuestions(100);
        QuestionProperties.addViewingQuestions('100');
        QuestionProperties.addViewingQuestions(100);
        QuestionProperties.addViewingQuestions(100);
        expect(this.props.viewingQuestions.length).toBe(1);
        QuestionProperties.addViewingQuestions(200);
        expect(this.props.viewingQuestions.length).toBe(2);
    });
    it('should remove viewing questions', function(){
        QuestionProperties.addViewingQuestions(1);
        QuestionProperties.addViewingQuestions(2);
        QuestionProperties.addViewingQuestions(3);
        QuestionProperties.addViewingQuestions(4);
        expect(this.props.viewingQuestions).toEqual([1, 2, 3, 4]);

        QuestionProperties.removeViewingQuestions(1);
        expect(this.props.viewingQuestions).toEqual([2, 3, 4]);

        QuestionProperties.removeViewingQuestions('2');
        expect(this.props.viewingQuestions).toEqual([3, 4]);
    });
    it('should clean questions from homes into objects with types', function(){
        var answers = QuestionProperties.cleanAnswers(this.testHome);
        for(var question_id in this.testHome.source_answers){
            var answer = answers[question_id];

            expect(answer.question_id).toBeDefined();
            expect(answer.answer_id).toBeDefined();
            expect(answer.type).toBeDefined();

            if(this.testHome.source_answers[answer.question_id]){
                expect(answer.type).toBe('source');
            } else if(this.testHome.failing_answers[answer.question_id]){
                expect(answer.type).toBe('failing');
            } else {
                expect(answer.type).toBe('contributed');
            }

        }

    })
});

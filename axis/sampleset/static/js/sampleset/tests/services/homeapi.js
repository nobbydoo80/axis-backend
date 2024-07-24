/**
 * Created by mjeffrey on 8/27/14.
 */
describe('Service: HomeAPI', function(){
    var HomeAPI, $httpBackend, APIMixin, HomeProperties;

    beforeEach(function(){
        inject(function(_HomeAPI_, _$httpBackend_, _APIMixin_, _HomeProperties_){
            HomeAPI = _HomeAPI_;
            $httpBackend = _$httpBackend_;
            APIMixin = _APIMixin_;
            HomeProperties = _HomeProperties_;
        });

        spyOn(APIMixin, 'call').andCallThrough();

        this.mockTestHome = {
            "metro_id": 264,
            "builder_id": 1,
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

        $httpBackend.expectGET('/api/v2/homestatus/1/question_summary/').respond(this.mockTestHome);

    });

    it('should exist', function(){
        expect(!!HomeAPI).toBe(true);
    });
    it('should fire a get request', function(){
        HomeAPI.get(1);
        $httpBackend.flush();
        expect(APIMixin.call).toHaveBeenCalled();
    });
    it('should not make a server request on subsequent calls to the same home', function(){
        HomeAPI.get(1);
        $httpBackend.flush();

        HomeAPI.get(1);
        expect($httpBackend.flush).toThrow();

        HomeAPI.get(1);
        expect($httpBackend.flush).toThrow();

        HomeAPI.get(1);
        expect($httpBackend.flush).toThrow();

        expect(APIMixin.call).toHaveBeenCalled();
        expect(APIMixin.call.callCount).toBe(1);
    });
});

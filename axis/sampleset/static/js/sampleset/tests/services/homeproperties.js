/**
 * Created by mjeffrey on 8/27/14.
 */
describe('Service: QuestionProperties', function(){
    var HomeProperties;

    beforeEach(function(){
        inject(function(_HomeProperties_){
            HomeProperties = _HomeProperties_;
        });

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
    });

    it('should exist', function(){
        expect(!!HomeProperties).toBe(true);
    });
    it('should start with no homes in the cache', function(){
        expect(HomeProperties.getCachedHomesIds().length).toBe(0);
    });
    it('should cache a home object properly', function(){
        expect(HomeProperties.getCachedHomesIds().length).toBe(0);
        HomeProperties.cacheHome(this.mockTestHome);
        expect(HomeProperties.getCachedHomesIds().length).toBe(1);
    });
    it('should retrieve a cached home', function(){
        expect(HomeProperties.getCachedHomesIds().length).toBe(0);
        HomeProperties.cacheHome(this.mockTestHome);
        expect(HomeProperties.getCachedHomesIds().length).toBe(1);
        var home = HomeProperties.getCachedHome(this.mockTestHome.home_status_id);
        expect(home).toBe(this.mockTestHome);
    });
    it('should give back an array of keys', function(){
        expect(HomeProperties.getCachedHomesIds().length).toBe(0);
        HomeProperties.cacheHome({home_status_id: 1});
        HomeProperties.cacheHome({home_status_id: 2});
        HomeProperties.cacheHome({home_status_id: 3});
        HomeProperties.cacheHome({home_status_id: 4});

        expect(HomeProperties.getCachedHomesIds()).toEqual([1, 2, 3, 4]);
        expect(HomeProperties.getCachedHomesIds().length).toBe(4);
    });
    it('move homes to the removed cache when they are removed', function(){
        expect(HomeProperties.getCachedHomesIds().length).toBe(0);
        HomeProperties.cacheHome({home_status_id: 1});
        HomeProperties.cacheHome({home_status_id: 2});
        HomeProperties.cacheHome({home_status_id: 3});
        HomeProperties.cacheHome({home_status_id: 4});

        expect(HomeProperties.getCachedHomesIds()).toEqual([1, 2, 3, 4]);
        expect(HomeProperties.getCachedHomesIds().length).toBe(4);

        HomeProperties.homeRemoved(2);

        expect(HomeProperties.getCachedHomesIds()).toEqual([1, 3, 4]);
        expect(HomeProperties.getCachedHomesIds().length).toBe(3);
    })

});

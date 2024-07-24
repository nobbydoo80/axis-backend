/**
 * Created by mjeffrey on 8/27/14.
 */
describe('Service: SampleSetAPI', function(){
    var SampleSetAPI, $httpBackend, APIMixin, HomeProperties;

    beforeEach(function(){
        inject(function(_SampleSetAPI_, _$httpBackend_, _APIMixin_, _HomeProperties_){
            SampleSetAPI = _SampleSetAPI_;
            $httpBackend = _$httpBackend_;
            APIMixin = _APIMixin_;
            HomeProperties = _HomeProperties_;
        });

        spyOn(APIMixin, 'call').andCallThrough();

        this.uuid = 'unique-string';
        this.alt_name = 'alt_name';
        this.mockSampleSet = {
            id: 1,
            name: this.uuid,
            alt_name: this.alt_name,
            test_homes: [
                {home_status_id: 1},
                {home_status_id: 2}
            ],
            sampled_homes: [
                {home_status_id: 3},
                {home_status_id: 4}
            ]
        };
    });

    afterEach(function(){
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    it('should exist', function(){
        expect(!!SampleSetAPI).toBe(true);
    });
    it('should create', function(){
        var uuid = 'unique-string';
        $httpBackend.expectGET('/api/v2/sampleset/uuid/').respond({uuid: uuid});

        SampleSetAPI.create().then(function(object){
            expect(object.name).toBeDefined();
            expect(object.name).toBe(uuid);
            expect(object.alt_name).toBeDefined();
            expect(object.test_homes).toBeDefined();
            expect(object.sampled_homes).toBeDefined();
            expect(object.id).not.toBeDefined();
        });

        $httpBackend.flush();
        expect(APIMixin.call).toHaveBeenCalled();
    });
    it('should get properly (correct url transformation)', function(){
        $httpBackend.expectGET('/api/v2/sampleset/1/').respond(this.mockSampleSet);
        SampleSetAPI.get(1);
        $httpBackend.flush();
        expect(APIMixin.call).toHaveBeenCalled();
    });
    it('should get a summary', function(){
        $httpBackend.expectGET('/api/v2/sampleset/1/summary/').respond(this.mockSampleSet);
        spyOn(SampleSetAPI, 'get').andCallThrough();
        SampleSetAPI.getSummary(1);
        $httpBackend.flush();
        // make sure summary is not adding its own trailing slash
        expect(SampleSetAPI.get).toHaveBeenCalledWith('1/summary');
        expect(APIMixin.call).toHaveBeenCalled();
    });
    it('should cache the homes retrieved by get summary', function(){
        $httpBackend.expectGET('/api/v2/sampleset/1/summary/').respond(this.mockSampleSet);
        spyOn(HomeProperties, 'cacheHome').andCallThrough();
        SampleSetAPI.getSummary(1);
        $httpBackend.flush();

        expect(HomeProperties.cacheHome).toHaveBeenCalled();
        expect(HomeProperties.getCachedHomesIds().length).toBe(4);
    });
    it('should analyze', function(){
        $httpBackend.expectGET(/\/api\/v2\/sampleset\/analyze\/\?*/).respond();

        SampleSetAPI.analyze(this.mockSampleSet);
        $httpBackend.flush();

        expect(APIMixin.call).toHaveBeenCalledWith({
            method: 'GET',
            url: '/api/v2/sampleset/analyze/',
            cache: false,
            params: {
                test: [1, 2],
                sampled: [3, 4]
            }
        })
    });
    it('should commit new samplesets', function(){
        $httpBackend.expectPOST('/api/v2/sampleset/commit/').respond();

        // new sample sets don't have 'id'
        delete this.mockSampleSet.id;
        SampleSetAPI.commit(this.mockSampleSet);
        $httpBackend.flush();

        // new samplesets send 'uuid' and 'alt_name'
        expect(APIMixin.call).toHaveBeenCalledWith({
            method: 'POST',
            url: '/api/v2/sampleset/commit/',
            cache: false,
            data: {
                alt_name: this.alt_name,
                uuid: this.uuid,
                test: [1, 2],
                sampled: [3, 4]
            }
        })
    });
    it('should update existing samplesets on commit', function(){
        $httpBackend.expectPUT('/api/v2/sampleset/commit/').respond();

        SampleSetAPI.commit(this.mockSampleSet);
        $httpBackend.flush();

        // existing sample sets do not send 'uuid' and 'alt_name'
        // sampleset 'id' gets tranformed into 'sampleset'
        expect(APIMixin.call).toHaveBeenCalledWith({
            method: 'PUT',
            url: '/api/v2/sampleset/commit/',
            cache: false,
            data: {
                sampleset: 1,
                test: [1, 2],
                sampled: [3, 4]
            }
        })
    });
    it('should advance', function(){
        $httpBackend.expectPOST('/api/v2/sampleset/1/advance/').respond();

        SampleSetAPI.advance(this.mockSampleSet.id);
        $httpBackend.flush();

        expect(APIMixin.call).toHaveBeenCalledWith({
            url: '/api/v2/sampleset/1/advance/',
            method: 'POST',
            cache: false
        })
    });
});

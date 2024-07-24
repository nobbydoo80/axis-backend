/**
 * Created by mjeffrey on 9/10/14.
 */

describe('Service: LocationService', function(){
    var LocationService, $location;

    beforeEach(inject(function(_LocationService_, _$location_){
        LocationService = _LocationService_;
        $location = _$location_;
    }));

    afterEach(function(){
        var newUrl = window.location.protocol + '//' + window.location.host + window.location.pathname;
        window.history.pushState({path: newUrl}, '', newUrl);
        $location.search('id', null);
    });


    it('should grab an id from url', function(){
        $location.search('id', 1);
        LocationService.getIdsFromUrl();
        expect(LocationService.getSampleSetIds().length).toBe(1);
    });
    it('should grab multiple ids from url', function(){
        $location.search('id', [1, 2, 3]);
        LocationService.getIdsFromUrl();
        expect(LocationService.getSampleSetIds().length).toBe(3);
    });
    it('should not read duplicate ids from angular url', function(){
        $location.search('id', [1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3]);
        LocationService.getIdsFromUrl();
        expect(LocationService.getSampleSetIds().length).toBe(3);
    });
    it('should grab ids from regular location', function(){
        var newurl = window.location.protocol +
        "//"
        + window.location.host
        + window.location.pathname +
        '?id=1&id=2&id=3';

        window.history.pushState({path: newurl}, '', newurl);

        LocationService.getIdsFromUrl();
        expect(LocationService.getSampleSetIds().length).toBe(3);

    });
    it('should not read duplicate ids from page url', function(){
        var newurl = window.location.protocol +
                "//"
                + window.location.host
                + window.location.pathname +
                '?id=1&id=1&id=1&id=1&id=1&id=2&id=3&id=3&id=3&id=3&id=3&id=3&id=3&id=3';

        window.history.pushState({path: newurl}, '', newurl);

        LocationService.getIdsFromUrl();
        expect(LocationService.getSampleSetIds().length).toBe(3);
    });
    it('should get ids from both page and angular url', function(){
        var newurl = window.location.protocol +
                "//"
                + window.location.host
                + window.location.pathname +
                '?id=1&id=2&id=3';
        window.history.pushState({path: newurl}, '', newurl);

        $location.search('id', [4, 5, 6]);

        LocationService.getIdsFromUrl();

        expect(LocationService.getSampleSetIds().length).toBe(6);
    });
    it('should not allow duplicate ids accross page and angular query params', function(){
        var newurl = window.location.protocol +
                "//"
                + window.location.host
                + window.location.pathname +
                '?id=1&id=2&id=3';
        window.history.pushState({path: newurl}, '', newurl);

        $location.search('id', [1, 2, 3]);
        LocationService.getIdsFromUrl();

        expect(LocationService.getSampleSetIds().length).toBe(3);
    });
    it('should add an id to angular search params', function(){
        expect(Object.keys($location.search()).length).toBe(0);
        LocationService.addId(1);
        expect(Object.keys($location.search()).length).toBe(1);
        expect($location.search()['id']).toBeDefined();
        expect($location.search()['id'].length).toBe(1);
    });
    it('should not add a duplicate id to the search params', function(){
        expect(Object.keys($location.search()).length).toBe(0);
        LocationService.addId(1);

        var params = $location.search();
        expect(Object.keys(params).length).toBe(1);
        expect(params['id']).toBeDefined();
        expect(params['id'].length).toBe(1);

        LocationService.addId(2);

        params = $location.search();
        expect(Object.keys(params).length).toBe(1);
        expect(params['id']).toBeDefined();
        expect(params['id'].length).toBe(2);

        LocationService.addId(1);

        params = $location.search();
        expect(Object.keys(params).length).toBe(1);
        expect(params['id']).toBeDefined();
        expect(params['id'].length).toBe(2);

    });
    it('should remove ids from url', function(){
        LocationService.addId(1);
        LocationService.addId(2);
        LocationService.addId(3);
        LocationService.addId(4);
        expect($location.search()['id']).toBeDefined();
        expect($location.search()['id'].length).toBe(4);

        LocationService.removeId(1);
        expect($location.search()['id']).toBeDefined();
        expect($location.search()['id'].length).toBe(3);
    });
    it('should remove ids param from url if there are no more', function(){
        LocationService.addId(1);
        expect($location.search()['id']).toBeDefined();
        LocationService.removeId(1);
        expect($location.search()['id']).not.toBeDefined();
    });
});

describe('Filter: SelectFilter', function(){

    // injected
    var $filter;
    // used
    var filter;

    beforeEach(module('axis.filters'));
    beforeEach(inject(function(_$filter_){
        $filter = _$filter_;
    }));
    beforeEach(function(){
        filter = $filter('selectFilter');
    });

    it('should exist', function(){
        expect(!!filter).toBe(true);
    });
    it('should return No Results if there is one entry', function(){
        var noResults = {text: 'No Results...', id: ''};
        var input = [noResults];
        expect(filter(input)).toEqual([noResults]);
        expect(filter(input), 'some input').toEqual([noResults]);
        expect(filter(input), 'test test test').toEqual([noResults]);
    });
    it('should return results with instances of the search text', function(){
        var one = {text: 'one', id: ''};
        var two = {text: 'two', id: ''};
        var three = {text: 'three', id: ''};
        var four = {text: 'one two three', id: ''};

        var input = [one, two, three, four];

        expect(filter(input, '')).toEqual([one, two, three, four]);
        expect(filter(input, 'one')).toEqual([one, four]);
        expect(filter(input, 'two')).toEqual([two, four]);
        expect(filter(input, 'one two')).toEqual([one, two, four]);
        expect(filter(input, 'one two', 'AND')).toEqual([four]);
        expect(filter(input, 't')).toEqual([two, three, four]);
    });
    it('should return if there is no input', function(){
        expect(filter(undefined, 'one')).toEqual(undefined);
    })
});

describe('Filter: Humanize', function(){

    // injected
    var $filter;
    // used
    var filter;

    beforeEach(module('axis.filters'));
    beforeEach(inject(function(_$filter_){
        $filter = _$filter_
    }));
    beforeEach(function(){
        filter = $filter('humanize');
    });

    it('should exist', function(){
        expect(!!filter).toBe(true);
    });
    it('should bypass things that are already Camel cased', function(){
        var result = 'This Is A Sentence With Many Spaces';
        var input = result.replace(/ /g, '');
        expect(filter(input)).toEqual(' '+ result);
    });
    it('should uppercase first letter and separate words with a space', function(){
        var result = 'This Is A Sentence With Many Spaces';
        expect(filter(result.toLowerCase())).toEqual(result);
    });
    it('should not work on lower cased strings with no spaces', function(){
        var result = 'This Is A Sentence With Many Spaces';
        var input = result.split(' ').join('');
        expect(filter(input.toLowerCase())).not.toEqual(result);
    });
    it('should return numbers as they were', function(){
        var result = 1234;
        expect(filter(result)).toEqual(result);
    });
});

/**
 * Created by mjeffrey on 12/15/14.
 */

describe('Filter: TruncateAtBreak', function(){

    // injected
    var $filter;
    // used
    var filter;

    beforeEach(module('axis.filters'));
    beforeEach(inject(function(_$filter_){
        $filter = _$filter_;
    }));
    beforeEach(function(){
        filter = $filter('truncateAtBreak');
    });

    it('should exist', function(){
        expect(!!filter).toBe(true);
    });
    it('should return the input up to but not including the first <br>', function(){
        var result = 'This is a string with a ';
        var styleOne = result + '<br> tag in it';
        var styleTwo = result + '<br/> tag in it';
        var styleThree = result + '<br /> tag in it';

        expect(filter(styleOne)).toEqual(result);
        expect(filter(styleTwo)).toEqual(result);
        expect(filter(styleThree)).toEqual(result);
    });
    it('should return things that are not string regularly', function(){
        var result = 1234;
        expect(filter(result)).toEqual(result);
    });
});

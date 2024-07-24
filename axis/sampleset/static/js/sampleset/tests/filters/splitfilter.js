/**
 * Created by mjeffrey on 9/8/14.
 */
describe('Filter: split', function(){
    var filter;

    beforeEach(inject(function($injector){
        filter = $injector.get("$filter")('split');
    }));

    it('should exist', function(){
        expect(!!filter).toBe(true);
    });

    it('should split a string and return requested index', function(){
        var str_array = ['1234', '2345', '3456', '4567', '5678'];
        var str = str_array.join('-');

        expect(filter(str, '-', 0)).toEqual(str_array[0]);
        expect(filter(str, '-', 1)).toEqual(str_array[1]);
        expect(filter(str, '-', 2)).toEqual(str_array[2]);
        expect(filter(str, '-', 3)).toEqual(str_array[3]);
    });
    it('should return an empty string if something out of index is requested', function(){
        expect(filter('1234-2345', '-', 5)).toEqual('');
    });
});

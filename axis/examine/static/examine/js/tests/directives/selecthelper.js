xdescribe('Directive: SelectHelper', function(){
    it('should exist');

    it('should determine if a field has grouped choices');
    it('should remove the group-by attr if field does not have grouped choices');
    it('should fill the choices with already chosen values');
    it('should convert choices from arrays into objects');

    describe('ajax selects', function(){
        it('should refresh choices');
        it('should add no results choice when nothing is returned');
        it('should add types to grouped inputs');
        it('should add currently typing choice under "Create New..." type when searching');
    });
});

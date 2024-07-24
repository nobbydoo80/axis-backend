/**
 * Created by mjeffrey on 9/8/14.
 */
describe('Service: CollapseHelper', function(){
    var CollapseHelper, $timeout;

    beforeEach(inject(function(_CollapseHelper_, _$timeout_){
        CollapseHelper = _CollapseHelper_.get();
        $timeout = _$timeout_
    }));

    it('should exist', function(){
        expect(!!CollapseHelper).toBe(true);
    });

    it('should start with defaults at null', function(){
        expect(CollapseHelper.open).toEqual(false);
        expect(CollapseHelper.currentClass).toEqual('');
        expect(CollapseHelper.previousClass).toEqual('');
    });
    it('should open and close', function(){
        expect(CollapseHelper.open).toBe(false);
        CollapseHelper.openCollapse();
        expect(CollapseHelper.open).toBe(true);
        CollapseHelper.closeCollapse();
        expect(CollapseHelper.open).toBe(false);
        CollapseHelper.show();
        expect(CollapseHelper.open).toBe(true);
        CollapseHelper.hide();
        expect(CollapseHelper.open).toBe(false);

    });
    it('should should set the accordion class', function(){
        expect(CollapseHelper.currentClass).toEqual('');
        CollapseHelper.setClass('something');
        expect(CollapseHelper.currentClass).toEqual('something');
    });
    it('should set the previous class on class set', function(){
        expect(CollapseHelper.previousClass).toBe('');
        CollapseHelper.currentClass = 'one';
        CollapseHelper.setClass('two');
        expect(CollapseHelper.previousClass).toBe('one');
    });
    it('should set the accordion class for amount of time then switch it back to what it was', function(){
        CollapseHelper.currentClass = 'one';
        expect(CollapseHelper.currentClass).toBe('one');
        expect(CollapseHelper.previousClass).toBe('');

        CollapseHelper.setClassForDuration('two');
        expect(CollapseHelper.currentClass).toBe('two');
        expect(CollapseHelper.previousClass).toBe('one');
        $timeout.flush();

        expect(CollapseHelper.currentClass).toBe('one');
        expect(CollapseHelper.previousClass).toBe('one');
    });
    it('should set accordion class from levels', function(){
        expect(CollapseHelper.currentClass).toBe('');

        CollapseHelper.setClassFromLevel(0);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[0]);

        CollapseHelper.setClassFromLevel(1);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[1]);

        CollapseHelper.setClassFromLevel(2);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[2]);

        CollapseHelper.setClassFromLevel(3);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[3]);

        CollapseHelper.setClassFromLevel(4);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[4]);
    });
    it('should set accordion class from level then set it back after duration has passed', function(){
        expect(CollapseHelper.currentClass).toBe('');

        CollapseHelper.setClassFromLevelForDuration(0);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[0]);
        $timeout.flush();
        expect(CollapseHelper.currentClass).toBe('');

        CollapseHelper.setClassFromLevelForDuration(1);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[1]);
        $timeout.flush();
        expect(CollapseHelper.currentClass).toBe('');

        CollapseHelper.setClassFromLevelForDuration(2);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[2]);
        $timeout.flush();
        expect(CollapseHelper.currentClass).toBe('');

        CollapseHelper.setClassFromLevelForDuration(3);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[3]);
        $timeout.flush();
        expect(CollapseHelper.currentClass).toBe('');

        CollapseHelper.setClassFromLevelForDuration(4);
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[4]);
        $timeout.flush();
        expect(CollapseHelper.currentClass).toBe('');
    });
    it('should set accordion to error', function(){
        expect(CollapseHelper.currentClass).toBe('');
        CollapseHelper.error();
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[4]);
    });
    it('should set accordion to success', function(){
        expect(CollapseHelper.currentClass).toBe('');
        CollapseHelper.success();
        expect(CollapseHelper.currentClass).toBe(CollapseHelper.alertClasses[1]);
    })
});

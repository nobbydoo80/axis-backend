'use strict';

describe('Directive: SampleSet, DisplayHome, PreventClose', function(){

    // load the directive's module
    beforeEach(module('app'));

    var element,
    scope;

    beforeEach(inject(function($rootScope){
        scope = $rootScope.$new();
    }));

    it('should exist', inject(function($compile){
        element = angular.element('<sample-set></sampleset>');
        element = $compile(element)(scope);
        expect(!!element).toBe(true);

        element = angular.element('<li display-home></li>');
        element = $compile(element)(scope);
        expect(!!element).toBe(true);
    }));
    it('should prevent a close when accordion is open', inject(function($compile, CollapseHelper){
        spyOn(Event.prototype, 'stopPropagation');
        this.clickEvent = document.createEvent('CustomEvent');
        this.clickEvent.initCustomEvent('click', false, false, false);

        scope.accordion = CollapseHelper.get('panel');

        element = angular.element('' +
        '<accordion close-others="false">' +
        '   <accordion-group>' +
        '       <accordion-heading>' +
        '           <button prevent-close></button>' +
        '       </accordion-heading>' +
        '   </accordion-group>' +
        '</accordion>' +
        '');
        element = $compile(element)(scope);
        scope.$apply();

        expect(this.clickEvent.stopPropagation).not.toHaveBeenCalled();
        // accordion is not open.
        element.find('button')[0].dispatchEvent(this.clickEvent);
        expect(this.clickEvent.stopPropagation).not.toHaveBeenCalled();

        scope.accordion.open = true;
        element.find('button')[0].dispatchEvent(this.clickEvent);
        expect(this.clickEvent.stopPropagation).toHaveBeenCalled();


    }));
});

/**
 * Created by mjeffrey on 12/17/14.
 */

describe('Directive: detailContent / formContent', function(){

    // injected
    var $rootScope, $compile, HttpQueue, $q;
    // used
    var scope, detailElement, detailReplaceElement, formElement, formReplaceElement;

    // have to wrap the directives to we don't lose our reference when replacing.
    var detailString = "<h1><div detail-content></div><h1>";
    var detailReplaceString = "<h1><div detail-content='replace'></div><h1>";
    var formString = "<h1><div form-content></div><h1>";
    var formReplaceString = "<h1><div form-content='replace'></div><h1>";

    beforeEach(module('axis.region.region', 'axis.region.singleRegion'));
    beforeEach(inject(function(_$rootScope_, _$compile_, _HttpQueue_, _$q_){
        $rootScope = _$rootScope_;
        $compile = _$compile_;
        HttpQueue = _HttpQueue_;
        $q = _$q_;
    }));
    beforeEach(function(){
        newScope();
        scope.detailTemplateLoaded = jasmine.createSpy('detailTemplateLoaded');
        scope.formTemplateLoaded = jasmine.createSpy('formTemplateLoaded');
    });
    function newScope(){
        scope = $rootScope.$new();
        scope.regionObject = {form_template_url: 'form.html', detail_template_url: 'detail.html'};
        scope.region = {
            activeState: 'default',
            editing: function(){
                return this.activeState == 'edit';
            }
        }
    }
    function newElements(){
        detailElement = $compile(detailString)(scope);
        detailReplaceElement = $compile(detailReplaceString)(scope);
        formElement = $compile(formString)(scope);
        formReplaceElement = $compile(formReplaceString)(scope);
    }

    it('should exist', function(){
        newElements();
        expect(!!detailElement).toBe(true);
        expect(!!detailReplaceElement).toBe(true);
        expect(!!formElement).toBe(true);
        expect(!!formReplaceElement).toBe(true);
    });

    it('should setup a watcher', function(){
        newScope();
        spyOn(scope, '$watch').andCallThrough();

        expect(scope.$watch).not.toHaveBeenCalled();
        newElements();
        expect(scope.$watch).toHaveBeenCalled();
    });

    describe('template fetching', function(){
        var content;
        beforeEach(function(){
            content = angular.element('<span>This is content.</span>');
            spyOn(HttpQueue, 'addTemplateRequest').andCallFake(function(){
                return $q.when(content);
            });
        });
        describe('insert', function(){
            it('should fetch the detail template and insert it into the element when no longer editing', function(){
                scope.region.activeState = 'edit';  // calling region.edit will return true now.
                var el = $compile(detailString)(scope);

                expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalled();
                scope.region.activeState = 'default';  // calling region.edit will return false.
                expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalled();
                scope.$apply();
                expect(HttpQueue.addTemplateRequest).toHaveBeenCalled();

                expect(el.html()).toContain('span');
                expect(el.html()).toContain('detail-content');
                expect(el.html()).toContain(content.html());
            });
            it('should fetch the form template and insert it into the element when editing', function(){
                var el = $compile(formString)(scope);

                expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalled();
                scope.region.activeState = 'edit';  // calling region.edit will return true now.
                expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalled();
                scope.$apply();
                expect(HttpQueue.addTemplateRequest).toHaveBeenCalled();

                expect(el.html()).toContain('span');
                expect(el.html()).toContain('form-content');
                expect(el.html()).toContain(content.html());
            });
        });
        describe('replace', function(){
            it('should fetch and replace the detail template when no longer editing', function(){
                scope.region.activeState = 'edit';  // calling region.edit will return true now.
                // need to wrap the replace in an element so we don't lose our reference to it.
                var el = $compile(detailReplaceString)(scope);

                expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalled();
                scope.region.activeState = 'default';  // calling region.edit will return false.
                expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalled();
                scope.$apply();
                expect(HttpQueue.addTemplateRequest).toHaveBeenCalled();

                expect(el.html()).not.toContain('detail-content');
                expect(el.html()).toContain('span');
                expect(el.html()).toContain(content.html());
            });
            it('should fetch and replace the form template with editing', function(){
                var el = $compile(formReplaceString)(scope);

                expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalled();
                scope.region.activeState = 'edit';  // calling region.edit will return true now.
                expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalled();
                scope.$apply();
                expect(HttpQueue.addTemplateRequest).toHaveBeenCalled();

                expect(el.html()).not.toContain('form-content');
                expect(el.html()).toContain('span');
                expect(el.html()).toContain(content.html());
            });
        });
        it('should call the parent to let it know that the content was loaded', function(){
            expect(scope.detailTemplateLoaded).not.toHaveBeenCalled();
            expect(scope.formTemplateLoaded).not.toHaveBeenCalled();

            newElements();

            expect(scope.detailTemplateLoaded).not.toHaveBeenCalled();
            expect(scope.formTemplateLoaded).not.toHaveBeenCalled();

            scope.$apply();

            expect(scope.detailTemplateLoaded).toHaveBeenCalled();
            expect(scope.formTemplateLoaded).not.toHaveBeenCalled();

            scope.region.activeState = 'edit';  // calling region.edit will return true now.
            expect(scope.formTemplateLoaded).not.toHaveBeenCalled();
            scope.$apply();
            expect(scope.formTemplateLoaded).toHaveBeenCalled();
        });
        it('should not make a request if region is still editing', function(){
            var count = 0;
            spyOn(scope.region, 'editing').andCallFake(function(){
                return ++count%2 ? 1 : 2;
            });

            expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalledWith(scope.regionObject.detail_template_url);

            newElements();
            expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalledWith(scope.regionObject.detail_template_url);

            scope.region.activeState = 'something';
            scope.$apply();
            expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalledWith(scope.regionObject.detail_template_url);
        });
        it('should not set up a watcher if there is no form template', function(){
            spyOn(scope, '$watch').andCallThrough();

            expect(scope.$watch.callCount).toBe(0);
            newElements();
            expect(scope.$watch.callCount).toBe(4);

            scope.$watch.callCount =0;
            delete scope.regionObject['form_template_url'];

            expect(scope.$watch.callCount).toBe(0);
            newElements();
            expect(scope.$watch.callCount).toBe(2); // two for the 2 detail elements
        });
        it('should not make a request if region is not editing', function(){
            var count = 0;
            spyOn(scope.region, 'editing').andCallFake(function(){
                return ++count%2 ? null : undefined;
            });

            expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalledWith(scope.regionObject.form_template_url);

            newElements();
            expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalledWith(scope.regionObject.form_template_url);

            scope.region.activeState = 'something';
            scope.$apply();
            expect(HttpQueue.addTemplateRequest).not.toHaveBeenCalledWith(scope.regionObject.form_template_url);
        });
    });
});

/**
 * Created by mjeffrey on 8/12/14.
 */
var d = angular.module('axis.directives', []);

function setDataTransferData(event, sampleSetId, home){
    var data = [sampleSetId||'-', home||'-'].join('.');
    if(event.originalEvent){
        event.originalEvent.dataTransfer.setData('text', data);
    } else {
        event.dataTransfer.setData('text', data);
    }
}
function getDataTransferData(event){
    var data = event.dataTransfer.getData('text');
    var parts = data.split('.');
    return {
        sampleSetId: parts[0],
        home: parts[1]
    };
}

d.directive('sampleSet', function(ExamineSettings){
    return {
        restrict: 'E',
        controller: 'SampleSetController',
        templateUrl: ExamineSettings.static_url + 'templates/sample_set.html',
        link: function(scope, elementm, attrs){
            if(angular.isDefined(attrs.accordionOpen)){
                scope.accordion.open = attrs.accordionOpen;
            }
            if(angular.isDefined(attrs.dragNDrop)){
                scope.flags.dragNDrop = scope.$eval(attrs.dragNDrop);
            }
        }
    };
});

d.directive('displayHome', function($log, ExamineSettings){
    return {
        restrict: 'A',
        controller: 'DisplayHomeController',
        templateUrl: ExamineSettings.static_url + 'templates/display_home.html',
    }
});

d.directive('draggable', function($log, $timeout, SampleSetProperties){
    return {
        link: function(scope, element){
            scope.changeDrag = function(state){
                // NOTE: $timeout prevents chrome from loosing a drag event when the page height changes.
                $timeout(function(){
                    SampleSetProperties.changeDrag(state);
                }, 100);
            };

            var el = element[0];
            if(scope.flags.dragNDrop && !scope.home.is_locked) el.draggable = true;

            el.addEventListener('dragstart', function(e){
                $log.debug("dragstart from angular elemnt");
                e.dataTransfer.effectAllowed = 'move';
                setDataTransferData(e, scope.sampleSet.name, scope.home.home_status_id);
                this.classList.add('drag');
                scope.$apply(function(){
                    scope.changeDrag(true);
                });
                return false;
            }, false);

            el.addEventListener('dragend', function(e){
                $log.debug("dragend from angular element");
                this.classList.remove('drag');
                scope.$apply(function(){
                    scope.changeDrag(false);
                });
                return false;
            }, false);

        }
    }
});

d.directive('questionTick', function($rootScope, QuestionProperties, CustomEvents){
    /**
     * Displays a little box representing a question connected to a home.
     * Question States:
     *  Green : has answer
     *  Gray : no answer
     *  yellow : being hovered
     */
    return {
        restrict: 'A',
        link: function(scope, element, attributes){

            scope.popoverText = scope.questionPopoverText(scope.question);
            if(!scope.home.is_test_home){
                // setup dynamic listener that only reacts to homes being moved to or from this sample set.
                var listener = scope.sampleSet.name + CustomEvents.suffixes.UPDATE_ANSWERS;
                $rootScope.$on(listener, function(){
                    scope.popoverText = scope.questionPopoverText(scope.question);
                });
            }

            element.on('mouseenter', function(){
                QuestionProperties.setCurrentQuestion(scope.question_id);
                element.addClass('hover');
                scope.$apply();
            });

            element.on('mouseleave', function(){
                QuestionProperties.setCurrentQuestion(null);
                element.removeClass('hover');
                scope.$apply();
            });

        }
    }
});

d.directive('droppable', function($log, SampleSetProperties){
    return {
        link: function(scope, element){
            var el = element[0];

            el.addEventListener('dragover', function(e){
                e.dataTransfer.dropEffect = 'move';
                if(e.preventDefault) e.preventDefault();
                this.classList.add('over');
                return false;
            }, false);

            el.addEventListener('dragenter', function(e){
                if(e.preventDefault) e.preventDefault();
                this.classList.add('over');
                return false;
            }, false);

            el.addEventListener('dragleave', function(e){
                this.classList.remove('over');
                return false;
            }, false);

            el.addEventListener('drop', function(e){
                $log.debug("dropping element");
                if(e.stopPropagation) e.stopPropagation();

                this.classList.remove('over');

                var _eventData = getDataTransferData(e);
                var ID = _eventData.home;
                var exSampleSetId = _eventData.sampleSetId;
                var newSampleSetId = scope.sampleSet ? scope.sampleSet.name : null;

                // this abomination is here to disable datatable homes that are dragged into samplesets.
                $(".popover-dismiss[home_id='"+ID+"']").attr('disabled', true);

                scope.$apply(function(){
                    if(!newSampleSetId){
                        SampleSetProperties.addBlankSampleSetWithHome(ID, exSampleSetId);
                    } else {
                        SampleSetProperties.moveHome(ID, exSampleSetId, newSampleSetId);
                    }
                    SampleSetProperties.changeDrag(false);
                });

                return false;
            }, false);
        }
    }
});

d.directive('preventClose', function($timeout){
    return {
        restrict: 'A',
        link: function(scope, element, attributes){
            element.on('click', function(e){
                if(scope.accordion.open && e){
                    $timeout(function(){
                        scope.accordion.open = true;
                    }, 0);
                }
            })
        }
    }
});

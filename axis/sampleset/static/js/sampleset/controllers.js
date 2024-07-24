/**
 * Created by mjeffrey on 8/12/14.
 */
var c = angular.module('axis.controllers', []);

c.controller('AppController', function($rootScope, $scope, $log, $timeout, $http, $location, SampleSetAPI, HomeAPI, SampleSetProperties, HomeProperties, CustomEvents, LocationService){
    $scope.viewingSampleSets = SampleSetProperties.getObject().viewingSampleSets;
    $scope.ssProperties = SampleSetProperties.getObject();

    $scope.showHelp = localStorage.getItem('showHelp') === 'true';
    $scope.$watch('showHelp', function(newValue, oldValue){
        localStorage.setItem('showHelp', newValue);
    });

    $scope.init = function(){
        /**
         Grabs sample sets from GET params and angular GET params
         Fills the List of sample sets.
         Get summaries of initial sample sets being viewed
         */
        LocationService.getIdsFromUrl();

        angular.forEach(LocationService.getSampleSetIds(), function(id){
            SampleSetProperties.addSampleSet(id);
        });
    };
    $scope.init();

    $scope.addSampleSet = function(id){
        /**
         * called from jquery for adding sample sets from datatables.
         */
        for(var i = 0; i < $scope.viewingSampleSets.length; i++){
            var obj = $scope.viewingSampleSets[i];
            if(obj.id == id){
                $rootScope.$broadcast(CustomEvents.OPEN_ACCORDION, id);
                return;
            }
        }
        SampleSetProperties.addSampleSet(id);
        LocationService.addId(id);
    };

    $scope.removeSampleSet = function(ss, changed){
        var confirmed = true;
        if(changed){
            confirmed = confirm("You have unsaved changes. Do you want to discard those?");
        }

        if(confirmed){
            $log.info('Removing', ss.name, 'from page.');
            if(ss.id) LocationService.removeId(ss.id);
            SampleSetProperties.removeSampleSet(ss.name);
        }
    };

    $scope.removeHome = function(home, ss){
        $log.info('removing', home.name, 'from', ss);
        SampleSetProperties.removeHome(home.home_status_id, ss, true);
    };

    $scope.startDragging = function(){
        /**
         * called from jquery listener for adding homes from datatables.
         */
        $timeout(function(){
            SampleSetProperties.changeDrag(true);
        }, 100)
    };

    $scope.cancelDragging = function(){
        $timeout(function(){
            SampleSetProperties.changeDrag(false);
        }, 100)
    };

    $scope.makeEmptySampleSet = SampleSetProperties.addBlankSampleSet;

    $scope.makeSampleSetWithHome = SampleSetProperties.addBlankSampleSetWithHome;

    $scope.getViewingHomeIds = HomeProperties.getCachedHomesIds;

    $scope.getViewingHomeIdsAndSampleSets = SampleSetProperties.getSampleSetHomeIds;

});

c.controller('SampleSetController', function($rootScope, $scope, $q, $sce, $timeout, $log, SampleSetAPI, QuestionProperties, SampleSetProperties, CustomEvents, CollapseHelper, LocationService){
    /**
     * NEVER set anything to $scope.sampleSet because it will break parent scope relationship.
     * You may however set attributes OF $scope.sampleSet.
     * TODO: update the contributing answers list when a sampleset is updated.
     */

    $scope.accordion = CollapseHelper.get('panel');
    $scope.notification = CollapseHelper.get('label');
    $scope.certifyUrl = '';
    $scope.messages = [];
    $scope.shared = SampleSetProperties.getObject();
    $scope.api = {};
    $scope.flags = {
        isDeleting: false,
        showHomeDetail: false,
        isCertifiable: false,
        changed: false,
        isProcessing: false,
        dragNDrop: true,
        editAltName: false,
        dropDownOpen: false
    };

    $scope.levels = {
        SUCCESS: 1,
        INFO: 2,
        WARNING: 3,
        ERROR: 4
    };

    $scope.timedAnalyze = null;

    var init = function(){
        if($scope.sampleSet.test_homes.length || $scope.sampleSet.sampled_homes.length){
            $scope.getCertifyUrl();
            $scope.api.analyze();
        }
    };

    $rootScope.$on($scope.sampleSet.name+CustomEvents.suffixes.HOME_MOVE, function(){
        $scope.flags.changed = true;
        $scope.api.analyze();
    });

    $rootScope.$on(CustomEvents.OPEN_ACCORDION, function(event, id){
        /**
         * called from application controller if it is decided that the Sample Set
         * already exists on the page.
         */
        if($scope.sampleSet.id == id){
            $scope.accordion.show();
            $scope.accordion.setClassFromLevelForDuration($scope.levels['INFO']);
        }
    });

    $scope.getCertifyUrl = function(){
        if($scope.sampleSet.sampled_homes.length){
            $scope.certifyUrl = '/home/' + $scope.sampleSet.sampled_homes[0].home_status_id + '/certify/';
        } else {
            $scope.certifyUrl = '/home/' + $scope.sampleSet.test_homes[0].home_status_id + '/certify/';
        }
    };

    $scope.getAlertLevel = function(level){
        var classes = {
            INFO: 'info',
            WARNING: 'warning',
            ERROR: 'danger'
        };
        return classes[level.toUpperCase()];
    };

    $scope.closeDropDown = function(e){
        e.preventDefault();
        e.stopPropagation();
        $scope.flags.dropDownOpen = !$scope.flags.dropDownOpen;
    }

    $scope.api.analyze = function(e){
        if($scope.timedAnalyze) $timeout.cancel($scope.timedAnalyze);

        $scope.timedAnalyze = $timeout(function(){
            $scope.flags.isProcessing = true;

            $log.debug('Analyzing Sample Set', $scope.sampleSet.name);
            SampleSetAPI.analyze($scope.sampleSet)
                .then($scope.api.analyze_success, $scope.api.analyze_error)
                .finally($scope.api.generic_finally);
        }, 1000);
    };

    $scope.api.analyze_success = function(data){
        $scope.sampleSet.builder_name = data.builder;
        $scope.flags.isCertifiable = data.is_certifiable;
        $scope.messages = data;
        var level = 0;
        if('messages' in data && data.messages.length){
            for(var i = 0; i < data.messages.length; i++){
                var obj = data.messages[i];
                level = $scope.levels[obj.level] > level ? $scope.levels[obj.level] : level;
            }
            $scope.accordion.setClassFromLevelForDuration(level);
            $scope.notification.setClassFromLevel(level);
        }
        $scope.sampleSet.isMetroSampled = data.is_metro_sampled;
    };

    $scope.api.analyze_error = function(data, code){
        // TODO: surface some kind of message for server errors
        if($scope.sampleSet.test_homes.length || $scope.sampleSet.sampled_homes.length){
            $log.error('analyze error');
            $scope.accordion.error();
            $scope.notification.error();
            $scope.messages = data;
        }
    };

    $scope.api.commit = function(e){
        $scope.flags.isProcessing = true;

        $log.info('Saving Sample Set', $scope.sampleSet.name, 'in current state.');
        SampleSetAPI.commit($scope.sampleSet)
            .then($scope.api.commit_success, $scope.api.commit_error)
            .finally($scope.api.generic_finally);
    };

    $scope.api.commit_success = function(data){
        $scope.sampleSet.id = data.sampleset;
        $scope.sampleSet.eep_program = data.eep_program;
        $scope.flags.isCertifiable = data.is_certifiable;
        $scope.messages = data;
        $scope.flags.changed = false;
        $scope.flags.editAltName = false;
        LocationService.addId($scope.sampleSet.id);
        $scope.accordion.success();
    };

    $scope.api.commit_error = function(data, code){
        $log.error('commit error');
        $scope.accordion.error();
    };

    $scope.api.advance = function(e){

        if($scope.flags.changed){
            alert("Please commit the current state of the Sample Set before advancing.");
            return;
        }

        var confirmed = confirm('Are you sure you want to advance this Sample Set to the next stage?');

        if(confirmed){
            $log.info('Advancing Sample Set', $scope.sampleSet.name, 'to next stage.');
            $scope.flags.isProcessing = true;

            SampleSetAPI.advance($scope.sampleSet.id)
                .then($scope.api.advance_success, $scope.api.advance_error)
                .finally($scope.api.advance_finally);
        }
    };

    $scope.api.advance_success = function(data){
        $scope.accordion.success();
    };

    $scope.api.advance_error = function(data, code){
        $log.error("problem advancing state");
        $scope.accordion.error();
    };

    $scope.api.advance_finally = function(){
        $scope.flags.isProcessing = false;
        SampleSetProperties.addSampleSet($scope.sampleSet.id);
    };

    $scope.api.generic_finally = function(){
        $scope.flags.isProcessing = false;
        $scope.getCertifyUrl();
    };

    $scope.certify = function(e){
        /**
         * Angular Accordion doesn't like having links inside a collapse.
         * So we need to trigger it from the window.
         * TODO: make sure this works in all browsers.
         */
        window.open($scope.certifyUrl, '_blank');
    };

    $q.when($scope.sampleSet).finally(function(){
        init();
    });
});

c.controller('DisplayHomeController', function($scope, $q, $log, $timeout, $modal, QuestionProperties, SampleSetProperties){
    /**
     * This Controller is used by both displayHome and draggable directives.
     */
    $scope.questions = QuestionProperties.getObject();
    $scope.availableTestAnswers = SampleSetProperties.getObject().availableTestAnswers;
    $scope.answers = {};

    $scope.popoverText = {
        provided: 'Answer provided by home.',
        contributed: 'Answer contributed from Sampling',
        receiving: 'Receiving answer upon advancement',
        unanswered: 'Unanswered',
        failing: 'Answer considered failing'
    };

    var init = function(){
        $scope.answers = QuestionProperties.cleanAnswers($scope.home);
    };

    $scope.getGettingAnswer = function(question){
        if(!question.answer_id){
            try{
                return !!$scope.availableTestAnswers[$scope.sampleSet.name].questions[question.question_id];
            }catch(e){
                // the sampleset has no test homes
                return false;
            }
        }
        return false;
    };

    $scope.questionPopoverText = function(question){
        var message = $scope.popoverText['unanswered'];
        if(question.answer_id){
            // answered, but where from.
            if(question.type == 'source'){
                message = $scope.popoverText['provided'];
            } else if(question.type == 'failing'){
                message = $scope.popoverText['failing'];
            } else {
                message = $scope.popoverText['contributed'];
            }
        } else {
            // not answered, will it be getting an answer?
            if($scope.getGettingAnswer(question)){
                message = $scope.popoverText['receiving'];
            }
        }
        return message;
    };

    /**
     * When question is brought back in uncomment this.
    $scope.showQuestion = function(id){
        $modal.open({
            size: 'lg',
            controller: 'ModalController',
            resolve: {
                question: function(){
                    return QuestionAPI.get({question_id: id, home_status_id: $scope.home.home_status_id})
                }
            },
            templateUrl: '/static/templates/question_modal.html'
        })
    };
     */

    $q.when($scope.home).finally(function(){
        init();
    })
});

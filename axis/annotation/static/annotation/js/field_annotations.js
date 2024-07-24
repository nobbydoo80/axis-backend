angular.module('axis.annotations', [])
.value('ReviewPopoverSettings', {
    'titlePattern': '<span><b>[[ vm.fieldName | humanize ]]</b>: Review</span>',
    'canTransitionState': false  // Don't use state transitioning checkbox on overlay by default
})

.config(function($httpProvider){
    /*
    Intercept the responses. If they're html add a field-review attr to all the axis-fields.
     */
    $httpProvider.defaults.transformResponse.push(function(value){
        if(angular.isString(value)){
            value = $(value);
            value.find('axis-field').each(function(index, el){
                $(el).attr('field-review', '');
            });
            value = $('<div>').append(value).html();
        }
        return value
    });
})


.factory('ApiTypeNames', function(){
    /**
     * This factory is used in the FieldReviews factory to clean type names that have
     * models with api endpoints different than their slugified model name.
     *
     * @example:
     *  AnnotationTypeNames('agreement')        -> 'agreementinformation'
     *  AnnotationTypeNames('subdivision')      -> 'subdivsion'
     *
     *  annotationTypeNames('agreement', true)  -> 'agreement'
     */

    var typeNames = {
        'builder_contact': 'buildercontact',
        'base_floorplan': 'basefloorplan'
    };

    return function getTypeName(typeName, reverse){
        var lookup = null;
        if(angular.isUndefined(reverse)){
            lookup = typeNames;
        } else {
            lookup = swap(typeNames);
        }

        if(lookup.hasOwnProperty(typeName)){
            return lookup[typeName];
        } else {
            return typeName;
        }
    };

    function swap(obj){
        var temp = {};
        for(var key in obj){
            temp[obj[key]] = key;
        }
        return temp;
    }

})


.factory('FieldReviews', function($q, $http, $interpolate, $timeout, ApiTypeNames){
    var postEndpoint = '/api/v2/annotation/';
    var getEndpoint = '/api/v2/[[ type_name ]]/field-annotations/[[ object_id ]]/';
    var fetchedEndpoints = {};
    var reviews = {};

    return {
        addReview: addReview,
        get: getReviews,
        prepReviewObject: prepReviewObject,
        reviews: reviews
    };

    function addReview(reviewObj){
        return _addReview(reviewObj).success(_.partial(storeReview, reviewObj.type_name));
    }

    function getReviews(typeName, objId){
        var url = $interpolate(getEndpoint)({type_name: ApiTypeNames(typeName), object_id: objId});

        if(fetchedEndpoints.hasOwnProperty(url)) return fetchedEndpoints[url];

        var ajax = $http.get(url).success(function(data){
            angular.forEach(data.field_annotations, function(annotation){
                storeReview(typeName, annotation);
            });
        }).finally(function(){
            $timeout(function(){
                delete fetchedEndpoints[url];
            }, 5000);
        });

        fetchedEndpoints[url] = ajax;
        return ajax;
    }
    function prepReviewObject(typeName, objId, fieldName){
        if(!reviews.hasOwnProperty(typeName)){
            reviews[typeName] = {};
        }

        if(!reviews[typeName].hasOwnProperty(objId)){
            reviews[typeName][objId] = {};
        }

        if(!reviews[typeName][objId].hasOwnProperty(fieldName)){
            reviews[typeName][objId][fieldName] = [];
        }
    }
    function _addReview(data){
        return $http.post(postEndpoint, data);
    }
    function storeReview(typeName, data){
        var objId = data.object_id,
            fieldName = data.field_name;
        typeName = ApiTypeNames(typeName, true);

        prepReviewObject(typeName, objId, fieldName);
        reviews[typeName][objId][fieldName].push(data);
        reviews[typeName][objId][fieldName] = _.uniq(reviews[typeName][objId][fieldName], 'id');
    }

})

.directive('reviewSection', function($rootScope, $compile){
    return {
        restrict: 'A',
        compile: function(element, attrs){
            angular.forEach(element.find('axis-field'), function(el){
                $(el).attr('field-review', '');
            });
        }
    }
})

.directive('fieldReview', function(){
    return {
        restrict: 'A',
        compile: function(element, attrs){
            var label = element.find('label');
            label.append('<a review-popover></a>');
        }
    }
})

.directive('reviewPopover', function($compile, $timeout, ReviewPopoverSettings){
    return {
        restrict: 'EA',
        scope: true,
        replace: true,
        /* '<a ng-show="$root.review">' + */
        template: '<a>' +
                        '<i class="fa f-fw fa-comments cursor-pointer text-muted"></i>' +
                        ' <span class="label label-default" ng-class="{\'label-success\': vm.processing == 2, \'label-danger\': vm.processing == 3}" ng-show="vm.reviews.length || vm.processing">' +
                            '<i class="fa fa-spin fa-spinner" ng-if="vm.processing == 1"></i>' +
                            '<i class="fa fa-check" ng-if="vm.processing == 2"></i>' +
                            '<i class="fa fa-times" ng-if="vm.processing == 3"></i>' +
                            '<span ng-if="!vm.processing">[[ vm.reviews.length ]]</span>' +
                        '</span>' +
                  '</a>',
        controllerAs: 'vm',
        controller: function($scope, $attrs, $interpolate, $element, FieldReviews, ApiTypeNames, Actions, RegionService){
            var ctrl = this;

            ctrl.reviews = [];
            ctrl.models = {
                //notifyBuilder: false,
                //notifyRater: false,
                //content: ''
                object_id: $scope.regionObject.object.id,
                content_type: ApiTypeNames($scope.regionObject.type_name),
                type_name: $scope.regionObject.type_name,
                type: 'field-annotation',
                field_name: getFieldName(),
            };
            angular.extend(ctrl.models, ReviewPopoverSettings.modelExtension);

            ctrl.model_options = {
                debounce: 500
            };
            ctrl.processing = 0;

            ctrl.close = close;
            ctrl.send = send;

            // helpers
            ctrl.typeName = $scope.regionObject.type_name;
            ctrl.objId = $scope.regionObject.object.id;
            ctrl.fieldName = getFieldName();

            init();

            function init(){
                if(ctrl.objId){
                    FieldReviews.get(ctrl.typeName, ctrl.objId).then(setReviews);
                }
            }
            function setReviews(){
                // Make sure it has an object to listen to even if there aren't any
                // reviews for it yet.
                FieldReviews.prepReviewObject(ctrl.typeName, ctrl.objId, ctrl.fieldName);
                ctrl.reviews = FieldReviews.reviews[ctrl.typeName][ctrl.objId][ctrl.fieldName];
            }
            function getFieldName(){
                if($scope.field){
                    return $scope.field.field_name;
                } else if($attrs.fieldName){
                    return $interpolate($attrs.fieldName)($scope);
                } else {
                    throw new Error("<review-popover> requires a field in scope or field-name attributes.");
                }
            }

            function close(){
                ctrl.models.content = '';
                $($element).popover('hide');
            }
            function send(){
                console.log(ctrl.models);
                ctrl.processing = 1;
                FieldReviews.addReview(ctrl.models).then(failState(ctrl.models.failState)).then(sendSuccess, sendError);
                $($element).popover('hide');
            }
            function sendSuccess(){
                ctrl.processing = 2;
                $timeout(function(){
                    ctrl.processing = 0;
                }, 1000);
            }
            function sendError(){
                ctrl.processing = 3;
                $timeout(function(){
                    ctrl.processing = 0;
                }, 1000);
            }
            function failState(correctionRequired){
                if(!correctionRequired) return angular.identity;
                return function _failState(){
                    var regionObject = RegionService.getRegionFromTypeName('agreement')[0];
                    return Actions.callMethod('failState', regionObject);
                }
            }
        },
        compile: function(){
            var reviews = '' +
                '<ul class="list-group" ng-show="vm.reviews.length">' +
                    '<li class="list-group-item disabled">' +
                        '<h5 class="list-group-item-heading">Notes</h5>' +
                    '</li>' +
                    '<li class="list-group-item" ng-repeat="item in vm.reviews">' +
                        '<h5 class="list-group-item-heading">[[ item.user ]]: [[ item.created_on | date:"MM/dd/yyyy" ]]</h5>' +
                        '<p class="list-group-item-text">[[ item.content ]]</p>' +
                    '</li>' +
                '</ul>',
                changeState = '' +
                    '<div class="form-group">' +
                        '<label><input type="checkbox" ng-model="vm.models.failState" ng-model-options="vm.model_options"/> Send to Corrections Required</label>' +
                    '</div>',
                textArea = '' +
                    '<div class="form-group">' +
                        '<label>Note:</label>' +
                        '<textarea class="form-control"cols="30" rows="2" ng-model="vm.models.content" ng-model-options="vm.model_options"></textarea>' +
                    '</div>',
                footer = '' +
                    '<div class="modal-footer">' +
                        '<button class="btn btn-default" role="button" ng-click="vm.close()">Cancel</button>' +
                        '<button class="btn btn-primary" role="button" ng-click="vm.send()">Submit</button>' +
                    '</div>';

            var compiledBody = $compile([
                '<div class="row"><div class="col-md-12">', reviews,
                // Don't show send to corrections checkbox if user can't do that.
                ReviewPopoverSettings.canTransitionState ? changeState : '',
                textArea, footer, '</div></div>'
            ].join(''));
            var compiledTitle = $compile(ReviewPopoverSettings.titlePattern);
            var popoverSettings = {
                trigger: 'click',
                html: true,
                placement: 'right',
                container: 'body'
            };

            return function postLink(scope, element){
                compiledBody(scope, function(element, _scope){
                    popoverSettings['content'] = element;
                });
                compiledTitle(scope, function(element, _scope){
                    popoverSettings['title'] = element;
                });
                $(element).popover(popoverSettings)
            }
        }
    }
})

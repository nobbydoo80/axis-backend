/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.fields.helpers.tab')
.directive('tabHelper', function($rootScope, $parse, TabService){
    return {
        restrict: 'A',
        compile: function(el, attrs){
            var endpoint_name = attrs.endpoint.split('.').pop();
            attrs.$set('active', "tabsActive['"+endpoint_name+"'].active");

            // NOTE: ui.bootstrap tab directive stops click propagations.
            // Instead of being able to set ui-sref we hook into the on Select callback they offer.
            //attrs.$set('ui-sref', attrs.endpoint);
            attrs.$set('select', 'go("'+attrs.endpoint+'")');
            var disabled = $parse(attrs.disabled)($rootScope);
            TabService.addTab(attrs.endpoint, disabled);

            return function postLink(scope, element, attrs){
                if(attrs.disabled){
                    var unwatch = scope.$watch(function(){
                        return !!scope.$eval(attrs.disabled)
                    }, function(newVal, oldVal){
                        if(newVal !== oldVal){
                            TabService.updateDisableListener(attrs.endpoint, newVal);
                            unwatch();
                        }
                    });
                }
                scope.go = TabService.go;
            }
        }
    }
});

angular.module('axis.fields.helpers.fileField')
.directive('fileFieldHelper', function($q, $timeout, Actions){
    return {
        restrict: 'EA',
        scope: true,
        link: function(scope, element, attrs){
            var field_name = scope.$eval(attrs.fileFieldHelper);
            const doAutoSave = scope.$eval(attrs.autoSave);
            scope.raw_key = field_name + '_raw';
            scope.name_key = field_name + '_raw_name';
            scope.highlightDropArea = false;
            scope.fileProgress = null;
            if(scope.field.widget.attrs.multiple){
                element.attr('multiple', true);
            }

            const loadFile = (f, index) => {
                var deferred = $q.defer();
                var fileName = f.name;
                var reader = new FileReader();

                reader.onload = function(file){
                    console.groupCollapsed('file');
                    console.log('name', name);
                    console.log('file', file);
                    console.groupEnd('file');

                    var raw = getRaw(file, fileName);

                    if(index === 0){
                        injectValues(scope, scope.regionObject, raw, fileName);
                        scope.$apply()
                        deferred.resolve();
                        if (doAutoSave) {
                            Actions.callMethod('save', scope.regionObject).then(() => {
                                return Actions.callMethod('exit', scope.regionObject);
                            });
                        }
                    } else {
                        scope.regionSet.fetchNewRegion().then(function(regionObject){
                            // set values in new regionObject
                            // then update the FileInput to show existing when its available
                            scope.fileProgress = null
                            injectValues(scope, regionObject, raw, fileName);
                            removeWatcherWhenAny(scope, waitForElement(regionObject), markFileAsExisting(regionObject));
                            deferred.resolve();
                            if (doAutoSave) {
                                Actions.callMethod('save', regionObject).then(() => {
                                    return Actions.callMethod('exit', regionObject);
                                });
                            }
                        });
                    }
                };

                reader.readAsDataURL(f);
                return deferred.promise;
            }
            function getRaw(file, name){
                /**
                 * Cleans the base64 version for file types that don't provide
                 * a MimeType. Mostly BLG files.
                 */
                var raw = file.target.result;
                var extension = name.split('.').pop();
                if(raw.indexOf(':;') > -1){
                    raw = raw.replace(':;', ':application/' + extension + ';');
                } else if(raw.indexOf('octet-stream') > -1 && extension == 'blg'){
                    raw = raw.replace('octet-stream', extension);
                }
                return raw;
            }
            function injectValues(scope, regionObject, raw, file_name){
                regionObject.object[scope.raw_key] = raw;
                regionObject.object[scope.name_key] = file_name;
                regionObject.fields[scope.field.prefixed_name].value = file_name;
            }

            const dropArea = attrs.dropArea || 'axis-field';
            $(element).closest(dropArea).on('dragover dragenter', (e) => {
              e.stopPropagation();
              e.preventDefault();
              scope.highlightDropArea = true
            }, false);
            $(element).closest(dropArea).on('dragleave', (e) => {
              e.stopPropagation();
              e.preventDefault();
              scope.highlightDropArea = false
            }, false);
            $(element).closest(dropArea).on('drop', (e) => {
                scope.highlightDropArea = false
                scope.fileProgress = 0
                e.stopPropagation();
                e.preventDefault();
                var promises = angular.forEach(e.originalEvent.dataTransfer.files, loadFile);
                $q.all(promises).then(() => {
                    $timeout(() => console.log('Triggering $scope.$apply()'), 1000)
                });
            });
            element.on('change', (e) => {
                var promises = angular.forEach(e.target.files, loadFile)
                $q.all(promises).then(function(){
                    // Just need a scope.$apply() to run later
                    // This causes any side effects from having multiple documents
                    // to take effect. In this case, the "save all" button shows up.
                    // Anything less than 1 second doesn't seem to work :/
                    $timeout(() => console.log('Triggering $scope.$apply()'), 1000)
                });
            })
        }
    }
});

angular.module('axis.fields.helpers.select2')
.directive('uiSelectHelper', function($sce, $http, $timeout){
    return {
        restrict: 'A',
        require: 'uiSelect',
        link: function(scope, element, attrs, uiSelectController){

            function init(){
                if(!isGrouped(scope.field)){
                    $timeout(function(){
                        element.find('ul.select2-results').removeAttr('group-by');
                        scope.$select.isGrouped = false;
                    })
                }
                init_values();
                init_choices();
            }
            function isGrouped(field){
                // Field is grouped if its not hidden field and the ajax results are to be processed.
                if(field.widget.widget_id === undefined){
                    return false;
                }
                return true;
            }
            function init_values(){
                // push the field values into the options.
                if(scope.field.value){
                    if(angular.isArray(scope.field.value)){
                        angular.forEach(scope.field.value, function(value, index){
                            var item = {id: value, text: scope.field.value_label[index]};
                            scope.selectOptions.push(item);
                        })
                    } else {
                        var item = {id: scope.field.value, text: scope.field.value_label};
                        scope.selectOptions.push(item);
                    }
                    if(!scope.regionObject.object[scope.field.field_name]){
                        scope.regionObject.object[scope.field.field_name] = scope.field.value;
                    }
                }
            }
            function init_choices(){
                // push the choices into the options
                if(scope.field.widget.choices && scope.field.widget.choices.length){
                    angular.forEach(scope.field.widget.choices, function(value, index, obj){
                        var item = {id: value[0], text: value[1]};
                        if(angular.isUndefined(_.find(scope.selectOptions, item))){
                            scope.selectOptions.push(item);
                        }
                    });
                }
            }
            function processResults(options, noResults){
                angular.forEach(options, function(option){
                    option['type'] = 'Select from existing:'
                });
                options.unshift({text: scope.$select.search, id: scope.$select.search, type: 'Create New:'});
                if (noResults) {
                    options.unshift({text: 'No Results...', id: null, type: 'Select from existing:'});
                }
                return options;
            }
            function refreshField(term){
                if(term){
                    var params = {term: term, page: 1, field_id: scope.field.widget.widget_id};
                    return $http.get('/select2/fields/auto.json', {params: params}).then(function(response){
                        if(response.data.results.length){
                            scope.selectOptions = response.data.results;
                        } else {
                            scope.selectOptions = [];
                        }
                        if(scope.field.widget.relationship_add_url !== null){
                            scope.selectOptions = processResults(scope.selectOptions, response.data.results.length === 0);
                        }
                    })
                }
            }

            scope.refreshField = refreshField;
            scope.trustAsHtml = $sce.trustAsHtml;
            scope.selectOptions = [];

            init();
        }
    }
})
.directive('uiSelectRelationship', function($log){
    return {
        restrict: 'A',
        require: 'uiSelect',
        link: function(scope, element, attrs, uiSelectController){

            function choiceSelected($item, $model){
                // Create New choices have same text and id to avoid reselecting null values.
                if(!angular.equals($item.text, $item.id) && $item.id !== null){
                    if(scope.field.widget.relationship_add_url){

                        var form = $("<form method='post'><input name='object' /><input name='go_to_detail' /></form>");
                        form.attr('action', scope.field.widget.relationship_add_url);
                        form.append($('input[name=csrfmiddlewaretoken]').clone());
                        form.find('input[name=object]').val($model);
                        form.appendTo('body');
                        form.submit();
                    }
                }
                scope.onChange({
                    $item: $item,
                    $model: $model
                });
            }

            scope.choiceSelected = choiceSelected;
        }
    }
});

angular.module('axis.fields.helpers.multiSelect')
.directive('multiSelectHelper', function(){
    return {
        restrict: 'A',
        link: function(scope, element, attrs){

            function init(){
                init_choices(init_values());
            }
            function init_values(){

                // check the region object to ensure we have no value.
                if(!scope.field.value) {
                    scope.field.value = scope.regionObject.object[scope.field.field_name];
                }

                if(scope.field.value){
                    return _.object(ensureArray(scope.field.value));
                }
                return {};
            }
            function init_choices(selected){

                var options = [];

                // push the choices into the options
                if(scope.field.widget.choices && scope.field.widget.choices.length){
                    angular.forEach(scope.field.widget.choices, function(value, index, obj){
                        if(value[0] === ''){
                            // blank strings for default none choices mess with
                            // fields that offer false as an option.
                            value[0] = null;
                        }

                        var item = makeItem(value[0], value[1], (value[0] in selected));

                        options.push(item);
                    });
                }
                scope.selectOptions = options;
            }
            function multipleSelect(){
                var values = [];
                angular.forEach(scope.tempOutputList, function(obj){
                    values.push(obj.id);
                });
                scope.regionObject.object[scope.field.field_name] = values;
            }
            function singleSelect(){
                scope.regionObject.object[scope.field.field_name] = scope.tempOutputList.length ? scope.tempOutputList[0].id : null;
            }
            function singleSelectModeReverseWatch(newVal, oldVal){
                _.forEach(scope.selectOptions, function(obj){
                    obj.selected = (obj.id == newVal);
                })
            }

            scope.selectOptions = [];
            scope.tempOutputList = [];
            init();

            scope.$watch('tempOutputList', (attrs.selectionMode && attrs.selectionMode == 'single') ? callWhenDifferent(singleSelect) : callWhenDifferent(multipleSelect));

            scope.$watchCollection('field.widget.choices', callWhenDifferent(function(){
                init_choices(init_values());
            }));

            // we only need this functionality for single selects. i.e. builder
            // watches the regionObject.object[field_name] to keep
            // selects in sync with programmatic changes.
            if(attrs.selectionMode && attrs.selectionMode == 'single'){
                scope.$watch(function(){
                    return scope.regionObject.object[scope.field.field_name];
                }, callWhenDifferent(singleSelectModeReverseWatch))
            }


            function ensureArray(arr){
                return angular.isArray(arr) ? arr : [arr];
            }
            function isChoiceDisabled(id){
                if(scope.regionObject.helpers.locked_company_ids){
                    return scope.regionObject.helpers.locked_company_ids.indexOf(id) > -1;
                }
                return false;
            }
            function makeItem(value, text, selected){
                var isDisabled = isChoiceDisabled(value);

                if(isDisabled) text = '<i class="fa fa-lock"></i> ' + text;

                return {
                    id: value,
                    text: text,
                    selected: selected,
                    checkboxDisabled: isDisabled
                };
            }

        }
    }
})
.directive('duallistHelper', function(){
    return {
        restrict: 'A',
        link: function(scope, element, attrs){

            /*
                Duallists are generally used by fields that get auto populated on the backend.
                  So lets watch for changes whenever that happens and re-init everything.
             */
            scope.$watch(function(){
                return scope.field;
            }, function(){
                init();
            });

            function init(){
                init_choices(init_values());
            }
            function init_values(){

                // check the region object to ensure we have no value.
                if(!scope.field.value) {
                    scope.field.value = scope.regionObject.object[scope.field.field_name];
                }

                if(scope.field.value){
                    return _.object(ensureArray(scope.field.value));
                }
                return {};
            }
            function init_choices(selected){

                var options = [];

                // push the choices into the options
                if(scope.field.widget.choices && scope.field.widget.choices.length){
                    angular.forEach(scope.field.widget.choices, function(value, index, obj){
                        if(value[0] === ''){
                            // blank strings for default none choices mess with
                            // fields that offer false as an option.
                            value[0] = null;
                        }

                        var item = makeItem(value[0], value[1]);

                        if(value[0] in selected) {
                            scope.tempOutputList.push(item);
                        } else {
                            options.push(item);
                        }
                    });
                }
                scope.selectOptions = options;
            }
            function multipleSelect(){
                var values = [];
                angular.forEach(scope.tempOutputList, function(obj){
                    values.push(obj.id);
                });
                scope.regionObject.object[scope.field.field_name] = values;
            }

            scope.selectOptions = [];
            scope.tempOutputList = [];
            // init();

            scope.$watch('tempOutputList', callWhenDifferent(multipleSelect), true);

            function ensureArray(arr){
                return angular.isArray(arr) ? arr : [arr];
            }
            function isChoiceDisabled(id){
                if(scope.regionObject.helpers.locked_company_ids){
                    return scope.regionObject.helpers.locked_company_ids.indexOf(id) > -1;
                }
                return false;
            }
            function makeItem(value, text){
                var isDisabled = isChoiceDisabled(value);

                if(isDisabled) text = '<i class="fa fa-lock"></i> ' + text;

                return {
                    id: value,
                    text: text
                    // selected: selected,
                    // checkboxDisabled: isDisabled
                };
            }
        }
    }
})

angular.module('axis.fields.helpers.datepicker')
.directive('datepickerHelper', function(){
    return {
        restrict: 'A',
        controller: function($scope){
            $scope.opened = false;
            $scope.format = 'MM/dd/yyyy';
            $scope.open = function($event){
                $event.preventDefault();
                $event.stopPropagation();
                $scope.opened = true;
            };
            // FIXME: fix until angular-ui datepicker supports formatted output.
            $scope.date = $scope.regionObject.object[$scope.field.field_name];
            $scope.$watch('date', function(newVal, oldVal){
                if(newVal !== oldVal){
                    var value;
                    try {
                        var dateArr = [newVal.getFullYear().toString(), (newVal.getMonth()+1).toString(), newVal.getDate().toString()];
                        value = dateArr.join('-');
                    } catch (e) {
                        value = newVal;
                    }
                    $scope.regionObject.object[$scope.field.field_name] = value;
                }
            })
        }
    }
});


angular.module('axis.fields.helpers')
.directive('nonNegativeNumber', function(){
    return buildRegexDirective(/[^\d.]/g);
})
.directive('nonNegativeWholeNumber', function(){
    return buildRegexDirective(/[^\d]/g)
}).directive('timepickerHelper', function(){
    return {
        restrict: 'A',
        controller: function($scope){
            if ($scope.regionObject.object[$scope.field.field_name]) {
                $scope.time = moment($scope.regionObject.object[$scope.field.field_name], 'HH:mm:ss');
            } else {
                $scope.time = new Date();
                $scope.regionObject.object[$scope.field.field_name] = $scope.time.getHours() + ':' + $scope.time.getMinutes();
            }

            $scope.$watch('time', function(newVal, oldVal){
                if(newVal !== oldVal){
                    if (newVal) {
                        $scope.regionObject.object[$scope.field.field_name] = newVal.getHours() + ':' + newVal.getMinutes();
                    } else {
                        $scope.regionObject.object[$scope.field.field_name] = newVal;
                    }
                }
            })
        }
    }
});


function buildRegexDirective(regex){
    return {
        restrict: 'A',
        require: '?ngModel',
        link: function(scope, element, attrs, ngModel){
            if(!ngModel) return;

            ngModel.$parsers.push(function(val){
                var clean = val ? val.replace(regex, '') : null;

                if(clean != val){
                    ngModel.$setViewValue(clean);
                    ngModel.$render();
                }
                return clean;
            })
        }
    }
}

function callWhenDifferent(fn){
    return function(newVal, oldVal){
        if(newVal != oldVal){
            fn(newVal, oldVal);
        }
    }
}
function removeWatcherWhenAny(scope, watch, execute){
    var unWatcher;
    unWatcher = scope.$watch(watch, function(newVal, oldVal){
        if(_.any([newVal, oldVal])){
            unWatcher();
            execute();
        }
    });
}
function waitForElement(region){
    return function(){
        // Make sure we always default to undefined so we don't
        // accidentally trigger the watcher to be executed.
        try{
            return region.$element.find('.fileinput').length || undefined;
        } catch(e){
            return undefined;
        }
    }
}
function markFileAsExisting(region){
    return function(){
        region.$element.find('.fileinput.fileinput-new').removeClass('fileinput-new').addClass('fileinput-exists');
    }
}

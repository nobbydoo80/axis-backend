angular.module('examineApp')

.controller('HomeFormController', function($scope, $http, $interpolate, RegionService, Actions){
    var endpointTemplates = {
        'subdivision': "/api/v2/subdivision/[[subdivision]]/",
        'subdivision_relationships': "/api/v2/subdivision/relationships/[[subdivision]]/"
    };
    var toPopulate = ['city'];
    var selects = ['city'];

    var addressOverrideInitialValue = $scope.regionObject.object.address_override;

    Actions.addPostMethodToType('save', 'home', updateAddressOverride);
    function updateAddressOverride(){
        addressOverrideInitialValue = $scope.regionObject.object.address_override;
    }

    function updateFields(data){
        var object = $scope.regionObject.object;
        for (var i in toPopulate) {
            var field = toPopulate[i];
            if (!object[field]) {
                if (selects.indexOf(field) !== -1) {
                    var element = $scope.region.axisFields[field];
                    var elementScope = angular.element(element.find('[ui-select-helper]')).scope();
                    elementScope.selectOptions.push(
                        {'id': data[field], 'text': data[field + "_name"]}
                    );
                }
                object[field] = data[field];
            }
        }
    }

    function _apiCall(endpoint, config){
        return $http.get(endpoint, config).error(function(data, code){
            console.log(data, code);
        });
    }

    var fn = {
        lookupSubdivisionInfo: function(){
            const object = $scope.regionObject.object;

            let endpointTemplate = endpointTemplates.subdivision;
            let endpoint = $interpolate(endpointTemplate)(object);
            _apiCall(endpoint).success(function(data){
                updateFields(data);
            });

            endpointTemplate = endpointTemplates.subdivision_relationships;
            endpoint = $interpolate(endpointTemplate)(object);
            _apiCall(endpoint).success(function(data){
                const rels = RegionService.getRegionFromTypeName('home_relationships');
                for (let companyType in data) {
                    // skip helper fields like 'urls'
                    const hasData = (rels.object[companyType] !== undefined);
                    const hasField = (rels.controller.axisFields[companyType] !== undefined);
                    if (hasData && hasField) {
                        const ids = data[companyType];
                        rels.object[companyType] = ids;  // array and singles

                        let names = []
                        if (_.isArray(ids)) {
                            for (let i in ids) {
                                names.push(data.names[ids[i]]);
                            }
                        } else {
                            names = data.names[ids];
                        }
                        console.log("Updating relationship field:", companyType, ids, names)
                        updateMultiSelectFieldLabel(rels, companyType, ids, names);
                    } else {
                        console.log("Skipping field %s (data: %s, field: %s)", companyType, hasData, hasField)
                    }
                }
            });
        },

        /* To be called via on-change by fields that make the existing geocoded result dirty. */
        makeGeocodeDirty: function(){
            // respect the users override if enabled during this edit phase
            if(!addressOverrideInitialValue) return;
            $scope.regionObject.object.address_override = false;
            $scope.regionObject.object.confirmed_address = false;
            $scope.regionObject.object.geocode_response = null;
        }
    };

    angular.extend($scope, fn);
})

.controller('CityOfHillsboroController', function($http, $scope, Actions){
    var ctrl = this;
    ctrl.linkThenReload = function(url) {
        ctrl.isProcessing = true;
        $http.get(url).then(function(){
            ctrl.isProcessing = false;
            Actions.callMethod('reload', $scope.regionObject);
        })
    }
})

.controller('HomeStatusFormController', function($scope, $http, $interpolate){
    var endpointTemplate = "/api/v2/company/[[company]]/users/";
    var toPopulate = ['rater_of_record'];
    var selects = ['rater_of_record'];

    function updateFields(data){
        var object = $scope.regionObject.object;
        for (var i in toPopulate) {
            var field = toPopulate[i];
            if (selects.indexOf(field) !== -1) {
                var element = $scope.region.axisFields[field];
                var elementScope = angular.element(element.find('[multi-select-helper]')).scope();
                elementScope.selectOptions.length = 0;
                $scope.regionObject.object[field] = null;
                for (var j in data) {
                    var choice_data = data[j];
                    elementScope.selectOptions.push({
                        'id': choice_data[0], 'text': choice_data[1]
                    })
                }
            }
            object[field] = data[field];
        }
    }

    function _apiCall(endpoint, config){
        return $http.get(endpoint, config).error(function(data, code){
            console.log(data, code);
        });
    }

    const fn = {
        lookupCompanyUsers: function(){
            const endpoint = $interpolate(endpointTemplate)($scope.regionObject.object);
            _apiCall(endpoint).success(function(data){
                updateFields(data.users);
            });
        }
    };

    angular.extend($scope, fn);
})

.controller('ProgramProgressBar', function($scope, $http){
    var ctrl = this;
    ctrl.region.reloadProgramRequirementsBar = loadProgramRequirementsBar;
    loadProgramRequirementsBar();

    function loadProgramRequirementsBar(){
        var unwatch;
        unwatch = $scope.$watch(function(){
            return ctrl.progressUrl;
        }, function(newVal, oldval){
            if(newVal){
                $http.get(ctrl.progressUrl, {cache: false}).success(function(data){
                    ctrl.progress_analysis = data;
                })
                unwatch();
            }
        })
    }
})
.directive('programProgressBar', function(){
    return {
        restrict: 'E',
        require: '^axisRegion',
        scope: {
            objectId: '=',
            progressUrl: '=',
            hasIppPayments: '=',
            objectState: '=',
            certificationDate: '=',
            region: '='
        },
        bindToController: true,
        controllerAs: 'progress',
        controller: 'ProgramProgressBar',
        templateUrl: '/examine/home/progress_analysis_bar.html'
    }
})

.controller('ProgramProgressList', function($scope, $sce, $http, $timeout, RegionService, Actions, $state){
    var ctrl = this;
    ctrl.showingCompleted = false;
    ctrl.trustAsHtml = $sce.trustAsHtml;
    ctrl.region.reloadProgramRequirements = loadProgramRequirements
    ctrl.routeRequirementLink = routeRequirementLink;
    ctrl.toggleCompleted = toggleCompleted;
    loadProgramRequirements();

    function loadProgramRequirements(){
        var unwatch;
        unwatch = $scope.$watch(function(){
            return ctrl.progressUrl;
        }, function(newVal, oldVal){
            if(newVal){
                $http.get(ctrl.progressUrl, {cache: false}).success(function(data){
                    ctrl.progress_analysis = data;
                });
                unwatch()
            }
        });
    }

    function toggleCompleted(){
        ctrl.showingCompleted = !ctrl.showingCompleted;
    }

    function routeRequirementLink(url) {
        // Try to route a url locally if it's in one of the forms:
        // * #instruction-edit
        // * #instruction-edit:typename-regionid
        // Where 'regionid' is regionObject.id, typically in the form "{typename}_{pk}"
        var bits = url.split('#instruction-', 2);
        var baseUrl = bits[0];
        var regionInstruction = bits[1];
        if (!regionInstruction) {
            // Recognize when we're trying to route to tabs
            if (url.indexOf('#/') === 0){  // starts with #/
                var tabEndpoint = url.substr(2).replace('/', '.');
                var tabLink = $('[tab-helper][endpoint="' + tabEndpoint + '"] a');
                $timeout(function(){
                    tabLink.click();
                });
            } else {
                // No special treatment
                window.location = url;
            }
            return;
        }

        var instructionBits = regionInstruction.split(':', 2);
        var instruction = instructionBits[0];
        var regionTarget = instructionBits[1];

        var regionObject = ctrl.regionObject;
        if (regionTarget) {
            var regionBits = regionTarget.split('-', 2);
            var typeName = regionBits[0];
            var typeId = regionBits[1];  // presently unused

            // Resolve target regionObject
            if (regionObject.type_name != typeName) {
                // FIXME: Climb the chain of parent regions first, before resorting to this?
                regionObject = RegionService.getRegionFromTypeName(typeName);
                if (_.isArray(regionObject)) {
                    // If the user went from our /add/ page, this operation will yield two regions
                    // claiming to be the relationships section because of how we inject one during
                    // the add-new Home region.  It's destroyed at this point, but it was still
                    // registered and never unregistered.
                    regionObject = regionObject[regionObject.length - 1];
                }
            }
        }

        Actions.callMethod(instruction, regionObject);

        // Activate any tabs
        var panes = $(regionObject.$element).parents('.tab-pane')
        _.forEach(panes, function(pane){
            pane = $(pane);
            var tabIndex = pane.index();

            // Go up to outer container (maybe an outer tab-pane wrapping this one)
            var container = pane.parent().closest('.tab-pane,body');

            // Follow it back down to find the tab strip
            var clicker = container.find('.nav-tabs').find('li a').eq(tabIndex);
            $timeout(function(){
                clicker.click();
            }, 0);
        });

        return true;
    }

    ctrl.scrollTo = function(requirement){
        var targetID = $scope.$parent.regionObject.id;
        var target_panel = null;
        var content_panel = null;
        var button = null;

        // We only handle annotation scrolls right now
        if (/annotations/.test(requirement.url)) {
            target_panel = $('#home_status_' + targetID + '_collapsible');
            content_panel = $('#home_status_' + targetID + '_panel');
            button = content_panel.find("axis-single-region[options='regionObject.helpers.machinery.annotations']")
                                  .find("action-strip[data-name='default'] button")
        }

        if (content_panel === null) {
            return;
        }

        $timeout(function(){
            target_panel.collapse('show');
            if (button !== null) {
                button.click();
            }

            // Activate any tabs
            var panes = content_panel.parents('.tab-pane')
            _.forEach(panes, function(pane){
                pane = $(pane);
                var tabIndex = pane.index();

                // Go up to outer container (maybe an outer tab-pane wrapping this one)
                var container = pane.parent().closest('.tab-pane,body');

                // Follow it back down to find the tab strip
                var clicker = container.find('.nav-tabs').find('li a').eq(tabIndex);
                $timeout(function(){
                    clicker.click();
                }, 0);
            });

            $timeout(function(){
                // Re-fetch, in case it was hidden and page offset unknown
                content_panel = $('#' + content_panel.attr('id'));

                $(window).scrollTop(content_panel.offset().top);
            }, 100);
        }, 0);
    }
})
.directive('programProgressList', function(){
    return {
        restrict: 'E',
        require: '^axisRegion',
        scope: {
            progressUrl: '=',
            typeName: '=',
            regionObject: '=',
            region: '='
        },
        bindToController: true,
        controllerAs: 'progress',
        controller: 'ProgramProgressList',
        templateUrl: '/examine/home/progress_analysis.html'
    }
})

.directive('genericAnnotationsList', function(){
    return {
        restrict: 'E',
        require: '^axisRegion',
        controller: function($scope){
            $scope.showingNotes = true;
            $scope.toggleNotes = function(){
                $scope.showingNotes = !$scope.showingNotes;
            }
        },
        templateUrl: '/examine/home/annotations_list.html'
    }
})

.controller('RemdataOnChangeController', function($scope, $http, $interpolate){
    const endpointTemplates = {
        remrate: '/api/v2/floorplan/rem_data_fields/',
        ekotrope: '/api/v2/floorplan/ekotrope_fields/',
        houseplans: '/api/v2/ekotrope/houseplan/'
    };
    const toPopulate = ['name', 'number', 'square_footage'];

    function updateFields(data){
        const object = $scope.regionObject.object;
        for (let i in toPopulate) {
            const field = toPopulate[i];
            if (!object[field]) {
                object[field] = data[field];
            }
        }
        $scope.loadingInputInfo = false;
    }

    /**
     * @returns {boolean} True if any of the region object's fields defined by toPopulate are empty
     */
    function hasEmptyFields(){
        const object = $scope.regionObject.object;
        for (let i in toPopulate) {
            const value = object[toPopulate[i]];
            if (value == null || value === "") {
                return true
            }
        }
        return false;
    }

    function _apiCall(config){
        return $http(config).error(function(data, code){
            console.log(data, code);
        });
    }

    $scope.$watchGroup(['regionObject.object.remrate_target', 'regionObject.object.remrate_data_file_raw'], function(nV, oV){
        if(_.every(nV)){
            console.log("sending the request");
            var config = {
                'url': '/api/v2/remrate/'+nV[0]+'/validate/',
                'method': 'POST',
                'data': {
                    'file': nV[1]
                }
            };
            _apiCall(config).success(function(data){
                console.log('success');
                $scope.validation_data = data
                $scope.data_has_mismatches = Object.keys($scope.validation_data).length !== 0;
            })
        }
    });

    var fn = {
        updateEkotropeHousePlanOptions: updateEkotropeHousePlanOptions,
        lookupRemrateInfo: lookupRemrateInfo,
        lookupEkotropeInfo: lookupEkotropeInfo,
        validationClass: function(obj){
            return obj.matches ? 'text-success' : {
                'info': 'text-info',
                'warning': 'text-warning',
                'error': 'text-danger'
            }[obj.level];
        }
    };

    function _lookupInputInfo(endpointType, triggerValue){
        if(!$scope.regionObject.object.id){
            if(triggerValue != null && hasEmptyFields()){
                var params = {
                    id: triggerValue,
                    base_name: $scope.regionObject.object.base_name
                }
                var config = {
                    'url': endpointTemplates[endpointType],
                    'method': 'GET',
                    'params': params
                };
                $scope.loadingInputInfo = true;
                _apiCall(config).success(updateFields);
            }
        }
    }
    function updateEkotropeHousePlanOptions(){
        var project_id = $scope.regionObject.object.ekotrope_project;
        $scope.regionObject.object.ekotrope_houseplan = null;
        _apiCall({
            url: endpointTemplates.houseplans,
            method: 'GET',
            params: {
                project: project_id
            }
        }).success(setHousePlanOptions);
    }
    function lookupEkotropeInfo(){
        var houseplan_id = $scope.regionObject.object.ekotrope_houseplan;
        _lookupInputInfo('ekotrope', houseplan_id);
    }
    function lookupRemrateInfo(){
        var simulation_id = $scope.regionObject.object.remrate_target;
        _lookupInputInfo('remrate', simulation_id);
    }
    function setHousePlanOptions(data){
        const choices = $scope.regionObject.fields.ekotrope_houseplan.widget.choices;
        choices.length = 0;
        for (let i in data.results) {
            choices.push([
                data.results[i].id,
                data.results[i].name
            ]);
        }
    }

    function _initInputType(){
        // Order of IF statements here determines default when multiple are allowed.
        // One day they're going to ask us to make Ekotrope default for certain programs.
        // Mark my words.

        // If there ends up being only one type available in the form, this value doesn't matter
        // and the template will show only that one.

        var inputChoice = {
            type: null
        }

        // FIXME: scan selected program to limit to valid types
        var form = $scope.regionObject.fields;
        if (form.remrate_target !== undefined) {
            inputChoice.type = 'remrate';
        } else if (form.ekotrope_houseplan !== undefined) {
            inputChoice.type = 'ekotrope';
        }

        $scope.inputChoice = inputChoice;
    }

    _initInputType();

    angular.extend($scope, fn);
})

.controller('NEEABOPController', function($scope){
    var _heatSource = $scope.regionObject.fields['heat-source'],
        _tco = $scope.regionObject.fields['tco-options'];

    var heatChoices = _heatSource.widget.choices,
        tcoChoices = _tco.widget.choices,
        heatDefaultChoices = angular.copy(heatChoices),
        tcoDefaultChoices = angular.copy(tcoChoices),
        heatDefaultChoice = [_heatSource.value, _heatSource.value_label || _heatSource.value],
        tcoDefaultChoice = [_tco.value, _tco.value_label || _tco.value],
        deprecated_options = {
            '2011 ID/MT BOP 1': ['2011 ID/MT BOP 1'],
            '2011 ID/MT BOP 2': ['2011 ID/MT BOP 2'],
            '2011 WA BOP 1': ['2011 WA BOP 1 - Ducts in Conditioned Space', '2011 WA BOP 1 - Equipment Upgrade', '2011 WA BOP 1 - Envelope Pathway'],
            '2011 WA BOP 2': ['2011 WA BOP 2 - Zonal Electric; Propane and Oil'],
            '2012 OR BOP 1': ['2012 OR BOP 1 - Ducts in Conditioned Space', '2012 OR BOP 1 - Equipment Upgrade', '2012 OR BOP 1 - Envelope Pathway'],
            '2012 OR BOP 2': ['2012 OR BOP 2 - Zonal Electric; Propane and Oil'],
            'OPPH': ['Oregon Premium Performance Home (OPPH)']
        };

    function trim_name(selected) {
        for(let name in deprecated_options) {
            if (deprecated_options[name].indexOf(selected) !== -1) {
                console.log("Trim BOP selected", selected);
                return name;
            }
        }
        console.log("No Trim BOP selected", selected)
        return selected;
    }

    function remove_heat_sources(selected) {
        var remove_options = {
            'one': ['Zonal Electric', 'Propane & Oil'],
            'two': ['Heat Pump', 'Gas with AC', 'Gas No AC']
        };

        var heat_remove_select = {
            'one': ['2011 ID/MT BOP 1', '2011 WA BOP 1', '2012 OR BOP 1', 'NW BOP 1 MF'],
            'two': ['2011 ID/MT BOP 2', '2011 WA BOP 2', '2012 OR BOP 2', 'NW BOP 2 MF' ]
        };

        var trimmed = false;
        for (var name in heat_remove_select) {
            if (heat_remove_select[name].indexOf(selected) !== -1) {
                trimmed = true;
                console.log("Heat", name, "trim selected", selected);

                var removeChoices = remove_options[name];
                heatChoices = heatChoices.filter(function(obj){
                    return removeChoices.indexOf(obj[1]) === -1 || obj[0] == heatDefaultChoice[0];
                });
            }
        }
        if(!trimmed) {
            console.log("Heat - no trim");
        }
        return heatChoices
    }

    function remove_tco_sources(selected) {
        var remove_options = {
            'one': ['Mechanically', 'Sealed', 'Tankless Water'],
            'two': ['Un-vented', 'Sealed'],
            'three': ['Reduced Thermal Bridging', 'Hybrid', 'Natural Gas', 'Un-vented', 'Mechanically', 'Sealed', 'Tankless Water']
        };

        var tco_remove_select = {
            'one': ['2011 ID/MT BOP 1'],
            'two': ['2011 WA BOP 1', '2012 OR BOP 1'],
            'three': ['2011 ID/MT BOP 2', '2011 WA BOP 2', '2012 OR BOP 2', 'OPPH', 'NW BOP 1 MF', 'NW BOP 2 MF' ]
        };

        var trimmed = false;
        for(var name in tco_remove_select){
            if(tco_remove_select[name].indexOf(selected) !== -1){
                trimmed = true;
                console.log("TCO", name, 'trim selected', selected);
                var removeChoices = remove_options[name];
                tcoChoices = tcoChoices.filter(function(obj){
                    return removeChoices.indexOf(obj[1]) === -1 || obj[0] == tcoDefaultChoice[0];
                });
            }
        }
        if(!trimmed) {
            console.log("TCO - no trim")
        }
        return tcoChoices;
    }

    var fn = {
        updateChoicesFromBOP: function(selected){
            //BOP onchange
            console.log("-- Change BOP --");
            heatChoices.length = 0; tcoChoices.length = 0;
            heatChoices.push.apply(heatChoices, heatDefaultChoices);
            tcoChoices.push.apply(tcoChoices, tcoDefaultChoices);
            //
            //var bop_sel = bop.find('option:selected').val();
            //bop_sel = trim_name(bop_sel);
            selected = trim_name(selected);
            //
            var one = remove_heat_sources(selected);
            var two = remove_tco_sources(selected);
            $scope.regionObject.fields['heat-source'].widget.choices = one;
            $scope.regionObject.fields['tco-options'].widget.choices = two;
        }
    };

    angular.extend($scope, fn);
})

.controller('NEEABOP2015Controller', function($scope){
    var _heatSource = $scope.regionObject.fields['heat-source'],
        valid_bops = [['NW BOP 1 MF', 'NW BOP 1 MF'], ['NW BOP 2 MF', 'NW BOP 2 MF']];

    var heatChoices = _heatSource.widget.choices,
        heatDefaultChoices = angular.copy(heatChoices),
        heatDefaultChoice = [_heatSource.value, _heatSource.value_label || _heatSource.value];

    function remove_heat_sources(selected) {
        var remove_options = {
            'one': ['Zonal Electric', 'Propane & Oil'],
            'two': ['Heat Pump', 'Gas with AC', 'Gas No AC']
        };

        var heat_remove_select = {
            'one': ['NW BOP 1 MF'],
            'two': ['NW BOP 2 MF' ]
        };

        var trimmed = false;
        for (var name in heat_remove_select) {
            if (heat_remove_select[name].indexOf(selected) !== -1) {
                trimmed = true;
                console.log("Heat", name, "trim selected", selected);

                var removeChoices = remove_options[name];
                heatChoices = heatChoices.filter(function(obj){
                    return removeChoices.indexOf(obj[1]) === -1 || obj[0] == heatDefaultChoice[0];
                });
            }
        }
        if(!trimmed) {
            console.log("Heat - no trim");
        }
        return heatChoices
    }

    var fn = {
        updateChoicesFromBOP: function(selected){
            //BOP onchange
            console.log("-- Change BOP --");
            heatChoices.length = 0;
            heatChoices.push.apply(heatChoices, heatDefaultChoices);

            var one = remove_heat_sources(selected);
            $scope.regionObject.fields['heat-source'].widget.choices = one;
        }
    };

    angular.extend($scope, fn);
    $scope.regionObject.fields['bop'].widget.choices = valid_bops;
})

.controller('NWESHDisclaimerController', function($scope){
    var init = JSON.parse(localStorage.getItem('show_nwesh_disclaimer'));

    // Show disclaimer if true, or nothing comes back from localStorage.
    $scope.showDisclaimer = (init === null || init);

    $scope.toggleDisclaimer = function(e){
        e.preventDefault();
        $scope.showDisclaimer = !$scope.showDisclaimer;
        localStorage.setItem('show_nwesh_disclaimer', $scope.showDisclaimer);
    }
})
.controller('QAStatusController', function ($scope, $http, Actions) {

})
.controller('QAStatusDetailController', function ($scope, $http, Actions) {
    $scope.perLevelWarningChecksMap = [
        {
            "eep_program_slugs": [
                "ngbs-sf-whole-house-remodel-2020-new",
                "ngbs-mf-whole-house-remodel-2020-new",
                "ngbs-sf-whole-house-remodel-2015-new",
                "ngbs-mf-whole-house-remodel-2015-new",
                "ngbs-sf-whole-house-remodel-2012-new",
                "ngbs-mf-whole-house-remodel-2012-new",
            ],
            "levels": [
                {
                    "level": "bronze",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded >= 125) {
                            $scope.certificationLevelWarningMessage = 'Is Bronze correct? Silver level may be available';
                        }
                    }
                },
                {
                    "level": "gold",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded >= 181) {
                            $scope.certificationLevelWarningMessage = 'Is Bronze correct? Gold level may be available';
                        }
                    }
                },
                {
                    "level": "emerald",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded >= 225) {
                            $scope.certificationLevelWarningMessage = 'Is Bronze correct? Emerald level may be available';
                        }
                    }
                },
            ],
        },
        {
            "eep_program_slugs": [
                "ngbs-sf-new-construction-2020-new",
                "ngbs-mf-new-construction-2020-new",
                "ngbs-sf-new-construction-2015-new",
                "ngbs-mf-new-construction-2015-new"
            ],
            "levels": [
                {
                    "level": "bronze",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded >= 334) {
                            $scope.certificationLevelWarningMessage = 'Is Bronze correct? Silver level may be available';
                        }
                    }
                },
                {
                    "level": "silver",
                    "points_awarded": 489,
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded >= 489) {
                            $scope.certificationLevelWarningMessage = 'Is Silver correct? Gold level may be available';
                        }
                    }
                },
                {
                    "level": "gold",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded >= 611) {
                            $scope.certificationLevelWarningMessage = 'Is Gold correct? Emerald level may be available';
                        }
                    }
                },
            ],
        },
        {
            "eep_program_slugs": [
                "ngbs-sf-new-construction-2012-new",
                "ngbs-mf-new-construction-2012-new",
            ],
            "levels": [
                {
                    "level": "bronze",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded >= 349) {
                            $scope.certificationLevelWarningMessage = 'Is Bronze correct? Silver level may be available';
                        }
                    }
                },
                {
                    "level": "silver",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded >= 509) {
                            $scope.certificationLevelWarningMessage = 'Is Silver correct? Gold level may be available';
                        }
                    }
                },
                {
                    "level": "gold",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded >= 641) {
                            $scope.certificationLevelWarningMessage = 'Is Gold correct? Emerald level may be available';
                        }
                    }
                }
            ],
        },
        {
            "eep_program_slugs": [
                "ngbs-land-development-2020-new",
            ],
            "levels": [
                {
                    "level": "one_star",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded < 95) {
                            $scope.certificationLevelWarningMessage = "Not enough points for any level !"
                        }
                    }
                },
                {
                    "level": "two_stars",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded < 122) {
                            $scope.certificationLevelWarningMessage = "Not enough points for Two Stars !"
                        }
                    }
                },
                {
                    "level": "three_stars",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded < 149) {
                            $scope.certificationLevelWarningMessage = "Not enough points for Three Stars !"
                        }
                    }
                },
                {
                    "level": "four_stars",
                    "validation": function (pointsAwarded) {
                        if (pointsAwarded < 176) {
                            $scope.certificationLevelWarningMessage = "Not enough points for Four Stars !"
                        }
                    }
                },
            ],
        },
    ]

    $scope.certificationLevelWarningMessage = '';
    $scope.greenEnergyBadgesWarningMessage = '';

    $scope.certificationLevelWarningCheck = function () {
        let pointsAwarded = parseFloat($scope.regionObject.object.hirl_verifier_points_awarded);
        let levelAwarded = $scope.regionObject.object.hirl_certification_level_awarded;

        if (!pointsAwarded || !levelAwarded) {
            return;
        }

        $scope.perLevelWarningChecksMap.forEach(function (levelData) {
            if (levelData['eep_program_slugs'].indexOf($scope.regionObject.object.requirement_eep_program_slug) > -1) {
                levelData['levels'].forEach(function (levelCheckData) {
                    if (levelCheckData['level'] === levelAwarded) {
                        levelCheckData['validation'](pointsAwarded);
                    }
                });
            }
        });
    }

    $scope.warningChecks = function () {
        $scope.certificationLevelWarningMessage = '';
        $scope.greenEnergyBadgesWarningMessage = '';
        $scope.waterSenseConfirmedsWarningMessage = '';
        $scope.wriValueAwardedWarningMessage = '';

        $scope.initialGreenEnrgyBadges = angular.copy($scope.regionObject.object.customer_hirl_project_green_energy_badges);
        $scope.initialWaterSenseConfirmed = angular.copy($scope.regionObject.object.customer_hirl_project_is_require_water_sense_certification);
        $scope.initialWRIValueAwarded = angular.copy($scope.regionObject.object.customer_hirl_project_is_require_wri_certification);

        $scope.certificationLevelWarningCheck($scope.regionObject.object.hirl_certification_level_awarded);

        if ($scope.initialGreenEnrgyBadges.length > 0 && $scope.regionObject.object.hirl_badges_awarded.length === 0) {
            $scope.greenEnergyBadgesWarningMessage = 'Badges were indicated at Registration, ' +
                'but nothing was specified in the “NGBS Green+ Badges Awarded” field'
        }

        if ($scope.initialWaterSenseConfirmed === 'True' && $scope.regionObject.object.hirl_water_sense_confirmed !== 'true') {
            $scope.waterSenseConfirmedsWarningMessage = 'WaterSense was indicated at Registration, ' +
                'but nothing was specified in the “WaterSense Confirmed” field'
        }

        if ($scope.initialWRIValueAwarded === 'True' && !$scope.regionObject.object.hirl_reviewer_wri_value_awarded) {
            $scope.wriValueAwardedWarningMessage = 'Water Performance Path was selected, ' +
                'but nothing was specified in the “Reviewer WRI Value Awarded” field'
        }
    }

    $scope.warningChecks();

    Actions.addPostMethodToType('save', ['qa_status', ], function () {
       $scope.warningChecks();
    });
})
.controller('QADocumentCustomerHIRLController', function ($scope, $http, Actions) {
    $scope.regionObject.object['is_public'] = true;
})

.controller('EtoLegacyCalculationsOutputController', function($scope, $timeout){
    var ctrl = this;
    var element = $($scope.regionObject.$element).find('.eto-legacy-calculations-output');

    function init_eto_output(wrapper, url) {
        var output = wrapper.find('.eto-calculations-legacy-output-data');
        var error_data = wrapper.find('.eto-calculations-errors');
        var input_form = wrapper.find('.eto-calculations-input');

        var xhr = $.get(url);
        xhr.success(function (data) {
            ctrl.loading = false;
            ctrl.error = false;
            ctrl.success = true;

            wrapper.find('.eto-calculations-progress-indicator').remove();
            populate_calculations_table(data, wrapper);
            $(output).slideDown('fast');

            var button_str = '<div class="btn-group pull-right"><button type="button" ' +
                'class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">' +
                'Full report <span class="caret"></span></button>' +
                '<ul class="dropdown-menu text-left"><li'

            var showview = element.attr('data-showview');
            if (typeof showview === 'undefined' || showview === "false") {
                button_str += ' class="hidden '
            }
            button_str += '><a class="eto-view-full-report" href="#">View Calculator</a></li>' +
                '<li><a href="'+data.eps_report_url+'">EPS Download</a></li></ul></div>';

            var button_group = $(button_str);
            button_group.find('.eto-view-full-report').on('click', function(){
                input_form.submit();
                return false;
            });

            if (typeof data['fasttracksubmission_id'] !== 'undefined' && data['fasttracksubmission_id'] !== null){
                head_txt = 'Home as Built &nbsp; <i class="fa fa-lock" data-toggle="tooltip" title="As reported to ETO"></i>';
                output.find('thead tr th').html(head_txt)
            }
            output.find('thead tr th').append(button_group);
            $scope.$apply();
        });
        xhr.fail(function(data) {
            let errors;
            try {
                errors = data.responseJSON['errors'];
            } catch (err) {
                errors = ["Unable to calculate EPS Score! Missing information."]
            }

            ctrl.loading = false;
            ctrl.error = true;
            ctrl.success = false;

            var ul_ = "<strong>Energy Performance Score cannot yet be calculated.<br />The following ";
            ul_ += "information items are missing or not valid for the program:</strong><br /><ul>";
            $.each(errors, function( index, value ) {
                ul_ += "<li>" + value + "</li>";
            });
            ul_ += "</ul>";
            error_data.show().html(ul_);
            $(error_data).slideDown('fast');
            $scope.$apply();
        });
    }
    function populate_calculations_table(data, output) {
        output.find('[data-name]').each(function(){
            var tr = $(this);
            var name = tr.attr('data-name');
            var value = data[name];
            var cell = tr.find('td.value');
            var is_html = false;
            if (tr.is('span')) {
                cell = tr;
            }
            if (cell.attr('data-precision')) {
                var precision = parseInt(cell.attr('data-precision'));
                if (cell.text().indexOf('$') !== -1) {
                    if (value) {
                        value = Math.round(value * Math.pow(10, precision)) / Math.pow(10, precision)
                        value = "$" + value.toFixed(precision);
                    } else {
                        value = "$0.00";
                    }
                } else {
                    if (cell.is('[data-percentage]')) {
                        value = '' + Math.round(value * 100 * Math.pow(10, precision)) / Math.pow(10, precision) + '%';
                    } else {
                        value = Math.round(value * Math.pow(10, precision)) / Math.pow(10, precision);
                    }
                }
            }
            console.log("Reviewing" + name)
            if (name === "rater_incentive" && data['original_rater_incentive']) {
                value += " &#8225;";
                is_html = true;
                $("#eps-manual-override").show()
            }
            if (name === "builder_incentive" && data['original_builder_incentive']) {
                value += " &#8225;";
                is_html = true;
                $("#eps-manual-override").show()
            }
            if (is_html) {
                cell.html(value);
            } else {
                cell.text(value);
            }
            var showview = tr.attr('data-showview');
            if (typeof showview !== 'undefined' && showview === "false") {
                tr.remove()
            }

        });
    }

    function init(){
        $timeout(function(){
            var regionObject = $scope.regionObject;
            var url = regionObject.helpers.eps_url;
            element.find('form .form-area').empty().append(regionObject.helpers.eps_calculations_form);
            init_eto_output(element, url);
        }, 0);
    }

    init();
    $scope.etoInit = init;
    ctrl.loading = true;
    ctrl.error = false;
    ctrl.success = false;
})

.directive('etoLegacyCalculationsOutput', function(){
    return {
        restrict: 'C',
        controller: 'EtoLegacyCalculationsOutputController',
        controllerAs: 'etoLegacyCalculationsOutputController'
    }
})

.directive('rtfCalculationsOutput', function (Actions) {
    return {
        restrict: 'C',
        controller: function ($scope, $http, $rootScope) {
            var ctrl = this;
            ctrl.loading = true;
            ctrl.success = false;
            ctrl.error = false;
            ctrl.show_admin = $scope.regionObject.helpers.show_admin;
            ctrl.show_utility_payment = $scope.regionObject.helpers.show_utility_payment;
            ctrl.has_bpa_affiliation = $scope.regionObject.helpers.has_bpa_affiliation;
            ctrl.program_slug = $scope.regionObject.helpers.program_slug;

            getCalculatorData(); // init data
            $scope.rtfInit = getCalculatorData;

            $rootScope.$on('navigation:from_checklist', getCalculatorData);
            var dependent_types = ['home', 'home_status', 'home_status_annotations', 'floorplan', 'home_relationships'];
            Actions.addPostMethodToType('save', dependent_types, getCalculatorData);

            function getCalculatorData() {
                ctrl.loading = true;
                $http.get($scope.regionObject.helpers.rtf_url).then(function (response) {
                    ctrl.success = true;
                    ctrl.error = false;
                    ctrl.errors = false;
                    ctrl.result = response.data;
                    ctrl.has_reports = (response.data.reports != null && Object.keys(response.data.reports).length > 0);
                    ctrl.loading = false;
                })
                    .catch(function (response) {
                        ctrl.success = false;
                        ctrl.errors = response.data;
                        ctrl.error = true;
                        ctrl.result = false;
                        ctrl.has_reports = false;
                        ctrl.loading = false;
                    })
            }
        },
        controllerAs: 'ctrl',

    }
})

.directive('wccCalculationsOutput', function (Actions) {
    return {
        restrict: 'C',
        controller: function ($scope, $http, $rootScope) {
            var ctrl = this;
            ctrl.loading = true;
            ctrl.success = false;
            ctrl.error = false;
            ctrl.show_admin = $scope.regionObject.helpers.show_admin;
            ctrl.program_slug = $scope.regionObject.helpers.program_slug;

            getCalculatorData(); // init data
            $scope.wccInit = getCalculatorData;

            $rootScope.$on('navigation:from_checklist', getCalculatorData);
            var dependent_types = ['home', 'home_status', 'home_status_annotations', ];
            Actions.addPostMethodToType('save', dependent_types, getCalculatorData);

            function getCalculatorData() {
                ctrl.loading = true;
                $http.post($scope.regionObject.helpers.wcc_url).then(function (response) {
                    ctrl.success = true;
                    ctrl.error = false;
                    ctrl.errors = false;
                    ctrl.result = response.data;
                    ctrl.has_reports = (response.data.reports != null && Object.keys(response.data.reports).length > 0);
                    ctrl.loading = false;
                })
                    .catch(function (response) {
                        ctrl.success = false;
                        ctrl.errors = response.data;
                        ctrl.error = true;
                        ctrl.result = false;
                        ctrl.has_reports = false;
                        ctrl.loading = false;
                    })
            }
        },
        controllerAs: 'ctrl',
    }
})

.directive('etoCalculationsOutput', function (Actions) {
    return {
        restrict: 'C',
        controller: function ($scope, $http, $rootScope) {
            var ctrl = this;
            ctrl.loading = true;
            ctrl.success = false;
            ctrl.error = false;
            ctrl.show_admin = $scope.regionObject.helpers.show_admin;
            ctrl.show_debug = $scope.regionObject.helpers.show_debug;

            getCalculatorData(); // init data
            $scope.wccInit = getCalculatorData;

            $rootScope.$on('navigation:from_checklist', getCalculatorData);
            var dependent_types = ['home', 'home_status', 'home_status_annotations', 'floorplan'];
            Actions.addPostMethodToType('save', dependent_types, getCalculatorData);

            function getCalculatorData() {
                ctrl.loading = true;
                $http.post(
                    $scope.regionObject.helpers.eps_url
                ).then(function (response) {
                    ctrl.success = true;
                    ctrl.error = false;
                    ctrl.errors = false;
                    ctrl.result = response.data;
                    ctrl.has_reports = (response.data.reports != null && Object.keys(response.data.reports).length > 0);
                }).catch(function (response) {
                    ctrl.success = false;
                    ctrl.errors = response.data;
                    ctrl.error = true;
                    ctrl.result = false;
                    ctrl.has_reports = false;
                }).finally(() => {
                    ctrl.loading = false;
                });
            }
        },
        controllerAs: 'ctrl',
    }
})

.controller('FloorplanCopyController', function($scope, $rootScope, Actions){
    this.copy = function(sourceHomestatusRegionObject){
        // Hooks load signal of new region so that floorplanId can be set on the new region.
        var unwatch = $rootScope.$on('addedRegion:floorplan', function(event, regionObject){
            unwatch();
            var floorplanId = sourceHomestatusRegionObject.object.floorplan;
            var targetHomestatusRegionObject = $scope.regionSet.parentRegionObject;

            regionObject._autosaving = true;
            regionObject.object.existing_floorplan = floorplanId;
            regionObject.fields.existing_floorplan.value = floorplanId;

            Actions.callMethod('save', targetHomestatusRegionObject).then(function(){
                return Actions.callMethod('save', regionObject).then(function(){
                    regionObject._autosaving = false;
                    return Actions.callMethod('exit', targetHomestatusRegionObject);
                });
            });
        });
        $scope.regionSet.fetchNewRegion({'form_type': 'existing'});
    };
})

.controller('BLGUploadController', function($scope, Actions){
    // Provides a fake action button
    // A 'home_blg' post-save hook is registered in .run(), triggering populateBLGFields()
    return {
        'upload': function(){
            Actions.callMethod('save', $scope.regionObject);
        }
    }
})

.controller('TaskTypeModalController', function($scope, Modal, $rootScope){
    var ctrl = this;
    ctrl.open = function _open(){
        return Modal({
            modal: {
                templateUrl: '/examine/scheduling/manage_task_types.html'
            }
        }, {
            controller: {
                // when inside a modal, regions will try to register themselves with a parent,
                // we don't have a nice way to tell them not to,
                // but we can give them somewhere to go that doesn't impact anything else.
                children: []
            },
            helpers: {
                machinery: {
                    task_types: $rootScope.examineApp.pageRegions.task_types
                }
            }
        });
    };
})

.controller('InvoiceItemGroupMachineriesController', function($rootScope, $scope, $http, RegionService){
    $scope.invoiceItemGroupMachineries = [];
    $scope.homeStatusRegion = RegionService.helpers.regionsMap['invoice_home_status'];

    $http({
        method : 'GET',
        url : '/api/v2/homestatus/'+$scope.homeStatusRegion.object.id+'/invoice_item_groups_machinery/'
    }).success(function(data) {
        $scope.invoiceItemGroupMachineries = [data];
    });

    $rootScope.$on('invoiceItemGroupMachineries', function(event, data){
        $scope.invoiceItemGroupMachineries = [data];
    });
})

.controller('InvoiceHomeStatusController', function($rootScope, $scope, $http, RegionService){
   var ctrl = this;

   ctrl.billingStatesMap = {
       'new': 'New',
       'new_queued': 'New - Queued',
       'new_notified': 'New - Notified',
       'notice_sent': 'Notice Sent',
       'not_pursuing': 'Not pursuing',
       'void': 'Void',
       'completed': 'Completed',
       'complimentary': 'Complimentary',
       'test': 'Test',
       '4300': '4300'
   }
   ctrl.state = '';
   ctrl.newState = angular.copy(ctrl.state);

   ctrl.changeState = function (objectId) {
        $http({
            method : 'PATCH',
            url: '/api/v3/hirl_projects/'+objectId+'/',
            data: {
                manual_billing_state: ctrl.newState
            }
        }).success(function(data, status) {
            ctrl.state = angular.copy(data['billing_state']);
            $('.modal').modal('hide');

            let homeStatusRegion = RegionService.helpers.regionsMap['invoice_home_status'];
            $http({
                method : 'GET',
                url : '/api/v2/homestatus/'+ homeStatusRegion.object.id +'/invoice_item_groups_machinery/'
            }).success(function(data, status) {
                $rootScope.$broadcast('invoiceItemGroupMachineries', data);
            });
        });
   }
})

.controller('MultipleDocumentController', function($scope, Actions, RegionService){
    var processing = false;

    $scope.region = {
        handleAction: function(action){
            processing = true;
            var regionObjects = RegionService.getRegionFromTypeName('home_documents'),
                regionObject = angular.isArray(regionObjects) ? regionObjects[0] : regionObjects;

            return Actions.callMethod(action, regionObject).finally(function(){
                processing = false;
            });
        },
        isProcessing: function(){
            return processing;
        },
        regionsEditing: _regionsEditing
    }
    function _regionsEditing(){
        return _.filter(RegionService.getRegionFromTypeName('home_documents'), function(region){
            return region.controller.editing();
        }).length;
    }

})
.filter('endsWith', () => {
  return (items, prefixes, itemProperty) => {
    if (items && items.length) {
      return items.filter((item) => {
        var findIn = itemProperty ? item[itemProperty] : item;
        return findIn.toString().endsWith(prefixes);
      });
    }
  };
})
.filter('startsWith', function() {
    return function(array, search) {
        var matches = [];
        for(var i = 0; i < array.length; i++) {
            if (array[i].indexOf(search) === 0 &&
                search.length < array[i].length) {
                matches.push(array[i]);
            }
        }
        return matches;
    };
})

.run(function($rootScope, $http, $timeout, $compile, Actions, RegionService, $ngRedux, QuestionActions, InteractionActions, EntitiesActions){
    var lazyCallMethod = _.debounce(Actions.callMethod, 1000, {leading: true, trailing: false});
    var handlers = (function(){
        var checklistRegionExists = false;

        // Check as we add QA Statuses if we have to reach out to the checklist tab and add
        // questions to the store.
        var homeStatusNewSaveProgramIds = [];
        var homeStatusOldSaveProgramIds = {};
        var qaProgramNewSaveIds = [];

        return {
            addLateChecklistHomeId: function(regionObject) {
                var homeId = regionObject.object.id;
                $ngRedux.dispatch(InteractionActions.setSetting('homeId', homeId));
            },
            reloadHomeStatusProgramProgressDisplay: function(regionObject) {
                var homestatusController = null;
                var reloadRegions = null;
                if (regionObject.type_name == "home_status") {
                    homestatusController = regionObject.controller;
                } else if (regionObject.parentRegionObject !== undefined) {
                    // Other regions are nested in home_status
                    homestatusController = regionObject.parentRegionObject.controller;
                } else {
                    // External regions
                    reloadRegions = _.filter(RegionService.helpers.regions, function(regionObject){
                        return regionObject.type_name == "home_status" && regionObject.object.id;
                    });
                }

                if (reloadRegions) {
                    _.forEach(reloadRegions, function(regionObject){
                        regionObject.controller.reloadProgramRequirements();
                        (regionObject.controller.reloadProgramRequirementsBar || angular.noop)();
                    });
                } else if (homestatusController && homestatusController.reloadProgramRequirements) {
                    homestatusController.reloadProgramRequirements();
                    (homestatusController.reloadProgramRequirementsBar || angular.noop)();
                }
            },
            reloadQAStatusProgramProgressDisplay: function(regionObject){
                var qaStatusController = null;
                var reloadRegions = null;
                if(regionObject.type_name == 'qa_status'){
                    qaStatusController = regionObject.controller;
                } else if (regionObject.parentRegionObject !== undefined){
                    // Other regions are nested in qa status
                    qaStatusController = regionObject.parentRegionObject.controller;
                } else {
                    // External regions
                    reloadRegions = _.filter(RegionService.helpers.regions, function(regionObject){
                        return regionObject.type_name == 'qa_status' && regionObject.object.id;
                    });
                }

                if(reloadRegions){
                    _.forEach(reloadRegions, function(regionObject){
                        if (regionObject.controller.reloadProgramRequirements) {
                            regionObject.controller.reloadProgramRequirements();
                            (regionObject.controller.reloadProgramRequirementsBar || angular.noop)();
                        }
                    });
                } else if (qaStatusController && qaStatusController.reloadProgramRequirements){
                    qaStatusController.reloadProgramRequirements();
                    (qaStatusController.reloadProgramRequirementsBar || angular.noop)();
                }
            },
            reloadAnalytics: function () {
                var reloadRegions = _.filter(RegionService.helpers.regions, function(regionObject){
                    return regionObject.type_name == "analytics";
                })
                _.forEach(reloadRegions, function(regionObject){
                    return Actions.callMethod('reload', regionObject).then(function(){
                        return regionObject;
                    });
                });
            },
            reloadFloatingChecklistStatusArea: function(regionObject) {
                if (checklistRegionExists) {
                    var checklistRegion = RegionService.getRegionFromTypeName('home_checklist_button');
                    return Actions.callMethod('reload', checklistRegion).then(function(){
                        return regionObject;
                    });
                }
                return regionObject;
            },
            reloadHomeStatus: function(regionObject) {
                var homestatusRegion = regionObject.parentRegionObject;
                var reloadRegions = [];
                if (homestatusRegion !== undefined) {
                    reloadRegions.push(homestatusRegion);
                } else {
                    reloadRegions = _.filter(RegionService.helpers.regions, function(regionObject){
                        return regionObject.type_name == "home_status";
                    });
                }
                _.forEach(reloadRegions, function(regionObject){
                    lazyCallMethod('reload', regionObject).then(handlers.reloadActiveFloorplan);
                });

                return regionObject;
            },
            reloadQAStatus: function(){
                var reloadRegions = _.filter(RegionService.helpers.regions, function(regionObject){
                    return regionObject.type_name == 'qa_status' && regionObject.object.id;
                });
                _.forEach(reloadRegions, function(regionObject){
                    lazyCallMethod('reload', regionObject);
                });

            },
            reloadEtoOutput: function(regionObject){
                var homestatusRegion = regionObject.parentRegionObject;
                if (homestatusRegion){
                    var element = $(homestatusRegion.$element).find('.eto-calculations-legacy-output');
                    if (element.length !== 0) {
                        element.scope().etoInit();
                    }
                }
            },
            reloadAnnotationsDisplay: function(regionObject){
                var controller = regionObject.controller;
                var annotationsRegion = null;
                for (var i in controller.children) {
                    if (controller.children[i].type_name == 'home_status_annotations') {
                        annotationsRegion = controller.children[i];
                        break;
                    }
                }

                if (annotationsRegion) {
                    return Actions.callMethod('reload', annotationsRegion).then(function(){
                        return regionObject;
                    });
                }
                return regionObject;
            },
            reloadActiveFloorplan: function(regionObject){
                if (regionObject.type_name == "floorplan") {
                    regionObject = regionObject.parentRegionObject;
                }

                // Find the floorplan region based on the homestatus's regionObject
                var activeFloorplanRegionObject = _.filter(regionObject.controller.children, function(child){
                    return child.type_name == "floorplan";
                })[0];
                if (activeFloorplanRegionObject !== undefined) {
                    Actions.callMethod('reload', activeFloorplanRegionObject);
                }
            },
            reloadAllFloorplans: function(){
                var floorplans = RegionService.getRegionFromTypeName('floorplan') || [];
                floorplans = _.isArray(floorplans) ? floorplans : [floorplans];
                _.forEach(floorplans, function(floorplan){
                    floorplan.controller.handleAction('reload');
                });
            },
            reloadRelationshipSidebar: function(regionObject) {
                var homeRegion = RegionService.getRegionFromTypeName('home');
                var relRegion = RegionService.getRegionFromTypeName('home_relationships');
                relRegion = _.isArray(relRegion) ? relRegion : [relRegion];
                _.forEach(relRegion, function(region){
                    region.controller.handleAction('reload');
                });
                build_relationship_sidebar(null, homeRegion);
                return regionObject;
            },
            reloadHistory: function(regionObject){
                $('[id^=history][id$=wrapper].dataTables_wrapper table').each(function(i, el){
                    $(el).dataTable().fnDraw();
                });

                return regionObject;
            },
            clearQAFields: function(regionObject){
                // The way we merge the objects that return from the server don't always clear values.
                regionObject.object.new_state = null;
                if (regionObject.object.state !== "complete") {
                    regionObject.object.result = null;
                }
                regionObject.object.note = null;
                regionObject.object.observation_types = [];

                // We need to get rid of any documents that they just added.
                var documents = RegionService.getRegionFromTypeName('qanote_documents');
                documents = angular.isArray(documents) ? documents : [documents];
                if(documents.length && documents[0] && documents[0].object.id){
                    var regionSet = documents[0].parentRegionSet;
                    // Need to remove from RegionService so things don't try and reload
                    angular.forEach(regionSet.regions, function(region){
                        RegionService.removeRegion(region);
                    });
                    // The simplest way to clear the regions, since the remove method is self referential
                    regionSet.regions.length = 0;
                    // Get a fresh form so the user can save a new note.
                    regionSet.fetchNewRegion();
                }

                return regionObject;
            },
            populateBLGFields: function(regionObject){
                // Reads the response data from the BLG upload and allocates it to the page regions.
                // regionObject.blg_data is the in-memory response payload, merged in after save
                var data = regionObject.blg_data;
                addDataToRegion(RegionService.getRegionFromTypeName('home'), data.home);
                addDataToRegion(RegionService.getRegionFromTypeName('home_relationships'), data.home_relationships);
                ensureProgram(data.home_status, function(){
                    data.floorplan.remrate_data_file_raw = regionObject.object.blg_file_raw;
                    data.floorplan.remrate_data_file_raw_name = regionObject.object.blg_file_raw_name;
                    ensureFloorplan(data.floorplan);
                });

                function addDataToRegion(regionObject, data){
                    function nonNullableFields(o){
                        return _.isBoolean(o) || _.isNull(o) || _.isUndefined(o);
                    }
                    _.reject(regionObject.visible_fields, function(key){
                        return nonNullableFields(regionObject.object[key])
                    }).forEach(function(key){
                        if(_.isArray(regionObject.object[key])){
                            // Keep arrays as arrays.
                            regionObject.object[key].length = 0;
                        } else {
                            regionObject.object[key] = null;
                        }
                    });
                    regionObject.errors = {};
                    console.log("Inserting data into region:", regionObject.type_name, data);
                    var hasErrors = false;
                    var errors = {};
                    for (var i in data) {
                        if (/_name$/.test(i) && !isNaN(parseInt(data[i.replace(/_name$/, '')]))) {
                            // skip over *_name items if there is a matching *_id item
                            continue;
                        }
                        if (_.isArray(data[i])) {
                            var array = regionObject.object[i];
                            array.length = 0;
                            array.push.apply(array, data[i]);
                        } else {
                            regionObject.object[i] = data[i];
                        }
                        if (data[i + '_name'] !== undefined && data[i + '_name'] !== null) {
                            if (data[i] === null || data[i].length === 0) {
                                // Data was provided, but no match in Axis was readily found
                                errors[i] = ["No exact match in Axis found for '" + data[i + '_name'] + "'"];
                                hasErrors = true;
                            } else {
                                if (/_raw$/.test(i)) {
                                    // alternate version of a value label
                                    regionObject.fields[i.replace(/_raw$/, '')].value = data[i + '_name'];
                                } else {
                                    var value = data[i];
                                    var label = data[i + '_name'];
                                    if (_.isArray(value)) {
                                        label = [label];
                                    }
                                    forceUpdateLabel(regionObject, i, value, label);
                                }
                            }
                        }
                    }
                    if (hasErrors) {
                        regionObject.controller.error(errors);
                    }
                }

                function forceUpdateLabel(regionObject, field_name, value, label) {
                    var element = regionObject.controller.axisFields[field_name];
                    regionObject.fields[field_name].value = value;
                    regionObject.fields[field_name].value_label = label;

                    var scope;
                    var item;

                    item = {id: value, text: label};
                    if (_.isArray(value)) {
                        item.id = value[0];
                        item.text = label[0];
                    }
                    scope = angular.element(element.find('[ui-select-helper]')[0]).scope();
                    if (scope !== undefined && angular.isUndefined(_.find(scope.selectOptions, {id: item.id}))) {
                        scope.selectOptions.push(item);
                    }

                    updateMultiSelectFieldLabel(regionObject, field_name, value, label);
                }

                function _ensureRegion(root, type_name, data, wait_for_type, callback) {
                    var region = RegionService.getRegionFromTypeName(type_name);
                    callback = (callback === undefined ? function(){} : callback)
                    if (region === undefined) {
                        var scope = angular.element(root.find('axis-region-set[options*='+type_name+']')).isolateScope();
                        if (scope.regionSet === undefined) {
                            return;
                        }

                        // Trick regionset into thinking we had 1 preloaded region so that we can correctly
                        // listen for a "RegionSetLoaded" signal that marks it as finished loading
                        scope.regionSet.endpoints.length = 0;
                        scope.regionSet.endpoints.push(null);

                        // Ask for new region
                        scope.regionSet.fetchNewRegion();

                        // Wait for region to finish loading, then get object and push data
                        var unwatch = $rootScope.$on('RegionSetLoaded:'+(wait_for_type || type_name), function(ctrl, element){
                            region = RegionService.getRegionFromTypeName(type_name);
                            addDataToRegion(region, data);
                            if (wait_for_type !== undefined) {
                                _ensureRegion(root, wait_for_type, {}, undefined, callback);
                            } else {
                                callback();
                            }
                            unwatch();
                        });

                    } else { // region or array of regions
                        if (region.length !== undefined) {
                            region = region[0];
                        }
                        addDataToRegion(region, data);
                        callback();
                    }
                }
                function ensureProgram(data, fnThen){
                    _ensureRegion($(document), 'home_status', data, 'floorplan', fnThen);
                }
                function ensureFloorplan(data){
                    var homestatus_node = $('axis-region-set[options*=home_status]');
                    _ensureRegion(homestatus_node, 'floorplan', data);
                }
            },
            updateInternalQANotesList: function(regionObject){
                if(regionObject.object.id){
                    regionObject.object.qanote_documents = [];
                    var documents = RegionService.getRegionFromTypeName('qanote_documents');

                    if (!documents) {
                        return;
                    }

                    documents = angular.isArray(documents) ? documents : [documents];
                    angular.forEach(documents, function(document){
                        if(document.object.document_raw_name){
                            regionObject.object.qanote_documents.push(document.object);
                        }
                    });
                }
                return regionObject;
            },

            // Checklist
            updateNewAndOldProgramIdCache: function(regionObject){
                const regionId = regionObject.object.id;
                if(!regionId){
                    homeStatusNewSaveProgramIds.push(regionObject.object.eep_program);
                } else {
                    homeStatusOldSaveProgramIds[regionId] = regionObject.object.eep_program
                }
            },
            updateChecklist: function(regionObject){
                var homeStatus = regionObject;
                if (regionObject.type_name === 'floorplan') {
                    homeStatus = regionObject.parentRegionObject;
                }

                if (homeStatus.helpers.collection_request) {
                    $ngRedux.dispatch(EntitiesActions.discoverCollectors(homeStatus.helpers.collection_request));
                }
            },
            updateQaRequirementIdCache: function(regionObject){
                if(!regionObject.object.id){
                    qaProgramNewSaveIds.push(regionObject.object.requirement);
                }
            }
        };
    })();

    var eventsInfo = {
        // Top half of page
        blg_creator_fills_out_regions: {
            handler: handlers.populateBLGFields, events: ['save'],
            regions: ['home_blg']
        },
        satellite_relationships_watch_homestatus: {
            handler: handlers.reloadRelationshipSidebar, events: ['save', 'delete'],
            regions: ['home_status']
        },
        satellite_checklist_button_watches_homestatus: {
            handler: handlers.reloadFloatingChecklistStatusArea, events: ['save'],
            regions: ['home_status', 'home_status_annotations']
        },

        // Programs tab
        homestatus_watches_region_updates: {
            handler: handlers.reloadHomeStatus, events: ['save'],
            regions: ['qa_status', 'home_status_annotations', 'floorplan', 'home_relationships']
        },
        annotations_watches_home_status: {
            handler: handlers.reloadAnnotationsDisplay, events: ['save'],
            regions: ['home_status']
        },
        program_requirements_watches_region_updates: {
            handler: handlers.reloadHomeStatusProgramProgressDisplay, events: ['save'],
            regions: ['home_status', 'home_status_annotations', 'floorplan', 'home_relationships', 'qa_status']
        },
        program_requirements_watches_region_removals: {
            handler: handlers.reloadHomeStatusProgramProgressDisplay, events: ['delete'],
            regions: ['floorplan']
        },
        stale_active_floorplan_reloads_to_acquire_update: {
            handler: handlers.reloadActiveFloorplan, events: ['delete'],
            regions: ['floorplan']
        },
        floorplan_refreshes_others_for_potential_loss_of_active_status: {
            // This is a little over-zealous, since it probably reloads programs from other programs
            handler: handlers.reloadAllFloorplans, events: ['save'],
            regions: ['floorplan']
        },
        homestatus_exit_refreshes_floorplans_for_new_active_after_possible_upload_event: {
            // This allows external events that were fired when the homestatus was in edit mode to
            // finally update floorplans.  I'm hard pressed for an example while documenting this.
            handler: handlers.reloadAllFloorplans, events: ['exit'],
            regions: ['home_status']
        },
        eto_watches_floorplan_updates: {
            handler: handlers.reloadEtoOutput, events: ['save', 'delete'],
            regions: ['floorplan']
        },
        home_status_hirl_project_updates: {
            /*
            * Update Invoice Items Group Region Set
            * */
            handler: function (regionObject) {
                let homestatusRegion = regionObject.parentRegionObject;

                // Update Invoice Item Group homestatus regions
                var homestatusItemGroupRegions =
                    RegionService.getRegionFromTypeName('invoice_home_status') || [];
                homestatusItemGroupRegions = _.isArray(homestatusItemGroupRegions) ? homestatusItemGroupRegions : [homestatusItemGroupRegions];
                _.forEach(homestatusItemGroupRegions, function(homestatusItemGroupRegion){
                    homestatusItemGroupRegion.controller.handleAction('reload');
                });

                $http({
                    method : 'GET',
                    url : '/api/v2/homestatus/'+ homestatusRegion.object.id +'/invoice_item_groups_machinery/'
                }).success(function(data, status) {
                    $rootScope.$broadcast('invoiceItemGroupMachineries', data);
                });
            },
            events: ['save'],
            regions: ['home_status_hirl_project']
        },
        hirl_invoice_item_updates: {
            handler: function(regionObject) {
                // reload InvoiceItemGroup region to update values
                let hirlInvoiceItemGroupRegion = regionObject.parentRegionObject;
                Actions.callMethod('reload', hirlInvoiceItemGroupRegion);

                // reload HomeStatus region to update values
                let homestatusItemGroupRegion = hirlInvoiceItemGroupRegion.parentRegionObject;
                Actions.callMethod('reload', homestatusItemGroupRegion);
            },
            events: ['save', 'delete'],
            regions: ['hirl_invoice_item']
        },
        // QA tab
        qa_form_clears_after_save: {
            handler: handlers.clearQAFields, events: ['save'],
            regions: ['qa_status']
        },
        qa_updates_internals_before_save: {
            type: 'pre',
            handler: handlers.updateInternalQANotesList, events: ['save'],
            regions: ['qa_status']
        },

        // Analytics tab
        analytics_watches_region_updates_watches_region_updates: {
            handler: handlers.reloadAnalytics, events: ['save', 'delete'],
            regions: ['home_status', 'home_status_annotations', 'floorplan', 'qa_status', 'home_relationships']
        },

        // Checklist tab
        push_home_id_to_checklist: {
            handler: handlers.addLateChecklistHomeId, events: ['save'],
            regions: ['home']
        },
        checklist_watches_homestatus: {
            handler: handlers.updateChecklist, events: ['save'],
            regions: ['home_status', 'qa_status']
        },
        checklist_watches_floorplan: {
            handler: handlers.updateChecklist, events: ['save', 'delete'],
            regions: ['floorplan']
        },

        // Legacy checklist
        homestatus_keeps_cache_of_program_ids: {
            type: 'pre',
            handler: handlers.updateNewAndOldProgramIdCache, events: ['save'],
            regions: ['home_status']
        },
        qastatus_keeps_cache_of_qa_requirement_ids: {
            type: 'pre',
            handler: handlers.updateQaRequirementIdCache, events: ['save'],
            regions: ['qa_status']
        },

        // History tab
        history_watches_regions_updates: {
            handler: handlers.reloadHistory, events: ['save'],
            regions: ['home', 'home_documents', 'base_floorplan']
        }
    };

    function noopActionHandler(regionObject){
        return regionObject;
    }
    var actionsInfo = {
        // Homestatus primary action alternates
        decertify: function(regionObject){
            return $http.post(regionObject.helpers.decertify_url).then(function(){
                lazyCallMethod('reload', regionObject);
                return regionObject;
            });
        },
        certify_today: function(regionObject){
            return $http.get(regionObject.helpers.certify_today_url).then(function(){
                lazyCallMethod('reload', regionObject);
                return regionObject;
            })
        },
        ready: function(regionObject){
            var data = {
                'action': 'qa_transition'
            };
            return $http.post(regionObject.helpers.state_transition_url, data).then(function(){
                lazyCallMethod('reload', regionObject);
                return regionObject;
            });
        },
        toggle_abandon: function(regionObject){
            var data = {
                'model_name': 'home.eepprogramhomestatus',
                'id': regionObject.object.id,
                'action': regionObject.helpers.next_state
            };
            var config = {
                'headers': {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            };
            return $http.post(regionObject.helpers.state_transition_url, $.param(data), config).then(function(){
                lazyCallMethod('reload', regionObject);
                regionObject.controller.success();
                return regionObject;
            }, function(data){
                regionObject.controller.error(data.data);
            });
        },
        multipleDocumentSave: function(regionObject){
            var regions = RegionService.getRegionFromTypeName(regionObject.type_name);
            angular.forEach(regions, function(region){
                if(region.controller.editing()){
                    region.controller.handleAction('save');
                }
            });
        },

        // Homestatus secondary action button events
        view_checklist: function(){
            // angular-ui router is not switching tabs for us anymore when the url changes so we're
            // compensating until someone figures out how to commune with the angular demon in a way
            // that it finds satisfying.
            var tabLink = $('[tab-helper][endpoint="tabs.checklist"] a');
            // $state.go(tabEndpoint);
            $timeout(function(){
                tabLink.click();
            });
        },
        upload_checklist: noopActionHandler,  // needed for modal
        manage_observations: noopActionHandler,  // needed for modal
        manage_tasks: noopActionHandler,  // needed for modal
        fasttrack: function(regionObject){
            return $http.post(regionObject.helpers.fasttrack_submission_url).then(function(){
                lazyCallMethod('reload', regionObject);
                return regionObject;
            }, function (response) {
                console.log("Error", response)
                regionObject.controller.error(response.data);
            });
        },
        resnet: function(regionObject){
            return $http.get(regionObject.helpers.resnet_submission_url).then(function () {
                Actions.callMethod('reload', regionObject);
                regionObject.controller.success();
                return regionObject;
            }, function (response) {
                console.log("Error", response)
                regionObject.controller.error(response.data);
            });

        },

        // Financial checklist internal actions
        financial_checklist: function(regionObject){
            return $http.post(regionObject.helpers.standarddisclosuresettings.url, regionObject.object);
        },
        clear_financial_checklist: function(regionObject){
            var data = regionObject.helpers.standarddisclosuresettings.question_data;
            for (var i in data) {
                for (var j in data[i].items) {
                    var name = data[i].items[j].name;
                    regionObject.object[name] = data[i].items[j].null_value;
                }
            }
            return regionObject;
        },

        // Financial checklist internal actions
        permitandoccupancysettings: function(regionObject){
            return $http.post(regionObject.helpers.permitandoccupancysettings.url, regionObject.object)
                .then(function(){
                    Actions.callMethod('reload', regionObject);
                });
        },
        clear_permitandoccupancysettings: function(regionObject){
            var data = regionObject.helpers.permitandoccupancysettings.question_data;
            for (var i in data) {
                for (var j in data[i].items) {
                    var name = data[i].items[j].name;
                    regionObject.object[name] = data[i].items[j].null_value;
                }
            }
            return regionObject;
        },

        /**
         * Trigger a HomeEnergyScore simulation
         * @param {object} regionObject
         */
        simulateHES: async function(regionObject) {
            /**
             * @var {RegionController} controller
             * @var {int} home_status_id Database ID of a EEPProgramHomeStatus
             * @var {string} simulation_endpoint URL of the HES API endpoint
             */
            const {
                controller,
                helpers: {
                    home_status_id,
                    hes_score_data: {
                        simulation_endpoint
                    }
                }
            } = regionObject;

            return $http.post(simulation_endpoint, { home_status_id }).then(
                // On success
                function() {
                    Actions.callMethod('reload', regionObject);
                    controller.success();
                },

                // On failure
                function(response) {
                    controller.error(response.data);
                }
            );
        },

        /**
         * Trigger an OpenStudio-ERI simulation
         * @param {object} regionObject
         */
        simulateOpenStudio: async function(regionObject) {
            /**
             * @var {RegionController} controller
             * @var {int} home_status_id Database ID of a EEPProgramHomeStatus
             * @var {string} simulation_endpoint URL of the HES API endpoint
             */
            const {
                controller,
                helpers: {
                    home_status_id,
                    open_studio_eri_data: { generate_url }
                }
            } = regionObject;

            const doReload = (regionObj) => {
                Actions.callMethod('reload', regionObj).then((regionObj) => {
                    const {helpers:{open_studio_eri_data: {status}}} = regionObj;
                    if ((status === "Pending") || (status === 'Started')  || (status === 'Retry')) {
                        window.setTimeout(() => doReload(regionObj), 2000);
                    }
                });
            }

            return $http.post(generate_url, { home_status_id }).then(
                // On success
                function() {
                    doReload(regionObject);
                    controller.success();
                },

                // On failure
                function(response) {
                    controller.error(response.data);
                }
            );
        },

        customer_hirl_qa_sync_batch: function(regionObject){
            if (regionObject.object.state !== "complete") {
                return Actions.callMethod('save', regionObject).then(function (regionObject) {
                    return $http.post(regionObject.helpers.customer_hirl_qa_sync_batch_endpoint, {}).then(function(response){
                        regionObject.controller.success();
                        return regionObject;
                    }, function(response){
                        regionObject.controller.error(response.data);
                    });
                });
            }
            return $http.post(regionObject.helpers.customer_hirl_qa_sync_batch_endpoint, {}).then(function (response) {
                regionObject.controller.success();
                return regionObject;
            }, function (response) {
                regionObject.controller.error(response.data);
            });

        },
        customer_hirl_certify_childrens: function(regionObject){
            return $http.post(regionObject.helpers.customer_hirl_certify_childrens_endpoint, {}).then(function (response) {
                Actions.callMethod('reload', regionObject);
                regionObject.controller.success();
                return regionObject;
            }, function (response) {
                regionObject.controller.error(response.data);
            });
        },
        customer_hirl_sync_documents_across_batch: function(regionObject){
            return $http.post(regionObject.helpers.customer_hirl_sync_documents_across_batch_endpoint, {}).then(function (response) {
                regionObject.controller.success();
                return regionObject;
            }, function (response) {
                regionObject.controller.error(response.data);
            });
        },
        updateProfile: function(regionObject){
            return window.open('/profile/' + window.user_id + "/", 'User Profile');
        }
    };


    // Register events
    _.forEach(eventsInfo, function(spec){
        _.forEach(spec.events, function(onEventName){
            var register = (spec.type === 'pre' ? Actions.addPreMethodToType : Actions.addPostMethodToType);
            register(onEventName, spec.regions, spec.handler);
        });
    });

    // Register actions
    _.forEach(actionsInfo, function(handler, actionName){
        Actions.addMethod(actionName, handler);
    });


    // Non-standard below this point ------------------------------------------

    // Track when the satellite checklist button first appears
    $rootScope.$on('addedRegion:home_checklist_button', function(event, regionObject){
        checklistRegionExists = true;
    });
    if (angular.isDefined(window.build_relationship_sidebar)){
        $rootScope.$on('SingleRegionLoaded:home:detailTemplateLoaded', build_relationship_sidebar);
    }

    // automatically create region after click button
    $rootScope.$on('addedRegion:hirl_invoice_item_group', function(event, regionObject){
        $timeout(function () {
            if (regionObject.controller) {
                regionObject.controller.handleAction('save');
            }
        }, 0);
    });

    // Reload HomeStatuses and QA Statuses when we switch away from the checklist tab
    var tab = {
        currentEndpoint: ''
    };
    var reloadProgress = _.debounce(function(){
        handlers.reloadHomeStatusProgramProgressDisplay({});
        handlers.reloadQAStatusProgramProgressDisplay({});
        handlers.reloadAnalytics();
        $rootScope.$broadcast('navigation:from_checklist');
    });

    $rootScope.$on('TabService.go', function(event, endpoint){
        var fromChecklist = tab.currentEndpoint.indexOf('checklist') > -1;
        var toChecklist = endpoint.indexOf('checklist') > -1;
        if (fromChecklist && !toChecklist){
            reloadProgress();
        }
        tab.currentEndpoint = endpoint;
    });
});

setInterval(function forceAnswerCommit(){
    var el = $('checklist-field input[ng-model="input.answer.data.input"]');
    if (el.length === 0) {
        return;
    }
    var input = angular.element(el).scope().input
    if (input.answer === undefined) {
        return;
    }
    input.hooks.update();
}, 1000)


function updateMultiSelectFieldLabel(regionObject, fieldName, value, label){
    /**
     * Utility function for updating the label of a <multi-select> element.
     * Places currently being used.
     *  Subdivision auto-populate.
     *  BLG auto populate.
     */
    var element = regionObject.controller.axisFields[fieldName];
    regionObject.fields[fieldName].value = value;
    regionObject.fields[fieldName].value_label = label;

    var scope = angular.element(element.find('[multi-select-helper]')[0]).scope();
    if(scope != undefined){
        var choicesValues = _.indexBy(scope.field.widget.choices, '0');
        if (!_.isArray(value)) {
            value = [value];
            label = [label];
        }
        for (var i in value) {
            if (angular.isUndefined(choicesValues[value[i]])) {
                scope.field.widget.choices.push([
                    value[i],
                    label[i]
                ]);
            }
        }

        scope.field.widget.choices.push([null, 'fake choice']);
        setTimeout(function(){
            /**
             * Alright. I'm so sorry. Now that we have that out of the way, here's whats going on.
             * For some reason angular won't update this widget unless something about the options
             * changes. In the case where the item we want to select is already in the list,
             * we don't want to push in a duplicate, so the widget doesn't update.
             * So... We're adding a fake choice, to trigger the update, then removing it so
             * the user won't see the hell we've brought.
             */
            scope.field.widget.choices.pop();
            scope.$digest();
        });
    }

}

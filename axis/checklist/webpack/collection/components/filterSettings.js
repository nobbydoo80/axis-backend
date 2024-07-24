import { questionFilters } from './../redux/selectors/questionFilters';

class FilterSettingsController {
    constructor($ngRedux, FilterActions){
        this.dispatch = $ngRedux.dispatch;
        this.FilterActions = FilterActions;
        this.showing = true;
    }
    resetFilters(e){
        e.preventDefault();
        this.dispatch(this.FilterActions.resetFilters());
    }
}

export function filterSettings(){
    return {
        scope: {},
        controller: FilterSettingsController,
        controllerAs: 'ctrl',
        template: `
            <h3 style="margin-top: 0;">Filter Options</h3>
            <div class="row">
                <div class="col-sm-12">
                    <a ng-click="ctrl.resetFilters($event)">
                        <i class="fa fa-fw fa-refresh"></i>
                        Reset Filters
                    </a>
                    <question-filter-setting-checkbox label="Question Display" prefix="Hide" lookup="states"></question-filter-setting-checkbox>
                    <question-filter-setting label="EEP Programs" lookup="programs"></question-filter-setting>
                    <question-filter-setting label="Checklist Sections" lookup="sections"></question-filter-setting>
                </div>
            </div>
        `
    }
}

class SingleFilterController {
    constructor($ngRedux, $scope, FilterActions){
        this.dispatch = $ngRedux.dispatch;
        this.FilterActions = FilterActions;

        this.toggleBox = this.createToggleAction(this.getFilterAction(this.lookup));

        $scope.$on('$destroy', $ngRedux.connect(questionFilters)(this));
    }
    createToggleAction(action){
        return function(data){
            if(!data) return;
            let {key, selected} = data;
            this.dispatch(action(key, selected));
        }
    }
    getFilterAction(key){
        return {
            'types': this.FilterActions.setTypeCheckbox,
            'states': this.FilterActions.setStateCheckbox,
            'sections': this.FilterActions.setSectionCheckbox,
            'programs': this.FilterActions.setProgramCheckbox
        }[key];
    }
}

export function filterSetting(){
    return {
        scope: {
            label: '@',
            lookup: '@'
        },
        controller: SingleFilterController,
        controllerAs: 'ctrl',
        bindToController: true,
        template: `
            <div class="form-group" ng-if="ctrl[ctrl.lookup].length > 1">
                <label>
                    [[ ctrl.label ]]
                </label>
                <multi-select
                    name="question_[[ ctrl.lookup ]]"
                    on-item-click="ctrl.toggleBox(data)"
                    helper-elements=""
                    button-label="name"
                    item-label="name"
                    input-model="ctrl[ctrl.lookup]"
                    output-model="ctrl.outputs"
                    tick-property="selected" >
                </multi-select>
            </div>
        `
    }
}

export function filterSettingCheckbox(){
    return {
        scope: {
            label: '@',
            lookup: '@',
            prefix: '@'
        },
        controller: SingleFilterController,
        controllerAs: 'ctrl',
        bindToController: true,
        template: `
            <div class="panel filter-panel panel-default form-group" ng-if="ctrl[ctrl.lookup].length > 1">
                <div class="panel-heading">[[ ctrl.label ]]</div>
                <ul class="list-group">
                    <li class="list-group-item" ng-repeat="box in ctrl[ctrl.lookup]">
                        <label>
                            <input type="checkbox" ng-checked="!box.selected" ng-click="ctrl.toggleBox({key: box.key, selected: !box.selected})"> [[ ctrl.prefix || '' ]] [[ box.name ]] &emsp;
                        </label>
                    </li>
                </ul>
            </div>
        `
    }
}

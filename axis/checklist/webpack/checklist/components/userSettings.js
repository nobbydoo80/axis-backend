import { DISPLAY_LABELS, DISPLAY_ORDER, INTERACTION_LABELS, INTERACTION_ORDER, DISPLAY_CAN_SHOW } from './../settings';

class UserSettingsController {
    constructor($ngRedux, $scope, InteractionActions){
        this.dispatch = $ngRedux.dispatch;
        this.labels = _.assign({}, INTERACTION_LABELS, DISPLAY_LABELS);
        this.InteractionActions = InteractionActions;
        this.interactionOrder = INTERACTION_ORDER;
        this.displayOrder = DISPLAY_ORDER;

        $scope.$on('$destroy', $ngRedux.connect(this.mapStateToThis.bind(this))(this));
    }
    mapStateToThis(state){
        let { interactions, display } = state.settings;
        DISPLAY_CAN_SHOW;

        display = _.omit(display, (value, key) => !DISPLAY_CAN_SHOW[key](state));
        let showDisplay = !!Object.keys(display).length;

        return { interactions, display, showDisplay};
    }
    toggleSetting(key, value){
        this.dispatch(this.InteractionActions.setInteractionSetting(key, !value));
    }
}

export function userSettings(){
    return {
        scope: {},
        controller: UserSettingsController,
        controllerAs: 'ctrl',
        template: `
        <h3>User Settings</h3>
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Interaction Settings</h3>
            </div>
            <div class="list-group">
                <label class="list-group-item" ng-repeat="key in ctrl.interactionOrder">
                    <input type="checkbox" ng-checked="ctrl.interactions[key]" ng-click="ctrl.toggleSetting(key, ctrl.interactions[key])" /> [[ ::ctrl.labels[key] ]]
                </label>
            </div>
            <div class="panel-heading" ng-if="ctrl.showDisplay">
                <h3 class="panel-title">Display Settings</h3>
            </div>
            <div class="list-group" ng-if="ctrl.showDisplay">
                <label class="list-group-item" ng-repeat="key in ctrl.displayOrder">
                    <input type="checkbox" ng-checked="ctrl.display[key]" ng-click="ctrl.toggleSetting(key, ctrl.display[key])" /> [[ ::ctrl.labels[key] ]]
                </label>
            </div>
        </div>`,
    }
}

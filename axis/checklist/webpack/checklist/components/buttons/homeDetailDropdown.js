export function homeDetailDropdown(){
    return {
        scope: {},
        controller: function($ngRedux){
            let homeId = $ngRedux.getState().settings.homeId;
            this.homeDetailUrl = `/home/${homeId}/`;
        },
        controllerAs: 'ctrl',
        template: `
        <div class="btn-group">
            <a role="button" ui-sref="checklist()" class="btn btn-default btn-xs">Home Detail</a>
            <a ng-href="[[ ctrl.homeDetailUrl ]]" target="_blank" class="btn btn-default btn-xs"
                tooltip="View full detail" tooltip-placement="bottom"
            >
                <i class="fa fa-external-link"></i>
            </a>
        </div>
        `
    }
}

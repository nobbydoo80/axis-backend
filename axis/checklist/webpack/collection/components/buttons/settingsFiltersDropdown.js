export function settingsButton(){
    return {
        scope: {},
        controller: function($ngRedux, FilterActions){
            this.resetFilters = (e) => {
                e.preventDefault();
                $ngRedux.dispatch(FilterActions.resetFilters());
            }
        },
        controllerAs: 'ctrl',
        template: `
            <a ui-sref="checklist.settings()" class="btn btn-default btn-xs">
                <i class="fa fa-fw fa-cog"></i>
                Settings
            </a>
        `
    }
}

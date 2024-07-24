export function searchField(){
    return {
        scope: {},
        template: `<input type='text' class='form-control' placeholder='Search...' ng-model='ctrl.searchString'/>`,
        controllerAs: 'ctrl',
        controller: function($ngRedux, $scope, FilterActions){
            const getSearchString = () => this.searchString;
            const setSearchString = (newVal, oldVal) => $ngRedux.dispatch(FilterActions.setSearchString(newVal));

            $scope.$on('$destroy', $scope.$watch(getSearchString, setSearchString));
            $scope.$on('$destroy', $ngRedux.connect(mapStateToThis.bind(this))(this));

            function mapStateToThis(state){
                return {
                    searchString: state.filters.searchString
                };
            }
        }
    }
}

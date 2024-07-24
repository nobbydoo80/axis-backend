import { previousQuestionId, nextQuestionId } from './../../redux/selectors/currentQuestion';

class ChecklistActionsController {
    constructor($ngRedux, $scope){
        $scope.$on('$destroy', $ngRedux.connect(this.mapStateToThis.bind(this))(this));
    }
    saveDisabled(){
        return this.isSaveDisabled || this.isSaving;
    }
    mapStateToThis(state){
        return {
            previousDisabled: previousQuestionId(state) === false,
            nextDisabled: nextQuestionId(state) === false
        };
    }
}

export function checklistActions(){
    return {
        scope: {
            previous: '&',
            save: '&',
            isSaveDisabled: '=',
            isSaving: '=',
            next: '&'
        },
        controller: ChecklistActionsController,
        controllerAs: 'actions',
        bindToController: true,
        template: `
        <div class='btn-group'>
            <a class='btn btn-default' ng-disabled="actions.previousDisabled" ng-click='actions.previous()'><i class='fa fa-angle-double-left'></i> Prev</a>
            <a class='btn btn-primary' ng-click='actions.save()' ng-disabled='actions.saveDisabled()'>
                <i class="fa fa-fw fa-spinner fa-spin" ng-show="actions.isSaving"></i>
                Save
            </a>
            <a class='btn btn-default' ng-disabled="actions.nextDisabled" ng-click='actions.next()'>Next <i class='fa fa-angle-double-right'></i></a>
        </div>
        `
    }
}

import { questionsStatistics } from './../../redux/selectors/questionStatistics';

export function checklistProgressBar(){
    return {
        controller: function($scope, $ngRedux){
            $scope.$on('$destroy', $ngRedux.connect(questionsStatistics)(this));
            $scope.$on('$destroy', $ngRedux.connect(state => {
                return { processing: state.settings.savingAnswer}
            })(this));

            this.getKlasses = () => {
                return this.processing ? 'progress-bar-striped active' : '';
            }

            this.calculateSuccess = () => {
                return this.answeredRequiredQuestions / this.totalQuestions * 100
            }
            this.calculateInfo = () => {
                return this.answeredOptionalQuestions / this.totalQuestions * 100;
            }
        },
        controllerAs: 'ctrl',
        template: `
        <div ng-if="ctrl.totalQuestions">
            <h5>
                <div> [[ ctrl.remainingRequiredQuestions ]] of [[ ctrl.totalRequiredQuestions ]] Required Questions Remaining. </div>
                <div ng-if="ctrl.totalOptionalQuestions"> [[ ctrl.remainingOptionalQuestions ]] of [[ ctrl.totalOptionalQuestions ]] Optional Questions Remaining. </div>
            </h5>
            <progress>
                <bar class="[[ ctrl.getKlasses() ]]" value="ctrl.calculateSuccess()" type="success"></bar>
                <bar class="[[ ctrl.getKlasses() ]]" value="ctrl.calculateInfo()" type="info"></bar>
            </progress>
        </div>
        `
    }
}

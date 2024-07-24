class ChecklistAppController {
    constructor($ngRedux, QuestionActions, InteractionActions, EntitiesActions){
        this.dispatch = $ngRedux.dispatch;
        this.QuestionActions = QuestionActions;
        this.InteractionActions = InteractionActions;
        this.EntitiesActions = EntitiesActions;
        if(!angular.isArray(this.eepProgramId)) this.eepProgramId = [this.eepProgramId];

        this.initSettings();
        this.initData();
    }
    initSettings(){
        this.dispatch(this.InteractionActions.setSetting('homeId', this.homeId));
        this.dispatch(this.InteractionActions.setSetting('debug', this.debug));
        this.dispatch(this.InteractionActions.setSetting('eepProgramIds', this.eepProgramId))
    }
    initData(){
        this.dispatch(this.QuestionActions.fetchQuestions(this.eepProgramId.sort().map(id => this.getUrl(id))));
        this.dispatch(this.EntitiesActions.fetchPrograms());
    }
    getUrl(programId){
        return `/api/v2/checklist/${this.homeId}/${programId}/questions/`;
    }
}

export function checklistApp(){
    return {
        scope: {
            homeId: '=',
            eepProgramId: '=',
            debug: '='
        },
        controller: ChecklistAppController,
        controllerAs: 'checklist',
        bindToController: true,
        template: `
        <div class="row">
            <div class="col-sm-3">
                <checklist-progress-bar></checklist-progress-bar>
                <hr>
                <question-filter-settings></question-filter-settings>
                <user-settings></user-settings>
            </div>
            <div class="col-sm-9">
                <div ui-view="detail"></div>
                <hr>
                <question-list></question-list>
            </div>
        </div>
        `
    }
}

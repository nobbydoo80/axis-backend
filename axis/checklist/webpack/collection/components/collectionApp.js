import { collector } from '../collector';

class CollectionAppController {
    constructor($http, $ngRedux, QuestionActions, InteractionActions, EntitiesActions){
        this.$http = $http;
        this.dispatch = $ngRedux.dispatch;
        this.getState = $ngRedux.getState;
        this.QuestionActions = QuestionActions;
        this.InteractionActions = InteractionActions;
        this.EntitiesActions = EntitiesActions;

        this.initSettings();
        this.initData();
    }
    initSettings(){
        this.dispatch(this.InteractionActions.setSetting('homeId', this.homeId));
        this.dispatch(this.InteractionActions.setSetting('debug', window.allow_debug));
    }
    initData(){
        if (this.homeId) {
            this.dispatch(this.EntitiesActions.discoverCollectors());
        }
    }
}

export function collectionApp(){
    return {
        scope: {
            homeId: '='
        },
        controller: CollectionAppController,
        controllerAs: 'collection',
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

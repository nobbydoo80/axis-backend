class QuestionDetailController {
    constructor($ngRedux, $scope, $sce, AnswerActions, InteractionActions){
        this.dispatch = $ngRedux.dispatch;
        this.trustAsHtml = $sce.trustAsHtml;
        this.AnswerActions = AnswerActions;
        this.InteractionActions = InteractionActions;

        this.data = { answer: false, comment: '', documents: [] };
        this.initNavigation();

        this.callbacks = {
            multipleChoiceAnswerCallback: this.multipleChoiceAnswerCallback.bind(this),
            openAnswerCallback: this.openAnswerCallback.bind(this)
        }

        $scope.$on('$destroy', $ngRedux.connect(this.mapStateToThis.bind(this))(this));
    }
    getAnswer(state, question){
        if(question.answer){
            return state.entities.answers[question.answer];
        } else if(state.entities.temporaryAnswer[question.id]){
            return state.entities.temporaryAnswer[question.id];
        } else {
            return { answer: false, comment: '', documents: [] };
        }
    }
    mapStateToThis(state){
        let { questions, answers, relatedAnswers, errors } = state.entities;
        let questionId = state.router.currentParams.id;

        let questionObj = questions[questionId] || {};
        let answerObj = answers[questionObj.answer];
        errors = errors[questionId];
        let relatedAnswer = questionObj.related_answer ? relatedAnswers[questionObj.related_answer] : false;

        let { 'savingAnswer': isSaving, 'interactions': interactionSettings, debug } = state.settings;
        let showRelatedAnswers = state.settings.display.showRelatedAnswers;

        let answerData = this.getAnswer(state, questionObj);
        let isSaveDisabled = this.getIsSaveDisabled(answerData);

        return {
            question: questionObj,
            answer: answerObj,
            data: answerData,
            isSaveDisabled,

            relatedAnswer, errors, interactionSettings, isSaving,
            showRelatedAnswers, debug
        };
    }
    getIsSaveDisabled(answer){
        if(answer.id){
            return true;
        } else if(!answer.answer){
            return true;
        } else if(answer.customer_documents.length > 0){
            return _.filter(answer.customer_documents, document => !!document.isLoading).length > 0
        } else {
            return false;
        }
    }
    initNavigation(){
        this.gotoNext = () => this.dispatch(this.InteractionActions.gotoNextQuestion(this.question.id));
        this.gotoPrevious = () => this.dispatch(this.InteractionActions.gotoPreviousQuestion(this.question.id));
    }
    triggerSave(){
        this.dispatch(this.AnswerActions.saveAnswer(this.data, this.question.id));
    }
    multipleChoiceAnswerCallback(choice, triggerSave=false){
        this.data.answer = choice.choice;
        this.selectedChoice = choice;
        this.dispatch(this.AnswerActions.storeTemporaryAnswer(this.data.answer, this.question, triggerSave));
    }
    openAnswerCallback(answer, triggerSave=false){
        this.data.answer = answer;
        this.dispatch(this.AnswerActions.storeTemporaryAnswer(this.data.answer, this.question, triggerSave));
    }
    documentCallback(name, file, extension){
        this.dispatch(this.AnswerActions.storeDocument({name, file, extension}, this.question.id));
    }
    removeDocument(doc){
        this.dispatch(this.AnswerActions.removeDocument(doc.name, this.question.id));
    }
    updateComment(comment){
        this.data.comment = comment;
        this.dispatch(this.AnswerActions.updateComment(this.data.comment, this.question.id));
    }
    retract(){
        this.dispatch(this.AnswerActions.retractAnswer(this.answer));
    }
}

export function questionDetail(){
    return {
        controller: QuestionDetailController,
        controllerAs: 'detail',
        template: `
            <div class="row">
                <div class="col-xs-12">
                    <div class="row">
                        <div class="col-xs-6">
                            <checklist-actions
                                previous="detail.gotoPrevious()"
                                save="detail.triggerSave()"
                                next="detail.gotoNext()"
                                is-save-disabled="detail.isSaveDisabled"
                                is-saving="detail.isSaving"
                            ></checklist-actions>
                        </div>
                        <div class="col-xs-6 text-right">
                            <retract answer="detail.answer" retract-callback="detail.retract()"></retract>
                        </div>
                    </div>
                    <br>
                    <!--Question-->
                    <div class="row" style="min-height: 3.5em;">
                        <div class="col-md-12">
                            <p><strong>[[ detail.question.question ]]</strong></p>
                        </div>
                    </div>
                    <!--Related Answer-->
                    <div class="row" ng-if="detail.showRelatedAnswers && detail.relatedAnswer.id">
                        <div class="col-xs-10">
                            <checklist-field
                                question="detail.question"
                                answer="detail.relatedAnswer"
                                is-related-answer="true"
                                is-disabled="true"
                            ></checklist-field>
                        </div>
                        <div class="col-xs-2">
                            <answered-by answer="detail.relatedAnswer"></answered-by>
                            <pending-review answer="detail.relatedAnswer"></pending-review>
                            <answer-misc answer="detail.relatedAnswer"></answer-misc>
                        </div>
                    </div>
                    <!--Answer-->
                    <div class="row">
                        <div class="col-xs-10">
                            <checklist-field
                                question="detail.question"
                                answer="detail.answer"
                                callbacks="detail.callbacks"
                                is-disabled="!!detail.answer.id || detail.question.readonly"
                            ></checklist-field>
                        </div>
                        <div class="col-xs-2">
                            <answered-by answer="detail.answer"></answered-by>
                            <pending-review answer="detail.answer"></pending-review>
                            <answer-misc answer="detail.answer" ng-if="detail.answer.id"></answer-misc>
                            <choice-misc answer="detail.answer" ng-if="!detail.answer.id"></choice-misc>
                        </div>
                    </div>
                    <!--Errors-->
                    <div class="row" ng-if="detail.errors">
                        <div class="col-xs-12">
                            <ul class="list-group">
                                <list class="list-group-item list-group-item-danger" ng-repeat="error in detail.errors">[[ error ]]</list>
                            </ul>
                        </div>
                    </div>
                    <!--Comments-->
                    <div class="row">
                        <!--Related Comment-->
                        <div class="col-xs-12" ng-if="detail.showRelatedAnswers && detail.relatedAnswer.id && detail.relatedAnswer.comment">
                            <comment-display
                                label="Original Comment"
                                comment="detail.relatedAnswer.comment"
                                commenter="detail.relatedAnswer.full_name"
                            ></comment-display>
                        </div>
                        <!--Comment-->
                        <div class="col-xs-12">
                            <comment-field
                                comment-required="detail.selectedChoice.comment_required"
                                change-callback="detail.updateComment(comment)"
                                question="detail.question"
                                answer="detail.answer"
                            ></comment-field>
                        </div>
                    </div>
                    <!--Documents-->
                    <div class="row">
                        <div class="col-xs-12">
                            <file-table
                                label="Documents[[ detail.selectedChoice.document_required ? '*' : '' ]] and Photos[[ detail.selectedChoice.photo_required ? '*' : '' ]]"
                                accepted-types=".txt .pdf .doc .docx .xls .xlsx .png .jpeg .jpg"
                                documents="detail.data.customer_documents"
                                documents-uploader="detail.answer.full_name"
                                related-documents="detail.relatedAnswer.customer_documents"
                                related-documents-uploader="detail.relatedAnswer.full_name"
                                show-related-documents="detail.showRelatedAnswers"
                                can-add="!detail.answer.id"
                                add-callback="detail.documentCallback(name, file, raw, extension)"
                                remove-callback="detail.removeDocument(doc)"
                            ></file-table>

                        </div>
                    </div>
                    <!--Description-->
                    <div ng-if="detail.question.description">
                        <button class="btn btn-link" ng-click="showDescription=!showDescription">[[ !showDescription ? 'Show' : 'Hide' ]] Description</button>
                        <p collapse="!showDescription" ng-bind-html="detail.trustAsHtml(detail.question.description)"></p>
                    </div>
                </div>
                <span ng-if="::detail.debug">[[ detail.question|json ]]</span>
            </div>
        `
    }
}

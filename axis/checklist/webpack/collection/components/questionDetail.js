import { collector } from '../collector';


class QuestionDetailController {
    constructor($ngRedux, $scope, $sce, AnswerActions, InteractionActions){
        this.getState = $ngRedux.getState;
        this.dispatch = $ngRedux.dispatch;
        this.trustAsHtml = $sce.trustAsHtml;
        this.AnswerActions = AnswerActions;
        this.InteractionActions = InteractionActions;

        this.initNavigation();
        this.hooks = {
            update: this.update.bind(this)
        }

        $scope.$on('$destroy', $ngRedux.connect(this.mapStateToThis.bind(this))(this));
    }
    mapStateToThis(state){
        let { questions, errors } = state.entities;
        let { 'savingAnswer': isSaving, 'interactions': interactionSettings, display, debug } = state.settings;

        let measure = state.router.currentParams.id;
        let question = questions[measure] || {};
        if (question.collection_request === undefined) {
            return {};
        }

        function getAnswerObj(measure) {
            let answer = state.entities.answers[measure];
            let tempAnswer = state.entities.temporaryAnswer[measure];
            return answer || tempAnswer || {data: {input: null, comment: null}, customer_documents: []};
        }

        let answer = getAnswerObj(measure);
        let activeRole = collector.collectors[question.collection_request].full_specification.user_role;

        let documentTypeRequired = (answer.selectedChoice && (answer.selectedChoice.image_required || answer.selectedChoice.document_required));
        let isValid = (
            (answer.data && answer.data.input) &&
            (!answer.selectedChoice || !answer.selectedChoice.comment_required || !!answer.data.comment) &&
            (!documentTypeRequired || answer.customer_documents.length)
        );
        let isDisabled = (
            question.read_only === true ||
            question.user_role != activeRole ||
            answer.id !== undefined ||
            (answer.user_role && answer.user_role != question.user_role)
        );
        let saveDisabled = (
            isDisabled || !isValid
        );
        let canRetract = (
            answer.id !== undefined && (answer.is_failure === false || answer.failure_is_reviewed === true) &&
            question.read_only === false
        );

        return {
            activeRole,
            question,
            answer,
            relatedAnswer: state.entities.relatedAnswers[measure],
            errors: errors[measure],
            showRelatedAnswers: display.showRelatedAnswers,
            interactionSettings, isValid, isDisabled, saveDisabled, isSaving, canRetract, debug
        };
    }
    initNavigation(){
        this.next = () => this.dispatch(this.InteractionActions.gotoNextQuestion(this.question.measure));
        this.previous = () => this.dispatch(this.InteractionActions.gotoPreviousQuestion(this.question.measure));
    }

    /* Widget interactivity */
    clear() {
        this.dispatch(this.AnswerActions.clear(this.question.measure));
    }
    update(save=false, selectedChoice=undefined){
        this.dispatch(this.AnswerActions.stage(this.question, this.answer.data, selectedChoice));
        if (save) {
            this.save();
        }
    }
    save(){
        this.dispatch(this.AnswerActions.save(this.question, this.answer.data, this.answer.customer_documents));
    }
    retract(){
        this.dispatch(this.AnswerActions.retract(this.question.measure));
    }

    documentCallback(name, file, extension){
        this.dispatch(this.AnswerActions.storeDocument({name, file, extension}, this.question.measure));
    }
    removeDocument(doc){
        this.dispatch(this.AnswerActions.removeDocument(doc.name, this.question.measure));
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
                                previous="detail.previous()"
                                save="detail.save()"
                                next="detail.next()"
                                is-save-disabled="detail.saveDisabled"
                                is-saving="detail.isSaving"
                            ></checklist-actions>
                        </div>
                        <div class="col-xs-6 text-right">
                            <a class="btn btn-default btn-xs" ng-if="detail.canRetract" ng-click="detail.retract()">Retract</a>
                        </div>
                    </div>
                    <br>

                    <!--Question-->
                    <div class="row" style="min-height: 3.5em;">
                        <div class="col-md-12">
                            <p><strong>[[ detail.question.text ]]</strong></p>
                        </div>
                    </div>

                    <!--Related Answer-->
                    <div class="row" ng-if="detail.showRelatedAnswers && detail.relatedAnswer.id">
                        <div class="col-xs-10">
                            <checklist-field
                                hooks="detail.hooks"
                                question="detail.question"
                                answer="detail.relatedAnswer"
                                is-disabled="true"
                            ></checklist-field>
                        </div>
                        <div class="col-xs-2">
                            <answered-by answer="detail.relatedAnswer"></answered-by>
                            <pending-review answer="detail.relatedAnswer"></pending-review>
                            <answer-misc answer="detail.relatedAnswer"></answer-misc>
                        </div>
                    </div>

                    <!--Description-->
                    <div ng-if="detail.question.description">
                        <p ng-bind-html="detail.trustAsHtml(detail.question.description)"></p>
                    </div>

                    <!--Answer-->
                    <div class="row" ng-if="detail.showRelatedAnswers && !detail.relatedAnswer.id || !detail.question.read_only">
                        <div class="col-xs-10">
                            <checklist-field
                                hooks="detail.hooks"
                                question="detail.question"
                                answer="detail.answer"
                                is-disabled="detail.isDisabled"
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
                            <ul class="list-group" ng-repeat="(errorField, errorList) in detail.errors">
                                <list class="list-group-item list-group-item-danger" ng-repeat="error in errorList">[[ error ]]</list>
                            </ul>
                        </div>
                    </div>

                    <!--Comments-->
                    <div class="row">

                        <!--Related Comment-->
                        <div class="col-xs-12" ng-if="detail.showRelatedAnswers && detail.relatedAnswer.id && detail.relatedAnswer.data.comment">
                            <comment-display
                                label="Original Comment"
                                comment="detail.relatedAnswer.data.comment"
                                commenter="detail.relatedAnswer.user.full_name"
                            ></comment-display>
                        </div>

                        <!--Comment-->
                        <div class="col-xs-12">
                            <div class="form-group" ng-switch="detail.answer.id">
                                <div class="controls" ng-switch-when="undefined">
                                    <label class="control-label">Comment[[ detail.selectedChoice.comment_required ? '*' : '' ]]</label>
                                    <textarea
                                        ng-attr-placeholder="[[ detail.selectedChoice.comment_required ? "Comment Required..." : "Comment..." ]]"
                                        ng-model="detail.answer.data.comment"
                                        ng-disabled="detail.isDisabled"
                                        class="textarea form-control" />
                                </div>
                                <comment-display ng-switch-default
                                    ng-if="detail.answer.data.comment"
                                    comment="detail.answer.data.comment"
                                    commenter="detail.answer.user.full_name"
                                ></comment-display>
                            </div>
                        </div>
                    </div>

                    <!--Documents-->
                    <div class="row">
                        <div class="col-xs-12">
                            <file-table
                                label="Documents[[ detail.selectedChoice.document_required ? '*' : '' ]] and Photos[[ detail.selectedChoice.photo_required ? '*' : '' ]]"
                                accepted-types=".txt .pdf .doc .docx .xls .xlsx .png .jpeg .jpg"
                                documents="detail.answer.customer_documents"
                                documents-uploader="detail.answer.user.full_name"
                                related-documents="detail.relatedAnswer.customer_documents"
                                related-documents-uploader="detail.relatedAnswer.user.full_name"
                                show-related-documents="detail.showRelatedAnswers"
                                can-add="!detail.answer.id"
                                add-callback="detail.documentCallback(name, file, raw, extension)"
                                remove-callback="detail.removeDocument(doc)"
                            ></file-table>

                        </div>
                    </div>

                    <!--Expanded Help-->
                    <div ng-if="detail.question.help">
                        <button class="btn btn-link" ng-click="showHelp=!showHelp">[[ !showHelp ? 'Show' : 'Hide' ]] Help</button>
                        <p collapse="!showHelp" ng-bind-html="detail.trustAsHtml(detail.question.help)"></p>
                    </div>
                </div>
                <div ng-if="::detail.debug" ng-init="showDebugValues=true">
                    <button ng-click="showDebugValues=!showDebugValues">Debugging</button>
                    <dl class="dl-horizontal" ng-show="showDebugValues">
                        <dt><code>[[ detail.question.measure ]]</code></dt>
                        <dd><pre style="white-space: pre-line">
                            id=[[ detail.question.id ]]
                            measure=[[ detail.question.measure ]]
                            collection_request_id=[[ detail.question.collection_request ]]
                            read_only=[[ detail.question.read_only ]]
                        </pre></dd>
                        </dd>

                        <dt>data</dt>
                        <dd><code>[[ detail.answer.data|json ]]</code></dd>

                        <dt>related @<code>[[ detail.question.measure ]]</code></dt>
                        <dd><code>[[ detail.relatedAnswer|json ]]</code></dd>
                        <dt>[[ detail.question.user_role ]] @<code>[[ detail.question.measure ]]</code></dt>
                        <dd><code>[[ detail.answer|json ]]</code></dd>

                        <dt>rater @<code>[[ detail.question.id ]]</code></dt>
                        <dd><code>[[ detail.question.collectedinput_set.rater|json ]]</code></dd>
                        <dt>qa @<code>[[ detail.question.id ]]</code></dt>
                        <dd><code>[[ detail.question.collectedinput_set.qa|json ]]</code></dd>
                    </dl>
                </div>
            </div>
        `
    }
}

import { collector } from '../collector';

import { createSelector } from 'reselect';
import { visibleQuestionsSelector } from './../redux/selectors/visibleQuestions';
import { questionListClasses } from './../redux/selectors/questionListClasses';
import { questionsStatistics } from './../redux/selectors/questionStatistics';

let listControllerInputSelectors = [
    state => state.entities,
    state => state.settings,
    state => state.filters.searchString
];

function listControllerResult(entities, settings, searchString){
    let { answers, relatedAnswers, temporaryAnswer, errors, eepPrograms} = entities;
    let { fetchingQuestions, debug } = settings;
    let { splitQuestionsByProgram } = settings.display;

    splitQuestionsByProgram = splitQuestionsByProgram && Object.keys(eepPrograms).length > 1;

    return {
        answers, relatedAnswers, temporaryAnswer, errors, debug, searchString, eepPrograms,
        splitQuestionsByProgram,
        coloringEnabled: settings.display.qaListColoringEnabled,
        isFetching: fetchingQuestions,
    };
}

const listControllerState = createSelector(...listControllerInputSelectors, listControllerResult);

const visibleQuestionsCount = createSelector(
    visibleQuestionsSelector,
    questions => {
        return _.isPlainObject(questions) ? [].concat(..._.values(questions)).length : questions.length;
    }
);

let inputSelectors = [
    state => state.entities.questions,
    state => state.entities.answers,
    state => state.entities.relatedAnswers,
    state => state.settings.display.showRelatedAnswerInQuestionList
];

function displayAnswerResult(questions={}, answers={}, relatedAnswers={}, showRelatedAnswerInQuestionList=false){
    /**
     * Determines which Answers to show in the question list.
     * In the case where there is no QA showRelatedAnswerInQuestionList will always be false,
     *  so we create a cache of answer text by question id.
     *
     * In the case where there ~is~ a QA program, showRelatedAnswerInQuestionList might be true,
     *  so we create a cache of related answer text by question id.
     */
    const roleAnswers = showRelatedAnswerInQuestionList ? relatedAnswers : answers;
    let answerIdsToKeep = Object.keys(_.indexBy(questions, 'measure'));
    let answersToKeep = _.pick(roleAnswers, answerIdsToKeep);
    return _.indexBy(answersToKeep, 'measure');
}

const answerDisplaySelector = createSelector(...inputSelectors, displayAnswerResult);

class QuestionListController {
    constructor($ngRedux, $scope, $interpolate){
        this.getState = $ngRedux.getState;
        this.$interpolate = $interpolate;
        const questionGetter = state => {
            return { questions: visibleQuestionsSelector(state) };
        }

        const questionColorGetter = state => {
            return { questionColors: questionListClasses(state) };
        }

        const visibleQuestionCountGetter = state => {
            return { questionCount: visibleQuestionsCount(state) };
        }

        const displayAnswerGetter = state => {
            return { answerDisplay: answerDisplaySelector(state) };
        }

        $scope.$on('$destroy', $ngRedux.connect(questionGetter)(this));
        $scope.$on('$destroy', $ngRedux.connect(listControllerState)(this));
        $scope.$on('$destroy', $ngRedux.connect(questionColorGetter)(this));
        $scope.$on('$destroy', $ngRedux.connect(questionsStatistics)(this));
        $scope.$on('$destroy', $ngRedux.connect(visibleQuestionCountGetter)(this));
        $scope.$on('$destroy', $ngRedux.connect(displayAnswerGetter)(this));

        this.getAnswerPreview = function(measure){
            let instrument = $ngRedux.getState().entities.questions[measure];
            let answers = this.answers;

            let {showRelatedAnswerInQuestionList} = this.getState().settings.display;
            let numPrograms = _.keys(this.getState().entities.eepPrograms).length;
            let raterIsSoleProgram = _.filter(this.getState().entities.eepPrograms, (programPicker) => {
                return programPicker.name.indexOf('QA') === -1;
            }).length > 0;
            if (showRelatedAnswerInQuestionList || (numPrograms == 1 && raterIsSoleProgram)) {
                if (instrument.user_role != 'rater') {
                    answers = this.relatedAnswers;
                }
            }

            let answer = answers[measure];
            if (answer === undefined) {
                return null;
            }

            let specification = collector.collectors[instrument.collection_request].full_specification;
            let {response_info} = specification.instruments_info.instruments[instrument.id];
            let displayFormat = response_info.method.display_format_short || '[[ input ]]';
            let data = answer.data;
            if (angular.isObject(data.input)) {
                data = data.input;
            }
            return this.format(displayFormat, data);
        };
    }

    format(spec, data) {
        // Convert spec to angular tokens
        spec = spec.replace(/\{/g, '[[ ').replace(/\}/g, ' ]]');
        return this.$interpolate(spec)(data);
    }
}

export function questionList() {
    return {
        controller: QuestionListController,
        controllerAs: 'list',
        template: `
            <search-field></search-field>
            <br>
            <li class="list-group-item text-center text-muted"
                ng-if="list.totalQuestions != list.questionCount">
                <small>Showing [[ list.questionCount ]] of [[ list.totalQuestions ]] questions.</small>
            </li>
            <div ng-switch="list.splitQuestionsByProgram">
                <program-separated-list ng-switch-when="true"></program-separated-list>
                <all-questions-list ng-switch-when="false"></all-questions-list>
            </div>
        `
    }
}

export function allQuestionsList(){
    return {
        template: `
            <div class="list-group scrollable" scroller>
                <question-list-items questions="list.questions" list="list"></question-list-items>
            </div>
        `
    }
}

export function programSeparatedList(){
    return {
        template: `
            <div class="list-group list-group-root scrollable" scroller>
                <div class="list-group" ng-repeat="(key, questions) in list.questions">
                    <strong class="list-group-item text-muted" ng-bind="::list.eepPrograms[key].name"></strong>
                    <div class="list-group">
                        <question-list-items questions="questions" list="list"></question-list-items>
                    </div>
                </div>
            </div>
        `
    }
}

export function questionListItems(){
    return {
        scope: {
            questions: '=',
            list: '=',
            collector: '='
        },
        template: `
        <li class="list-group-item text-center text-muted"
            ng-if="questions.length != filteredQuestions.length">
            <small>Search showing [[ filteredQuestions.length ]] of [[ questions.length ]] questions.</small>
        </li>
        <a ui-sref-active='active'
           ui-sref='checklist.detail({id: question.measure})'
           ng-class="list.questionColors[question.id]"
           class="list-group-item"
           id='question_[[::question.id]]'
           ng-repeat="question in questions | filter:{text: list.searchString} as filteredQuestions track by question.id">
           <question-list-item question="question" list="list"></question-list-item>
        </a>
    <li class='list-group-item text-center' ng-if='filteredQuestions.length == 0'>
        <i class="fa fa-fw fa-spin fa-spinner" ng-if="list.isFetching"></i>
        No Questions
    </li>
    `
    }
}

export function questionListItem(){
    return {
        scope: {
            question: '=',
            list: '='
        },
        template: `
            <div class="row">
                <div class="col-sm-10">
                    <i class="fa fa-fw fa-pencil" ng-if="!question.answer.id && list.temporaryAnswer[question.measure]"></i>
                    <i class='fa fa-fw fa-exclamation-triangle' ng-if='list.errors[question.measure]'></i>
                    <i class='fa fa-fw fa-long-arrow-right' ng-if='question.parent_instruments.length && question.is_condition_met'></i>
                    <span ng-if="::!question.response_policy.required">(Optional)</span>
                    <span ng-bind="::question.text"></span>

                    <div ng-if="list.debug" class="row">
                        <div class="col-sm-1"><code ng-bind="::question.collection_request"></code></div>
                        <div class="col-sm-1"><span class="label label-default" ng-bind="::question.order"></span></div>
                        <div class="col-sm-4"><span class="label label-primary" ng-bind="::question.measure"></span></div>
                        <div class="col-sm-2"><span class="label label-warning" ng-bind="::question.type"></span></div>
                        <div class="col-sm-2"><span class="label label-info" ng-bind="::question.segment"></span></div>
                        <div class="col-sm-1"><span class="label label-info" ng-bind="::question.group"></span></div>
                    </div>
                </div>
                <div class="col-sm-2">
                    <div ng-bind="list.getAnswerPreview(question.measure) || '-'"></div>
                    <answer-misc answer="list.answerDisplay[question.measure]" show-comment-tooltip="true"></answer-misc>
                </div>
            </div>
        `
    }
}

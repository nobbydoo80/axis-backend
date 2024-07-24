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
        answers, relatedAnswers, temporaryAnswer, errors, debug, searchString, eepPrograms, splitQuestionsByProgram,
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
    const key = showRelatedAnswerInQuestionList ? 'related_answer' : 'answer';
    const object = showRelatedAnswerInQuestionList ? relatedAnswers : answers;

    let answerIdsToKeep = _.filter(_.pluck(questions, key));
    let answersToKeep = _.pick(object, answerIdsToKeep);

    return _.indexBy(answersToKeep, 'question');
}

const answerDisplaySelector = createSelector(...inputSelectors, displayAnswerResult);

class QuestionListController {
    constructor($ngRedux, $scope){
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
            <div ng-if="list.splitQuestionsByProgram">
                <program-separated-list></program-separated-list>
            </div>
            <div ng-if="!list.splitQuestionsByProgram">
                <all-questions-list></all-questions-list>
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
            list: '='
        },
        template: `
        <li class="list-group-item text-center text-muted"
            ng-if="questions.length != filteredQuestions.length">
            <small>Search showing [[ filteredQuestions.length ]] of [[ questions.length ]] questions.</small>
        </li>
        <a ui-sref-active='active'
           ui-sref='checklist.detail({id: question.id})'
           ng-class="list.questionColors[question.id]"
           class="list-group-item"
           id='question_[[::question.id]]'
           ng-repeat="question in questions | filter:{question: list.searchString} as filteredQuestions track by question.id">
                <div class="row">
                    <div class="col-sm-10">
                        <i class='fa fa-fw fa-pencil' ng-if='list.temporaryAnswer[question.id]'></i>
                        <i class='fa fa-fw fa-exclamation-triangle' ng-if='list.errors[question.id]'></i>
                        <span ng-if="::list.debug">
                            [ <span ng-bind="::question.type"></span> ]
                            [ <span ng-bind="::question.priority"></span> ]
                            [ <span ng-bind="::question.id"></span> ]
                        </span>
                        <span ng-if="::question.is_optional">(Optional)</span>
                        <span ng-bind="::question.question"></span>
                    </div>
                    <div class="col-sm-2">
                        <div ng-bind="list.answerDisplay[question.id].answer || '-'"></div>
                        <answer-misc answer="list.answerDisplay[question.id]" show-comment-tooltip="true"></answer-misc>
                    </div>
                </div>
        </a>
        <li class='list-group-item text-center' ng-if='filteredQuestions.length == 0'>
            <i class="fa fa-fw fa-spin fa-spinner" ng-if="list.isFetching"></i>
            No Questions
        </li>
        `
    }
}

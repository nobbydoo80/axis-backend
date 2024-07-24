import { visibleQuestionIdsSelector } from './visibleQuestions';
import { createSelector } from 'reselect';

let inputSelectors = [
    state => state.router.currentParams.id,
    state => state.entities.questions
];

function questionGetter(id, questions){
    return questions[id];
}

export const currentQuestion = createSelector(...inputSelectors, questionGetter);

let previousSelectors = [
    visibleQuestionIdsSelector,
    state => state.router.currentParams.id
];

let nextSelectors = [
    visibleQuestionIdsSelector,
    state => state.router.currentParams.id
];

function previousResult(questionIds, currentId){
    let currentIndex = questionIds.indexOf(parseInt(currentId));
    return currentIndex === 0 ? false : questionIds[currentIndex-1];
}

function nextResult(questionIds, currentId){
    let currentIndex = questionIds.indexOf(parseInt(currentId));
    return currentIndex === (questionIds.length - 1) ? false : questionIds[currentIndex + 1];
}

export const previousQuestionId = createSelector(...[
    visibleQuestionIdsSelector,
    state => state.router.currentParams.id
], previousResult);
export const nextQuestionId = createSelector(...[
    visibleQuestionIdsSelector,
    state => state.router.currentParams.id
], nextResult);

//export const previousQuestionId = (state) => previousResult(visibleQuestionIdsSelector(state), state.router.currentParams.id);
//export const nextQuestionId = (state) => nextResult(visibleQuestionIdsSelector(state), state.router.currentParams.id);

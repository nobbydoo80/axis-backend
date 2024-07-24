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

function previousResult(measures, currentMeasure){
    let currentIndex = measures.indexOf(currentMeasure);
    return currentIndex === 0 ? false : measures[currentIndex-1];
}

function nextResult(measures, currentMeasure){
    let currentIndex = measures.indexOf(currentMeasure);
    return currentIndex === (measures.length - 1) ? false : measures[currentIndex + 1];
}

export const previousQuestionId = createSelector(...[
    visibleQuestionIdsSelector,
    state => state.router.currentParams.id
], previousResult);
export const nextQuestionId = createSelector(...[
    visibleQuestionIdsSelector,
    state => state.router.currentParams.id
], nextResult);

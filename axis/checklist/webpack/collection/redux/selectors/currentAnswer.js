import { createSelector } from 'reselect';

import { currentQuestion } from './currentQuestion';

let inputSelectors = [
    currentQuestion,
    state => state.entities.answers
];

function answerGetter(question, answers){
    return answers[question.answer];
}

export const currentAnswer = createSelector(...inputSelectors, answerGetter);

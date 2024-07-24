import { createSelector } from 'reselect';

import { currentAnswer } from './currentAnswer';
import { currentQuestion } from './currentQuestion';

let inputSelectors = [
    currentQuestion, currentAnswer,
    state => state.entities.temporaryAnswer
];

function choiceGetter(question, answer, temporaryAnswer){
    if(!question) return {};

    if(answer){
        return _.find(question.choices, {'choice': answer.answer});
    } else if(temporaryAnswer[question.id]){
        let answer = temporaryAnswer[question.id].answer;
        return _.find(question.choices, {'choice': answer});
    }
    return {};
}

export const multipleChoiceSelectedChoice = createSelector(...inputSelectors, choiceGetter);

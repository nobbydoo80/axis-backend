import { createSelector } from 'reselect';

let inputSelector = [
    state => state.entities.questions
];

function calculateStatistics(questions){
    let totalQuestions = Object.keys(questions).length;

    let [totalRequired, totalOptional] = _.partition(questions, {is_optional: false});

    let remainingRequired = totalRequired.filter(q => !q.answer);
    let remainingOptional = totalOptional.filter(q => !q.answer);

    return {
        totalQuestions,
        totalRequiredQuestions: totalRequired.length,
        totalOptionalQuestions: totalOptional.length,
        answeredRequiredQuestions: totalRequired.length - remainingRequired.length,
        answeredOptionalQuestions: totalOptional.length - remainingOptional.length,
        remainingRequiredQuestions: remainingRequired.length,
        remainingOptionalQuestions: remainingOptional.length
    };
}

export const questionsStatistics = createSelector(...inputSelector, calculateStatistics);

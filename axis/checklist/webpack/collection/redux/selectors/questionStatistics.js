import { createSelector } from 'reselect';

let inputSelector = [
    state => state.entities.questions,
    state => state.entities.answers
];

function calculateStatistics(questions, answers){
    let activeQuestions = _.filter(questions, question => question.is_condition_met);
    let totalQuestions = Object.keys(activeQuestions).length;
    let [required, optional] = _.partition(activeQuestions, question => question.response_policy.required);

    // Get stats
    let totalRequired = required.length;
    let totalOptional = optional.length;
    let remainingRequired = required.filter(q => !answers[q.measure]).length;
    let remainingOptional = optional.filter(q => !answers[q.measure]).length;
    let answeredRequired = totalRequired - remainingRequired;
    let answeredOptional = totalOptional - remainingOptional;

    return {
        totalQuestions: totalQuestions,
        totalRequiredQuestions: totalRequired,
        totalOptionalQuestions: totalOptional,
        answeredRequiredQuestions: answeredRequired,
        answeredOptionalQuestions: answeredOptional,
        remainingRequiredQuestions: remainingRequired,
        remainingOptionalQuestions: remainingOptional,
    };
}

export const questionsStatistics = createSelector(...inputSelector, calculateStatistics);

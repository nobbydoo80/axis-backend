import { createSelector } from 'reselect';
import { visibleQuestionsSelector } from './visibleQuestions';

let inputSelectors = [
    visibleQuestionsSelector,
    state => state.entities.answers,
    state => state.entities.relatedAnswers,
    state => state.settings.display.qaListColoringEnabled
];

function colorize(questions, answers, relatedAnswers, coloringEnabled) {
    let questionColors = {};
    let callback = getClasses(answers, relatedAnswers, coloringEnabled, questionColors);

    if (_.isPlainObject(questions)) {
        questions = _.union.apply(null, _.values(questions));
    }

    questions.map(callback);

    return questionColors;
}

export const questionListClasses = createSelector(...inputSelectors, colorize);

function getClasses(answers, relatedAnswers, coloringEnabled, result) {
    return function(item){
        let klasses = [];

        let roleAnswer = answers[item.measure] || {};
        let relatedAnswer = relatedAnswers[item.measure] || {};

        if (item.read_only) {
            klasses.push('disabled pointer-cursor');
        } else if (coloringEnabled) {
            if (relatedAnswer.id) {
                if (!roleAnswer.id) {
                    klasses.push('list-group-item-info');
                } else if (roleAnswer.data.input === relatedAnswer.data.input) {
                    klasses.push('list-group-item-success');
                } else {
                    klasses.push('list-group-item-danger');
                }
            } else if (roleAnswer.id) {
                klasses.push('disabled pointer-cursor');
            }
        } else if (roleAnswer.id) {
            klasses.push('disabled pointer-cursor');
        }

        result[item.id] = klasses.join(' ');
    }
}

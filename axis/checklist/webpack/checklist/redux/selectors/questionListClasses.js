import { createSelector } from 'reselect';
import { visibleQuestionsSelector } from './visibleQuestions';

let inputSelectors = [
    visibleQuestionsSelector,
    state => state.entities.answers,
    state => state.entities.relatedAnswers,
    state => state.settings.display.qaListColoringEnabled
];

function colorize(questions, answers, relatedAnswers, coloringEnabled){
    let questionColors = {};
    let callback = getClasses(answers, relatedAnswers, coloringEnabled, questionColors);

    if(_.isPlainObject(questions)){
        questions = _.union.apply(null, _.values(questions));
    }

    questions.map(callback);

    return questionColors;
}

export const questionListClasses = createSelector(...inputSelectors, colorize);

function getClasses(answers, relatedAnswers, coloringEnabled, result){
    return function(item){
        let klasses = [];

        if(coloringEnabled){
            if(item.related_answer){
                if(!item.answer){
                    klasses.push('list-group-item-info');
                } else if(answers[item.answer].answer === relatedAnswers[item.related_answer].answer){
                    klasses.push('list-group-item-success');
                } else {
                    klasses.push('list-group-item-danger');
                }
            } else if(item.answer){
                klasses.push('disabled pointer-cursor');
            }
        } else if(item.answer){
            klasses.push('disabled pointer-cursor');
        }

        result[item.id] = klasses.join(' ');
    }
}

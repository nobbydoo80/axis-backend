import { collector } from '../../collector';

import { createSelector } from 'reselect';

let inputSelectors = [
    state => state.entities.questions,
    state => state.entities.sections,
    state => state.entities.eepPrograms,
    state => state.entities.checklists,
    state => state.filters,
    state => state.settings.display.splitQuestionsByProgram,
    state => state.router.currentParams.id
];

function visibleQuestions(questions={}, sections={}, programs={}, checklists={}, filters={}, splitByProgram=false, currentQuestionId=null){
    let {types: filterTypes, states: filterStates, sections: filterSections, programs: filterPrograms} = filters;

    filterPrograms = getProgramsQuestions(programs, filterPrograms, checklists);

    let instruments = questions;
    let filter = questionFilter(filterTypes, filterStates, filterPrograms, currentQuestionId);
    let filteredQuestions = _.filter(instruments, filter)
        .sort((a, b) => a.order - b.order)
        .sort((a, b) => a.collection_request - b.collection_request)

    if(!Object.keys(programs).length || !splitByProgram){
        return filteredQuestions;
    }

    return splitQuestionsByProgram(filteredQuestions, programs, checklists);
}

function splitQuestionsByProgram(questions, programs, checklists){
    let byProgram = {};

    _.each(programs, program => {
        let questionList = [];
        _.each(questions, question => {
            if (question.eep_program_id == program.id) {
                questionList.push(question);
            }
        });
        if (questionList.length){
            byProgram[program.collection_request] = questionList;
        }
    })

    return byProgram;
}

function getProgramsQuestions(programs, filterPrograms, checklists){
    // get active program ids
    const activeProgramIds = Object.keys(filterPrograms).filter(k => filterPrograms[k]);
    const measures = [].concat(..._.map(activeProgramIds, id => {
        return _.pluck(collector.collectors[id].instruments, 'measure');
    }));

    return measures;
}

function questionFilter(types, states, programs, currentQuestionId){
    return function(question){
        if (question.collection_request === undefined) {
            return false;
        }

        // Never exclude the current question.  This is vital to correctly detecting the next
        // question id in the list when answered questions are being hidden.  Because the question
        // list can change after saving an answer, we cannot exclude the current question just
        // because it now has an answer.
        if (question.id == currentQuestionId) return true;

        let collectorObj = collector.collectors[question.collection_request];
        let activeRole = ((collectorObj || {}).full_specification || {}).user_role;
        let answer = (question.collectedinput_set[activeRole] || [])[0] || {};

        // if(!types[question.type]) return false;
        if (!question.is_condition_met) return false;
        if(!states.required && question.response_policy.required) return false;
        if(!states.optional && !question.response_policy.required) return false;
        if(!states.answered && answer.id) return false;
        if(!states.unanswered && !answer.id) return false;
        if(programs.length && programs.indexOf(question.measure) == -1) return false;
        return true;
    }
}

export const visibleQuestionsSelector = createSelector(...inputSelectors, visibleQuestions);

export const visibleQuestionIdsSelector = createSelector(visibleQuestionsSelector, visibleQuestions => _.pluck(visibleQuestions, 'measure'));

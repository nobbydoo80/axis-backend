import { createSelector } from 'reselect';

let inputSelectors = [
    state => state.entities.questions,
    state => state.entities.sections,
    state => state.entities.eepPrograms,
    state => state.entities.checklists,
    state => state.filters,
    state => state.settings.display.splitQuestionsByProgram
];

function visibleQuestions(questions={}, sections={}, programs={}, checklists={}, filters={}, splitByProgram=false){
    let {types: filterTypes, states: filterStates, sections: filterSections, programs: filterPrograms} = filters;

    filterSections = getSectionQuestions(sections, filterSections);
    filterPrograms = getProgramsQuestions(programs, filterPrograms, checklists);

    let questionIds = Object.keys(questions);

    let filteredQuestions = questionIds
        .map(id => questions[id])
        .filter(questionFilter(filterTypes, filterStates, filterSections, filterPrograms))
        .sort((a, b) => {
            let priority = a.priority - b.priority;
            return priority === 0 ? a.id - b.id : priority;
        })

    if(!Object.keys(programs).length || !Object.keys(checklists).length || !splitByProgram){
        return filteredQuestions;
    }

    return splitQuestionsByProgram(filteredQuestions, programs, checklists);
}

function splitQuestionsByProgram(questions, programs, checklists){
    let indexed = _.indexBy(questions, 'id');

    let temp = {};

    _.values(programs).map(program => {
        let questionList = [];

        program.required_checklists.map(id => checklists[id]).map(checklist => {
            checklist.questions.map(questionId => {
                let question = indexed[questionId];
                if(question) questionList.push(question);
            });
        })
        if(questionList.length){
            temp[program.id] = questionList;
        }
    })

    return temp;
}

function getProgramsQuestions(programs, filterPrograms, checklists){
    const activeProgramIds = Object.keys(filterPrograms).filter(k => filterPrograms[k]);  // get active program ids
    const checklistIds = [].concat(...activeProgramIds.map(k => programs[k].required_checklists));  // list of checklists from active programs
    const questionsIds = [].concat(...checklistIds.map(k => checklists[k].questions));  // combined list of question ids from checklists
    return questionsIds;
}

function questionFilter(types, states, sections, programs){
    return function(question){
        if(!types[question.type]) return false;
        if(!states.required && !question.is_optional) return false;
        if(!states.optional && question.is_optional) return false;
        if(!states.answered && question.answer) return false;
        if(!states.unanswered && !question.answer) return false;
        if(sections.length && sections.indexOf(question.id) == -1) return false;
        if(programs.length && programs.indexOf(question.id) == -1) return false;
        return true;
    }
}

function getSectionQuestions(sections, filterSections){
    return _.union(..._.map(getActiveSections(filterSections), id => sections[id].questions));
}

function getActiveSections(filterSections={}){
    return Object.keys(filterSections).filter(key => filterSections[key]);
}

export const visibleQuestionsSelector = createSelector(...inputSelectors, visibleQuestions);

export const visibleQuestionIdsSelector = createSelector(visibleQuestionsSelector, visibleQuestions => _.pluck(visibleQuestions, 'id'));

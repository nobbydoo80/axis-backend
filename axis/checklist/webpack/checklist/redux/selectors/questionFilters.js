import { createSelector } from 'reselect';
import { QuestionTypeLabels, QuestionStateLabels } from './../../settings';

let inputSelectors = [
    state => state.filters.types,
    state => state.filters.states,
    state => state.filters.sections,
    state => state.entities.sections,
    state => state.filters.programs,
    state => state.entities.eepPrograms
];

function cleanFilters(types, states, filterSections, entitiesSections, filterPrograms, entitiesPrograms){
    let cleanedTypes = Object.keys(types).map(getCleanedObject(types, QuestionTypeLabels));
    let cleanedStates = Object.keys(states).map(getCleanedObject(states, QuestionStateLabels));
    let cleanedSections = Object.keys(entitiesSections).map(getCleanedObject(filterSections, _.mapValues(entitiesSections, 'name')));
    let cleanedPrograms = Object.keys(entitiesPrograms).map(getCleanedObject(filterPrograms, _.mapValues(entitiesPrograms, 'name')));
    return {
        types: cleanedTypes,
        states: cleanedStates,
        sections: cleanedSections,
        programs: cleanedPrograms
    }
}

function getCleanedObject(valuesObj, labelsObj){
    return function(key){
        return {
            key,
            name: labelsObj[key],
            selected: valuesObj[key]
        }
    }
}

export const questionFilters = createSelector(...inputSelectors, cleanFilters)

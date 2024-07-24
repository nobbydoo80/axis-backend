import filterActions from './../constants/filters';
import sectionActions from './../constants/sections';
import entityActions from './../constants/entities';
import {QuestionFilters} from './../../settings';

// Clean types and states key to only include active state.
const typeDefaults = _.mapValues(QuestionFilters.types, n => n.active);
const stateDefaults = _.mapValues(QuestionFilters.states, n => n.active);
const defaultState = _.assign({}, QuestionFilters, {types: typeDefaults, states: stateDefaults});
const defaultStateWithLocalStorage = _.assign({}, defaultState,
    JSON.parse(localStorage.getItem('checklist:filter_settings')) || {},
    // JSON.parse(localStorage.getItem('checklist:settings')) || {}
);

export default function filters(state=defaultStateWithLocalStorage, action){
    switch(action.type){
        case filterActions.RESET_FILTERS:
            // manually set sections to false because they don't exist in defaultState.
            let resetSections = _.mapValues(state.sections, () => false);
            return _.assign({}, defaultState, {sections: resetSections});

        case filterActions.SET_FILTER_STRING:
            return _.assign({}, state, {searchString: action.payload.value});

        case filterActions.SET_TYPE_CHECKBOX:
            var newTypes = _.assign({}, state.types, {
                [action.payload.key]: action.payload.value
            });
            return _.assign({}, state, {types: newTypes});

        case filterActions.SET_STATE_CHECKBOX:
            var newStates = _.assign({}, state.states, {
                [action.payload.key]: action.payload.value
            });
            return _.assign({}, state, {states: newStates});

        case sectionActions.RECEIVE_SECTIONS:
            let sectionIds = _.pluck(action.payload.sections, 'id');
            let temp = {};
            sectionIds.map(id => temp[id] = false);
            var newSections = _.assign({}, state.sections, temp);
            return _.assign({}, state, {sections: newSections});

        case filterActions.SET_SECTION_CHECKBOX:
            var newSections = _.assign({}, state.sections, {
                [action.payload.key]: action.payload.value
            });
            return _.assign({}, state, {sections: newSections});

        case entityActions.RECEIVE_EEP_PROGRAM:
            let program = action.payload.program;
            var newPrograms = _.assign({}, state.programs, {[program.id]: false});
            return _.assign({}, state, {programs: newPrograms});

        case filterActions.SET_PROGRAM_CHECKBOX:
            var newPrograms = _.assign({}, state.programs, {
                [action.payload.key]: action.payload.value
            });
            return _.assign({}, state, {programs: newPrograms});

        default:
            return state;
    }
}

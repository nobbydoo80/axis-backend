import {INTERACTION_VALUES, DISPLAY_VALUES} from './../../settings';

import questionActions from './../constants/questions';
import answerActions from './../constants/answers';
import interactionActions from './../constants/interactions';
import entityActions from './../constants/entities';

const defaultInteractionSettings = _.assign({}, INTERACTION_VALUES, JSON.parse(localStorage.getItem('checklist:interaction_settings')) || {});
const defaultDisplaySettings = _.assign({}, DISPLAY_VALUES, JSON.parse(localStorage.getItem('checklist:display_settings')) || {});

const defaultState = {
    showInteractionSettings: false,
    showFilterSettings: false,
    questionOrder: [],
    interactions: defaultInteractionSettings,
    display: defaultDisplaySettings,
    baseUrl: '',
    homeId: 0,
    eepProgramIds: [],
    readonly: true,
    savingAnswer: false,
    fetchingQuestions: false,
    debug: false
};

function orderQuestions(data){
    let questions = Object.keys(data.questions).map(key => data.questions[key]);
    let sorted = questions.sort((a, b) => a[data.order_by] > b[data.order_by] ? 1 : -1);
    return sorted.map(obj => obj.id);
}

export default function settings(state=defaultState, action){
    switch(action.type){
        case questionActions.ORDER_QUESTIONS:
            return _.assign({}, state, {questionOrder: orderQuestions(action.payload)});

        case interactionActions.SET_INTERACTION_SETTING:
            if(action.payload.key in state.interactions){
                var update = {
                    interactions: _.assign({}, state.interactions, {
                        [action.payload.key]: action.payload.value
                    })
                }
            } else if (action.payload.key in state.display){
                var update = {
                    display: _.assign({}, state.display, {
                        [action.payload.key]: action.payload.value
                    })
                };
            }
            return _.assign({}, state, update);

        case interactionActions.SET_SETTING:
            return _.assign({}, state, {
                [action.payload.key] : action.payload.value
            });

        case answerActions.SAVING_ANSWER:
            return _.assign({}, state, {savingAnswer: true});
        case answerActions.ANSWER_SAVED:
            return _.assign({}, state, {savingAnswer: false});

        case questionActions.REQUEST_QUESTIONS:
            return _.assign({}, state, {fetchingQuestions: true});
        case questionActions.RECEIVE_QUESTIONS:
            return _.assign({}, state, {fetchingQuestions: false});

        case entityActions.CLEAR_ENTITIES:
            return _.assign({}, state, {'eepProgramIds': []});

        default:
            return state
    }
}

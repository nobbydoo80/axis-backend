import {combineReducers} from 'redux';
import questionActions from './../constants/questions';
import answerActions from './../constants/answers';
import sectionActions from './../constants/sections';
import entityActions from './../constants/entities';
import interactionActions from './../constants/interactions';

import * as temporaryAnswerReducers from './temporaryAnswers';

function _extendByKey(currentState, object, key='id'){
    return _.assign({}, currentState, {
        [object[key]]: object
    });
}

function questions(state={}, action){
    switch(action.type){
        case entityActions.CLEAR_ENTITIES:
            return {}
        case questionActions.RECEIVE_QUESTIONS:
            return _.assign({}, state, _.indexBy(action.payload.questions, 'id'));
        case entityActions.DISCARD_QUESTIONS:
            return _.omit(state, action.payload.questionIds);
        default:
            return state;
    }
}

function answers(state={}, action){
    switch(action.type){
        case entityActions.CLEAR_ENTITIES:
            return {}
        case answerActions.RECEIVE_ANSWERS:
            return _.assign({}, state, _.indexBy(action.payload.answers, 'id'));
        case answerActions.DELETE_ANSWER:
            return _.omit(state, action.payload.answerId);

        case answerActions.ATTACH_DOCUMENT:
            let newDocuments = state[action.payload.answerId].customer_documents.concat([action.payload.document]);
            let newAnswer = _.assign({}, state[action.payload.answerId], {
                customer_documents: newDocuments
            });
            return _.assign({}, state, {[action.payload.answerId]: newAnswer});
        default:
            return state;
    }
}

function relatedAnswers(state={}, action){
    switch(action.type){
        case entityActions.CLEAR_ENTITIES:
            return {}
        case answerActions.RECEIVE_RELATED_ANSWERS:
            return _.assign({}, state, _.indexBy(action.payload.answers, 'id'));
        default:
            return state;
    }
}

function eepPrograms(state={}, action){
    switch(action.type){
        case entityActions.CLEAR_ENTITIES:
            return {}
        case entityActions.RECEIVE_EEP_PROGRAM:
            return _extendByKey(state, action.payload.program);
        case entityActions.DISCARD_PROGRAM:
            return _.omit(state, action.payload.programId);
        default:
            return state;
    }
}

function checklists(state={}, action){
    switch(action.type){
        case entityActions.CLEAR_ENTITIES:
            return {}
        case entityActions.RECEIVE_CHECKLIST:
            return _extendByKey(state, action.payload.checklist);
        case entityActions.DISCARD_CHECKLISTS:
            return _.omit(state, action.payload.checklistIds);
        default:
            return state;
    }
}

function sections(state={}, action){
    switch(action.type){
        case entityActions.CLEAR_ENTITIES:
            return {}
        case sectionActions.RECEIVE_SECTIONS:
            return _.assign({}, state, _.indexBy(action.payload.sections, 'id'));

        default:
            return state;
    }
}

function temporaryAnswer(state={}, action){
    switch(action.type){
        case entityActions.CLEAR_ENTITIES:
            return {}
        case answerActions.STORE_MULTIPLE_CHOICE_ANSWER:
        case answerActions.STORE_OPEN_ANSWER:
        case answerActions.UPDATE_COMMENT:
        case answerActions.STORE_DOCUMENT:
        case answerActions.REMOVE_DOCUMENT:
        case answerActions.STORE_DOCUMENTS_SHELL:
        case answerActions.REMOVE_DOCUMENT_SHELL:
            let currentTempAnswer = state[action.payload.questionId] || {};
            let updatedQuestion = {
                answer: temporaryAnswerReducers.answer(currentTempAnswer.answer, action),
                comment: temporaryAnswerReducers.comment(currentTempAnswer.comment, action),
                customer_documents: temporaryAnswerReducers.customer_documents(currentTempAnswer.customer_documents, action)
            };
            return _.assign({}, state, {[action.payload.questionId]: updatedQuestion});

        case answerActions.REMOVE_MULTIPLE_CHOICE_ANSWER:
        case answerActions.REMOVE_OPEN_ANSWER:
            return _.omit(state, action.payload.questionId);
        default:
            return state;
    }
}

function errors(state={}, action){
    switch(action.type){
        case entityActions.CLEAR_ENTITIES:
            return {}
        case interactionActions.CLIENT_ERROR:
        case interactionActions.SERVER_ERROR:
            return _.assign({}, state, {
                [action.payload.questionId]: action.payload.errors
            });
        case interactionActions.REMOVE_ERROR:
            return _.omit(state, action.payload.questionId);
        default:
            return state;
    }
}

const entities = combineReducers({
    questions, answers, sections, temporaryAnswer, errors, relatedAnswers, eepPrograms, checklists
});

export default entities;

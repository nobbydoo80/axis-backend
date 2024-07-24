import * as actions from './../constants/interactions';
import { stateGo } from 'redux-ui-router';
import { visibleQuestionIdsSelector } from './../selectors/visibleQuestions';
import { previousQuestionId, nextQuestionId } from './../selectors/currentQuestion';

export function getNextQuestionId(state, questionId, skipAnswered){
    // only allow questions that are in the visible list.
    let nextId = nextQuestionId(state);


    if(!nextId){
        return questionId;
    } else if(skipAnswered && state.entities.questions[nextId].answer){
        /*
        In the case where there are not more unanswered questions the line above
        will throw a TypeError for trying to look and the `.answer` of undefined.
        When that happens, just return the last thing.
         */
        try{
            return getNextQuestionId(state, nextId, skipAnswered);
        } catch(e){
            return questionId;
        }
    } else {
        return nextId;
    }
}

function getPreviousQuestionId(state, questionId){
    return previousQuestionId(state);
}

function setSetting(key, value){
    return {
        type: actions.SET_SETTING,
        payload: {key, value}
    };
}

export function interactionActions(){

    function setInteractionSetting(key, value){
        return function(dispatch, getState){
            dispatch({
                type: actions.SET_INTERACTION_SETTING,
                payload: {key, value}
            });
            localStorage.setItem('checklist:interaction_settings', JSON.stringify(getState().settings.interactions));
        }
    }

    function setInteractionSettingVisibility(value){
        return {
            type: actions.SET_SHOW_INTERACTION_SETTINGS,
            payload: {value}
        };
    }

    function setFilterSettingVisibility(value){
        return {
            type: actions.SET_SHOW_FILTER_SETTINGS,
            payload: {value}
        };
    }

    function gotoNextQuestion(questionId){
        return function (dispatch, getState){
            let state = getState();
            let nextId = getNextQuestionId(state, questionId, state.settings.interactions.skipAnsweredQuestions);

            dispatch(stateGo('checklist.detail', {id: nextId}));
        }
    }

    function gotoPreviousQuestion(questionId){
        return function (dispatch, getState){
            let previousId = getPreviousQuestionId(getState(), questionId);

            dispatch(stateGo('checklist.detail', {id: previousId}));
        }
    }

    return {
        setSetting,
        setInteractionSetting,
        gotoNextQuestion,
        gotoPreviousQuestion,
        setInteractionSettingVisibility,
        setFilterSettingVisibility
    };
}

import { collector } from '../../collector';
import * as actions from './../constants/questions';
import {receiveAnswers, receiveRelatedAnswers} from './answers';
import { entitiesActions } from './entities';
import { interactionActions } from './interactions'

export function requestingQuestions(){
    return {
        type: actions.REQUEST_QUESTIONS
    }
}

export function receiveQuestions(questions){
    return {
        type: actions.RECEIVE_QUESTIONS,
        payload: {questions}
    }
}

function saveToLocalStorage(fn){
    return function (...args){
        return function (dispatch, getState){
            dispatch(fn(...args));
            localStorage.setItem('checklist:filter_settings', JSON.stringify(getState().filters));
        }
    }
}


export function questionActions($q, $http){
    function setSearchString(value){
        return {
            type: actions.SET_FILTER_STRING,
            payload: {value}
        };
    }

    function setSearchCheckBox(key, value){
        return {
            type: actions.SET_FILTER_CHECKBOX,
            payload: {key, value}
        };
    }

    return {
        setSearchString: saveToLocalStorage(setSearchString),
        setSearchCheckBox: saveToLocalStorage(setSearchCheckBox)
    }
}

function utils(dispatch, getState){

    function getQuestionsUrl(programId){
        let homeId = getState().settings.homeId;
        return `/api/v2/checklist/${homeId}/${programId}/questions/`;
    }

    function extractObject(key, action){
        return function(items){
            let extracted = items.filter(hasKey(key)).map(replaceKeyWithId(key));

            if(extracted.length) dispatch(action(extracted));

            return items;
        }
    }

    function replaceKeyWithId(key){
        return function(item){
            let temp = item[key];
            item[key] = temp.id;
            return temp;
        }
    }

    function hasKey(key){
        return function(item){
            return !!item[key];
        }
    }

    return { extractObject, replaceKeyWithId, hasKey, getQuestionsUrl };

}

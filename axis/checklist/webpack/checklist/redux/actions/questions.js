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

export function orderQuestions(questions, order_by){
    return {
        type: actions.ORDER_QUESTIONS,
        payload: {questions, order_by}
    }
}

function shouldFetchQuestions(state){
    return !Object.keys(state.entities.questions).length;
}

export function questionActions($q, $http){

    function externalFetchQuestions(programId){
        return function _externalFetchQuestions(dispatch, getState){
            if(!programId) return;
            dispatch(requestingQuestions());

            let { extractObject, getQuestionsUrl } = utils(dispatch, getState);

            return $http.get(getQuestionsUrl(programId)).then(response => response.data)
                .then(extractObject('answer', receiveAnswers))
                .then(extractObject('related_answer', receiveRelatedAnswers))
                .then(questions => dispatch(receiveQuestions(questions)))
                .then(() => dispatch(orderQuestions(getState().entities.questions, 'priority')))
                .then(() => {
                    let currIds = getState().settings.eepProgramIds;
                    dispatch(interactionActions().setSetting('eepProgramIds', [].concat(currIds, [programId])))
                })
                // Since we're doing this action outside the normal angular flow,
                // we don't have DI happening, so we have to do it ourselves.
                .then(() => dispatch(entitiesActions($q, $http).fetchPrograms()));
        }
    }

    function fetchQuestions(urls){
        return function _fetchQuestions(dispatch, getState){
            if(!urls.length) return;
            dispatch(requestingQuestions());

            let requests = urls.map(url => $http.get(url).then(response => response.data));

            let { extractObject } = utils(dispatch, getState);

            // Make sure we get the requests returned in order.
            return $q.all(requests)
                .then(questionSets => {
                    questionSets
                        .map(extractObject('answer', receiveAnswers))
                        .map(extractObject('related_answer', receiveRelatedAnswers))
                        .map(questions => dispatch(receiveQuestions(questions)));
                })
                // order questions when we're all done.
                .then(() => dispatch(orderQuestions(getState().entities.questions, 'priority')));
        }
    }

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

    function saveToLocalStorage(fn){
        return function (...args){
            return function (dispatch, getState){
                dispatch(fn(...args));
                localStorage.setItem('checklist:filter_settings', JSON.stringify(getState().filters));
            }
        }
    }

    return {
        fetchQuestions,
        externalFetchQuestions,
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

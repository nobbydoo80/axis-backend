import { collector } from '../../collector';
import * as actions from './../constants/answers';
import interactionActions from './../constants/interactions';
import {receiveQuestions} from './questions';
import {entitiesActions} from './entities';
import {stateGo} from 'redux-ui-router';
import { getNextQuestionId } from './interactions';

let easyTransform = response => response;

export function savingAnswer(){
    return {
        type: actions.SAVING_ANSWER
    };
}

export function answerSaved(){
    return {
        type: actions.ANSWER_SAVED
    };
}

export function receiveAnswers(answers){
    return {
        type: actions.RECEIVE_ANSWERS,
        payload: {answers}
    };
}

export function receiveRelatedAnswers(answers){
    return {
        type: actions.RECEIVE_RELATED_ANSWERS,
        payload: {answers}
    };
}

export function deleteAnswer(measure){
    return {
        type: actions.DELETE_ANSWER,
        payload: {
            answerId: measure
        }
    }
}

export function attachDocumentToAnswer(document, answerId){
    return {
        type: actions.ATTACH_DOCUMENT,
        payload: {document, answerId}
    };
}

export function attachDocumentShellToTemporaryAnswer(file, questionId){
    return {
        type: actions.STORE_DOCUMENTS_SHELL,
        payload: {file, questionId}
    };
}

export function attachDocumentToTemporaryAnswer(file, questionId){
    return {
        type: actions.STORE_DOCUMENT,
        payload: {file, questionId}
    };
}

function updateComment(comment, questionId){
    return {
        type: actions.UPDATE_COMMENT,
        payload: {comment, questionId}
    };
}

function removeDocumentShell(fileName, questionId){
    return {
        type: actions.REMOVE_DOCUMENT_SHELL,
        payload: {fileName, questionId}
    }
}

function removeDocument(fileName, questionId){
    return {
        type: actions.REMOVE_DOCUMENT,
        payload: {fileName, questionId}
    };
}

export function clientError(error, questionId){
    return {
        type: interactionActions.CLIENT_ERROR,
        payload: {
            questionId,
            errors: [error.message]
        }
    }
}

export function serverError(errors, questionId){
    return {
        type: interactionActions.SERVER_ERROR,
        payload: {
            questionId,
            errors
        }
    };
}

export function documentValidationError(errors, questionId){
    /**
     * This action is a temporary.
     * https://pivotalenergysolutions.zendesk.com/agent/tickets/4520
     * I believe a document being marked as invalid,
     * and previously we weren't removing the document shell,
     * but also there was no error going through, because
     * none of the users said anything about errors.
     * So, until we diagnose what is actually going on,
     * let's give them an error to see.
     */
    return {
        type: interactionActions.SERVER_ERROR,
        payload: {
            questionId,
            errors: ['Document is invalid']
        }
    };
}

export function removeErrors(questionId){
    return {
        type: interactionActions.REMOVE_ERROR,
        payload: {questionId}
    };
}

function keep(questionId, answer, suggestedResponse){
    return {
        type: actions.STORE_OPEN_ANSWER,
        payload: {questionId, answer, suggestedResponse}
    };
}

function remove(questionId){
    return {
        type: actions.REMOVE_OPEN_ANSWER,
        payload: {questionId}
    };
}

export function answerActions($ngRedux, $http, $q, InteractionActions){
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function stage(instrument, data) { return (dispatch, getState) => {
        dispatch(keep(instrument.measure, data));
    }}

    function save(instrument, data, customerDocuments) { return (dispatch, getState) => {
        let state = getState();
        let {autoAdvanceOnAnswer} = state.settings.interactions;
        return $q.when()
            .then(isValid)
            .then(() => dispatch(savingAnswer()))
            .catch(errorHandler(clientError))
            .then(() => store(instrument, data, customerDocuments))
            .then(updateInstruments(dispatch, instrument.user_role))
            .then(() => saveDocuments())
            .then(() => dispatch(remove(instrument.measure)))
            .then(autoAdvanceQuestion)
            .finally(() => dispatch(answerSaved()));

        function errorHandler(handler){
            return function({ json, status }){
                if (json.length !== undefined) {
                    dispatch(removeErrors(instrument.measure));
                    return json
                } else if (status === 400) {
                    dispatch(handler(json, instrument.measure));
                }

                // // The create/update/delete responses return a list of instrument availability
                // // changes.
                // let errors = _.flatten(_.values(json.data));
                // errors = errors.length ? errors : json;
                // dispatch(handler(errors, instrument.measure));

                // if(autoAdvanceOnAnswer && deferCorrection){
                //     dispatch(InteractionActions.gotoNextQuestion(instrument.measure));
                // }

                return $q.reject();
            }
        }

        function isValid() {
            return true;
        }

        function store(instrument, stagedData, customerDocuments){
            let data = {
                // collector_comment: ``,
                instrument: instrument.id,
                data: stagedData,
                expected_documents: _.map(customerDocuments, document => document.name)
            };
            collector.setCollector(instrument.collection_request);
            let promise = collector.api.promise.inputAdd(data, {}, csrftoken);
            let handler = errorHandler(serverError)
            return promise.then(handler, handler);
        }

        function saveDocuments(){
            $q.all(_.map(customerDocuments, document => saveDocument(document).then(document => {
                dispatch(attachDocumentToAnswer(document, instrument.measure));
                return document;
            })));
        }

        function saveDocument(document){
            return $http.post(`/api/v2/checklist/documents/?machinery=input-collection`, {
                document_raw: document.raw,
                document_raw_name: document.name,
                object_id: $ngRedux.getState().entities.answers[instrument.measure].id
            }).then(response => response.data.object);
        }

        function autoAdvanceQuestion(){
            /**
             * Return a function with a closure over the next measure.
             * We need to find the next question before we save an answer
             * and possible cause a change in the list of viewable question.
             */
            if (autoAdvanceOnAnswer) {
                dispatch(InteractionActions.gotoNextQuestion(instrument.measure));
            }
        }
    }}

    function clear(measure) { return (dispatch, getState) => {
        dispatch(remove(measure));
    }}

    function retract(measure) { return (dispatch, getState) => {
        let entities = getState().entities;
        let instrument = entities.questions[measure];
        let answer = entities.answers[measure];
        collector.setCollector(instrument.collection_request);
        let activeRole = collector.collector.full_specification.user_role;
        return collector.api.promise.inputDelete({}, {id: answer.id}, csrftoken)
            .then((instruments) => {
                dispatch(deleteAnswer(measure));
                return instruments;
            })
            .then(updateInstruments(dispatch, activeRole), function(){
                console.error('Handle errors for non retractable answers');
                debugger;
            });
    }}

    function updateInstruments(dispatch, userRole) { return (instrumentList) => {
        entitiesActions($http).addInstruments(instrumentList, userRole, dispatch);
        return instrumentList;
    }}

    function storeDocument(file, measure) { return (dispatch, getState) => {
        dispatch(attachDocumentShellToTemporaryAnswer(file, measure));
        let url = `/api/v2/answer/documents/validate/`;
        let reader = new FileReader();

        reader.onload = function(readFile){
            let raw = readFile.target.result;
            let extension = file.name.split('.').pop();

            if(raw.indexOf(':;') > -1){
                raw = raw.replace(':;', `:application/${extension};`);
            } else if(raw.indexOf('octet-stream') > -1){
                raw = raw.replace('octet-stream', extension);
            }
            file.raw = raw;

            $http.post(url, {document: raw})
                .then(() => dispatch(attachDocumentToTemporaryAnswer(file, measure)))
                .catch(response => {
                    dispatch(removeDocumentShell(file.name, measure));
                    dispatch(documentValidationError(response.data, measure));
                })
        }

        reader.readAsDataURL(file.file);
    }}

    return {
        stage,
        save,
        retract,
        clear,
        updateComment,
        storeDocument,
        removeDocument,
        stateGo
    };
}

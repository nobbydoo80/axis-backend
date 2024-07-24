import * as actions from './../constants/answers';
import interactionActions from './../constants/interactions';
import {receiveQuestions} from './questions';
import {stateGo} from 'redux-ui-router';
import { getNextQuestionId } from './interactions';

let easyTransform = response => response.data;

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

export function deleteAnswer(answer){
    return {
        type: actions.DELETE_ANSWER,
        payload: {
            answerId: answer.id
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

class MultipleChoiceAnswer {
    constructor(answer, choice, question){
        this.answer = answer;
        this.choice = choice;
        this.question = question;
    }
    is_valid(){
        if(this.choice.comment_required && !this.answer.comment){
            throw new Error('Comment Required');
        }
        if(this.choice.image_required && !this.answer.customer_documents.length){
            throw new Error('Images Required');
        }
        if(this.choice.document_required && !this.answer.customer_documents.length){
            throw new Error('Documents Required');
        }
    }
    clean(){
        return {
            answer: this.answer.answer,
            comment: this.answer.comment,
            customer_documents: this.answer.customer_documents
        }
    }
}

class OpenAnswer {
    constructor(answer, question){
        this.answer = answer;
        this.question = question;
    }
    is_valid(){
        console.info('No checks for open answers.');
    }
    clean(){
        return {
            answer: this.answer.answer,
            comment: this.answer.comment,
            customer_documents: this.answer.customer_documents
        };
    }
}

function storeMultipleChoiceAnswer(answer, questionId){
    return {
        type: actions.STORE_MULTIPLE_CHOICE_ANSWER,
        payload: {answer, questionId}
    };
}

function removeMultipleChoiceAnswer(questionId){
    return {
        type: actions.REMOVE_MULTIPLE_CHOICE_ANSWER,
        payload: {questionId}
    };
}

function storeOpenAnswer(answer, questionId){
    return {
        type: actions.STORE_OPEN_ANSWER,
        payload: {answer, questionId}
    };
}

function removeOpenAnswer(questionId){
    return {
        type: actions.REMOVE_OPEN_ANSWER,
        payload: {questionId}
    };
}

export function answerActions($http, $q, InteractionActions){

    function storeTemporaryAnswer(answer, question, triggerSave=false){
        return function(dispatch, getState){
            let isMultipleChoice = question.type === 'multiple-choice';
            let storeAction = isMultipleChoice ? storeMultipleChoiceAnswer : storeOpenAnswer;

            dispatch(storeAction(answer, question.id));

            let state = getState();
            if(triggerSave || (isMultipleChoice && state.settings.interactions.autoSubmitMultipleChoice)){
                dispatch(saveAnswer(state.entities.temporaryAnswer[question.id], question.id));
            }
        }
    }

    function removeTemporaryAnswer(question){
        if(question.type === 'multiple-choice'){
            return removeMultipleChoiceAnswer(question.id);
        } else {
            return removeOpenAnswer(question.id);
        };
    }

    function saveAnswer(answerData, questionId){
        return function(dispatch, getState){
            let state = getState();
            let question = state.entities.questions[questionId];
            let {autoAdvanceOnAnswer, deferCorrection} = state.settings.interactions;
            let handler;

            if(question.type === 'multiple-choice'){
                let choice = _.find(question.choices, {choice: answerData.answer});
                handler = new MultipleChoiceAnswer(answerData, choice, question);
            } else {
                handler = new OpenAnswer(answerData, question);
            }

            return $q.when()
                .then(() => handler.is_valid())
                .then(() => dispatch(savingAnswer()))
                .catch(errorHandler(clientError))
                .then(() => _saveAnswer(handler.clean(), questionId))
                .then(storeAnswer)
                .then(saveDocuments(handler))
                .then(autoAdvanceQuestion())
                .finally(() => dispatch(answerSaved()));

            function errorHandler(handler){
                return function(response){
                    let errors = _.flatten(_.values(response.data));
                    errors = errors.length ? errors : response;
                    dispatch(handler(errors, questionId));

                    if(autoAdvanceOnAnswer && deferCorrection){
                        dispatch(InteractionActions.gotoNextQuestion(questionId));
                    }

                    return $q.reject();
                }
            }

            function _saveAnswer(cleanedData, questionId){
                let { homeId } = getState().settings;
                let url = '/api/v2/answer/';
                let data = {
                    'home': homeId,
                    'question': questionId,
                    'user': window.user_id,
                    'answer': cleanedData.answer,
                    'comment': cleanedData.comment
                };

                return $http.post(url, data).then(easyTransform).catch(errorHandler(serverError));
            }

            function storeAnswer(question){
                dispatch(removeErrors(question.id));

                if(question.answer){
                    let answer =  question.answer;
                    question.answer = answer.id;
                    dispatch(receiveAnswers([answer]));
                }

                if(question.related_answer){
                    let relatedAnswer = question.related_answer;
                    question.related_answer = relatedAnswer.id;
                    dispatch(receiveRelatedAnswers([relatedAnswer]));
                }

                dispatch(receiveQuestions([question]));
                dispatch(removeTemporaryAnswer(question));

                return question;
            }

            function saveDocuments(handler){
                return function(question){
                    let answerModelType = getState().entities.answers[question.answer].model_type;
                    let promises = _.map(handler.clean().customer_documents, document => saveDocument(document, question, answerModelType));

                    return $q.all(promises)
                    .then(documents => documents.map(document => dispatch(attachDocumentToAnswer(document, question.answer))));

                }
            }

            function saveDocument(document, question, answerModel){
                return $http.post(`/api/v2/${answerModel}/documents/?machinery=${answerModel}`, {
                    document_raw: document.raw,
                    document_raw_name: document.name,
                    object_id: question.answer
                }).then(easyTransform)
                // endpoint returns a examine region response.
                .then(doc => doc.object);
            }

            function autoAdvanceQuestion(){
                /**
                 * Return a function with a closure over the next questionId.
                 * We need to find the next question before we save an answer
                 * and possible cause a change in the list of viewable question.
                 */
                let { skipAnsweredQuestions } = state.settings.interactions;
                let nextId = getNextQuestionId(state, questionId, skipAnsweredQuestions);
                return function(){
                    if(autoAdvanceOnAnswer) dispatch(stateGo('checklist.detail', {id: nextId}));
                }
            }
        }
    }

    function retractAnswer(answer){
        return function(dispatch, getState){
            function successCallback(question){
                dispatch(receiveQuestions([question]));
                dispatch(deleteAnswer(answer));
            }

            return $http.delete(answer.delete_url).then(easyTransform).then(successCallback, function(){
                console.error('Handle errors for non retractable answers');
                debugger;
            });
        }
    }

    function storeDocument(file, questionId){
        return function(dispatch, getState){
            dispatch(attachDocumentShellToTemporaryAnswer(file, questionId));
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
                    .then(() => dispatch(attachDocumentToTemporaryAnswer(file, questionId)))
                    .catch(response => {
                        dispatch(removeDocumentShell(file.name, questionId));
                        dispatch(documentValidationError(response.data, questionId));
                    })
            }

            reader.readAsDataURL(file.file);
        }
    }

    return {
        storeTemporaryAnswer,
        saveAnswer,
        retractAnswer,
        updateComment,
        storeDocument,
        removeDocument,
        stateGo
    };
}

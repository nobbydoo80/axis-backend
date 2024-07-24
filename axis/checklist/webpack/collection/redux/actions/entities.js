import { collector } from '../../collector';

import { requestingQuestions, receiveQuestions } from './questions';
import { receiveAnswers, receiveRelatedAnswers } from './answers';
import actions from './../constants/entities';


export function receiveEEPProgram(program){
    return {
        type: actions.RECEIVE_EEP_PROGRAM,
        payload: { program }
    };
}

export function clearEntities(){
    return {
        type: actions.CLEAR_ENTITIES
    };
}

function ingest(dispatch) { return (info) => {
    // Ensure collector is stored/update
    collector.initialize(info, true);
    dispatch(receiveEEPProgram({
        id: info.specification.eep_program_id,
        name: info.specification.name,
        user_role: info.specification.user_role
    }));
    ingestInstruments(dispatch)(info.instruments, info.specification.user_role);
}}

function ingestInstruments(dispatch) { return (instruments, user_role) => {
    if (instruments.json !== undefined) {
        instruments = instruments.json
    }
    dispatch(receiveQuestions(_.indexBy(instruments, 'measure')));
    _.each(instruments, (instrument) => { // each instrument of spec
        instrument.user_role = user_role;
        collector.setCollector(instrument.collection_request);
        let read_only = collector.collector.full_specification.read_only;
        if (read_only) {
            instrument.read_only = read_only;
        }

        _.each(instrument.collectedinput_set, (inputList, role) => { // each role group for instrument's inputs
            _.each(inputList, (input) => {
                input.measure = instrument.measure;
            });
            if (role == instrument.user_role) {
                dispatch(receiveAnswers(inputList));
            } else {
                dispatch(receiveRelatedAnswers(inputList));
            }
        });
    });
}}

export function entitiesActions($http){
    return {
        discoverCollectors(discoverId) { return (dispatch, getState) => {
            dispatch(requestingQuestions());
            let { homeId } = getState().settings;
            let queryParams = {};
            if (discoverId !== undefined) {
                queryParams['collection_request_id'] = discoverId;
            }
            return $http.get(`/api/v2/home/${homeId}/collectors/`, queryParams)
                    .success(collections => _.map(collections, ingest(dispatch)));
        }},
        addInstruments(instrumentsList, userRole, dispatch) {
            return ingestInstruments(dispatch)(instrumentsList, userRole);
        }
    }
}

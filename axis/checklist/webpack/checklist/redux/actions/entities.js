import { receiveSections } from './sections';
import actions from './../constants/entities';
import { questionActions } from './questions';

export function receiveEEPProgram(program){
    return {
        type: actions.RECEIVE_EEP_PROGRAM,
        payload: { program }
    };
}

export function receiveChecklist(checklist){
    return {
        type: actions.RECEIVE_CHECKLIST,
        payload: { checklist }
    };
}

export function clearEntities(){
    return {
        type: actions.CLEAR_ENTITIES
    };
}


export function entitiesActions($q, $http){

    function fetchPrograms(){
        return function(dispatch, getState){
            return getState().settings.eepProgramIds.map(eepId => {
                return $http.get(`/api/v2/eep_program/${eepId}/`)
                    .then(response => response.data)
                    .then(program => {
                        dispatch(receiveEEPProgram(program));
                        dispatch(fetchChecklists(program.required_checklists));
                    });
            });
        }
    }

    function fetchChecklists(checklistIds){
        return function(dispatch){
            return checklistIds.map(checklistId => {
                return $http.get(`/api/v2/checklists/${checklistId}/`)
                    .then(response => response.data)
                    .then(checklist => {
                        dispatch(receiveChecklist(checklist));
                        dispatch(receiveSections(checklist.sections));
                    });
            })
        }
    }

    function matchPrograms(programIds){
        return function(dispatch, getState){
            dispatch(clearEntities());

            let _questionActions = questionActions($q, $http);
            programIds.sort().forEach(programId => dispatch(_questionActions.externalFetchQuestions(programId)));

        }
    }

    return { fetchPrograms, matchPrograms };

}

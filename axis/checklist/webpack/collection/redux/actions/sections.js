import actions from './../constants/sections';

export function receiveSections(sections){
    return {
        type: actions.RECEIVE_SECTIONS,
        payload: { sections }
    };
}

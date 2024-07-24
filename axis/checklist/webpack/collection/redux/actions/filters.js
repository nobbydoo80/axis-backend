import actions from './../constants/filters'

export function setSearchString(value){
    return {
        type: actions.SET_FILTER_STRING,
        payload: {value}
    };
}

export function setTypeCheckbox(key, value){
    return {
        type: actions.SET_TYPE_CHECKBOX,
        payload: {key, value}
    };
}

export function setStateCheckbox(key, value){
    return {
        type: actions.SET_STATE_CHECKBOX,
        payload: {key, value}
    };
}

export function setSectionCheckbox(key, value){
    return {
        type: actions.SET_SECTION_CHECKBOX,
        payload: {key, value}
    };
}

export function setProgramCheckbox(key, value){
    return {
        type: actions.SET_PROGRAM_CHECKBOX,
        payload: {key, value}
    };
}

export function resetFilters(){
    return {
        type: actions.RESET_FILTERS
    }
}

export function filterActions(){
    return {
        setSearchString,
        setTypeCheckbox,
        setStateCheckbox,
        setSectionCheckbox,
        setProgramCheckbox,
        resetFilters
    }
}

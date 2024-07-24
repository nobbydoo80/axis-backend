import * as actions from './../constants/answers';

export function answer(state='', action){
    switch(action.type){
        case actions.STORE_MULTIPLE_CHOICE_ANSWER:
        case actions.STORE_OPEN_ANSWER:
            return action.payload.answer;
        default:
            return state;
    }
}

export function comment(state='', action){
    switch(action.type){
        case actions.UPDATE_COMMENT:
            return action.payload.comment;
        default:
            return state;
    }
}

export function customer_documents(state=[], action){
    switch(action.type){
        case actions.STORE_DOCUMENTS_SHELL:
            return _.uniq([...state, _.assign({}, action.payload.file, {isLoading: true})]);
        case actions.STORE_DOCUMENT:
            return _.map(state, file => {
                if(file.name === action.payload.file.name){
                    return _.assign({}, file, action.payload.file, {isLoading: false});
                }
                return file;
            });
        case actions.REMOVE_DOCUMENT:
        case actions.REMOVE_DOCUMENT_SHELL:
            return state.filter(f => f.name != action.payload.fileName);
        default:
            return state;
    }
}

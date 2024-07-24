import {combineReducers} from 'redux';
import {router} from 'redux-ui-router';
import filters from './reducers/filters';
import settings from './reducers/settings';
import entities from './reducers/entities';

const rootReducer = combineReducers({
    router,
    filters,
    settings,
    entities,
});

export default rootReducer;

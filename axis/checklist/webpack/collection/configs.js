import thunk from 'redux-thunk';
import { createLogger } from 'redux-logger';

import * as routes from './routes';
import rootReducer from './redux/rootReducer';

const isHomePage = window.__ExamineSettings.page === 'home';

export function routing($urlRouterProvider, $stateProvider){
    // Having this otherwise on an examine page breaks
    // the ability to open and close panels without
    // an wrong redirect to the index route.
    if(!isHomePage) $urlRouterProvider.otherwise('/');

    $stateProvider
        .state('checklist', routes.checklistList)
        .state('checklist.detail', routes.checklistDetail)
        .state('checklist.settings', routes.settings);
}

export function redux($ngReduxProvider){
    const logger = createLogger({
        level: 'info',
        collapsed: true
    });

    let myMiddleware = store => next => action => {
        let result = next(action);
        window.state = store.getState();
        window.store = store;
        return result;
    }

    $ngReduxProvider.createStoreWith(rootReducer, ['ngUiRouterMiddleware', thunk, logger, myMiddleware]);
}

export function async($httpProvider){
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}

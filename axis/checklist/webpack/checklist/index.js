import ngRedux from 'ng-redux';
import ngReduxRouter from 'redux-ui-router';

import * as actions from './redux/actions/index';
import * as buttons from './components/buttons/index';
import * as components from './components/index';
import * as config from './configs';
import * as displays from './components/display/index';
import * as fields from './components/fields/index';
import * as utils from './components/utils/index';

import rootReducer from './redux/rootReducer.js';

export default angular.module('checklist', ['ui.bootstrap', 'ui.router', ngRedux, ngReduxRouter])
.config(config.routing)
.config(config.redux)
.config(config.async)

// Actions
.service('QuestionActions', actions.questionActions)
.service('AnswerActions', actions.answerActions)
.service('InteractionActions', actions.interactionActions)
.service('FilterActions', actions.filterActions)
.service('EntitiesActions', actions.entitiesActions)
// Components
.directive('fileTable', components.fileTable)
.directive('checklist', components.checklistApp)
.directive('userSettings', components.userSettings)
.directive('questionList', components.questionList)
.directive('allQuestionsList', components.allQuestionsList)
.directive('programSeparatedList', components.programSeparatedList)
.directive('questionListItems', components.questionListItems)
.directive('questionDetail', components.questionDetail)
.directive('questionFilterSettings', components.filterSettings)
.directive('questionFilterSetting', components.filterSetting)
.directive('questionFilterSettingCheckbox', components.filterSettingCheckbox)
// Fields
.directive('openInput', fields.openInput)
.directive('fileInput', fields.fileInput)
.directive('searchField', fields.searchField)
.directive('commentField', fields.commentField)
.directive('checklistField', fields.checklistField)
.directive('multipleChoice', fields.multipleChoice)
.directive('multipleChoiceInput', fields.multipleChoiceInput)
// Displays
.directive('answeredBy', displays.answeredBy)
.directive('answerMisc', displays.answerMisc)
.directive('choiceMisc', displays.choiceMisc)
.directive('fileDisplay', displays.fileDisplay)
.directive('pendingReview', displays.pendingReview)
.directive('commentDisplay', displays.commentDisplay)
.directive('checklistProgressBar', displays.checklistProgressBar)
// Buttons
.directive('retract', buttons.retract)
.directive('checklistActions', buttons.checklistActions)
.directive('homeDetailDropdown', buttons.homeDetailDropdown)
.directive('settingsButton', buttons.settingsButton)
// Utils
.directive('scroller', utils.scroller)

.filter('words', function(){
    return function (input, words){
        if(isNaN(words)) return input;
        if(words <= 0) return '';
        if(input){
            let inputWords = input.split(/\s+/);
            if(inputWords.length > words){
                input = inputWords.slice(0, words).join(' ') + '...';
            }
        }
        return input;
    }
})
.filter('bytes', function(){
    let units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'];
    return function(bytes, precision=1){
        if(bytes === 0){
            return '0 bytes';
        }
        if(isNaN( (bytes|0) || !isFinite(bytes))){
            return '-';
        }
        let number = Math.floor(Math.log(bytes) / Math.log(1024));
        let val = (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision);

        return `${(val.match(/\.0*$/) ? val.substr(0, val.indexOf('.')) : val)} ${units[number]}`;
    }
})

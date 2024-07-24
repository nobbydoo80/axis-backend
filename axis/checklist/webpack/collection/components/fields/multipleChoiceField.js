import { createSelector } from 'reselect';

class MultipleChoiceController {
    constructor($ngRedux, $scope, $element, $timeout, AnswerActions){
        this.dispatch = $ngRedux.dispatch;
        this.getState = $ngRedux.getState;
        this.$scope = $scope;
        this.$element = $element;
        this.$timeout = $timeout;
        this.AnswerActions = AnswerActions;
        this.clear = () => this.data.input = {};
    }
    getDisplayClass(choice) {
        if (choice.is_failure){
            return 'btn-danger';
        } else {
            return 'btn-success';
        }
    }
    update(choice) {
        let {'data': input, _suggested_response} = choice;
        Object.assign(this.answer.data, {input, _suggested_response});
        this.$timeout(() => this.$scope.$digest(), 0);
    }
    clickUpdate(choice) {
        this.update(choice);
        let andSave = this.getState().settings.interactions.autoSubmitMultipleChoice;
        this.hooks.update(andSave, choice);
    }
}

class MultipleChoiceInputController {
    constructor(){
        // used in template
        this.getClasses = createSelector(...this.inputSelectors(), this.classesGetter);
    }
    inputSelectors(){
        return [
            () => this.selectedClass,
            () => this.isSelected,
            () => this.isDisabled
        ];
    }
    classesGetter(selectedClass, isSelected, isDisabled){
        return {
            [selectedClass]: isSelected,
            'disabled': isDisabled
        };
    }
}

export function multipleChoice(){
    return {
        scope: {
            hooks: '=',
            choices: '=',
            question: '=',
            answer: '=',
            isDisabled: '=',
        },
        template: `
        <copy-value-button text-to-copy="ctrl.answer.data.input"></copy-value-button>
        <div class="control btn-group form-group" data-toggle="buttons">
            <multiple-choice-input
                hooks="ctrl.hooks"
                name="ctrl.question.measure"
                label="choice.data"
                ng-click="ctrl.clickUpdate(choice)"
                is-selected="ctrl.answer.data.input == choice.data"
                selected-class="ctrl.getDisplayClass(choice)"
                is-disabled="ctrl.isDisabled"
                ng-repeat="choice in ctrl.choices"
            ></multiple-choice-input>
        </div>
        `,
        controller: MultipleChoiceController,
        controllerAs: 'ctrl',
        bindToController: true
    };
}

export function multipleChoiceInput(){
    return {
        scope: {
            hooks: '=',
            name: '=',
            label: '=',
            isDisabled: '=',
            isSelected: '=',
            selectedClass: '='
        },
        template: `
        <label class="btn btn-default" ng-class="input.getClasses()">
            <input type="radio"
                name="[[ input.name ]]"
                ng-class="[[ isSelected ? input.selectedClass : '' ]]"
                ng-value="input.label"
                ng-disabled="input.isDisabled" /> [[ input.label ]]
        </label>
        `,
        replace: true,  // deprecated in next version of angular
        controller: MultipleChoiceInputController,
        controllerAs: 'input',
        bindToController: true
    };
}

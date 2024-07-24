import { createSelector } from 'reselect';

import { multipleChoiceSelectedChoice } from './../../redux/selectors/multipleChoiceSelectedChoice';

class MultipleChoiceController {
    constructor($ngRedux, $scope, $element, $timeout){
        this.$element = $element;
        this.$timeout = $timeout;
        this.setSelectedChoice = () => this.selectedChoice = this.getSelectedChoice($ngRedux.getState());
        this.setSelectedChoice();

        $scope.$on('$destroy', $ngRedux.subscribe(() => this.setSelectedChoice()));
        $scope.$on('$destroy', $scope.$watch(() => this.question, () => this.setSelectedChoice(), true));
    }
    isChoiceSelected(choice){
        return this.selectedChoice && this.selectedChoice.id === choice.id;
    }
    getDisplayClass(choice){
        // FIXME: do we want this to be red if its technically not a failure, but will display as one?
        if(choice.display_as_failure || choice.is_considered_failure){
            return 'btn-danger';
        } else {
            return 'btn-success';
        }
    }
    getSelectedChoice(state){
        if(this.answer){
            return _.find(this.question.choices, {'choice': this.answer.answer});
        } else if(state.entities.temporaryAnswer[this.question.id]){
            let answer = state.entities.temporaryAnswer[this.question.id].answer;
            return _.find(this.question.choices, {'choice': answer});
        }
        return {};
    }
    clickHandler(choice){
        /**
         * Bob wasn't happy with the way opening the file dialog felt.
         * We decided to remove it until we could get a better feel for the problem.
        // if(choice.choice.toLowerCase().indexOf('upload document') > -1 || choice.choice.toLowerCase().indexOf('upload photo') > -1){
        //     let fileField = this.$element.closest('question-detail').find('[data-provides=fileinput]').fileinput();
        //     this.$timeout(function(){
        //         fileField.data('bs.fileinput').trigger($.Event());
        //     }, 100);
        // }
        */
        this.answerCallback({choice: choice});
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
            choices: '=',
            question: '=',
            answer: '=',
            isDisabled: '=',
            answerCallback: '&'
        },
        template: `
        <div class='control btn-group form-group' data-toggle='buttons'>
            <multiple-choice-input
                name='ctrl.question.id'
                label='choice.choice'
                is-disabled='ctrl.isDisabled'
                is-selected='ctrl.isChoiceSelected(choice)'
                selected-class='ctrl.getDisplayClass(choice)'
                ng-click="ctrl.clickHandler(choice)"
                ng-repeat='choice in ctrl.choices'
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
            name: '=',
            label: '=',
            isDisabled: '=',
            isSelected: '=',
            selectedClass: '='
        },
        template: `
        <label class='btn btn-default' ng-class='input.getClasses()'>
            <input type='radio'
                name='[[ input.name ]]'
                ng-value='input.label'
                ng-disabled='input.isDisabled' /> [[ input.label ]]
        </label>
        `,
        replace: true,  // deprecated in next version of angular
        controller: MultipleChoiceInputController,
        controllerAs: 'input',
        bindToController: true
    };
}

import { PLACEHOLDERS, TOOLTIPS } from './../../settings';

class OpenFieldInputController {
    constructor($ngRedux, $scope, $element, $timeout){
        this.placeholder = PLACEHOLDERS[this.question.type] || '';
        this.tooltip = TOOLTIPS[this.question.type] || '';

        this.answerSetter = () => this.answer = this.getDisplay($ngRedux.getState());

        $scope.$on('$destroy', $scope.$watchGroup([() => this.question.answer, () => this.question.id], () => this.answerSetter()));

        if(!this.isRelatedAnswer){
            $timeout(function(){
                $element.find('input').focus();
            },0 );
        }
    }
    getDisplay(state){
        let {temporaryAnswer, answers, relatedAnswers} = state.entities;
        if(this.isRelatedAnswer){
            return relatedAnswers[this.question.related_answer].answer;
        } else {
            if(this.question.answer){
                return answers[this.question.answer].answer;
            } else if(temporaryAnswer[this.question.id]){
                return temporaryAnswer[this.question.id].answer;
            }
        }
        return '';
    }
}

export function openInput(){
    return {
        scope: {
            question: '=',
            answer: '=',
            isDisabled: '=',
            isRelatedAnswer: '=',
            answerCallback: '&'
        },
        template: `
        <div class='form-group'>
            <form class='controls' ng-submit='input.answerCallback({answer: input.answer, triggerSave: true})'>
                <div class="input-group" ng-if="input.question.unit">
                    <input type='text'
                        class='textinput textInput form-control'
                        ng-model='input.answer'
                        ng-change='input.answerCallback({answer: input.answer})'
                        ng-attr-placeholder='[[ input.placeholder ]]'
                        ng-readonly='input.isDisabled'
                        />
                    <span class="input-group-addon">[[ input.question.unit  ]]</span>
                </div>
                <input type="text"
                    class="textinput textInput form-control"
                    ng-model="input.answer"
                    ng-change="input.answerCallback({answer: input.answer})"
                    ng-attr-placeholder="[[ input.placeholder ]]"
                    ng-readonly="input.isDisabled"
                    ng-if="!input.question.unit">
            </form>
        </div>
        `,
        replace: true,
        controller: OpenFieldInputController,
        controllerAs: 'input',
        bindToController: true,
    };
}

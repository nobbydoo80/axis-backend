import { PLACEHOLDERS, TOOLTIPS } from './../../settings';

class OpenInputController {
    constructor($element, $timeout){
        if (!this.question) {
            return;
        }
        this.placeholder = PLACEHOLDERS[this.question.type] || '';
        this.tooltip = TOOLTIPS[this.question.type] || '';

        if (!this.isRelatedAnswer) {
            $timeout(function(){
                $element.find('input').focus();
            },0 );
        }
    }
}

export function openInput(){
    return {
        scope: {
            question: '=',
            answer: '=',
            isDisabled: '=',
            isRelatedAnswer: '=',
            hooks: '='
        },
        replace: true,
        controller: OpenInputController,
        controllerAs: 'input',
        bindToController: true,
        template: `
        <div class='form-group'>
            <form class='controls' ng-submit='ctrl.hooks.save()'>
                <div class="input-group" ng-if="input.question.unit">
                    <input type='text'
                        class="textinput textInput form-control"
                        name="input.question.measure"
                        ng-model="input.answer.data.input"
                        ng-change='input.hooks.update()'
                        ng-attr-placeholder='[[ input.placeholder ]]'
                        ng-readonly='input.isDisabled'
                        />
                    <span class="input-group-addon">[[ input.question.unit  ]]</span>
                </div>
                <input type="text"
                    class="textinput textInput form-control"
                    ng-model="input.answer.data.input"
                    ng-change="input.hooks.update()"
                    ng-attr-placeholder="[[ input.placeholder ]]"
                    ng-readonly="input.isDisabled"
                    ng-if="!input.question.unit">
            </form>
        </div>
        `
    };
}

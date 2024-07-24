import { PLACEHOLDERS, TOOLTIPS } from './../../settings';

class DateInputController {
    constructor($element, $timeout){
        if (!this.question) {
            return;
        }
        this.placeholder = PLACEHOLDERS[this.question.type] || '';
        this.tooltip = TOOLTIPS[this.question.type] || '';

        if (!this.isRelatedAnswer) {
            $timeout(function(){
                $element.find('input').focus();
            }, 0);
        }
    }
}

export function dateInput(){
    return {
        scope: {
            question: '=',
            answer: '=',
            isDisabled: '=',
            isRelatedAnswer: '=',
            hooks: '='
        },
        replace: true,
        controller: DateInputController,
        controllerAs: 'input',
        bindToController: true,
        template: `
        <div class='form-group'>
            <form class='controls' ng-submit='ctrl.hooks.save()'>
                <div class="row">
                    <div class="col-md-5">
                        <input type='text'
                            class="textinput textInput form-control"
                            name="input.question.measure"
                            ng-model="input.answer.data.input"
                            ng-change='input.hooks.update()'
                            ng-attr-placeholder='[[ input.placeholder ]]'
                            ng-readonly='input.isDisabled'
                            datepicker-popup="shortDate"
                            />
                    </div>
                </div>
                <div class="row" style="margin-top: 2px">
                    <div class="col-md-5 text-center">
                        <datepicker
                            class="well well-sm"
                            show-weeks="false"
                            ng-model="input.answer.data.input"
                            date-disabled="input.isDisabled"
                            />
                    </div>
                </div>
            </form>
        </div>
        `
    };
}

import { collector } from '../../collector';

export function checklistField($compile){
    return {
        scope: {
            question: '=',
            answer: '=',
            isDisabled: '=',
            isRelatedAnswer: '=',
            hooks: '=',
        },
        template: `
        <div ng-switch="question.type">
            <div ng-switch-when="multiple-choice">
                <multiple-choice
                    hooks="hooks"
                    choices="question.suggested_responses"
                    question="question"
                    answer="answer"
                    is-disabled="isDisabled"
                    is-related-answer="isRelatedAnswer"
                ></multiple-choice>
            </div>
            <div ng-switch-when='cascading-select'>
                <cascade-field
                    hooks="hooks"
                    question="question"
                    answer="answer"
                    is-disabled="isDisabled"
                    is-related-answer="isRelatedAnswer"
                    ></cascade-field>
            </div>
            <div ng-switch-when='date'>
                <date-input
                    hooks="hooks"
                    question="question"
                    answer="answer"
                    is-disabled="isDisabled"
                    is-related-answer="isRelatedAnswer"
                    ></date-input>
            </div>
            <div ng-switch-default>
                <open-input
                    hooks="hooks"
                    question="question"
                    answer="answer"
                    is-disabled="isDisabled"
                    is-related-answer="isRelatedAnswer"
                ></open-input>
            </div>
        </div>
        `
        // link: function postLink(scope, element, attrs) {
        //     var question = scope.question;
        //     if (question === undefined || question.id === undefined) {
        //         // This thing gets initialized an insane number of times before it's actually got
        //         // a real value for ``question``.
        //         return;
        //     }
        //     var info = collector.specification.instruments_info.instruments[question.id];
        //     element.html(info.response_info.method.template);
        //     $compile(element.contents())(scope);
        // }
    }
}

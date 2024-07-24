export function checklistField(){
    return {
        scope: {
            question: '=',
            answer: '=',
            isDisabled: '=',
            isRelatedAnswer: '=',
            callbacks: '='
        },
        template: `
        <div ng-switch='question.type'>
            <div ng-switch-when='multiple-choice'>
                <multiple-choice
                    choices='question.choices'
                    question='question'
                    answer='answer'
                    is-disabled='isDisabled'
                    is-related-answer="isRelatedAnswer"
                    answer-callback='callbacks.multipleChoiceAnswerCallback(choice, triggerSave)'
                ></multiple-choice>
            </div>
            <div ng-switch-default>
                <open-input
                    question='question'
                    answer='answer.answer'
                    is-disabled='isDisabled'
                    is-related-answer='isRelatedAnswer'
                    answer-callback='callbacks.openAnswerCallback(answer, triggerSave)'
                ></open-input>
            </div>
        </div>
        `
    }
}

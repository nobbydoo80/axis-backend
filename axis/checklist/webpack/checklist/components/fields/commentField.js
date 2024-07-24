class CommentFieldInputController {
    constructor($ngRedux, $scope){
        this.displaySetter = () => this.comment = this.getDisplay($ngRedux.getState());

        $scope.$on('$destroy', $scope.$watch(() => this.question.answer, () => this.displaySetter()));
    }
    getDisplay(state){
        if(this.question.answer){
            return state.entities.answers[this.question.answer].comment;
        } else if(state.entities.temporaryAnswer[this.question.id]){
            return state.entities.temporaryAnswer[this.question.id].comment;
        }
        return '';
    }

}

export function commentField(){
    return {
        scope: {
            commentRequired: '=',
            changeCallback: '&',
            question: '=',
            answer: '='
        },
        controller: CommentFieldInputController,
        controllerAs: 'input',
        bindToController: true,
        template: `
        <div class='form-group'>
            <div class='controls' ng-if='!input.answer.id'>
                <label class='control-label'>Comment[[ input.commentRequired ? '*' : '' ]]</label>
                <textarea
                    ng-attr-placeholder='[[ input.commentRequired ? "Comment Required..." : "Comment..." ]]'
                    ng-model='input.comment'
                    ng-change='input.changeCallback({comment: input.comment})'
                    class='textarea form-control' />
            </div>
            <comment-display
                ng-if="input.answer.id && input.answer.comment"
                comment="input.answer.comment"
                commenter="input.answer.full_name"
            ></comment-display>
        </div>
        `
    }
}

class CommentFieldInputController {
    constructor($ngRedux, $scope){
        this.displaySetter = () => this.comment = this.getDisplay($ngRedux.getState());

        $scope.$on('$destroy', $scope.$watch(() => this.answer, () => this.displaySetter()));
    }
    getDisplay(state){
        return this.data;
    }

}

export function commentField(){
    return {
        scope: {
            data: '=',
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
            <div class='controls' ng-if='!input.data.id'>
                <label class='control-label'>Comment[[ input.commentRequired ? '*' : '' ]]</label>
                <textarea
                    ng-attr-placeholder='[[ input.commentRequired ? "Comment Required..." : "Comment..." ]]'
                    ng-model='input.data'
                    ng-change='input.hooks.update()'
                    class='textarea form-control' />
            </div>
            <comment-display
                ng-if="input.data.id"
                comment="input.data.comment"
                commenter="input.data.user.full_name"
            ></comment-display>
        </div>
        `
    }
}

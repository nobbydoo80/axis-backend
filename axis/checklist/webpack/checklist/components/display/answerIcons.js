export function answerMisc(){
    // TODO: make sure documents come down in answer(image|document)_set keys.
    return {
        scope: {
            answer: '=',
            showCommentTooltip: '='
        },
        template: `
        <div>
            <i class='fa fa-fw fa-comment-o' ng-if='answer.comment && showCommentTooltip' tooltip="[[ answer.comment ]]"></i>
            <i class='fa fa-fw fa-comment-o' ng-if='answer.comment && !showCommentTooltip'></i>
            <i class='fa fa-fw fa-picture-o' ng-if='answer.answerimage_set.length'></i>
            <i class='fa fa-fw fa-file-text' ng-if='answer.answerdocument_set.length || answer.customer_documents.length'></i>
        </div>
        `
    }
}

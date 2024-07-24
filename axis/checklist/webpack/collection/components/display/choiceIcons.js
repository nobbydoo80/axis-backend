export function choiceMisc(){
    return {
        scope: {
            choice: '='
        },
        template: `
        <div>
            <i class='fa fa-fw fa-comment-o' ng-if='choice.comment_required'></i>
            <i class='fa fa-fw fa-picture-o' ng-if='choice.photo_required'></i>
            <i class='fa fa-fw fa-file-text' ng-if='choice.document_required'></i>
        </div>
        `
    }
}

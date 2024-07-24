export function commentDisplay(){
    return {
        scope: {
            label: '@',
            comment: '=',
            commenter: '='
        },
        template: `
        <div>
            <label class="control-label">[[ label || 'Comment' ]]</label>
            <blockquote>
                <p>[[ comment ]]</p>
                <footer ng-if="commenter">[[ commenter ]]</footer>
            </blockquote>
        </div>
        `
    }
}

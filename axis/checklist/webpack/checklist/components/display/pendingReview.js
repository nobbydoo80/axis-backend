export function pendingReview(){
    return {
        scope: {
            answer: '='
        },
        template: `<em ng-if='reviewIsPending'>Pending Review</em>`,
        link: function(scope){
            scope.reviewIsPending = _reviewIsPending();

            function _reviewIsPending(){
                let answer  = scope.answer;
                if(answer){
                    let {confirmed, is_considered_failure, failure_is_reviewed} = answer;
                    return !confirmed && is_considered_failure && !failure_is_reviewed;
                }
                return false;
            }
        }
    }
}

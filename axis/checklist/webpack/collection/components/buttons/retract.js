import { READONLY } from './../../settings';

export function retract(){
    return {
        scope: {
            answer: '=',
            retractCallback: '&'
        },
        template: `<a class='btn btn-default btn-xs' ng-if='answerIsRetractable()' ng-click='retractCallback()'>Retract</a>`,
        link: function(scope){
            scope.answerIsRetractable = function(){
                let answer = scope.answer;
                if(answer){
                    let {confirmed, is_considered_failure} = answer;
                    return !confirmed && !is_considered_failure && !READONLY;
                }
                return false;
            }
        }
    }
}

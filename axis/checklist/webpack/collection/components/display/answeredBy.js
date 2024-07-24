export function answeredBy(){
    return {
        scope: {
            answer: '='
        },
        template: `
        <small ng-if='answer.id'>
            By: [[ answer.user.full_name ]] <br>
            On: [[ answer.date_created | date:'shortDate' ]]
        </small>
        `
    };
}

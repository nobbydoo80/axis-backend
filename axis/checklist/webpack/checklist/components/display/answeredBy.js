export function answeredBy(){
    return {
        scope: {
            answer: '='
        },
        template: `
        <small ng-if='answer'>
            By: [[ answer.full_name ]] <br>
            On: [[ answer.created_date ]]
        </small>
        `
    };
}

export function fileDisplay(){
    return {
        scope: {
            doc: '=',
            removeCallback: '&',
            uploadedBy: '='
        },
        template: `
        <tr>
            <td ng-if="doc.id">
                <a ng-href="[[ doc.document ]]">
                <i class="fa fa-cloud-download"></i>
                [[ doc.filename ]]
                </a>
                <small class="text-muted" ng-if="doc.filesize">
                    ([[ doc.filesize | bytes ]])
                </small>
                <small class="text-muted" ng-bind="uploadedBy"></small>
            </td>
            <td ng-if="!doc.id">
                <i class="fa fa-fw fa-spin fa-spinner fa-lg" ng-if="doc.isLoading"></i>
                [[ doc.name || doc.filename ]]
                <small class="text-muted" ng-if="doc.file.size">([[ doc.file.size | bytes ]])</small>
            </td>
            <td>
                <a ng-if="!doc.id" ng-click="removeCallback({doc: doc})"><i class="fa fa-fw fa-times"></i></a>
            </td>
        </tr>
        `,
        replace: true  // deprecated in next version of angular
    }
}

export function fileTable(){
    return {
        scope: {
            label: '@',
            acceptedTypes: '@',
            documents: '=',
            documentsUploader: '=',
            relatedDocuments: '=',
            relatedDocumentsUploader: '=',
            showRelatedDocuments: '=',
            canAdd: '=',
            addCallback: '&',
            removeCallback: '&'
        },
        controller: function(){
            this.add = (name, file, extension) => {
                this.addCallback({name, file, extension});
            };
            this.remove = (doc) => {
                this.removeCallback({doc});
            };
        },
        controllerAs: 'table',
        bindToController: true,
        template: `
        <table class='table table-striped table-bordered'>
            <thead>
                <th>
                    [[ table.label ]]
                    <i class="fa fa-info-circle" tooltip="Accepted File Types: [[table.acceptedTypes]]"></i>
                </th>
                <th>[[ table.canAdd ? 'Delete' : '' ]]</th>
            </thead>
            <tbody>
                <tr file-display ng-if="table.showRelatedDocuments" ng-repeat="doc in table.relatedDocuments" doc="doc" uploaded-by="table.relatedDocumentsUploader"></tr>
                <tr file-display ng-repeat='doc in table.documents' doc='doc' uploaded-by="table.documentsUploader" remove-callback='table.remove(doc)'></tr>
                <tr ng-if='!table.canAdd && !table.documents.length' class='text-center'>
                    <td colspan='2'>No Documents</td>
                </tr>

                <tr ng-if='table.canAdd'>
                    <td>
                        <file-input callback='table.add(name, file, extension)'></file-input>
                    </td>
                    <td></td>
                </tr>
            </tbody>
        </table>
        `,
        replace: true, // deprecated in next version of angular
    }
}

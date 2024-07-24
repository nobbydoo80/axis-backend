angular.module('examineApp')

.run(function($rootScope, Actions){
    var object_id = window.__primary_object_id;

    Actions.addPreMethodToType('save', 'builderagreement_documents', function(regionObject){
        regionObject.object.object_id = object_id;
    });

    $rootScope.$on("addedRegion:builderagreement_documents", function(e, regionObject){
        regionObject.region_dependencies = {};
    });
});

angular.module(
    'axis.navigation',
    ['ui.bootstrap',]
).controller('MainNavigationController', function ($scope, $modal, $rootScope) {
    const ctrl = this;
    ctrl.changeCompany = function ($event) {
        $event.preventDefault();
        return $modal.open({
            controller: 'ChangeCompanyModalInstanceCtrl',
            templateUrl: '/examine/core/change_company_dialog.html',
            size: 'lg'
        });
    };
}).controller('ChangeCompanyModalInstanceCtrl', function ($scope, $modalInstance, $rootScope, $http, $timeout, $compile) {

    $scope.isLoading = false;

    $timeout(function () {
        $('#change-company-modal-datatable').DataTable(
        {
            ajax: {
                url: '/api/v3/company_accesses/',
                dataSrc: 'results'
            },
            buttons: [],
            ordering: false,
            lengthChange: false,
            "createdRow": function ( row, data, index ) {
                $compile(row)($scope);  //add this to compile the DOM
            },
            columns: [
                {
                    title: "Company",
                    data: 'company',
                    render: function (data, type, row) {
                        return row.company_info.name + ' [' + row.company_info.company_type + ']';
                    }
                },
                {
                    title: "Roles",
                    data: 'roles',
                    render: function (data, type, row) {
                        let roles = [];
                        if (!row.roles_info.length) {
                            return 'Common User';
                        }
                        for (let i = 0; i < row.roles_info.length; i++) {
                            roles.push(row.roles_info[i].name);
                        }
                        return roles.join(',');
                    }
                },
                {
                    title: "Actions",
                    data: 'id',
                    render: function (data, type, row) {
                        return '<button class="btn btn-primary" ng-click="changeCompany('+row.id+')">Change</button>'
                    }
                }
            ],
        }
    );
    }, 0)

    $scope.changeCompany = function (companyAccessId) {
        $scope.isLoading = true;
        $http.post('/api/v3/companies/change_company/', {
            company_access: companyAccessId
        }).then(response => {
            window.location.reload();
        });
    }

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
});
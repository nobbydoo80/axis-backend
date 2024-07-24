var AxisMessaging = {
    '_date': function(data){
        var date = new Date(data);
        if (data !== null) {
            var minutes = '' + date.getMinutes();
            if (minutes.length == 1) {
                minutes = '0' + minutes;
            }
            return (date.getMonth()+1) + '/' + date.getDate() + '/' + ((date.getYear() + 1900) % 100) + ' ' + (date.getHours() % 12 || '12') + ":" + minutes + ' ' + (date.getHours() < 12 ? 'AM' : 'PM');
        }
        return data;
    },
    'renderers': {
        'level': function(data){
            var icons = {
                'debug': 'code',
                'info': 'info-circle',
                'success': 'check-circle',
                'warning': 'warning',
                'error': 'exclamation-circle',
                'system': 'circle-o-notch'
            }
            return '<i class="fa fa-fw fa-'+icons[data]+'"></i>'
        },
        'title': function(data, type, full){
            if (full.url) {
                return '<a href="'+full.url+'">'+data+'</a>';
            }
            return data;
        },
        'date_created': function(data){
            return AxisMessaging._date(data);
        },
        'date_alerted': function(data, type, full){
            var DELIVERY_GRACE_PERIOD = 5;  // minutes
            var date_alerted = new Date(data);
            var date_created = new Date(full.date_created);
            var check_date = new Date(date_created.getTime() + DELIVERY_GRACE_PERIOD * 60 * 1000);
            if (check_date > date_alerted) {
                return '<i class="fa fa-check"></i>';
            }
            return AxisMessaging._date(data);
        },
        'date_sent': function(data){
            if (data) {
                return '<i class="fa fa-check"></i>'
            }
            return '';
        },
        'actions': function(data, type, full){
            var actions = ""
            if (!full.alert_read){
                actions += '<a href class="mark-read" ng-click="messages.markTargetMessageAsRead('+full.id+')" title="Mark as read">' +
                               '<i class="fa fa-fw fa-check-circle text-[[ messages.getMessage('+full.id+').level | bootstrapcontext ]]"></i>' +
                           '</a>';
            }
            actions += '<a ng-show="messages.getMessage('+full.id+').url"' +
                          'ng-href="[[ messages.getMessage('+full.id+').url || \'\' ]]"' +
                          'title="Go to page"' +
                          'target="_blank">' +
                           '<i class="fa fa-fw fa-external-link text-[[ messages.getMessage('+full.id+').level | bootstrapcontext ]]"></i>' +
                       '</a>';
            actions += '<a ng-click="messages.openTargetMessage('+full.id+')"' +
                          'title="Show full notification">' +
                           '<i class="fa fa-fw fa-list-alt text-[[ messages.getMessage('+full.id+').level | bootstrapcontext ]]"></i>' +
                       '</a>';
            return actions;
        }
    },

    'ajax': {
        'data': function(data, settings){
            $('form').find('input,select').each(function(){
                var input = $(this);
                data[input.attr('name')] = input.val();
            });
        }
    },

    'options': {
        'fnRowCallback': function(row, data, i){
            var level = data.level;
            if (data.level == "error") {
                level = "danger";
            }
            $(row).addClass(level + ' text-' + level);
        }
    },

    // copy-pasted from bootstrap_datatables.js default structure shortcode
    'dom_shortcode': "<'row'<'col-xs-6'f><'col-xs-6 text-right'l>>" +
                     "rt" +
                     "<'row'<'col-xs-5'T><'col-xs-2 text-center'i><'col-lg-5'p>>"
}

angular.module('axis.messaging.inbox', ['axis.messaging', 'datatables', 'datatables.bootstrap'])

.controller('TabsController', function($scope){
    $scope.activate = function(tab_a){
        $(tab_a).tab('show');
    }
    $('[href="#tab-unread"]').tab('show');
})
.controller('DigestPreferenceController', function($http){
    var ctrl = this;
    var URLS = {
        'preference': "/api/v2/messages/preferences/digest/"
    }

    ctrl.threshold = null;
    ctrl.save = function(){
        ctrl.busy = true;
        $http.post(URLS.preference, {'threshold': ctrl.threshold})
             .success(function(){
                 ctrl.busy = false;
                 ctrl.error = null;
                 ctrl.success = true;
             })
             .error(function(error, statusCode){
                 ctrl.busy = false;
                 ctrl.success = false;
                 if (statusCode !== 500) {
                     ctrl.error = JSON.stringify(error);
                 } else {
                     ctrl.error = "An unexpected error occurred."
                 }
             })
    }

    $http.get(URLS.preference)
         .success(function(data){
             ctrl.threshold = data.threshold;
         });
})

.controller('MessagePreferencesController', function($http){
    var ctrl = this;
    var URLS = {
        'preferences': "/api/v2/messages/preferences/report/"
    }
    ctrl.busy = false;
    ctrl.error = null;
    ctrl.success = false;
    ctrl.preferences = [];
    ctrl.save = function(){
        ctrl.busy = true;
        var data = {};
        for (var category in ctrl.preferences) {
            data[category] = {};
            for (var name in ctrl.preferences[category]) {
                var preference = ctrl.preferences[category][name];
                data[category][name] = {
                    'id': preference.id,
                    'receive_notification': preference.receive_notification,
                    'receive_email': preference.receive_email
                };
            }
        }
        $http.post(URLS.preferences, data)
             .success(function(){
                 ctrl.busy = false;
                 ctrl.error = null;
                 ctrl.success = true;
             })
             .error(function(error, statusCode){
                 ctrl.busy = false;
                 ctrl.success = false;
                 if (statusCode !== 500) {
                     ctrl.error = JSON.stringify(error);
                 } else {
                     ctrl.error = "An unexpected error occurred."
                 }
             })
    }

    $http.get(URLS.preferences)
         .success(function(data){
             ctrl.preferences = data;
         });
})

.controller('UnreadMessagingRetrievalController', function($scope, $compile, DTOptionsBuilder, DTColumnBuilder, DTInstances){
    var ctrl = this;
    var URLS = {
        'data_source': "/api/v2/messages/datatable/?alert_read=0"
    }
    ctrl.options = DTOptionsBuilder.newOptions()
                        .withOption('ajax', {
                            'url': URLS.data_source,
                            'data': AxisMessaging.ajax.data
                        })
                        .withOption('bServerSide', true)
                        .withOption('dom', AxisMessaging.dom_shortcode)
                        .withDataProp('data')
                        .withOption('fnRowCallback', function(row, data, i){
                            AxisMessaging.options.fnRowCallback(row, data, i);
                            $scope.messages.informOfMessage(data);
                        })
                        .withOption('fnDrawCallback', function(settings){
                            var scope = angular.element(settings.oInstance).scope();
                            $compile(settings.oInstance.contents())(scope);
                        })
                        .withOption('order', [[4, 'desc']])
                        .withBootstrap()
    ctrl.columns = [
        DTColumnBuilder.newColumn('level').withTitle('<i class="fa fa-fw fa-bell"></i>')
                                          .renderWith(AxisMessaging.renderers.level),
        DTColumnBuilder.newColumn('title').withTitle('Type').renderWith(AxisMessaging.renderers.title),
        DTColumnBuilder.newColumn('content').withTitle('Content'),
        DTColumnBuilder.newColumn('category').withTitle('Category'),
        DTColumnBuilder.newColumn('date_created').withTitle('Date').renderWith(AxisMessaging.renderers.date_created).withOption('type', 'date'),
        DTColumnBuilder.newColumn('date_alerted').withTitle('Received').renderWith(AxisMessaging.renderers.date_alerted).withOption('type', 'date'),
        DTColumnBuilder.newColumn('date_sent').withTitle('Emailed').renderWith(AxisMessaging.renderers.date_sent).withOption('type', 'date'),
        DTColumnBuilder.newColumn('actions').withTitle('Actions').renderWith(AxisMessaging.renderers.actions)
    ]

    var datatable = null;
    DTInstances.getLast().then(function(dt) {
        datatable = dt;
    });
})
.controller('ReadMessagingRetrievalController', function($scope, $compile, DTOptionsBuilder, DTColumnBuilder){
    var ctrl = this;
    var URLS = {
        'data_source': "/api/v2/messages/datatable/?alert_read=1"
    }
    ctrl.options = DTOptionsBuilder.newOptions()
                        .withOption('ajax', {
                            'url': URLS.data_source,
                            'data': AxisMessaging.ajax.data
                        })
                        .withOption('bServerSide', true)
                        .withOption('dom', AxisMessaging.dom_shortcode)
                        .withDataProp('data')
                        .withOption('fnRowCallback', function(row, data, i){
                            AxisMessaging.options.fnRowCallback(row, data, i);
                            $scope.messages.informOfMessage(data);
                        })
                        .withOption('fnDrawCallback', function(settings){
                            var scope = angular.element(settings.oInstance).scope();
                            $compile(settings.oInstance.contents())(scope);
                        })
                        .withOption('order', [[4, 'desc']])
                        .withBootstrap()
    ctrl.columns = [
        DTColumnBuilder.newColumn('level').withTitle('<i class="fa fa-fw fa-bell"></i>')
                                          .renderWith(AxisMessaging.renderers.level),
        DTColumnBuilder.newColumn('title').withTitle('Type').renderWith(AxisMessaging.renderers.title),
        DTColumnBuilder.newColumn('content').withTitle('Content'),
        DTColumnBuilder.newColumn('category').withTitle('Category'),
        DTColumnBuilder.newColumn('date_created').withTitle('Date').renderWith(AxisMessaging.renderers.date_created).withOption('type', 'date'),
        DTColumnBuilder.newColumn('date_alerted').withTitle('Received').renderWith(AxisMessaging.renderers.date_alerted).withOption('type', 'date'),
        DTColumnBuilder.newColumn('date_sent').withTitle('Emailed').renderWith(AxisMessaging.renderers.date_sent).withOption('type', 'date'),
        DTColumnBuilder.newColumn('actions').withTitle('Actions').renderWith(AxisMessaging.renderers.actions)
    ]
})
// .controller('SentMessagingRetrievalController', function($compile, DTOptionsBuilder, DTColumnBuilder){
//     var ctrl = this;
//     var URLS = {
//         'data_source': "/api/v2/messages/datatable/?sent=1"
//     }
//     ctrl.options = DTOptionsBuilder.newOptions()
//                         .withOption('ajax', {'url': URLS.data_source})
//                         .withOption('bServerSide', true)
//                         .withOption('sPaginationType', 'simple_numbers')
//                         .withOption('dom', AxisMessaging.dom_shortcode)
//                         .withDataProp('data')
//                         .withOption('fnRowCallback', AxisMessaging.options.fnRowCallback)
//                         .withOption('fnDrawCallback', function(settings){
//                             var scope = angular.element(settings.oInstance).scope();
//                             $compile(settings.oInstance.contents())(scope);
//                         })
//                         .withOption('order', [[4, 'desc']])
//                         .withBootstrap()
//     ctrl.columns = [
//         DTColumnBuilder.newColumn('level').withTitle('<i class="fa fa-fw fa-bell"></i>')
//                                           .renderWith(AxisMessaging.renderers.level),
//         DTColumnBuilder.newColumn('title').withTitle('Type').renderWith(AxisMessaging.renderers.title),
//         DTColumnBuilder.newColumn('content').withTitle('Content'),
//         DTColumnBuilder.newColumn('category').withTitle('Category'),
//         DTColumnBuilder.newColumn('date_created').withTitle('Date').renderWith(AxisMessaging.renderers.date_created).withOption('type', 'date'),
//         DTColumnBuilder.newColumn('date_alerted').withTitle('Received').renderWith(AxisMessaging.renderers.date_alerted).withOption('type', 'date'),
//         DTColumnBuilder.newColumn('date_sent').withTitle('Emailed').renderWith(AxisMessaging.renderers.date_sent).withOption('type', 'date'),
//         DTColumnBuilder.newColumn('actions').withTitle('Actions').renderWith(AxisMessaging.renderers.actions)
//     ]
// })

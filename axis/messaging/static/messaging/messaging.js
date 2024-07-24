angular.module('axis.messaging', ['cgNotify'])

.factory('MessagingService', function($http, $rootScope){
    function sendMessage() {
        // user_id will be implied by the request sent to the API
        return $http.post('/api/v2/messages/send/');
    }

    function introduceExternalMessage(message) {
        return $rootScope.$$childHead.messages.introduceExternalMessage(message);
    }

    return {
        sendMessage: sendMessage,
        introduceExternalMessage: introduceExternalMessage
    }
})

.controller('MessagingController', function($scope, $http, $timeout, notify){
    var WEBSOCKETS_SERVER_IS_BUSTED = false;
    try {
        io
    } catch (e) {
        WEBSOCKETS_SERVER_IS_BUSTED = true;
    }

    var ctrl = this;
    var messages = {
        'unread': [],
        'read': [],
        '_sticky': {},
        '_seenIds': {},
        '_id_map': {}
    }

    var URLS = {
        'socket_host': window.WEBSOCKET_HOST + "/messages",
        'socket_endpoint': window.WEBSOCKET_ENDPOINT,
        'pull_new': '/api/v2/messages/pull/',
        'mark_read': '/api/v2/messages/__id__/read/',
        'mark_all_read': '/api/v2/messages/mark_all_read/',
        'send_email': '/api/v2/messages/__id__/email/'
    }
    var user_id = window.user_id;

    notify.config({
        'templateUrl': window.STATIC_URL + 'messaging/toast.html',
        'container': $('#toast-area'),
        'maximumOpen': 10,
        'verticalSpacing': 10,
        'duration': 5 * 1000,
        'startTop': -10  // relative to its starting spot
    });

    var slowLoadTimer = setTimeout(function(){
        ctrl.loaded = true;
        ctrl.error = true;
    }, 3000);

    var socket = null;
    if (WEBSOCKETS_SERVER_IS_BUSTED) {
        console.error("Websocket server is down!");
        introduceMessage({
            'level': 'error',
            'category': 'axis',
            'title': "Realtime message delivery is paused",
            'content': "An unexpected outage has occurred with the realtime delivery of messages " +
                       "from the server.  Messages will be delivered only when a page loads."
        });
    } else {
        socket = io(URLS.socket_host, {
            'path': URLS.socket_endpoint,
            'reconnectionDelay': 5000,
            'transports': ['websocket']
        })
        .on('connect', function(){
            console.info("Successfully established background websocket connection to server.");

            // Doing this every 'connect' event ensures that disruptions in the connection are smoothed
            // out once things are back to normal.
            preloadMessages();
        })
        .on('connect:acknowledge', function(client_id){
            console.debug("Server identifying me as:", client_id);
            socket.emit('connect:ready', window.session_key);
        })
        .on('disconnect', function(){
            console.warn("Lost background websocket connection to server.");
        })
        .on('message:push', function(message){
            console.log("Receiving message:", message);
            message = JSON.parse(message);
            addMessage(message);
            ctrl.serverMessageCount += 1;
        })
        .on('message:read', function(message_id){
            console.log("Receiving read receipt from other source:", message_id)
            message_id = JSON.parse(message_id);
            var message = messages._id_map[message_id];
            if (!message.alert_read) {  // possible we're the one that issued original read receipt
                markMessageRead(message);
            }
        })
        .on('message:read_bulk', function(message_ids){
            console.log("Receiving multiple read receipts from other source:", message_ids)
            if (message_ids.length === 0) {
                for (var i in messages._id_map) {  // Select everything
                    message_ids.push(i);
                }
            }
            for (var i in message_ids) {
                var message_id = message_ids[i];
                var message = messages._id_map[message_id];
                if (messages.unread.indexOf(message) > -1) {  // possible we're the one that issued original read receipt
                    markMessageRead(message);
                }
            }
        })
    }

    function preloadMessages(){
        $http.post(URLS.pull_new).success(function(data){
            clearErrorCondition();
            ctrl.loaded = true;
            ctrl.serverMessageCount = data.count;
            ctrl.messageCountLimit = data.results.length;
            $.map(data.results, addMessage);
        });
    }
    function addMessage(message){
        clearErrorCondition();

        function _verifyUnhandled(){
            // superuser impersonation gotcha
            if (message.user != user_id) {
                return false;
            }

            if (message.id in messages._seenIds) {
                return false;
            }
            return true;
        }

        // Avoid scheduling the timeout if this is already obsoleted by a datatable injection
        if (!_verifyUnhandled()) {
            return;
        }

        $timeout(function(){
            // Double check that datatable injection didn't sneak in between the scheduling and
            // execution of this timeout.
            if (!_verifyUnhandled()) {
                return;
            }
            var messagePool = (message.alert_read ? messages.read : messages.unread)
            messagePool.splice(0, 0, message);
            messages._id_map[message.id] = message;
            messages._seenIds[message.id] = true;
            if (!message.alert_read && message.is_recent) {
                if (message.sticky_alert) {
                    messages._sticky[message.id] = true;
                }
                introduceMessage(message);
            }
            $scope.$apply();
        });
    }
    function introduceMessage(message){
        // visual introduction of message popup onto the page
        var notification = {
            'message': message
        }
        if (message.sticky_alert) {
            notification.duration = 0;  // Don't auto-close
        }
        notify(notification);
    }
    function deliverReadReceipt(id){
        socket.emit('message:read', id);
    }
    function markMessageRead(message){
        $timeout(function(){
            // The work required to actually mark the message as read, separated from the act of
            // pushing the event upstream for distribution of read receipts.
            message.alert_read = true;
            messages.unread.splice(messages.unread.indexOf(message), 1);
            messages.read.splice(0, 0, message);
            ctrl.serverMessageCount -= 1;
            if (message.sticky_alert) {
                delete messages._sticky[message.id];
            }
            // $scope.$apply();  // FIXME: When bulk read receipts arrive, $apply() gets called way too much
        });
    }

    ctrl.error = false;
    ctrl.loaded = false;
    ctrl.unread = messages.unread;
    ctrl.read = messages.read;
    ctrl.informOfMessage = function(data){
        // If some message exists now that was not delivered over the websocket, this function can
        // store it in the internal mapping so that it is tracked.
        // This is safe to call multiple times on any message.
        var bucket = (data.alert_read ? messages.read : messages.unread);
        if (_.find(bucket, data) === undefined) {
            messages._id_map[data.id] = data;
            messages._seenIds[data.id] = true;
            bucket.push(data);
        }
    }
    ctrl.inspectMessage = null;
    ctrl.getHighestUnreadSeverity = function(){
        // Note that we're excluding 'success' because it's not supposed to be a persistent
        // attention-grabber.
        var rankings = ['system', 'error', 'warning', 'default']
        var classes = ['primary', 'danger', 'warning', 'default']
        var level = rankings.length - 1;
        for (var i in messages.unread) {
            var message = messages.unread[i];
            var messageLevel = rankings.indexOf(message.level)
            if (messageLevel > -1 && messageLevel < level) {
                level = messageLevel;
            }
        }
        return classes[level];
    }
    ctrl.hasSticky = function(){
        return Object.keys(messages._sticky).length > 0;
    }
    ctrl.hasUnread = function(){
        return messages.unread.length > 0;
    }
    ctrl.hasRead = function(){
        return messages.read.length > 0;
    }
    ctrl.unreadCount = function(){
        var count = ctrl.serverMessageCount;
        if (count > ctrl.messageCountLimit) {
            count = ctrl.messageCountLimit;

            // Messages introduced since the page load will be allowed to bump the count over the
            // normal limit.
            var overflowCount = ctrl.unread.length - ctrl.messageCountLimit;
            if (overflowCount > 0) {
                count += overflowCount;
            }
        }

        if (ctrl.serverMessageCount > ctrl.messageCountLimit) {
            return "" + count + "+";
        }
        return count;
    }
    ctrl.serverHasMore = function(){
        return ctrl.serverMessageCount > messages.unread.length;
    }
    ctrl.introduceExternalMessage = introduceMessage;
    ctrl.markAsRead = function(message){
        $http.post(URLS.mark_read.replace('__id__', message.id))
             .success(function(){
                markMessageRead(message);
                deliverReadReceipt(message.id);
             })
             .error(function(data, status, headers, config){
                 console.error(data, status, headers, config);
             });
    }
    ctrl.markAllAsRead = function(){
        function getMsgId(message){
            return message.id;
        }
        var url = URLS.mark_all_read + "?id=" + _.map(messages.unread, getMsgId).join('&id=')
        $http.post(url)
             .success(function(){
                 // We don't generate individual read receipts here for other clients;
                 // the API endpoint will send these acknowledgements down on its own.

                 // Remove untracked message count from total.  Individual read receipts will take
                 // care of the rest.
                 ctrl.serverMessageCount -= (ctrl.serverMessageCount - messages.unread.length);
             })
             .error(function(data, status, headers, config){
                 console.error(data, status, headers, config);
             });
    }
    ctrl.dismissPopups = function(){
        notify.closeAll();
    }
    ctrl.openMessage = function(message){
        ctrl.inspectMessage = message;
        var modal = $('#inspect-message-modal');
        var scope = angular.element(modal).scope();
        scope.message = message;
        scope.messageController = message.messageController;
        modal.modal({});
    }
    ctrl.sendEmail = function(message){
        message.sending_email = true;
        return $http.post(URLS.send_email.replace('__id__', message.id))
                    .success(function(){
                        message.date_sent = true;  // Server will assign date, we just need bool
                        message.sending_email = false;
                    })
                    .error(function(data, status, headers, config){
                        console.error(data, status, headers, config);
                    });
    }

    // Relay methods for global use
    ctrl.getMessage = function(id){
        return messages._id_map[id];
    }
    ctrl.markTargetMessageAsRead = function(id){
        ctrl.markAsRead(ctrl.getMessage(id));
    }
    ctrl.openTargetMessage = function(id){
        ctrl.openMessage(ctrl.getMessage(id));
    }

    function clearErrorCondition(){
        if (slowLoadTimer !== null) {
            clearTimeout(slowLoadTimer);
            slowLoadTimer = null;
        }
        ctrl.error = false;
    }

})
.directive('messagingWrapper', function(){
    return {
        'restrict': 'A',
        'scope': true,
        'controller': 'MessagingController',
        'controllerAs': 'messages'
    }
})

.controller('messagingNotificationPulldownController', function($scope){
    var ctrl = this;
    ctrl.showRead = false;
    ctrl.checkForAutoExpand = function(){
        ctrl.showRead = (!$scope.messages.hasUnread() && $scope.messages.hasRead());
    }
})

.controller('Message', function($scope, $sce, $timeout){
    var ctrl = this;
    var DISMISS_DELAY_AFTER_MOUSEOVER = 2000;  // 2 seconds

    $scope.message.messageController = ctrl;

    var isSending = false;

    ctrl.isToast = function(){
        // Indicates if this instance of the message is a popup notification or not.
        return $scope.isToast;
    }
    ctrl.startHover = function(){
        $timeout.cancel($scope.$parent.$closeTimeout);
    }
    ctrl.endHover = function(){
        $scope.$parent.$closeTimeout = $timeout(function(){
            $scope.closePopup();
        }, DISMISS_DELAY_AFTER_MOUSEOVER);
    }

    ctrl.dismissPopup = function(){
        $scope.closePopup();
    }
    ctrl.htmlContent = $sce.trustAsHtml($scope.message.content);
    ctrl.markAsRead = function(){
        $scope.messages.markAsRead($scope.message);
        $scope.closePopup();
    }
    ctrl.sendEmail = function(){
        isSending = true;
        $scope.messages.sendEmail($scope.message)
                       .success(function(){
                           isSending = false;
                       });
        $scope.closePopup();
    }
    ctrl.goToUrlCallback = function(event){
        if (ctrl.isOtherUrl()) {
            $scope.closePopup();
        } else {
            event.preventDefault();
        }
    }
    ctrl.getFullUrl = function(){
        // This is primarily for display purposes.
        // message.url is safe to navigate by itself.
        if ($scope.message.url[0] === '/') {
            return window.location.host + $scope.message.url;
        }
        return $scope.message.url;
    }
    ctrl.isOtherUrl = function(){
        return window.location.pathname != $scope.message.url;
    }
    ctrl.isSending = function(){
        return isSending;
    }
})
.directive('message', function(){
    return {
        'restrict': 'A',
        'require': '^messagingWrapper',
        'scope': {
            'message': '=item'
        },
        'controller': 'Message',
        'controllerAs': 'messageController',
        'templateUrl': window.STATIC_URL + 'messaging/message.html',
        'link': function(scope, element, attrs, messages) {
            scope.messages = messages;

            // angular-notify doesn't put $close() in the scope until after template rendering,
            // so this is a lazy binding we can use in our controller.
            scope.isToast = (scope.$parent.$close !== undefined);
            scope.closePopup = function(){
                if (scope.isToast) {  // If the notification is in tray, do nothing
                    scope.$parent.$close();
                }
            }
        }
    }
})

.directive('viewMessage', function(){
    return {
        'restrict': 'E',
        'require': '^messagingWrapper',
        'scope': true,
        'templateUrl': window.STATIC_URL + 'messaging/inspect.html',
        'link': function(scope, element, attrs, messages){
            scope.messages = messages;
        }
    }
})





.filter('bootstrapcontext', function(){
    var contextualNames = {
        'system': 'primary',
        'error': 'danger'
    }
    return function(term){
        if (contextualNames[term] !== undefined) {
            return contextualNames[term];
        }
        return term;
    }
})

.filter('fontawesomecontext', function(){
    var contextualNames = {
        'system': 'fa-circle-o-notch',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'success': 'fa-check-circle',
        'info': 'fa-info-circle',
        'debug': 'fa-code',
    }
    return function(term){
        if (contextualNames[term] !== undefined) {
            return contextualNames[term];
        }
        return term;
    }
})

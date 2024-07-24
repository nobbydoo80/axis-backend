/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.services.HttpQueue')
.factory('HttpQueue', function($q, $http, $templateCache){
    var requests = [];
    var processing = false;

    return {
        addObjectRequest: addObjectRequest,
        addTemplateRequest: addTemplateRequest
    };

    function addObjectRequest(endpoint, additionalScope){
        // Add to the beginning because we're going to pop the next requests.
        additionalScope = additionalScope || {};
        var deferred = $q.defer();
        requests.unshift([deferred, endpoint, additionalScope]);
        triggerRequestCycle();
        return deferred.promise;
    }
    function addTemplateRequest(endpoint){
        // Call Template paths right away.
        var deferred = $q.defer();
        $http.get(endpoint, {cache: $templateCache}).success(deferred.resolve).error(deferred.reject);
        return deferred.promise;
    }

    // helpers
    function _apiCall(promise, endpoint, additionalScope){
        $http.get(endpoint).success(function(data){
            data.additionalScope = additionalScope;
            promise.resolve(data);
        }).error(function(data, code){
            promise.reject(data, code);
        }).finally(function(){
            requests.length ? _apiCall.apply(this, requests.pop()) : processing = false;
        });
    }
    function triggerRequestCycle(){
        if(!processing && requests.length){
            processing = true;
            _apiCall.apply(this, requests.pop())
        }
    }
});

/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.services.UrlService')
.factory('UrlService', function($location, $state){
    var originalLink = $location.pathname || location.pathname;
    var updatedLink = false;

    $location.$$$compose = $location.$$compose.bind($location);
    $location.$$compose = function(){
        this.$$$compose();
        if(updatedLink){
            this.$$absUrl = this.$$absUrl.replace(originalLink, updatedLink);
        }
    }.bind($location);

    function setUpdatedLink(link){
        updatedLink = link;
        try{
            $state.reload();
        } catch(e){
            $state.go('index');
        }
    }

    return {
        setUpdatedLink: setUpdatedLink
    }

});

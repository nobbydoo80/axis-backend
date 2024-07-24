/**
 * Examine View Angular Filters.
 */

angular.module('axis.filters', [])
.filter('humanize', function(){
    function ucwords(text){
        return text.replace(/^([a-z])|\s+([a-z])/g, function($1){
            return $1.toUpperCase();
        });
    }

    function breakup(text, separator){
        return text.replace(/[A-Z]/g, function(match){
            return separator + match;
        });
    }

    function humanize(value){
        return ucwords(breakup(value, ' ').split('_').join(' '));
    }

    return function(text){
        if(angular.isString(text)){
            return humanize(text)
        } else {
            return text;
        }
    }
})
.filter('selectFilter', function(){
    return function selectFilter(input, searchText, AND_OR){

        if(!input || input.length === 0) return input;

        if(input[0].id === null && input[0].text == 'No Results...') return input;

        var returnArray = [];

        var splitText = searchText.toLowerCase().split(/\s+/);

        var regAnd = "(?=.*" + splitText.join(")(?=.*") + ")";

        var regOr = searchText.toLowerCase().replace(/\s+/g, "|");

        var re = new RegExp((AND_OR == 'AND') ? regAnd : regOr, 'i');

        for(var i = 0; i < input.length; i ++){
            if(re.test(input[i].text)) returnArray.push(input[i]);
        }

        return returnArray;
    }
})
.filter('truncateAtBreak', function(){
    function simplifyhtml(text){
        return text.split(/<br( ?\/)?>/g, 1)[0].replace(/<[^>]+>/g, '');
    }

    return function(text){
        if (angular.isString(text)) {
            return simplifyhtml(text);
        } else {
            return text;
        }
    }
})
.filter('filename', function(){
    return function(text){
        if (angular.isString(text)) {
            return text.replace(/^https?:\/\/.*?\/([^/]+)\?.*$/, '$1');
        }
        return text;
    }
})
.filter('axisDurationFormat', function(){
    function axisDurationFormatFilter(value, format, suffix, precision){
        if(typeof value === 'undefined' || value === null){
            return '';
        }
        precision = precision || 0;

        return moment.duration(value, format).format(suffix, precision);
    }

    return axisDurationFormatFilter;
})
.filter('trustAsHtml', function($sce){
    return function(input){
        input = input || '';
        return $sce.trustAsHtml(input);
    }
});

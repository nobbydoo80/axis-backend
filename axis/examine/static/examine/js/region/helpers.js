/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.region.helpers')
.directive('nonFieldErrors', function(){
    /**
     * Place this anywhere there is access to the regionObject and it will display any
     * non_field_errors returned by the server.
     */
    return {
        restrict: 'EA',
        replace: true,
        link: function(scope, element, attrs){
            /**
            * FIXME: This is a hack because we don't allow differentiation in how we deal with different regions' errors.
            * Bob brough up that when there is an error for the primary region, and it shows up at the top, it's not always
            * apparent to the user. The current solution is to pop the scroll position to the top of the page so the error
            * is in sight. A more correct solution would be to better utilize the MessagingService. Currently we can't mark
            * messages for notifications, and it would be overkill to send every error recieved there.
            * So until we can retool this. Window scrolling it is.
            * NOTE: this is only happening for the primary region currently.
            */
            scope.$watch('regionObject.errors.non_field_errors', function(newVal, oldVal){
                if(!newVal)return;
                if(scope.regionSet.isPrimaryRegion){
                    $(document).scrollTop(0);
                }
            });
        },
        template: '<ul class="text-danger" ng-if="regionObject.errors.non_field_errors">\n    <li ng-repeat="message in regionObject.errors.non_field_errors track by $index" ng-bind-html="message | trustAsHtml"></li>\n</ul>'
    }
})
.directive('ngIncludeReplace', function(){
    return {
        restrict: 'A',
        link: function(scope, element, attrs){
            element.replaceWith(element.children())
        }
    }
})
.directive('loadingSpinner', function(){
    return {
        restrict: 'E',
        replace: true,
        template: '<div class="examine-spinner">\n    <i class="fa fa-spinner fa-lg fa-spin"></i>\n    <div class="loading-message"> Please Wait</div>\n</div>'
    }
})
.directive('axisRegionHeading', function(){
    return {
        restrict: 'EA',
        transclude: true,   // Grab the contents to be used as the heading
        template: '',       // In effect remove this element
        replace: true,
        require: '^axisSingleRegion',
        link: function(scope, element, attr, parentController, transclude){
            parentController.setHeadingElement(transclude(scope, function(){}))
        }
    }
})
.directive('axisTransclude', function(){
    return {
        restrict: 'EA',
        require: '^?axisSingleRegion',
        link: function(scope, element, attrs, parentController){
            if(parentController) parentController.setHeadingDestination(element);
        }
    }
})
.directive('sidetabButton', function($timeout){
    return {
        restrict: 'A',
        require: '^axisRegionSet',
        link: function(scope, element, attrs, controller){
            var shouldActivate = scope.$index === 0;
            if (!scope.regionObject.object.id) {
                shouldActivate = true;
            }
            if (shouldActivate) {
                $timeout(function(){
                    element.find('a').tab('show');
                }, 0);
            }
            element.on('$destroy', function(){
                var tagName = element.prop('tagName').toLowerCase();
                var select = element.parent().find(tagName+'[ng-repeat]:not(.active)').first();
                select.find('a').tab('show');
            })
        }
    }
})
// .directive('examineDatatable', function($timeout){
//     return {
//         restrict: 'C',
//         link: function(scope, element, attrs){
//             var unwatch = scope.$watch('regionSet.initialLoad', function(newVal, oldVal){
//                 if(newVal){
//                     $timeout(function(){
//                         var dTable = $(element);
//                         dTable.dataTable();
//                         datatable_stylize(dTable);
//                         unwatch();
//                     }, 1)
//                 }
//             })
//         }
//     }
// })
.directive('hideActionStrip', function(){
    return {
        restrict: 'A',
        require: ['^?axisSingleRegion', '^?axisRegionSet'],
        link: function(scope, element, attrs, controllers){
            // Action Strip looks up to the regionset so we don't have to add
            // this directive in every single template.
            (controllers[0] || controllers[1]).hideActionStrip = true;
            // Also add it to the region controller, just for good measure.
            scope.hideActionStrip = true;
        }
    }
}).directive('readMore', function() {
  return {
    restrict: 'A',
    transclude: true,
    replace: true,
    template: '<p></p>',
    scope: {
      moreText: '@',
      lessText: '@',
      words: '@',
      ellipsis: '@',
      char: '@',
      limit: '@',
      content: '@'
    },
    link: function(scope, elem, attr, ctrl, transclude) {
      var moreText = angular.isUndefined(scope.moreText) ? ' <a class="read-more">Read More...</a>' : ' <a class="read-more">' + scope.moreText + '</a>',
        lessText = angular.isUndefined(scope.lessText) ? ' <a class="read-less">Less ^</a>' : ' <a class="read-less">' + scope.lessText + '</a>',
        ellipsis = angular.isUndefined(scope.ellipsis) ? '' : scope.ellipsis,
        limit = angular.isUndefined(scope.limit) ? 150 : scope.limit;

      attr.$observe('content', function(str) {
        readmore(str);
      });

      transclude(scope.$parent, function(clone, scope) {
        readmore(clone.text().trim());
      });

      function readmore(text) {

        var text = text,
          orig = text,
          regex = /\s+/gi,
          charCount = text.length,
          wordCount = text.trim().replace(regex, ' ').split(' ').length,
          countBy = 'char',
          count = charCount,
          foundWords = [],
          markup = text,
          more = '';

        if (!angular.isUndefined(attr.words)) {
          countBy = 'words';
          count = wordCount;
        }

        if (countBy === 'words') { // Count words

          foundWords = text.split(/\s+/);

          if (foundWords.length > limit) {
            text = foundWords.slice(0, limit).join(' ') + ellipsis;
            more = foundWords.slice(limit, count).join(' ');
            markup = text + moreText + '<span class="more-text">' + more + lessText + '</span>';
          }

        } else { // Count characters

          if (count > limit) {
            text = orig.slice(0, limit) + ellipsis;
            more = orig.slice(limit, count);
            markup = text + moreText + '<span class="more-text">' + more + lessText + '</span>';
          }

        }

        elem.append(markup);
        elem.find('.read-more').on('click', function() {
          $(this).hide();
          elem.find('.more-text').addClass('show').slideDown();
        });
        elem.find('.read-less').on('click', function() {
          elem.find('.read-more').show();
          elem.find('.more-text').hide().removeClass('show');
        });

      }
    }
  };
});

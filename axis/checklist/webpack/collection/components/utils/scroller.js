export function scroller(){
    /**
     * Keeps moved to questions always in view.
     */
    return {
        controller: function($scope, $ngRedux, $stateParams, $element){
            const unwatch = $scope.$watch(() => $stateParams.id, (newVal, oldVal) => {
                // make sure newVal is a number by trying to shift it. Anything letters will result in 0.
                if(newVal|0 && (oldVal != newVal)){
                    let activeEl = $element.find('.active');
                    if(!activeEl.length) return;

                    let currScroll = $element.scrollTop();
                    let {top: parentTop} = $element.offset();
                    let {top: selectedTop} = activeEl.offset();

                    let parentBottom = parentTop + $element.outerHeight();
                    let selectedBottom = selectedTop + activeEl.outerHeight();

                    if(selectedBottom > parentBottom){
                        // is below
                        $element.scrollTop(currScroll + (selectedBottom - parentBottom));
                    } else if (selectedTop < parentTop){
                        // is above
                        // BEWARE: order of subtraction matters bug time here.
                        $element.scrollTop(currScroll - (parentTop - selectedTop));
                    }
                }
            });
            $scope.$on('$destroy', unwatch);
        }
    }
}

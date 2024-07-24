class CopyValueButtonController {
    constructor($scope, $element, $timeout){
        this.$element = $element;
        this.$timeout = $timeout;
        this.busy = false;
    }

    copyValue() {
        let self = this;
        let $temp_input = $("<input>");
        self.busy = true;
        $("body").append($temp_input);
        $temp_input.val(this.textToCopy()).select();
        document.execCommand("copy");
        $temp_input.remove();
        self.$timeout(function () {
            self.busy = false;
        }, 250);
    }
}


export function copyValueButton(){
    return {
        scope: {
            textToCopy: '&'
        },
        template: `
        <button ng-show="ctrl.textToCopy()" ng-disabled="ctrl.busy" type="button" class="btn btn-link copy-value-btn" title="Copy value" ng-click="ctrl.copyValue()">
            <i class="fa fa-copy" ng-hide="ctrl.busy"></i>
            <i class="fa fa-fw fa-spinner fa-spin" ng-show="ctrl.busy"></i>
        </button>
        `,
        controller: CopyValueButtonController,
        controllerAs: 'ctrl',
        bindToController: true
    };
}

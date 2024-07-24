// required to show button
window.JSZip = true;

var _OriginalBuildButton = $.fn.dataTable.Buttons.prototype._buildButton;

$.fn.dataTable.Buttons.prototype._buildButton = function(conf, collectionButton){
    if(conf.name && conf.name === 'excel'){
        var originalAction = conf.action;
        conf.action = function(...args){
            require.ensure(['jszip'], function _excelHtml5Action(require){
                // Exports the JSZip object. Up to us to strap it to the window.
                window.JSZip = require('jszip');
                originalAction(...args);
            }, 'datatable_exports_lazy')
        }
    }
    return _OriginalBuildButton.call(this, conf, collectionButton);
};

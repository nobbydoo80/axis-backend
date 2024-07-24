// required to show button.
window.pdfMake = true;

var _OriginalBuildButton = $.fn.dataTable.Buttons.prototype._buildButton;

$.fn.dataTable.Buttons.prototype._buildButton = function(conf, collectionButton){
    if(conf.name && conf.name === 'pdf'){
        var originalAction = conf.action;
        conf.action = function(...args){
            require.ensure(['./1.3.0/pdfmake', './1.3.0/vfs_fonts'], function _pdfHtml5Action(require){
                // Part of the export in this file is to put pdfMake on the window.
                require('./1.3.0/pdfmake.js');
                require('./1.3.0/vfs_fonts.js');
                var config = args.pop();
                config.customize = function(doc){
                    doc.content.push({
                        margin: [10, 10, 10, 10],
                        alignment: 'left',
                        image: require('url!core/../../images/axis_light_grey_75x271.png'),
                        fit: [75,271]
                    });
                };
                originalAction(...args, config);
            }, 'datatable_exports_lazy');

        }
    }
    return _OriginalBuildButton.call(this, conf, collectionButton);
};

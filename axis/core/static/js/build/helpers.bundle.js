webpackJsonpLegacy([4],{

/***/ 0:
/***/ (function(module, exports, __webpack_require__) {

	__webpack_require__(166);
	__webpack_require__(132);
	__webpack_require__(131);
	__webpack_require__(120);
	__webpack_require__(121);
	module.exports = __webpack_require__(122);


/***/ }),

/***/ 120:
/***/ (function(module, exports) {

	// We're explicitly requiring localStorage or nothing at all (no cookie fallback) in order to reduce
	// client and support confusion over conditions where some browsers might require different
	// cache-invalidating processes.
	"use strict";

	var datatables_state_scope_name = "Axis_DataTables_" + window.location.pathname + "_";
	var use_datatables_localStorage = false;
	try {
	    use_datatables_localStorage = typeof window.localStorage !== "undefined";
	} catch (e) {}

	if (use_datatables_localStorage) {
	    $.extend($.fn.dataTable.defaults, {
	        "stateSave": true,
	        "stateSaveCallback": function stateSaveCallback(settings, data) {
	            localStorage.setItem(datatables_state_scope_name + settings.sTableId, JSON.stringify(data));
	        },
	        "stateLoadCallback": function stateLoadCallback(settings) {
	            var obj = JSON.parse(localStorage.getItem(datatables_state_scope_name + settings.sTableId));
	            if (obj) {
	                return obj;
	            }
	            return null;
	        }
	    });
	}

	$.extend($.fn.dataTable.defaults, {
	    "bSort": true,
	    "bProcessing": true,
	    "sPaginationType": "simple_numbers",
	    "iDisplayLength": 25,
	    "searchDelay": 1000,
	    "aLengthMenu": [[10, 25, 50, 100, 250, -1], [10, 25, 50, 100, 250, "All"]]
	});

	$.fn.dataTableExt.sErrMode = "throw";

	$(function () {
	    $(document).bind("clear.datatable", function (event, datatable) {
	        // Invalidate the state-saving mechanism's settings
	        if (use_datatables_localStorage) {
	            localStorage.removeItem(datatables_state_scope_name + datatable.fnSettings().sTableId);
	        }
	        datatable.fnSortNeutral();
	    });
	});

	// Some configurations of IE present 'access denied' messages just for touching the localStorage
	// variable, even if it is available.  This 'catch' block should allow the disabling of
	// localStorage.

/***/ }),

/***/ 121:
/***/ (function(module, exports) {

	'use strict';

	var default_attr_dict = {
	    'type': 'text',
	    'placeholder': 'Enter answer',
	    'data-toggle': 'tooltip',
	    'title': 'Enter answer',
	    'data-trigger': 'focus',
	    'class': 'textinput textInput form-control'
	};
	var attr_dict = {
	    'textarea': {
	        'type': 'textarea',
	        'placeholder': 'Comment...',
	        'class': 'textarea form-control'
	    },
	    'date': $.extend({}, default_attr_dict, {
	        placeholder: 'Enter a date',
	        title: 'Enter a date'
	    }),
	    'integer': $.extend({}, default_attr_dict, {
	        placeholder: 'Enter a Whole Number',
	        title: 'Enter a Whole Number'
	    }),
	    'float': $.extend({}, default_attr_dict, {
	        placeholder: 'Enter a Decimal',
	        title: 'Enter a Decimal'
	    }),
	    'open': default_attr_dict,
	    'csv': default_attr_dict,
	    'kvfloatcsv': default_attr_dict,
	    'text': default_attr_dict,
	    'hidden': {}
	};

	Handlebars.registerHelper('debug', function (optionalValue) {
	    console.log('Current Context');
	    console.log('====================');
	    console.log(this);
	});

	Handlebars.registerHelper('compare', function (lvalue, rvalue, options) {
	    if (arguments.length < 3) {
	        throw new Error('Handlebars Helper \'compare\' needs 2 parameters');
	    }

	    var operator = options.hash.operator || '==';

	    var operators = {
	        '==': function _(l, r) {
	            return l == r;
	        },
	        '===': function _(l, r) {
	            return l === r;
	        },
	        '!=': function _(l, r) {
	            return l != r;
	        },
	        '<': function _(l, r) {
	            return l < r;
	        },
	        '>': function _(l, r) {
	            return l > r;
	        },
	        '<=': function _(l, r) {
	            return l <= r;
	        },
	        '>=': function _(l, r) {
	            return l >= r;
	        },
	        'typeof': function _typeof(l, r) {
	            return typeof l == r;
	        }
	    };

	    if (!operators[operator]) {
	        throw new Error('Handlebars helper \'compare\' doesn\'t know the operator ' + operator);
	    }

	    var result = operators[operator](lvalue, rvalue);
	    if (result) {
	        return options.fn(this);
	    } else {
	        return options.inverse(this);
	    }
	});

	Handlebars.registerHelper('checklist_textarea', function (context, options) {
	    var scaffolding = $('<div class=\'form-group\'><div class=\'controls\'></div></div>');
	    var el = $('<textarea/>');

	    scaffolding.prepend('<label class=\'control-label\'>Comment</label>');

	    var dynamic = {
	        'id': 'id_' + context.id + '-comment',
	        'name': context.id + '-comment'
	    };

	    el.attr(attr_dict['textarea']);
	    el.attr(dynamic);
	    if ('hash' in options) el.attr(options.hash);
	    el = scaffolding.find('.controls').append(el).parent();
	    return new Handlebars.SafeString($('<div></div>').append(el).html());
	});

	Handlebars.registerHelper('checklist_input', function (context, options) {
	    var scaffolding = $('<div class=\'form-group\'><div class=\'controls\'></div></div>');
	    var el = $('<input/>');

	    var dynamic = {
	        'id': 'id_' + context.id + '-answer',
	        'name': context.id + '-answer'
	    };

	    var attributes = jQuery.extend(true, {}, attr_dict[context.type]);

	    if (context.answer && context.answer.answer) {
	        dynamic['value'] = context.answer.answer;
	        if (context.answer.answer.length > 20) {
	            attributes['title'] = context.answer.answer;
	        } else {
	            delete attributes['data-toggle'];
	        }
	    }

	    el.attr(attributes);
	    el.attr(dynamic);
	    if ('hash' in options) el.attr(options.hash);
	    el = scaffolding.find('.controls').append(el).parent();
	    return new Handlebars.SafeString($('<div></div>').append(el).html());
	});

	Handlebars.registerHelper('yesno', function (value, options) {
	    return value ? '1' : '0';
	});

	Handlebars.registerHelper('media_url', function (value, options) {
	    return [media_url, value].join('');
	});

	Handlebars.registerHelper('join', function (list, options) {
	    var list = Array.isArray(list) ? list : [list];
	    var separator = options.hash.separator || ' / ';
	    return list.join(separator);
	});

	Handlebars.registerHelper('panel-class', function (context) {
	    if (context.has_errors) return 'panel-danger';

	    var importance = {
	        'CRITICAL': 3,
	        'ERROR': 3,
	        'WARNING': 2,
	        'INFO': 1
	    };

	    var levels = {
	        3: 'panel-danger',
	        2: 'panel-warning',
	        1: 'panel-info'
	    };

	    var values = $.map(context, function (val, i) {
	        return importance[i];
	    });

	    var level = Math.max.apply(Math, values);
	    return levels[level] || 'panel-default';
	});

	Handlebars.registerHelper('active-tab', function (context, checker) {
	    var importance = {
	        'CRITICAL': 4,
	        'ERROR': 3,
	        'WARNING': 2,
	        'INFO': 1
	    };

	    var values = $.map(context, function (val, i) {
	        return importance[i];
	    });

	    return Math.max.apply(Math, values) == importance[checker] ? 'active' : '';
	});

	Handlebars.registerHelper('list', function (context) {
	    var ret = '<ul>';
	    for (var i = 0, j = context.length; i < j; i++) {
	        ret = ret + '<li>' + context[i] + '</li>';
	    }
	    return ret + '</ul>';
	});

	Handlebars.registerHelper('strip', function (str) {
	    return str.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
	});

	Handlebars.registerHelper('set_key', function (key, value) {
	    this[key] = value;
	});

/***/ }),

/***/ 122:
/***/ (function(module, exports) {

	"use strict";

	window.dynamic_get_or_create = dynamic_get_or_create;
	window.process_results_and_inject_option = process_results_and_inject_option;

	function dynamic_get_or_create(name_field_selector) {
	    var field = $(name_field_selector || "#id_name");
	    if (!field.is(":hidden")) {
	        // This appears to be a text-based input, not a select2.  This likely means that the page is
	        // an edit page, not a creation page.
	        return;
	    }
	    var form = $("<form method='post'><input name='object' /><input name='go_to_detail' /></form>").hide();
	    form.attr("action", field.attr("data-relationship-url"));
	    form.append($("input[name=csrfmiddlewaretoken]").clone());

	    field.change(function (event) {
	        var id = parseInt(event.val);
	        if (event.type == "change" && id) {
	            form.find("input[name=object]").val(id);
	            form.appendTo("body");

	            service = angular.element(field).injector().get("MessagingService");
	            service.introduceExternalMessage({
	                "title": "Redirecting...",
	                "content": "Please wait while we create an association...",
	                "sticky_alert": true,
	                "level": "info",
	                "sender": null
	            });
	            form.submit();
	        }
	    });
	}

	function process_results_and_inject_option(data, page, context) {
	    // This is a modified version of django_select2.process_results

	    var results;
	    if (data.err && data.err.toLowerCase() === "nil") {
	        /*
	        * When navigating away from select2 element, then coming back, select2 makes a new input.
	        * Since we can't be sure in which order the inputs are returned, grab the value of all of them.
	        * We can be sure that select2 clears the value of all old inputs.
	        * */
	        var term = $(".select2-drop-active .select2-input").map(function (i, element) {
	            return $(element).val();
	        }).toArray();
	        term = term.join("");
	        if (data.results.length == 0) {
	            data.results = [{ "text": "(No matches)" }];
	        }
	        results = {
	            "results": [{
	                "text": "Create new:",
	                "children": [{ "id": term, "text": term }]
	            }, {
	                "text": "Select from existing:",
	                "children": data.results
	            }]
	        };
	        if (context) {
	            results["context"] = context;
	        }
	        if (data.more === true || data.more === false) {
	            results["more"] = data.more;
	        }
	    } else {
	        results = { "results": [] };
	    }
	    if (results.results) {
	        $(this).data("results", results.results);
	    } else {
	        $(this).removeData("results");
	    }
	    return results;
	}

/***/ }),

/***/ 131:
/***/ (function(module, exports, __webpack_require__) {

	// required to show button
	'use strict';

	window.JSZip = true;

	var _OriginalBuildButton = $.fn.dataTable.Buttons.prototype._buildButton;

	$.fn.dataTable.Buttons.prototype._buildButton = function (conf, collectionButton) {
	    if (conf.name && conf.name === 'excel') {
	        var originalAction = conf.action;
	        conf.action = function () {
	            for (var _len = arguments.length, args = Array(_len), _key = 0; _key < _len; _key++) {
	                args[_key] = arguments[_key];
	            }

	            __webpack_require__.e/* nsure */(0, function _excelHtml5Action(require) {
	                // Exports the JSZip object. Up to us to strap it to the window.
	                window.JSZip = __webpack_require__(19);
	                originalAction.apply(undefined, args);
	            });
	        };
	    }
	    return _OriginalBuildButton.call(this, conf, collectionButton);
	};

/***/ }),

/***/ 132:
/***/ (function(module, exports, __webpack_require__) {

	// required to show button.
	'use strict';

	window.pdfMake = true;

	var _OriginalBuildButton = $.fn.dataTable.Buttons.prototype._buildButton;

	$.fn.dataTable.Buttons.prototype._buildButton = function (conf, collectionButton) {
	    if (conf.name && conf.name === 'pdf') {
	        var originalAction = conf.action;
	        conf.action = function () {
	            for (var _len = arguments.length, args = Array(_len), _key = 0; _key < _len; _key++) {
	                args[_key] = arguments[_key];
	            }

	            __webpack_require__.e/* nsure */(0, function _pdfHtml5Action(require) {
	                // Part of the export in this file is to put pdfMake on the window.
	                __webpack_require__(114);
	                __webpack_require__(115);
	                var config = args.pop();
	                config.customize = function (doc) {
	                    doc.content.push({
	                        margin: [10, 10, 10, 10],
	                        alignment: 'left',
	                        image: __webpack_require__(190),
	                        fit: [75, 271]
	                    });
	                };
	                originalAction.apply(undefined, args.concat([config]));
	            });
	        };
	    }
	    return _OriginalBuildButton.call(this, conf, collectionButton);
	};

/***/ }),

/***/ 166:
/***/ (function(module, exports, __webpack_require__) {

	var __WEBPACK_AMD_DEFINE_FACTORY__, __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/*** IMPORTS FROM imports-loader ***/
	var exports = false;

	/*! DataTables Bootstrap 3 integration
	 * ©2011-2014 SpryMedia Ltd - datatables.net/license
	 */

	/**
	 * DataTables integration for Bootstrap 3. This requires Bootstrap 3 and
	 * DataTables 1.10 or newer.
	 *
	 * This file sets the defaults and adds options to DataTables to style its
	 * controls using Bootstrap. See http://datatables.net/manual/styling/bootstrap
	 * for further information.
	 */
	(function(window, document, undefined){

	var factory = function( $, DataTable ) {
	"use strict";

	    function strip(str){
	        /**
	         * DataTables doesn't give us access to override the defaults
	         * for cleaning things for export.
	         * So we get to redeclare their stripping method like they do
	         * many times.
	         */
	        if ( typeof str !== 'string' ) {
				return str;
			}

	        str = str.replace( /<.*?>/g, '' );

	        str = str.replace( /^\s+|\s+$/g, '' );

	        str = str.replace( /\n/g, ' ' );

			return str;
	    }

		function buttonConfig(name){
	        let buttonConfig = {
	            name: name,
	            extend: name,
	            beforeAction: function(e, dt, node, config){
	                node.attr('disabled', true);
	                node.prepend($("<i class='fa fa-fw fa-spinner fa-spin'></i>"));
	            },
	            afterAction: function(e, dt, node, config){
	                setTimeout(function(){
	                    node.attr('disabled', false);
	                    node.find('.fa-spinner').remove();
	                }, 500);
	            }
	        };
	        if (name.includes('excel')){
	            buttonConfig['exportOptions'] = {
	                format: {
	                    body: function (d) {
	                        if (d.includes('</button>')){
	                            return $($(d).data('content')).first().text();
	                        }

	                        return strip(d);
	                    }
	                }
	            }
	        }
	        return buttonConfig
		}
		window.buttonConfig = buttonConfig;

	/* Set the defaults for DataTables initialisation */
	$.extend( true, DataTable.defaults, {
		dom:
			"<'row'<'col-sm-6'f><'col-sm-6'l>>" +
			"<'row'<'col-sm-12'tr>>" +
			"<'row'<'col-sm-4'B><'col-sm-4'i><'col-sm-4'p>>",
		buttons: $.map(['csv', 'excel', 'pdf', 'copy', 'print'], buttonConfig),
		//buttons: ['csv', 'excel', 'pdf', 'copy', 'print'],
		renderer: 'bootstrap',
	    language: {
	        // Why do these two not work..
	        "info": "Showing _START_ to _END_ of _TOTAL_",
	        "infoFiltered": ' (filtered from _MAX_ total)',
	        "lengthMenu": "Show _MENU_ Rows",
	        "search": "",
	        'loadingRecords': '<div class="row dataTables_processing_row"><h4 class="text-center"><i class="fa fa-spinner fa-spin fa-lg"></i>&nbsp;Loading Data</h4></div>',
	        'processing': '<div class="row dataTables_processing_row"><h4 class="text-center"><i class="fa fa-spinner fa-spin fa-lg"></i>&nbsp;Processing Data</h4></div>',
	        "paginate": {
	            'next': '<i class="fa fa-angle-double-right"></i> ',
	            'previous': '<i class="fa fa-angle-double-left"></i>'
	        }
	    }
	} );


	/* Default class modification */
	$.extend( DataTable.ext.classes, {
		sWrapper:      "dataTables_wrapper form-inline dt-bootstrap",
		sFilterInput:  "form-control input-sm",
		sLengthSelect: "form-control input-sm"
	} );


	/* Bootstrap paging button renderer */
	DataTable.ext.renderer.pageButton.bootstrap = function ( settings, host, idx, buttons, page, pages ) {
		var api     = new DataTable.Api( settings );
		var classes = settings.oClasses;
		var lang    = settings.oLanguage.oPaginate;
		var btnDisplay, btnClass, counter=0;

		var attach = function( container, buttons ) {
			var i, ien, node, button;
			var clickHandler = function ( e ) {
				e.preventDefault();
				if ( !$(e.currentTarget).hasClass('disabled') ) {
					api.page( e.data.action ).draw( 'page' );
				}
			};

			for ( i=0, ien=buttons.length ; i<ien ; i++ ) {
				button = buttons[i];

				if ( $.isArray( button ) ) {
					attach( container, button );
				}
				else {
					btnDisplay = '';
					btnClass = '';

					switch ( button ) {
						case 'ellipsis':
							btnDisplay = '&hellip;';
							btnClass = 'disabled';
							break;

						case 'first':
							btnDisplay = lang.sFirst;
							btnClass = button + (page > 0 ?
								'' : ' disabled');
							break;

						case 'previous':
							btnDisplay = lang.sPrevious;
							btnClass = button + (page > 0 ?
								'' : ' disabled');
							break;

						case 'next':
							btnDisplay = lang.sNext;
							btnClass = button + (page < pages-1 ?
								'' : ' disabled');
							break;

						case 'last':
							btnDisplay = lang.sLast;
							btnClass = button + (page < pages-1 ?
								'' : ' disabled');
							break;

						default:
							btnDisplay = button + 1;
							btnClass = page === button ?
								'active' : '';
							break;
					}

					if ( btnDisplay ) {
						node = $('<li>', {
								'class': classes.sPageButton+' '+btnClass,
								'id': idx === 0 && typeof button === 'string' ?
									settings.sTableId +'_'+ button :
									null
							} )
							.append( $('<a>', {
									'href': '#',
									'aria-controls': settings.sTableId,
									'data-dt-idx': counter,
									'tabindex': settings.iTabIndex
								} )
								.html( btnDisplay )
							)
							.appendTo( container );

						settings.oApi._fnBindAction(
							node, {action: button}, clickHandler
						);

						counter++;
					}
				}
			}
		};

		// IE9 throws an 'unknown error' if document.activeElement is used
		// inside an iframe or frame.
		var activeEl;

		try {
			// Because this approach is destroying and recreating the paging
			// elements, focus is lost on the select button which is bad for
			// accessibility. So we want to restore focus once the draw has
			// completed
			activeEl = $(host).find(document.activeElement).data('dt-idx');
		}
		catch (e) {}

		attach(
			$(host).empty().html('<ul class="pagination"/>').children('ul'),
			buttons
		);

		if ( activeEl ) {
			$(host).find( '[data-dt-idx='+activeEl+']' ).focus();
		}
	};


	/*
	 * TableTools Bootstrap compatibility
	 * Required TableTools 2.1+
	 */
	if ( DataTable.TableTools ) {
		// Set the classes that TableTools uses to something suitable for Bootstrap
		$.extend( true, DataTable.TableTools.classes, {
			"container": "DTTT btn-group",
			"buttons": {
				"normal": "btn btn-default",
				"disabled": "disabled"
			},
			"collection": {
				"container": "DTTT_dropdown dropdown-menu",
				"buttons": {
					"normal": "",
					"disabled": "disabled"
				}
			},
			"print": {
				"info": "DTTT_print_info"
			},
			"select": {
				"row": "active"
			}
		} );

		// Have the collection use a bootstrap compatible drop down
		$.extend( true, DataTable.TableTools.DEFAULTS.oTags, {
			"collection": {
				"container": "ul",
				"button": "li",
				"liner": "a"
			}
		} );
	}

	}; // /factory


	// Define as an AMD module if possible
	if ( true ) {
		!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(6), __webpack_require__(15)], __WEBPACK_AMD_DEFINE_FACTORY__ = (factory), __WEBPACK_AMD_DEFINE_RESULT__ = (typeof __WEBPACK_AMD_DEFINE_FACTORY__ === 'function' ? (__WEBPACK_AMD_DEFINE_FACTORY__.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__)) : __WEBPACK_AMD_DEFINE_FACTORY__), __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
	}
	else if ( typeof exports === 'object' ) {
	    // Node/CommonJS
	    factory( require('jquery'), require('datatables') );
	}
	else if ( jQuery ) {
		// Otherwise simply initialise as normal, stopping multiple evaluation
		factory( jQuery, jQuery.fn.dataTable );
	}


	})(window, document);



/***/ })

});
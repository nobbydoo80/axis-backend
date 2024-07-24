/******/ (function(modules) { // webpackBootstrap
/******/ 	// install a JSONP callback for chunk loading
/******/ 	function webpackJsonpCallback(data) {
/******/ 		var chunkIds = data[0];
/******/ 		var moreModules = data[1];
/******/ 		var executeModules = data[2];
/******/
/******/ 		// add "moreModules" to the modules object,
/******/ 		// then flag all "chunkIds" as loaded and fire callback
/******/ 		var moduleId, chunkId, i = 0, resolves = [];
/******/ 		for(;i < chunkIds.length; i++) {
/******/ 			chunkId = chunkIds[i];
/******/ 			if(Object.prototype.hasOwnProperty.call(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 				resolves.push(installedChunks[chunkId][0]);
/******/ 			}
/******/ 			installedChunks[chunkId] = 0;
/******/ 		}
/******/ 		for(moduleId in moreModules) {
/******/ 			if(Object.prototype.hasOwnProperty.call(moreModules, moduleId)) {
/******/ 				modules[moduleId] = moreModules[moduleId];
/******/ 			}
/******/ 		}
/******/ 		if(parentJsonpFunction) parentJsonpFunction(data);
/******/
/******/ 		while(resolves.length) {
/******/ 			resolves.shift()();
/******/ 		}
/******/
/******/ 		// add entry modules from loaded chunk to deferred list
/******/ 		deferredModules.push.apply(deferredModules, executeModules || []);
/******/
/******/ 		// run deferred modules when all chunks ready
/******/ 		return checkDeferredModules();
/******/ 	};
/******/ 	function checkDeferredModules() {
/******/ 		var result;
/******/ 		for(var i = 0; i < deferredModules.length; i++) {
/******/ 			var deferredModule = deferredModules[i];
/******/ 			var fulfilled = true;
/******/ 			for(var j = 1; j < deferredModule.length; j++) {
/******/ 				var depId = deferredModule[j];
/******/ 				if(installedChunks[depId] !== 0) fulfilled = false;
/******/ 			}
/******/ 			if(fulfilled) {
/******/ 				deferredModules.splice(i--, 1);
/******/ 				result = __webpack_require__(__webpack_require__.s = deferredModule[0]);
/******/ 			}
/******/ 		}
/******/
/******/ 		return result;
/******/ 	}
/******/
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// object to store loaded and loading chunks
/******/ 	// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 	// Promise = chunk loading, 0 = chunk loaded
/******/ 	var installedChunks = {
/******/ 		"zendesk": 0
/******/ 	};
/******/
/******/ 	var deferredModules = [];
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	var jsonpArray = window["webpackJsonp"] = window["webpackJsonp"] || [];
/******/ 	var oldJsonpFunction = jsonpArray.push.bind(jsonpArray);
/******/ 	jsonpArray.push = webpackJsonpCallback;
/******/ 	jsonpArray = jsonpArray.slice();
/******/ 	for(var i = 0; i < jsonpArray.length; i++) webpackJsonpCallback(jsonpArray[i]);
/******/ 	var parentJsonpFunction = oldJsonpFunction;
/******/
/******/
/******/ 	// add entry module to deferred list
/******/ 	deferredModules.push(["../axis/core/webpack/zendesk/index.js","vendors~zendesk"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "../axis/core/webpack/zendesk/index.js":
/*!*********************************************!*\
  !*** ../axis/core/webpack/zendesk/index.js ***!
  \*********************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var angular__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! angular */ \"angular\");\n/* harmony import */ var angular__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(angular__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _settings_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./settings.js */ \"../axis/core/webpack/zendesk/settings.js\");\n/* harmony import */ var user_agent_parser__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! user-agent-parser */ \"./node_modules/user-agent-parser/src/ua-parser.js\");\n/* harmony import */ var user_agent_parser__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(user_agent_parser__WEBPACK_IMPORTED_MODULE_2__);\n\n\n\nvar module_name = 'axis.zendesk';\n/* harmony default export */ __webpack_exports__[\"default\"] = (module_name);\nvar module = angular__WEBPACK_IMPORTED_MODULE_0___default.a.module(module_name, []);\nmodule.factory('Zendesk', function ($http, $q) {\n  var obj = {\n    ticket_fields: []\n  };\n  init();\n  return {\n    all: function all() {\n      return $http.get(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].urls.list);\n    },\n    create: function create(data) {\n      return $http.post(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].urls.create, data);\n    },\n    data: obj\n  };\n\n  function init() {//getTicketFields().then((fields) => obj.ticket_fields.push.apply(obj.ticket_fields, fields));\n  }\n\n  function getTicketFields() {\n    return $q(function (resolve, reject) {\n      var ticket_fields = sessionStorage.getItem(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].keys.ticket_fields);\n\n      if (ticket_fields !== null) {\n        resolve(JSON.parse(ticket_fields));\n      } else {\n        $http.get(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].urls.ticket_fields).success(storeTicketFields(resolve)).error(reject);\n      }\n    });\n  }\n\n  function storeTicketFields(resolve) {\n    return function _storeTicketFields(data) {\n      data = data.ticket_fields;\n      sessionStorage.setItem(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].keys.ticket_fields, JSON.stringify(data));\n      resolve(data);\n    };\n  }\n});\nmodule.controller('ZendeskController', function ($scope, User, Zendesk, Impersonate) {\n  var ctrl = this;\n  ctrl.processing = 0;\n  ctrl.requester_name = '';\n  ctrl.requester_email = '';\n  ctrl.ticket_type = 'question';\n  ctrl.ticket_priority = 'low';\n  ctrl.submit = submit;\n  ctrl.show = false;\n  ctrl.ticket = null; // Where we store the response.\n\n  ctrl.model = {\n    'subject': '',\n    'description': ''\n  };\n  ctrl.type_options = [{\n    'name': 'Question',\n    'value': 'question'\n  }, {\n    'name': 'Incident',\n    'value': 'incident'\n  }, {\n    'name': 'Problem',\n    'value': 'problem'\n  }, {\n    'name': 'Task',\n    'value': 'task'\n  }];\n  ctrl.priority_options = [{\n    name: 'Low',\n    value: 'low'\n  }, {\n    name: 'Normal',\n    value: 'normal'\n  }, {\n    name: 'High',\n    value: 'high'\n  }, {\n    name: 'Urgent',\n    value: 'urgent'\n  }];\n  User.subscribe(function (user) {\n    ctrl.requester_name = \"\".concat(user.first_name, \" \").concat(user.last_name);\n    ctrl.requester_email = user.email;\n    ctrl.show = !!Impersonate.current_user && !Impersonate.is_impersonating;\n  });\n\n  function submit() {\n    ctrl.processing = 1;\n    return Zendesk.create(clean_data(ctrl.model)).then(submit_success, submit_error)[\"finally\"](submit_finally);\n  }\n\n  function clean_data(model) {\n    var data = angular__WEBPACK_IMPORTED_MODULE_0___default.a.copy(model);\n    data.requester = {\n      \"name\": ctrl.requester_name,\n      \"email\": ctrl.requester_email\n    };\n    data.current_page = getCurrentPage();\n    data.other_pages = getOtherPages();\n    data.type = ctrl.ticket_type;\n    data.priority = ctrl.ticket_priority;\n    data.comment = {\n      body: getCommentWithCustomFields(data)\n    }; // TODO: browser and browser version.\n\n    delete data.description;\n    return data;\n  }\n\n  function submit_success(data) {\n    ctrl.processing = 2;\n    ctrl.ticket = data.data.ticket || data.data.request;\n  }\n\n  function submit_error() {\n    ctrl.processing = 3;\n  }\n\n  function submit_finally() {\n    setTimeout(function () {\n      ctrl.processing = 0;\n      $scope.$digest();\n    }, 2000);\n  }\n\n  function getCommentWithCustomFields(data) {\n    var ua = new user_agent_parser__WEBPACK_IMPORTED_MODULE_2___default.a(navigator.userAgent).getResult();\n    return \"\".concat(data.description, \"\\n\\n        ---\\n        Current Page:\\n        \").concat(data.current_page, \"\\n        ---\\n        Other Pages:\\n        \").concat(data.other_pages || 'None', \"\\n        ---\\n        Browser:\\n        \").concat(ua.browser.name, \" - \").concat(ua.browser.version, \"\\n        ---\\n        OS:\\n        \").concat(ua.os.name, \" - \").concat(ua.os.version, \"\\n        \");\n  }\n\n  function getCurrentPage() {\n    return window.location.href;\n  }\n\n  function getOtherPages() {\n    var other_pages = JSON.parse(localStorage.getItem('zendesk_open_pages'));\n    other_pages.splice(other_pages.indexOf(window.location.href), 1);\n    return other_pages.join(', ');\n  }\n});\nmodule.directive('zendesk', function () {\n  return {\n    controller: 'ZendeskController',\n    controllerAs: 'zendesk',\n    link: function link(scope, element, attrs, ctrl) {\n      ctrl.is_open = false;\n\n      ctrl.negate_is_open = function () {\n        return ctrl.is_open = !ctrl.is_open;\n      }; // init\n\n\n      element.css('max-height', _settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].widget.min_height);\n\n      ctrl.toggle = function () {\n        element.css('max-height', !ctrl.is_open ? _settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].widget.max_height : _settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].widget.min_height);\n        toggle_is_open(!!ctrl.ticket);\n      };\n\n      function toggle_is_open() {\n        var reset_fields = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;\n\n        // if it's open, we wait until the next digest cycle to remove the panel body\n        // so the animation has time to take place.\n        if (ctrl.is_open) {\n          setTimeout(function () {\n            ctrl.negate_is_open();\n\n            if (reset_fields) {\n              ctrl.ticket = null;\n              ctrl.model = {\n                'subject': '',\n                'description': ''\n              };\n            }\n          }, 1);\n        } else {\n          ctrl.negate_is_open();\n        }\n      }\n    }\n  };\n});\n$(function () {\n  var original_href = window.location.href;\n  var open_pages = JSON.parse(localStorage.getItem(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].keys.open_pages)) || [];\n  open_pages.push(original_href);\n\n  try {\n    localStorage.setItem(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].keys.open_pages, JSON.stringify(open_pages));\n  } catch (e) {\n    localStorage.removeItem(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].keys.open_pages);\n  }\n\n  $(window).unload(function removePageFromStorage() {\n    var open_pages = JSON.parse(localStorage.getItem(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].keys.open_pages)) || [];\n    open_pages.splice(open_pages.indexOf(original_href), 1);\n\n    try {\n      localStorage.setItem(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].keys.open_pages, JSON.stringify(open_pages));\n    } catch (e) {\n      localStorage.removeItem(_settings_js__WEBPACK_IMPORTED_MODULE_1__[\"zendesk\"].keys.open_pages);\n    }\n  });\n});\n\n//# sourceURL=webpack:///../axis/core/webpack/zendesk/index.js?");

/***/ }),

/***/ "../axis/core/webpack/zendesk/settings.js":
/*!************************************************!*\
  !*** ../axis/core/webpack/zendesk/settings.js ***!
  \************************************************/
/*! exports provided: zendesk */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"zendesk\", function() { return zendesk; });\nvar zendesk = {\n  'urls': {\n    'create': '/api/v2/zendesk/new_ticket/'\n  },\n  'keys': {\n    'ticket_fields': 'zendesk_ticket_fields',\n    'open_pages': 'zendesk_open_pages'\n  },\n  'widget': {\n    'min_height': '39px',\n    'max_height': '500px'\n  }\n};\n\n//# sourceURL=webpack:///../axis/core/webpack/zendesk/settings.js?");

/***/ }),

/***/ "angular":
/*!**************************!*\
  !*** external "angular" ***!
  \**************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("module.exports = angular;\n\n//# sourceURL=webpack:///external_%22angular%22?");

/***/ })

/******/ });

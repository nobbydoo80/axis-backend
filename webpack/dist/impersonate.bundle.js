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
/******/ 		"impersonate": 0
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
/******/ 	deferredModules.push(["../axis/core/webpack/impersonate/index.js","vendors~auth~impersonate"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "../axis/core/webpack/impersonate/index.js":
/*!*************************************************!*\
  !*** ../axis/core/webpack/impersonate/index.js ***!
  \*************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var angular__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! angular */ \"angular\");\n/* harmony import */ var angular__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(angular__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var angular_ui_bootstrap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! angular-ui-bootstrap */ \"./node_modules/angular-ui-bootstrap/index.js\");\n/* harmony import */ var angular_ui_bootstrap__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(angular_ui_bootstrap__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var _settings_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./settings.js */ \"../axis/core/webpack/impersonate/settings.js\");\n\n\n\nvar module_name = 'axis.impersonate';\n/* harmony default export */ __webpack_exports__[\"default\"] = (module_name);\nvar RELOAD_ON_IMPERSONATE = true;\nvar module = angular__WEBPACK_IMPORTED_MODULE_0___default.a.module(module_name, [angular_ui_bootstrap__WEBPACK_IMPORTED_MODULE_1___default.a]);\nmodule.factory('Impersonate', function ($q, $http, $interpolate, User) {\n  var obj = {\n    current_user: null,\n    super_user: null,\n    is_impersonating: window.is_impersonate,\n    all: function all() {\n      return $http.get(_settings_js__WEBPACK_IMPORTED_MODULE_2__[\"impersonate\"].urls.list);\n    },\n    start: start,\n    stop: stop\n  };\n\n  var _url = function _url(url, id) {\n    return $interpolate(url)({\n      id: id\n    });\n  },\n      user_url = function user_url(id) {\n    return _url(_settings_js__WEBPACK_IMPORTED_MODULE_2__[\"impersonate\"].urls.detail, id);\n  },\n      start_url = function start_url(id) {\n    return _url(_settings_js__WEBPACK_IMPORTED_MODULE_2__[\"impersonate\"].urls.impersonate_start, id);\n  },\n      set_user = function set_user(data) {\n    return obj.current_user = data.data;\n  },\n      set_super = function set_super(data) {\n    return obj.super_user = data.data;\n  },\n      set_both = function set_both(data) {\n    set_user(data);\n    set_super(data);\n  }; // init\n\n\n  User.subscribe(function (user) {\n    return (obj.is_impersonating ? set_user : set_both)({\n      data: user\n    });\n  });\n  getSuperUser();\n  return obj;\n\n  function start(user) {\n    if (obj.is_impersonating) {\n      return _stop(false).then(function () {\n        return _start(user);\n      }).then(User.getUser);\n    } else {\n      return _start(user).then(User.getUser);\n    }\n  }\n\n  function stop() {\n    return _stop().then(User.getUser);\n  }\n\n  function _start(user) {\n    addImpersonateCount(user.id);\n    return $http.post(start_url(user.id)).then(function (data) {\n      obj.is_impersonating = true;\n      window.user_id = user.id;\n      if (RELOAD_ON_IMPERSONATE) window.location.reload(true);\n      return data;\n    });\n  }\n\n  function _stop() {\n    var reloadPage = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : true;\n    return $http.post(_settings_js__WEBPACK_IMPORTED_MODULE_2__[\"impersonate\"].urls.impersonate_stop).then(function (data) {\n      storeLatestImpersonate(User.user);\n      obj.is_impersonating = false;\n      window.user_id = window.impersonator_id;\n      if (RELOAD_ON_IMPERSONATE && reloadPage) window.location.reload(true);\n      return data;\n    });\n  }\n\n  function getSuperUser() {\n    if (obj.is_impersonating) {\n      $http.get(user_url(window.impersonator_id)).then(set_super);\n    }\n  }\n\n  function addImpersonateCount(userId) {\n    var counts = JSON.parse(localStorage.getItem(_settings_js__WEBPACK_IMPORTED_MODULE_2__[\"impersonate\"].keys.counts)) || {};\n\n    if (userId in counts) {\n      counts[userId]++;\n    } else {\n      counts[userId] = 1;\n    }\n\n    localStorage.setItem(_settings_js__WEBPACK_IMPORTED_MODULE_2__[\"impersonate\"].keys.counts, JSON.stringify(counts));\n  }\n\n  function storeLatestImpersonate(user) {\n    var latest = JSON.parse(localStorage.getItem(_settings_js__WEBPACK_IMPORTED_MODULE_2__[\"impersonate\"].keys.latest_impersonate)) || [];\n    latest = _.reject(latest, user); // remove if already in list\n\n    latest.unshift(user); // add to the front\n\n    latest.splice(5, 1); // trim list to 5 max\n\n    localStorage.setItem(_settings_js__WEBPACK_IMPORTED_MODULE_2__[\"impersonate\"].keys.latest_impersonate, JSON.stringify(latest));\n  }\n});\nmodule.controller('ImpersonateController', function (Impersonate, User) {\n  var ctrl = this; // variables\n\n  ctrl.processing = false;\n  ctrl.user = null;\n  ctrl.users = []; // helpers\n\n  ctrl.processing_start = function () {\n    return ctrl.processing = true;\n  };\n\n  ctrl.processing_stop = function () {\n    return ctrl.processing = false;\n  };\n\n  ctrl.user_null = function () {\n    return ctrl.user = null;\n  };\n\n  ctrl.is_impersonating = function () {\n    return Impersonate.is_impersonating;\n  };\n\n  ctrl.current_user = function () {\n    return User.user;\n  }; // hoisted\n\n\n  ctrl.impersonate = impersonate;\n  ctrl.stop = stop; // init\n\n  Impersonate.all().then(function (users) {\n    return ctrl.users = users.data;\n  });\n\n  function impersonate(user) {\n    if (typeof user === 'number') {\n      user = _.indexBy(ctrl.users, 'id')[user];\n    }\n\n    ctrl.processing_start();\n    Impersonate.start(user).then(ctrl.user_null)[\"finally\"](ctrl.processing_stop);\n  }\n\n  function stop() {\n    ctrl.processing_start();\n    Impersonate.stop()[\"finally\"](ctrl.processing_stop);\n  }\n});\nmodule.directive('impersonate', function (User, $compile) {\n  return {\n    controller: 'ImpersonateController',\n    controllerAs: 'impersonate',\n    link: function link(scope, element, attrs, ctrl) {\n      User.subscribe(function (user) {\n        if (scope.impersonate.is_impersonating()) {\n          setImpersonatePersist(user);\n        }\n\n        setUserProfileText(user);\n        setPreviousImpersonateList();\n      }); //User.subscribe((user) => element.find('.user').text(get_current_user(user)));\n\n      function setImpersonatePersist(user) {\n        $(\".impersonate-persist\").html(getImpersonatePersistText(user)).removeClass('hidden');\n      }\n\n      function setUserProfileText(user) {\n        element.find('.user').html(getUserProfileText(user));\n      }\n\n      function setPreviousImpersonateList() {\n        element.find('.impersonation-list').html($compile(getPreviousImpersonateList())(scope));\n      }\n\n      ;\n\n      function getPreviousImpersonateList() {\n        var latest = JSON.parse(localStorage.getItem(_settings_js__WEBPACK_IMPORTED_MODULE_2__[\"impersonate\"].keys.latest_impersonate)) || [];\n        if (!latest.length) return;\n        return \"\\n                    <h5>Previous Impersonations</h5>\\n                    <div class=\\\"list-group\\\">\\n                        \".concat(latest.map(function (user) {\n          return \"\\n                            <a class=\\\"list-group-item\\\" ng-click=\\\"impersonate.impersonate(\".concat(user.id, \")\\\">\\n                                \").concat(getImpersonatePersistText(user), \"\\n                            </a>\\n                        \");\n        }).join(''), \"\\n                    </div>\\n                \");\n      }\n\n      function getUserProfileText(user) {\n        return \"\\n                    <h4>\\n                        <span class=\\\"text-muted\\\">[\".concat(user.id, \"]</span>\\n                        \").concat(user.first_name, \" \").concat(user.last_name, \" \").concat(userIsAdmin(user), \"\\n                        - <small>\").concat(user.title, \"</small>\\n                    </h4>\\n                    <h5>\\n                        <span class=\\\"text-muted\\\">[\").concat(user.company, \"]</span>\\n                        \").concat(user.company_name, \" - <small>\").concat(user.company_type, \"</small>\\n                    </h5>\\n                \");\n      }\n\n      function userIsAdmin(user) {\n        if (user.is_company_admin) {\n          return '<i class=\"fa fa-fw fa-user-secret\"></i>';\n        }\n      }\n\n      function getImpersonatePersistText(user) {\n        return \"\\n                \".concat([user.first_name, user.last_name].join(' '), \" (\").concat(user.username, \") | \").concat(user.company_name, \" (\").concat(user.company_type, \")\\n                \");\n      }\n    }\n  };\n});\nmodule.directive('preventTypeaheadClose', function ($document, $timeout) {\n  return {\n    restrict: 'A',\n    link: function link(scope, element, attrs) {\n      $document.on('click', function (e) {\n        if (scope.impersonate.is_open) {\n          if ($(e.target).closest('a').hasClass('typeahead-item')) {\n            e.stopImmediatePropagation();\n          }\n        }\n      });\n      scope.$watch(function () {\n        return scope.impersonate.is_open;\n      }, function (newVal, oldVal) {\n        if (newVal && newVal !== oldVal) {\n          // This fires before the DOM is redrawn.\n          // We need to wait until this field is focus-able.\n          $timeout(function () {\n            element.find('input.form-control').focus();\n          }, 0);\n        }\n      });\n    }\n  };\n});\nmodule.run(function ($templateCache) {\n  $templateCache.put(\"template/typeahead/typeahead-impersonate-match.html\", \" <a tabindex='-1' class='typeahead-item'>\\n            <span bind-html-unsafe=\\\"match.model.first_name | typeaheadHighlight:query\\\"></span>\\n            <span bind-html-unsafe=\\\"match.model.last_name | typeaheadHighlight:query\\\"></span>\\n            (<span bind-html-unsafe=\\\"match.model.username | typeaheadHighlight:query\\\"></span>)\\n            <br>\\n            <span bind-html-unsafe=\\\"match.model.company_name | typeaheadHighlight:query\\\"></span>\\n            <span bind-html-unsafe=\\\"match.model.company_type | typeaheadHighlight:query\\\"></span>\\n        </a> \");\n});\n\n//# sourceURL=webpack:///../axis/core/webpack/impersonate/index.js?");

/***/ }),

/***/ "../axis/core/webpack/impersonate/settings.js":
/*!****************************************************!*\
  !*** ../axis/core/webpack/impersonate/settings.js ***!
  \****************************************************/
/*! exports provided: USER_DETAIL, impersonate */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"USER_DETAIL\", function() { return USER_DETAIL; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"impersonate\", function() { return impersonate; });\nvar USER_DETAIL = \"/api/v2/user/[[ id ]]/\";\nvar impersonate = {\n  'urls': {\n    list: \"/api/v2/user/impersonate_list/\",\n    detail: USER_DETAIL,\n    impersonate_start: \"/api/v2/user/[[ id ]]/impersonate_start/\",\n    impersonate_stop: \"/api/v2/user/impersonate_stop/\"\n  },\n  'keys': {\n    'counts': 'axis_impersonate_user_counts',\n    'latest_impersonate': 'axis_latest_impersonate_users_list'\n  }\n};\n\n//# sourceURL=webpack:///../axis/core/webpack/impersonate/settings.js?");

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

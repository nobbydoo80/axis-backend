/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
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
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "../axis/core/webpack/login/index.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "../axis/core/webpack/login/index.js":
/*!*******************************************!*\
  !*** ../axis/core/webpack/login/index.js ***!
  \*******************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("/* This is for all local mods */\n(function ($) {\n  /* Taken directly from Django https://docs.djangoproject.com/en/dev/ref/contrib/csrf/ */\n  function getCookie(name) {\n    var cookieValue = null;\n\n    if (document.cookie && document.cookie != '') {\n      var cookies = document.cookie.split(';');\n\n      for (var i = 0; i < cookies.length; i++) {\n        var cookie = jQuery.trim(cookies[i]); // Does this cookie string begin with the name we want?\n\n        if (cookie.substring(0, name.length + 1) == name + '=') {\n          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));\n          break;\n        }\n      }\n    }\n\n    return cookieValue;\n  }\n\n  var csrftoken = getCookie('csrftoken');\n  /* Taken directly from Django https://docs.djangoproject.com/en/dev/ref/contrib/csrf/ */\n\n  function setupAjaxPostCSRF() {\n    var csrftoken = getCookie('csrftoken');\n\n    function csrfSafeMethod(method) {\n      // these HTTP methods do not require CSRF protection\n      return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);\n    }\n\n    $.ajaxSetup({\n      crossDomain: false,\n      // obviates need for sameOrigin test\n      beforeSend: function beforeSend(xhr, settings) {\n        if (!csrfSafeMethod(settings.type)) {\n          xhr.setRequestHeader(\"X-CSRFToken\", csrftoken);\n        }\n      }\n    });\n  }\n\n  function setupAjaxLogin() {\n    // login submit\n    $('#login-form').submit(function (evt) {\n      evt.preventDefault();\n      var url = $(this).attr('action'),\n          username = $('#id_username').val(),\n          password = $('#id_password').val();\n\n      function showError(error) {\n        $('#login-error').removeClass('hidden').fadeOut('fast', function () {\n          $(this).text(error).fadeIn('fast');\n        });\n      }\n\n      $.ajax({\n        url: url,\n        type: 'POST',\n        data: {\n          'username': username,\n          'password': password\n        },\n        error: function error(response) {\n          showError(\"Sorry, there was a network problem. Please try again.\");\n        },\n        success: function success(response) {\n          response = JSON.parse(response);\n\n          if (response.status) {\n            window.location.replace(\"/\");\n          } else {\n            showError(\"Sorry, there was a problem with your username or password\");\n          }\n        }\n      });\n    });\n  }\n});\n\n//# sourceURL=webpack:///../axis/core/webpack/login/index.js?");

/***/ })

/******/ });

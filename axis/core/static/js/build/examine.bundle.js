webpackJsonpLegacy([2],{

/***/ 0:
/***/ (function(module, exports, __webpack_require__) {

	__webpack_require__(143);
	__webpack_require__(140);
	__webpack_require__(141);
	__webpack_require__(142);
	__webpack_require__(147);
	__webpack_require__(145);
	__webpack_require__(146);
	__webpack_require__(150);
	__webpack_require__(152);
	__webpack_require__(153);
	__webpack_require__(151);
	__webpack_require__(149);
	__webpack_require__(161);
	__webpack_require__(154);
	__webpack_require__(156);
	__webpack_require__(155);
	__webpack_require__(157);
	__webpack_require__(158);
	__webpack_require__(159);
	__webpack_require__(160);
	__webpack_require__(148);
	__webpack_require__(144);
	__webpack_require__(194);
	__webpack_require__(14);
	__webpack_require__(193);
	__webpack_require__(192);
	__webpack_require__(116);
	module.exports = __webpack_require__(179);


/***/ }),

/***/ 116:
/***/ (function(module, exports, __webpack_require__) {

	var __WEBPACK_AMD_DEFINE_FACTORY__, __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/* angular-moment.js / v0.10.3 / (c) 2013, 2014, 2015 Uri Shaked / MIT Licence */

	'format amd';
	/* global define */

	(function () {
		'use strict';

		function angularMoment(angular, moment) {

			/**
			 * @ngdoc overview
			 * @name angularMoment
			 *
			 * @description
			 * angularMoment module provides moment.js functionality for angular.js apps.
			 */
			return angular.module('angularMoment', [])

			/**
			 * @ngdoc object
			 * @name angularMoment.config:angularMomentConfig
			 *
			 * @description
			 * Common configuration of the angularMoment module
			 */
				.constant('angularMomentConfig', {
					/**
					 * @ngdoc property
					 * @name angularMoment.config.angularMomentConfig#preprocess
					 * @propertyOf angularMoment.config:angularMomentConfig
					 * @returns {string} The default preprocessor to apply
					 *
					 * @description
					 * Defines a default preprocessor to apply (e.g. 'unix', 'etc', ...). The default value is null,
					 * i.e. no preprocessor will be applied.
					 */
					preprocess: null, // e.g. 'unix', 'utc', ...

					/**
					 * @ngdoc property
					 * @name angularMoment.config.angularMomentConfig#timezone
					 * @propertyOf angularMoment.config:angularMomentConfig
					 * @returns {string} The default timezone
					 *
					 * @description
					 * The default timezone (e.g. 'Europe/London'). Empty string by default (does not apply
					 * any timezone shift).
					 */
					timezone: '',

					/**
					 * @ngdoc property
					 * @name angularMoment.config.angularMomentConfig#format
					 * @propertyOf angularMoment.config:angularMomentConfig
					 * @returns {string} The pre-conversion format of the date
					 *
					 * @description
					 * Specify the format of the input date. Essentially it's a
					 * default and saves you from specifying a format in every
					 * element. Overridden by element attr. Null by default.
					 */
					format: null,

					/**
					 * @ngdoc property
					 * @name angularMoment.config.angularMomentConfig#statefulFilters
					 * @propertyOf angularMoment.config:angularMomentConfig
					 * @returns {boolean} Whether angular-moment filters should be stateless (or not)
					 *
					 * @description
					 * Specifies whether the filters included with angular-moment are stateful.
					 * Stateful filters will automatically re-evaluate whenever you change the timezone
					 * or language settings, but may negatively impact performance. true by default.
					 */
					statefulFilters: true
				})

			/**
			 * @ngdoc object
			 * @name angularMoment.object:moment
			 *
			 * @description
			 * moment global (as provided by the moment.js library)
			 */
				.constant('moment', moment)

			/**
			 * @ngdoc object
			 * @name angularMoment.config:amTimeAgoConfig
			 * @module angularMoment
			 *
			 * @description
			 * configuration specific to the amTimeAgo directive
			 */
				.constant('amTimeAgoConfig', {
					/**
					 * @ngdoc property
					 * @name angularMoment.config.amTimeAgoConfig#withoutSuffix
					 * @propertyOf angularMoment.config:amTimeAgoConfig
					 * @returns {boolean} Whether to include a suffix in am-time-ago directive
					 *
					 * @description
					 * Defaults to false.
					 */
					withoutSuffix: false,

					/**
					 * @ngdoc property
					 * @name angularMoment.config.amTimeAgoConfig#serverTime
					 * @propertyOf angularMoment.config:amTimeAgoConfig
					 * @returns {number} Server time in milliseconds since the epoch
					 *
					 * @description
					 * If set, time ago will be calculated relative to the given value.
					 * If null, local time will be used. Defaults to null.
					 */
					serverTime: null,

					/**
					 * @ngdoc property
					 * @name angularMoment.config.amTimeAgoConfig#titleFormat
					 * @propertyOf angularMoment.config:amTimeAgoConfig
					 * @returns {string} The format of the date to be displayed in the title of the element. If null,
					 *        the directive set the title of the element.
					 *
					 * @description
					 * The format of the date used for the title of the element. null by default.
					 */
					titleFormat: null,

					/**
					 * @ngdoc property
					 * @name angularMoment.config.amTimeAgoConfig#fullDateThreshold
					 * @propertyOf angularMoment.config:amTimeAgoConfig
					 * @returns {number} The minimum number of days for showing a full date instead of relative time
					 *
					 * @description
					 * The threshold for displaying a full date. The default is null, which means the date will always
					 * be relative, and full date will never be displayed.
					 */
					fullDateThreshold: null,

					/**
					 * @ngdoc property
					 * @name angularMoment.config.amTimeAgoConfig#fullDateFormat
					 * @propertyOf angularMoment.config:amTimeAgoConfig
					 * @returns {string} The format to use when displaying a full date.
					 *
					 * @description
					 * Specify the format of the date when displayed as full date. null by default.
					 */
					fullDateFormat: null
				})

			/**
			 * @ngdoc directive
			 * @name angularMoment.directive:amTimeAgo
			 * @module angularMoment
			 *
			 * @restrict A
			 */
				.directive('amTimeAgo', ['$window', 'moment', 'amMoment', 'amTimeAgoConfig', 'angularMomentConfig', function ($window, moment, amMoment, amTimeAgoConfig, angularMomentConfig) {

					return function (scope, element, attr) {
						var activeTimeout = null;
						var currentValue;
						var currentFormat = angularMomentConfig.format;
						var withoutSuffix = amTimeAgoConfig.withoutSuffix;
						var titleFormat = amTimeAgoConfig.titleFormat;
						var fullDateThreshold = amTimeAgoConfig.fullDateThreshold;
						var fullDateFormat = amTimeAgoConfig.fullDateFormat;
						var localDate = new Date().getTime();
						var preprocess = angularMomentConfig.preprocess;
						var modelName = attr.amTimeAgo;
						var currentFrom;
						var isTimeElement = ('TIME' === element[0].nodeName.toUpperCase());

						function getNow() {
							var now;
							if (currentFrom) {
								now = currentFrom;
							} else if (amTimeAgoConfig.serverTime) {
								var localNow = new Date().getTime();
								var nowMillis = localNow - localDate + amTimeAgoConfig.serverTime;
								now = moment(nowMillis);
							}
							else {
								now = moment();
							}
							return now;
						}

						function cancelTimer() {
							if (activeTimeout) {
								$window.clearTimeout(activeTimeout);
								activeTimeout = null;
							}
						}

						function updateTime(momentInstance) {
							var daysAgo = getNow().diff(momentInstance, 'day');
							var showFullDate = fullDateThreshold && daysAgo >= fullDateThreshold;

							if (showFullDate) {
								element.text(momentInstance.format(fullDateFormat));
							} else {
								element.text(momentInstance.from(getNow(), withoutSuffix));
							}

							if (titleFormat && !element.attr('title')) {
								element.attr('title', momentInstance.local().format(titleFormat));
							}

							if (!showFullDate) {
								var howOld = Math.abs(getNow().diff(momentInstance, 'minute'));
								var secondsUntilUpdate = 3600;
								if (howOld < 1) {
									secondsUntilUpdate = 1;
								} else if (howOld < 60) {
									secondsUntilUpdate = 30;
								} else if (howOld < 180) {
									secondsUntilUpdate = 300;
								}

								activeTimeout = $window.setTimeout(function () {
									updateTime(momentInstance);
								}, secondsUntilUpdate * 1000);
							}
						}

						function updateDateTimeAttr(value) {
							if (isTimeElement) {
								element.attr('datetime', value);
							}
						}

						function updateMoment() {
							cancelTimer();
							if (currentValue) {
								var momentValue = amMoment.preprocessDate(currentValue, preprocess, currentFormat);
								updateTime(momentValue);
								updateDateTimeAttr(momentValue.toISOString());
							}
						}

						scope.$watch(modelName, function (value) {
							if ((typeof value === 'undefined') || (value === null) || (value === '')) {
								cancelTimer();
								if (currentValue) {
									element.text('');
									updateDateTimeAttr('');
									currentValue = null;
								}
								return;
							}

							currentValue = value;
							updateMoment();
						});

						if (angular.isDefined(attr.amFrom)) {
							scope.$watch(attr.amFrom, function (value) {
								if ((typeof value === 'undefined') || (value === null) || (value === '')) {
									currentFrom = null;
								} else {
									currentFrom = moment(value);
								}
								updateMoment();
							});
						}

						if (angular.isDefined(attr.amWithoutSuffix)) {
							scope.$watch(attr.amWithoutSuffix, function (value) {
								if (typeof value === 'boolean') {
									withoutSuffix = value;
									updateMoment();
								} else {
									withoutSuffix = amTimeAgoConfig.withoutSuffix;
								}
							});
						}

						attr.$observe('amFormat', function (format) {
							if (typeof format !== 'undefined') {
								currentFormat = format;
								updateMoment();
							}
						});

						attr.$observe('amPreprocess', function (newValue) {
							preprocess = newValue;
							updateMoment();
						});

						attr.$observe('amFullDateThreshold', function (newValue) {
							fullDateThreshold = newValue;
							updateMoment();
						});

						attr.$observe('amFullDateFormat', function (newValue) {
							fullDateFormat = newValue;
							updateMoment();
						});

						scope.$on('$destroy', function () {
							cancelTimer();
						});

						scope.$on('amMoment:localeChanged', function () {
							updateMoment();
						});
					};
				}])

			/**
			 * @ngdoc service
			 * @name angularMoment.service.amMoment
			 * @module angularMoment
			 */
				.service('amMoment', ['moment', '$rootScope', '$log', 'angularMomentConfig', function (moment, $rootScope, $log, angularMomentConfig) {
					/**
					 * @ngdoc property
					 * @name angularMoment:amMoment#preprocessors
					 * @module angularMoment
					 *
					 * @description
					 * Defines the preprocessors for the preprocessDate method. By default, the following preprocessors
					 * are defined: utc, unix.
					 */
					this.preprocessors = {
						utc: moment.utc,
						unix: moment.unix
					};

					/**
					 * @ngdoc function
					 * @name angularMoment.service.amMoment#changeLocale
					 * @methodOf angularMoment.service.amMoment
					 *
					 * @description
					 * Changes the locale for moment.js and updates all the am-time-ago directive instances
					 * with the new locale. Also broadcasts an `amMoment:localeChanged` event on $rootScope.
					 *
					 * @param {string} locale Locale code (e.g. en, es, ru, pt-br, etc.)
					 * @param {object} customization object of locale strings to override
					 */
					this.changeLocale = function (locale, customization) {
						var result = moment.locale(locale, customization);
						if (angular.isDefined(locale)) {
							$rootScope.$broadcast('amMoment:localeChanged');

						}
						return result;
					};

					/**
					 * @ngdoc function
					 * @name angularMoment.service.amMoment#changeTimezone
					 * @methodOf angularMoment.service.amMoment
					 *
					 * @description
					 * Changes the default timezone for amCalendar, amDateFormat and amTimeAgo. Also broadcasts an
					 * `amMoment:timezoneChanged` event on $rootScope.
					 *
					 * @param {string} timezone Timezone name (e.g. UTC)
					 */
					this.changeTimezone = function (timezone) {
						angularMomentConfig.timezone = timezone;
						$rootScope.$broadcast('amMoment:timezoneChanged');
					};

					/**
					 * @ngdoc function
					 * @name angularMoment.service.amMoment#preprocessDate
					 * @methodOf angularMoment.service.amMoment
					 *
					 * @description
					 * Preprocess a given value and convert it into a Moment instance appropriate for use in the
					 * am-time-ago directive and the filters.
					 *
					 * @param {*} value The value to be preprocessed
					 * @param {string} preprocess The name of the preprocessor the apply (e.g. utc, unix)
					 * @param {string=} format Specifies how to parse the value (see {@link http://momentjs.com/docs/#/parsing/string-format/})
					 * @return {Moment} A value that can be parsed by the moment library
					 */
					this.preprocessDate = function (value, preprocess, format) {
						if (angular.isUndefined(preprocess)) {
							preprocess = angularMomentConfig.preprocess;
						}
						if (this.preprocessors[preprocess]) {
							return this.preprocessors[preprocess](value, format);
						}
						if (preprocess) {
							$log.warn('angular-moment: Ignoring unsupported value for preprocess: ' + preprocess);
						}
						if (!isNaN(parseFloat(value)) && isFinite(value)) {
							// Milliseconds since the epoch
							return moment(parseInt(value, 10));
						}
						// else just returns the value as-is.
						return moment(value, format);
					};

					/**
					 * @ngdoc function
					 * @name angularMoment.service.amMoment#applyTimezone
					 * @methodOf angularMoment.service.amMoment
					 *
					 * @description
					 * Apply a timezone onto a given moment object. It can be a named timezone (e.g. 'America/Phoenix') or an offset from UTC (e.g. '+0300')
					 * moment-timezone.js is needed when a named timezone is used, otherwise, it'll not apply any timezone shift.
					 *
					 * @param {Moment} aMoment a moment() instance to apply the timezone shift to
					 * @param {string=} timezone The timezone to apply. If none given, will apply the timezone
					 *        configured in angularMomentConfig.timezone. It can be a named timezone (e.g. 'America/Phoenix') or an offset from UTC (e.g. '+0300')
					 *
					 * @returns {Moment} The given moment with the timezone shift applied
					 */
					this.applyTimezone = function (aMoment, timezone) {
						timezone = timezone || angularMomentConfig.timezone;
						if (!timezone) {
							return aMoment;
						}

						if (timezone.match(/^Z|[+-]\d\d:?\d\d$/i)) {
							aMoment = aMoment.utcOffset(timezone);
						} else if (aMoment.tz) {
							aMoment = aMoment.tz(timezone);
						} else {
							$log.warn('angular-moment: named timezone specified but moment.tz() is undefined. Did you forget to include moment-timezone.js?');
						}

						return aMoment;
					};
				}])

			/**
			 * @ngdoc filter
			 * @name angularMoment.filter:amCalendar
			 * @module angularMoment
			 */
				.filter('amCalendar', ['moment', 'amMoment', 'angularMomentConfig', function (moment, amMoment, angularMomentConfig) {
					function amCalendarFilter(value, preprocess, timezone) {
						if (typeof value === 'undefined' || value === null) {
							return '';
						}

						value = amMoment.preprocessDate(value, preprocess);
						var date = moment(value);
						if (!date.isValid()) {
							return '';
						}

						return amMoment.applyTimezone(date, timezone).calendar();
					}

					// Since AngularJS 1.3, filters have to explicitly define being stateful
					// (this is no longer the default).
					amCalendarFilter.$stateful = angularMomentConfig.statefulFilters;

					return amCalendarFilter;
				}])

			/**
			 * @ngdoc filter
			 * @name angularMoment.filter:amDifference
			 * @module angularMoment
			 */
				.filter('amDifference', ['moment', 'amMoment', 'angularMomentConfig', function (moment, amMoment, angularMomentConfig) {
					function amDifferenceFilter(value, otherValue, unit, usePrecision, preprocessValue, preprocessOtherValue) {
						if (typeof value === 'undefined' || value === null) {
							return '';
						}

						value = amMoment.preprocessDate(value, preprocessValue);
						var date = moment(value);
						if (!date.isValid()) {
							return '';
						}

						var date2;
						if (typeof otherValue === 'undefined' || otherValue === null) {
							date2 = moment();
						} else {
							otherValue = amMoment.preprocessDate(otherValue, preprocessOtherValue);
							date2 = moment(otherValue);
							if (!date2.isValid()) {
								return '';
							}
						}

						return amMoment.applyTimezone(date).diff(amMoment.applyTimezone(date2), unit, usePrecision);
					}

					amDifferenceFilter.$stateful = angularMomentConfig.statefulFilters;

					return amDifferenceFilter;
				}])

			/**
			 * @ngdoc filter
			 * @name angularMoment.filter:amDateFormat
			 * @module angularMoment
			 * @function
			 */
				.filter('amDateFormat', ['moment', 'amMoment', 'angularMomentConfig', function (moment, amMoment, angularMomentConfig) {
					function amDateFormatFilter(value, format, preprocess, timezone, inputFormat) {
						var currentFormat = inputFormat || angularMomentConfig.format;
						if (typeof value === 'undefined' || value === null) {
							return '';
						}

						value = amMoment.preprocessDate(value, preprocess, currentFormat);
						var date = moment(value);
						if (!date.isValid()) {
							return '';
						}

						return amMoment.applyTimezone(date, timezone).format(format);
					}

					amDateFormatFilter.$stateful = angularMomentConfig.statefulFilters;

					return amDateFormatFilter;
				}])

			/**
			 * @ngdoc filter
			 * @name angularMoment.filter:amDurationFormat
			 * @module angularMoment
			 * @function
			 */
				.filter('amDurationFormat', ['moment', 'angularMomentConfig', function (moment, angularMomentConfig) {
					function amDurationFormatFilter(value, format, suffix) {
						if (typeof value === 'undefined' || value === null) {
							return '';
						}

						return moment.duration(value, format).humanize(suffix);
					}

					amDurationFormatFilter.$stateful = angularMomentConfig.statefulFilters;

					return amDurationFormatFilter;
				}])

			/**
			 * @ngdoc filter
			 * @name angularMoment.filter:amTimeAgo
			 * @module angularMoment
			 * @function
			 */
				.filter('amTimeAgo', ['moment', 'amMoment', 'angularMomentConfig', function (moment, amMoment, angularMomentConfig) {
					function amTimeAgoFilter(value, preprocess, suffix, from) {
						var date, dateFrom;

						if (typeof value === 'undefined' || value === null) {
							return '';
						}

						value = amMoment.preprocessDate(value, preprocess);
						date = moment(value);
						if (!date.isValid()) {
							return '';
						}

						dateFrom = moment(from);
						if (typeof from !== 'undefined' && dateFrom.isValid()) {
							return amMoment.applyTimezone(date).from(dateFrom, suffix);
						}

						return amMoment.applyTimezone(date).fromNow(suffix);
					}

					amTimeAgoFilter.$stateful = angularMomentConfig.statefulFilters;

					return amTimeAgoFilter;
				}])

			/**
			 * @ngdoc filter
			 * @name angularMoment.filter:amSubtract
			 * @module angularMoment
			 * @function
			 */
				.filter('amSubtract', ['moment', 'angularMomentConfig', function (moment, angularMomentConfig) {
					function amSubtractFilter(value, amount, type) {

						if (typeof value === 'undefined' || value === null) {
							return '';
						}

						return moment(value).subtract(parseInt(amount, 10), type);
					}

					amSubtractFilter.$stateful = angularMomentConfig.statefulFilters;

					return amSubtractFilter;
				}])

			/**
			 * @ngdoc filter
			 * @name angularMoment.filter:amAdd
			 * @module angularMoment
			 * @function
			 */
				.filter('amAdd', ['moment', 'angularMomentConfig', function (moment, angularMomentConfig) {
					function amAddFilter(value, amount, type) {

						if (typeof value === 'undefined' || value === null) {
							return '';
						}

						return moment(value).add(parseInt(amount, 10), type);
					}

					amAddFilter.$stateful = angularMomentConfig.statefulFilters;

					return amAddFilter;
				}]);
		}

		if (true) {
			!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(4), __webpack_require__(1)], __WEBPACK_AMD_DEFINE_FACTORY__ = (angularMoment), __WEBPACK_AMD_DEFINE_RESULT__ = (typeof __WEBPACK_AMD_DEFINE_FACTORY__ === 'function' ? (__WEBPACK_AMD_DEFINE_FACTORY__.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__)) : __WEBPACK_AMD_DEFINE_FACTORY__), __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
		} else if (typeof module !== 'undefined' && module && module.exports) {
			angularMoment(angular, require('moment'));
			module.exports = 'angularMoment';
		} else {
			angularMoment(angular, (typeof global !== 'undefined' ? global : window).moment);
		}
	})();


/***/ }),

/***/ 140:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.actionStrip.actionStrip').directive('actionButton', function () {
	    /**
	     * Action buttons can be made manually by passing in attributes.
	     * The exception is dropdown buttons. Those required a nice options object.
	     */
	    return {
	        restrict: 'EA',
	        require: '^actionStrip',
	        scope: {
	            type: '@?btnType',
	            style: '@?btnStyle',
	            size: '@?btnSize',
	            instruction: '@?',
	            href: '@?link',
	            disabled: '=?',

	            options: '=?'
	        },
	        transclude: true,
	        templateUrl: '/examine/actions/angular-button.html',
	        link: function link(scope, element, attrs) {
	            scope.region = scope.$parent.region;
	            scope.getType = function () {
	                return scope.type || scope.options.type;
	            };
	        }
	    };
	});

/***/ }),

/***/ 141:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.actionStrip.actionStrip').controller('ActionStripController', function () {}).directive('actionStrip', function () {
	    return {
	        restrict: 'EA',
	        require: '^actionStripSet',
	        controller: 'ActionStripController'
	    };
	});

	// empty controller so directives can require this.

/***/ }),

/***/ 142:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.actionStrip.actionStripSet').controller('ActionStripSetController', function () {
	    var ctrl = this;

	    ctrl.singleInstance = false;
	    ctrl.actionsAttribute = false;
	}).directive('standaloneActionStripSet', function () {
	    return {
	        restrict: 'EA',
	        scope: true,
	        templateUrl: '/examine/actions/action-strip.html',
	        controller: 'ActionStripSetController',
	        controllerAs: 'stripSet',
	        link: function link(scope, element, attrs) {
	            var listener = scope.$watch(attrs.actions, function (newVal, oldVal) {
	                scope.actionsObject = newVal;
	            });

	            scope.$on('$destroy', function () {
	                listener();
	            });
	        }
	    };
	}).directive('actionStripSet', function () {
	    /**
	     * Used when you need to place controls somewhere on the page.
	     *
	     * Default use is with the 'actions' attr.
	     *    Pass it the regionObjects .actions dict.
	     *
	     * For single instances use the single-instance attr.
	     *    Pass it the string of the action for it to look up in regionObject.actions
	     */
	    return {
	        restrict: 'EA',
	        require: '^?axisRegion',
	        scope: true,
	        templateUrl: '/examine/actions/action-strip.html',
	        controller: 'ActionStripSetController',
	        controllerAs: 'stripSet',
	        link: function link(scope, element, attrs, regionController) {
	            if (regionController) {
	                var actionAttr = attrs.actions || 'regionObject.actions';

	                scope.singleInstance = attrs.singleInstance;
	                scope.actionsObject = scope.$eval(actionAttr);
	            }
	        }
	    };
	});

/***/ }),

/***/ 143:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.actionStrip.actionStripSet', ['axis.actionStrip.actionStrip', 'axis.actionStrip.actionButton']);
	angular.module('axis.actionStrip.actionStrip', []);
	angular.module('axis.actionStrip.actionButton', []);

	angular.module('axis.actionStrip', ['axis.actionStrip.actionStripSet', 'axis.actionStrip.actionStrip', 'axis.actionStrip.actionButton']);

/***/ }),

/***/ 144:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 10/20/14.
	 */

	'use strict';

	var dependencies = ['ui.bootstrap', 'ui.router', 'ui.select', 'axis.filters', 'axis.services', 'axis.fields', 'axis.region', 'axis.actionStrip'];

	function getDependencies(deps) {
	    var temp = angular.copy(dependencies);
	    if (typeof deps !== 'undefined') {
	        angular.forEach(deps, function (dep) {
	            temp.push(dep);
	        });
	    }
	    return temp;
	}

	angular.module('examineApp', getDependencies(window.__extraDependencies)).controller('ExamineViewController', function ($rootScope, $state, $scope, ExamineSettings, TabService, RegionService) {
	    var ctrl = this;

	    $rootScope.ExamineSettings = ExamineSettings;
	    $rootScope.isHiddenField = isHiddenField;
	    $rootScope.$state = $state;
	    $rootScope.creating = ctrl.creating = ExamineSettings.creating;
	    ctrl.pageRegions = $scope.pageRegions = ExamineSettings.regions_endpoints;
	    ctrl.tabsActive = $scope.tabsActive = TabService.tabs;
	    ctrl.regionsMap = RegionService.helpers.regionsMap;
	    ctrl.getRegionCounter = RegionService.getRegionCounter;
	    $rootScope.examineApp = ctrl;

	    function isHiddenField(field) {
	        if (field.widget.input_type == 'hidden') {
	            if (field.widget._widget.toLowerCase().indexOf('hidden') > -1) {
	                return true;
	            }
	        }
	        return false;
	    }
	}).constant('ExamineSettings', window.__ExamineSettings).config(function ($httpProvider, $interpolateProvider, $sceDelegateProvider, ExamineSettings, $stateProvider, uiSelectConfig, $provide) {

	    $sceDelegateProvider.resourceUrlWhitelist(['self', ExamineSettings.static_url + '**']);

	    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
	    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

	    $interpolateProvider.startSymbol('[[');
	    $interpolateProvider.endSymbol(']]');

	    uiSelectConfig.theme = 'select2';

	    $stateProvider.state('index', { url: '/' });
	});

/***/ }),

/***/ 145:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.fields.field').directive('axisField', function ($timeout) {
	    /**
	     * Attributes:
	     *  field: ={field object}
	     *  on-change: &
	     *  show-label: {no arguments}
	     *  label: @
	     *  disabled: =
	     */
	    return {
	        restrict: 'EA',
	        require: '^?ngRepeat',
	        scope: true,
	        templateUrl: '/examine/angular_field.html',
	        controller: function controller($scope) {
	            $scope.hasAttr = hasAttr;

	            function hasAttr(attr) {
	                return $scope.field.widget.attrs.hasOwnProperty(attr);
	            }
	        },
	        link: function link(scope, element, attrs) {

	            if (!angular.isDefined(scope.field)) {
	                set_field();
	                if (!angular.isDefined(scope.field)) {
	                    throw new Error('Axis Field requires \'field\'.');
	                }
	                scope.regionObject.controller.axisFields[scope.field.field_name] = element;
	            }
	            var initial_value = attrs.value ? scope.$eval(attrs.value) : scope.field.value;
	            if (attrs.value || initial_value !== null && initial_value !== undefined && initial_value !== '') {
	                scope.regionObject.object[scope.field.field_name] = initial_value;
	            }

	            // NOTE: implementation taken from ngChange
	            scope.onChange = function (data) {
	                if (angular.isDefined(attrs.onChange)) {
	                    scope.$eval(attrs.onChange, data);
	                }
	            };

	            // Options for overwriting labels
	            scope.showLabel = !angular.isDefined(attrs.noLabel);
	            if (angular.isDefined(attrs.label)) {
	                scope.label = scope.$eval(attrs.label);
	            }

	            // Options for forcefully disabling fields
	            if (angular.isDefined(attrs.disabled)) {
	                scope.field.widget.attrs.disabled = scope.$eval(attrs.disabled);
	            }

	            function set_field() {
	                scope.field = scope.$eval(attrs.field);
	                if (angular.isDefined(attrs.expectUpdate)) {
	                    scope.$watch(attrs.field, function (value) {
	                        scope.field = value;
	                    });
	                }
	            }
	        }
	    };
	}).directive('fieldError', function () {
	    /**
	     * Place this anywhere there is access to the `regionObject` and `field` and it will
	     * display any non_field_errors returned by the server.
	     */
	    return {
	        restrict: 'EA',
	        replace: true,
	        template: '<ul class="text-danger" ng-if="regionObject.errors[field.field_name]">\n    <li ng-repeat="message in regionObject.errors[field.field_name] track by $index">[[ message ]]</li>\n</ul>'
	    };
	});

/***/ }),

/***/ 146:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.fields.helpers.tab').directive('tabHelper', function ($rootScope, $parse, TabService) {
	    return {
	        restrict: 'A',
	        compile: function compile(el, attrs) {
	            var endpoint_name = attrs.endpoint.split('.').pop();
	            attrs.$set('active', 'tabsActive[\'' + endpoint_name + '\'].active');

	            // NOTE: ui.bootstrap tab directive stops click propagations.
	            // Instead of being able to set ui-sref we hook into the on Select callback they offer.
	            //attrs.$set('ui-sref', attrs.endpoint);
	            attrs.$set('select', 'go("' + attrs.endpoint + '")');
	            var disabled = $parse(attrs.disabled)($rootScope);
	            TabService.addTab(attrs.endpoint, disabled);

	            return function postLink(scope, element, attrs) {
	                if (attrs.disabled) {
	                    var unwatch = scope.$watch(function () {
	                        return !!scope.$eval(attrs.disabled);
	                    }, function (newVal, oldVal) {
	                        if (newVal !== oldVal) {
	                            TabService.updateDisableListener(attrs.endpoint, newVal);
	                            unwatch();
	                        }
	                    });
	                }
	                scope.go = TabService.go;
	            };
	        }
	    };
	});

	angular.module('axis.fields.helpers.fileField').directive('fileFieldHelper', function ($q, $timeout, Actions) {
	    return {
	        restrict: 'EA',
	        scope: true,
	        link: function link(scope, element, attrs) {
	            var field_name = scope.$eval(attrs.fileFieldHelper);
	            var doAutoSave = scope.$eval(attrs.autoSave);
	            scope.raw_key = field_name + '_raw';
	            scope.name_key = field_name + '_raw_name';
	            scope.highlightDropArea = false;
	            scope.fileProgress = null;
	            if (scope.field.widget.attrs.multiple) {
	                element.attr('multiple', true);
	            }

	            var loadFile = function loadFile(f, index) {
	                var deferred = $q.defer();
	                var fileName = f.name;
	                var reader = new FileReader();

	                reader.onload = function (file) {
	                    console.groupCollapsed('file');
	                    console.log('name', name);
	                    console.log('file', file);
	                    console.groupEnd('file');

	                    var raw = getRaw(file, fileName);

	                    if (index === 0) {
	                        injectValues(scope, scope.regionObject, raw, fileName);
	                        scope.$apply();
	                        deferred.resolve();
	                        if (doAutoSave) {
	                            Actions.callMethod('save', scope.regionObject).then(function () {
	                                return Actions.callMethod('exit', scope.regionObject);
	                            });
	                        }
	                    } else {
	                        scope.regionSet.fetchNewRegion().then(function (regionObject) {
	                            // set values in new regionObject
	                            // then update the FileInput to show existing when its available
	                            scope.fileProgress = null;
	                            injectValues(scope, regionObject, raw, fileName);
	                            removeWatcherWhenAny(scope, waitForElement(regionObject), markFileAsExisting(regionObject));
	                            deferred.resolve();
	                            if (doAutoSave) {
	                                Actions.callMethod('save', regionObject).then(function () {
	                                    return Actions.callMethod('exit', regionObject);
	                                });
	                            }
	                        });
	                    }
	                };

	                reader.readAsDataURL(f);
	                return deferred.promise;
	            };
	            function getRaw(file, name) {
	                /**
	                 * Cleans the base64 version for file types that don't provide
	                 * a MimeType. Mostly BLG files.
	                 */
	                var raw = file.target.result;
	                var extension = name.split('.').pop();
	                if (raw.indexOf(':;') > -1) {
	                    raw = raw.replace(':;', ':application/' + extension + ';');
	                } else if (raw.indexOf('octet-stream') > -1 && extension == 'blg') {
	                    raw = raw.replace('octet-stream', extension);
	                }
	                return raw;
	            }
	            function injectValues(scope, regionObject, raw, file_name) {
	                regionObject.object[scope.raw_key] = raw;
	                regionObject.object[scope.name_key] = file_name;
	                regionObject.fields[scope.field.prefixed_name].value = file_name;
	            }

	            var dropArea = attrs.dropArea || 'axis-field';
	            $(element).closest(dropArea).on('dragover dragenter', function (e) {
	                e.stopPropagation();
	                e.preventDefault();
	                scope.highlightDropArea = true;
	            }, false);
	            $(element).closest(dropArea).on('dragleave', function (e) {
	                e.stopPropagation();
	                e.preventDefault();
	                scope.highlightDropArea = false;
	            }, false);
	            $(element).closest(dropArea).on('drop', function (e) {
	                scope.highlightDropArea = false;
	                scope.fileProgress = 0;
	                e.stopPropagation();
	                e.preventDefault();
	                var promises = angular.forEach(e.originalEvent.dataTransfer.files, loadFile);
	                $q.all(promises).then(function () {
	                    $timeout(function () {
	                        return console.log('Triggering $scope.$apply()');
	                    }, 1000);
	                });
	            });
	            element.on('change', function (e) {
	                var promises = angular.forEach(e.target.files, loadFile);
	                $q.all(promises).then(function () {
	                    // Just need a scope.$apply() to run later
	                    // This causes any side effects from having multiple documents
	                    // to take effect. In this case, the "save all" button shows up.
	                    // Anything less than 1 second doesn't seem to work :/
	                    $timeout(function () {
	                        return console.log('Triggering $scope.$apply()');
	                    }, 1000);
	                });
	            });
	        }
	    };
	});

	angular.module('axis.fields.helpers.select2').directive('uiSelectHelper', function ($sce, $http, $timeout) {
	    return {
	        restrict: 'A',
	        require: 'uiSelect',
	        link: function link(scope, element, attrs, uiSelectController) {

	            function init() {
	                if (!isGrouped(scope.field)) {
	                    $timeout(function () {
	                        element.find('ul.select2-results').removeAttr('group-by');
	                        scope.$select.isGrouped = false;
	                    });
	                }
	                init_values();
	                init_choices();
	            }
	            function isGrouped(field) {
	                // Field is grouped if its not hidden field and the ajax results are to be processed.
	                if (field.widget.widget_id === undefined) {
	                    return false;
	                }
	                return true;
	            }
	            function init_values() {
	                // push the field values into the options.
	                if (scope.field.value) {
	                    if (angular.isArray(scope.field.value)) {
	                        angular.forEach(scope.field.value, function (value, index) {
	                            var item = { id: value, text: scope.field.value_label[index] };
	                            scope.selectOptions.push(item);
	                        });
	                    } else {
	                        var item = { id: scope.field.value, text: scope.field.value_label };
	                        scope.selectOptions.push(item);
	                    }
	                    if (!scope.regionObject.object[scope.field.field_name]) {
	                        scope.regionObject.object[scope.field.field_name] = scope.field.value;
	                    }
	                }
	            }
	            function init_choices() {
	                // push the choices into the options
	                if (scope.field.widget.choices && scope.field.widget.choices.length) {
	                    angular.forEach(scope.field.widget.choices, function (value, index, obj) {
	                        var item = { id: value[0], text: value[1] };
	                        if (angular.isUndefined(_.find(scope.selectOptions, item))) {
	                            scope.selectOptions.push(item);
	                        }
	                    });
	                }
	            }
	            function processResults(options, noResults) {
	                angular.forEach(options, function (option) {
	                    option['type'] = 'Select from existing:';
	                });
	                options.unshift({ text: scope.$select.search, id: scope.$select.search, type: 'Create New:' });
	                if (noResults) {
	                    options.unshift({ text: 'No Results...', id: null, type: 'Select from existing:' });
	                }
	                return options;
	            }
	            function refreshField(term) {
	                if (term) {
	                    var params = { term: term, page: 1, field_id: scope.field.widget.widget_id };
	                    return $http.get('/select2/fields/auto.json', { params: params }).then(function (response) {
	                        if (response.data.results.length) {
	                            scope.selectOptions = response.data.results;
	                        } else {
	                            scope.selectOptions = [];
	                        }
	                        if (scope.field.widget.relationship_add_url !== null) {
	                            scope.selectOptions = processResults(scope.selectOptions, response.data.results.length === 0);
	                        }
	                    });
	                }
	            }

	            scope.refreshField = refreshField;
	            scope.trustAsHtml = $sce.trustAsHtml;
	            scope.selectOptions = [];

	            init();
	        }
	    };
	}).directive('uiSelectRelationship', function ($log) {
	    return {
	        restrict: 'A',
	        require: 'uiSelect',
	        link: function link(scope, element, attrs, uiSelectController) {

	            function choiceSelected($item, $model) {
	                // Create New choices have same text and id to avoid reselecting null values.
	                if (!angular.equals($item.text, $item.id) && $item.id !== null) {
	                    if (scope.field.widget.relationship_add_url) {

	                        var form = $('<form method=\'post\'><input name=\'object\' /><input name=\'go_to_detail\' /></form>');
	                        form.attr('action', scope.field.widget.relationship_add_url);
	                        form.append($('input[name=csrfmiddlewaretoken]').clone());
	                        form.find('input[name=object]').val($model);
	                        form.appendTo('body');
	                        form.submit();
	                    }
	                }
	                scope.onChange({
	                    $item: $item,
	                    $model: $model
	                });
	            }

	            scope.choiceSelected = choiceSelected;
	        }
	    };
	});

	angular.module('axis.fields.helpers.multiSelect').directive('multiSelectHelper', function () {
	    return {
	        restrict: 'A',
	        link: function link(scope, element, attrs) {

	            function init() {
	                init_choices(init_values());
	            }
	            function init_values() {

	                // check the region object to ensure we have no value.
	                if (!scope.field.value) {
	                    scope.field.value = scope.regionObject.object[scope.field.field_name];
	                }

	                if (scope.field.value) {
	                    return _.object(ensureArray(scope.field.value));
	                }
	                return {};
	            }
	            function init_choices(selected) {

	                var options = [];

	                // push the choices into the options
	                if (scope.field.widget.choices && scope.field.widget.choices.length) {
	                    angular.forEach(scope.field.widget.choices, function (value, index, obj) {
	                        if (value[0] === '') {
	                            // blank strings for default none choices mess with
	                            // fields that offer false as an option.
	                            value[0] = null;
	                        }

	                        var item = makeItem(value[0], value[1], value[0] in selected);

	                        options.push(item);
	                    });
	                }
	                scope.selectOptions = options;
	            }
	            function multipleSelect() {
	                var values = [];
	                angular.forEach(scope.tempOutputList, function (obj) {
	                    values.push(obj.id);
	                });
	                scope.regionObject.object[scope.field.field_name] = values;
	            }
	            function singleSelect() {
	                scope.regionObject.object[scope.field.field_name] = scope.tempOutputList.length ? scope.tempOutputList[0].id : null;
	            }
	            function singleSelectModeReverseWatch(newVal, oldVal) {
	                _.forEach(scope.selectOptions, function (obj) {
	                    obj.selected = obj.id == newVal;
	                });
	            }

	            scope.selectOptions = [];
	            scope.tempOutputList = [];
	            init();

	            scope.$watch('tempOutputList', attrs.selectionMode && attrs.selectionMode == 'single' ? callWhenDifferent(singleSelect) : callWhenDifferent(multipleSelect));

	            scope.$watchCollection('field.widget.choices', callWhenDifferent(function () {
	                init_choices(init_values());
	            }));

	            // we only need this functionality for single selects. i.e. builder
	            // watches the regionObject.object[field_name] to keep
	            // selects in sync with programmatic changes.
	            if (attrs.selectionMode && attrs.selectionMode == 'single') {
	                scope.$watch(function () {
	                    return scope.regionObject.object[scope.field.field_name];
	                }, callWhenDifferent(singleSelectModeReverseWatch));
	            }

	            function ensureArray(arr) {
	                return angular.isArray(arr) ? arr : [arr];
	            }
	            function isChoiceDisabled(id) {
	                if (scope.regionObject.helpers.locked_company_ids) {
	                    return scope.regionObject.helpers.locked_company_ids.indexOf(id) > -1;
	                }
	                return false;
	            }
	            function makeItem(value, text, selected) {
	                var isDisabled = isChoiceDisabled(value);

	                if (isDisabled) text = '<i class="fa fa-lock"></i> ' + text;

	                return {
	                    id: value,
	                    text: text,
	                    selected: selected,
	                    checkboxDisabled: isDisabled
	                };
	            }
	        }
	    };
	}).directive('duallistHelper', function () {
	    return {
	        restrict: 'A',
	        link: function link(scope, element, attrs) {

	            /*
	                Duallists are generally used by fields that get auto populated on the backend.
	                  So lets watch for changes whenever that happens and re-init everything.
	             */
	            scope.$watch(function () {
	                return scope.field;
	            }, function () {
	                init();
	            });

	            function init() {
	                init_choices(init_values());
	            }
	            function init_values() {

	                // check the region object to ensure we have no value.
	                if (!scope.field.value) {
	                    scope.field.value = scope.regionObject.object[scope.field.field_name];
	                }

	                if (scope.field.value) {
	                    return _.object(ensureArray(scope.field.value));
	                }
	                return {};
	            }
	            function init_choices(selected) {

	                var options = [];

	                // push the choices into the options
	                if (scope.field.widget.choices && scope.field.widget.choices.length) {
	                    angular.forEach(scope.field.widget.choices, function (value, index, obj) {
	                        if (value[0] === '') {
	                            // blank strings for default none choices mess with
	                            // fields that offer false as an option.
	                            value[0] = null;
	                        }

	                        var item = makeItem(value[0], value[1]);

	                        if (value[0] in selected) {
	                            scope.tempOutputList.push(item);
	                        } else {
	                            options.push(item);
	                        }
	                    });
	                }
	                scope.selectOptions = options;
	            }
	            function multipleSelect() {
	                var values = [];
	                angular.forEach(scope.tempOutputList, function (obj) {
	                    values.push(obj.id);
	                });
	                scope.regionObject.object[scope.field.field_name] = values;
	            }

	            scope.selectOptions = [];
	            scope.tempOutputList = [];
	            // init();

	            scope.$watch('tempOutputList', callWhenDifferent(multipleSelect), true);

	            function ensureArray(arr) {
	                return angular.isArray(arr) ? arr : [arr];
	            }
	            function isChoiceDisabled(id) {
	                if (scope.regionObject.helpers.locked_company_ids) {
	                    return scope.regionObject.helpers.locked_company_ids.indexOf(id) > -1;
	                }
	                return false;
	            }
	            function makeItem(value, text) {
	                var isDisabled = isChoiceDisabled(value);

	                if (isDisabled) text = '<i class="fa fa-lock"></i> ' + text;

	                return {
	                    id: value,
	                    text: text
	                    // selected: selected,
	                    // checkboxDisabled: isDisabled
	                };
	            }
	        }
	    };
	});

	angular.module('axis.fields.helpers.datepicker').directive('datepickerHelper', function () {
	    return {
	        restrict: 'A',
	        controller: function controller($scope) {
	            $scope.opened = false;
	            $scope.format = 'MM/dd/yyyy';
	            $scope.open = function ($event) {
	                $event.preventDefault();
	                $event.stopPropagation();
	                $scope.opened = true;
	            };
	            // FIXME: fix until angular-ui datepicker supports formatted output.
	            $scope.date = $scope.regionObject.object[$scope.field.field_name];
	            $scope.$watch('date', function (newVal, oldVal) {
	                if (newVal !== oldVal) {
	                    var value;
	                    try {
	                        var dateArr = [newVal.getFullYear().toString(), (newVal.getMonth() + 1).toString(), newVal.getDate().toString()];
	                        value = dateArr.join('-');
	                    } catch (e) {
	                        value = newVal;
	                    }
	                    $scope.regionObject.object[$scope.field.field_name] = value;
	                }
	            });
	        }
	    };
	});

	angular.module('axis.fields.helpers').directive('nonNegativeNumber', function () {
	    return buildRegexDirective(/[^\d.]/g);
	}).directive('nonNegativeWholeNumber', function () {
	    return buildRegexDirective(/[^\d]/g);
	}).directive('timepickerHelper', function () {
	    return {
	        restrict: 'A',
	        controller: function controller($scope) {
	            if ($scope.regionObject.object[$scope.field.field_name]) {
	                $scope.time = moment($scope.regionObject.object[$scope.field.field_name], 'HH:mm:ss');
	            } else {
	                $scope.time = new Date();
	                $scope.regionObject.object[$scope.field.field_name] = $scope.time.getHours() + ':' + $scope.time.getMinutes();
	            }

	            $scope.$watch('time', function (newVal, oldVal) {
	                if (newVal !== oldVal) {
	                    if (newVal) {
	                        $scope.regionObject.object[$scope.field.field_name] = newVal.getHours() + ':' + newVal.getMinutes();
	                    } else {
	                        $scope.regionObject.object[$scope.field.field_name] = newVal;
	                    }
	                }
	            });
	        }
	    };
	});

	function buildRegexDirective(regex) {
	    return {
	        restrict: 'A',
	        require: '?ngModel',
	        link: function link(scope, element, attrs, ngModel) {
	            if (!ngModel) return;

	            ngModel.$parsers.push(function (val) {
	                var clean = val ? val.replace(regex, '') : null;

	                if (clean != val) {
	                    ngModel.$setViewValue(clean);
	                    ngModel.$render();
	                }
	                return clean;
	            });
	        }
	    };
	}

	function callWhenDifferent(fn) {
	    return function (newVal, oldVal) {
	        if (newVal != oldVal) {
	            fn(newVal, oldVal);
	        }
	    };
	}
	function removeWatcherWhenAny(scope, watch, execute) {
	    var unWatcher;
	    unWatcher = scope.$watch(watch, function (newVal, oldVal) {
	        if (_.any([newVal, oldVal])) {
	            unWatcher();
	            execute();
	        }
	    });
	}
	function waitForElement(region) {
	    return function () {
	        // Make sure we always default to undefined so we don't
	        // accidentally trigger the watcher to be executed.
	        try {
	            return region.$element.find('.fileinput').length || undefined;
	        } catch (e) {
	            return undefined;
	        }
	    };
	}
	function markFileAsExisting(region) {
	    return function () {
	        region.$element.find('.fileinput.fileinput-new').removeClass('fileinput-new').addClass('fileinput-exists');
	    };
	}

/***/ }),

/***/ 147:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.fields.field', []);
	angular.module('axis.fields.helpers', ['axis.fields.field', 'axis.fields.helpers.tab', 'axis.fields.helpers.fileField', 'axis.fields.helpers.select2', 'axis.fields.helpers.multiSelect', 'axis.fields.helpers.datepicker']);

	angular.module('axis.fields.helpers.tab', ['axis.services.TabService', 'ui.bootstrap']);
	angular.module('axis.fields.helpers.fileField', []);
	angular.module('axis.fields.helpers.select', []);
	angular.module('axis.fields.helpers.select2', ['ui.select']);
	angular.module('axis.fields.helpers.multiSelect', ['multi-select']);
	angular.module('axis.fields.helpers.datepicker', ['ui.bootstrap.datepicker']);

	angular.module('axis.fields', ['axis.fields.field', 'axis.fields.helpers']);

/***/ }),

/***/ 148:
/***/ (function(module, exports) {

	/**
	 * Examine View Angular Filters.
	 */

	'use strict';

	angular.module('axis.filters', []).filter('humanize', function () {
	    function ucwords(text) {
	        return text.replace(/^([a-z])|\s+([a-z])/g, function ($1) {
	            return $1.toUpperCase();
	        });
	    }

	    function breakup(text, separator) {
	        return text.replace(/[A-Z]/g, function (match) {
	            return separator + match;
	        });
	    }

	    function humanize(value) {
	        return ucwords(breakup(value, ' ').split('_').join(' '));
	    }

	    return function (text) {
	        if (angular.isString(text)) {
	            return humanize(text);
	        } else {
	            return text;
	        }
	    };
	}).filter('selectFilter', function () {
	    return function selectFilter(input, searchText, AND_OR) {

	        if (!input || input.length === 0) return input;

	        if (input[0].id === null && input[0].text == 'No Results...') return input;

	        var returnArray = [];

	        var splitText = searchText.toLowerCase().split(/\s+/);

	        var regAnd = '(?=.*' + splitText.join(')(?=.*') + ')';

	        var regOr = searchText.toLowerCase().replace(/\s+/g, '|');

	        var re = new RegExp(AND_OR == 'AND' ? regAnd : regOr, 'i');

	        for (var i = 0; i < input.length; i++) {
	            if (re.test(input[i].text)) returnArray.push(input[i]);
	        }

	        return returnArray;
	    };
	}).filter('truncateAtBreak', function () {
	    function simplifyhtml(text) {
	        return text.split(/<br( ?\/)?>/g, 1)[0].replace(/<[^>]+>/g, '');
	    }

	    return function (text) {
	        if (angular.isString(text)) {
	            return simplifyhtml(text);
	        } else {
	            return text;
	        }
	    };
	}).filter('filename', function () {
	    return function (text) {
	        if (angular.isString(text)) {
	            return text.replace(/^https?:\/\/.*?\/([^/]+)\?.*$/, '$1');
	        }
	        return text;
	    };
	}).filter('axisDurationFormat', function () {
	    function axisDurationFormatFilter(value, format, suffix, precision) {
	        if (typeof value === 'undefined' || value === null) {
	            return '';
	        }
	        precision = precision || 0;

	        return moment.duration(value, format).format(suffix, precision);
	    }

	    return axisDurationFormatFilter;
	}).filter('trustAsHtml', function ($sce) {
	    return function (input) {
	        input = input || '';
	        return $sce.trustAsHtml(input);
	    };
	});

/***/ }),

/***/ 149:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.region.helpers').directive('nonFieldErrors', function () {
	    /**
	     * Place this anywhere there is access to the regionObject and it will display any
	     * non_field_errors returned by the server.
	     */
	    return {
	        restrict: 'EA',
	        replace: true,
	        link: function link(scope, element, attrs) {
	            /**
	            * FIXME: This is a hack because we don't allow differentiation in how we deal with different regions' errors.
	            * Bob brough up that when there is an error for the primary region, and it shows up at the top, it's not always
	            * apparent to the user. The current solution is to pop the scroll position to the top of the page so the error
	            * is in sight. A more correct solution would be to better utilize the MessagingService. Currently we can't mark
	            * messages for notifications, and it would be overkill to send every error recieved there.
	            * So until we can retool this. Window scrolling it is.
	            * NOTE: this is only happening for the primary region currently.
	            */
	            scope.$watch('regionObject.errors.non_field_errors', function (newVal, oldVal) {
	                if (!newVal) return;
	                if (scope.regionSet.isPrimaryRegion) {
	                    $(document).scrollTop(0);
	                }
	            });
	        },
	        template: '<ul class="text-danger" ng-if="regionObject.errors.non_field_errors">\n    <li ng-repeat="message in regionObject.errors.non_field_errors track by $index" ng-bind-html="message | trustAsHtml"></li>\n</ul>'
	    };
	}).directive('ngIncludeReplace', function () {
	    return {
	        restrict: 'A',
	        link: function link(scope, element, attrs) {
	            element.replaceWith(element.children());
	        }
	    };
	}).directive('loadingSpinner', function () {
	    return {
	        restrict: 'E',
	        replace: true,
	        template: '<div class="examine-spinner">\n    <i class="fa fa-spinner fa-lg fa-spin"></i>\n    <div class="loading-message"> Please Wait</div>\n</div>'
	    };
	}).directive('axisRegionHeading', function () {
	    return {
	        restrict: 'EA',
	        transclude: true, // Grab the contents to be used as the heading
	        template: '', // In effect remove this element
	        replace: true,
	        require: '^axisSingleRegion',
	        link: function link(scope, element, attr, parentController, transclude) {
	            parentController.setHeadingElement(transclude(scope, function () {}));
	        }
	    };
	}).directive('axisTransclude', function () {
	    return {
	        restrict: 'EA',
	        require: '^?axisSingleRegion',
	        link: function link(scope, element, attrs, parentController) {
	            if (parentController) parentController.setHeadingDestination(element);
	        }
	    };
	}).directive('sidetabButton', function ($timeout) {
	    return {
	        restrict: 'A',
	        require: '^axisRegionSet',
	        link: function link(scope, element, attrs, controller) {
	            var shouldActivate = scope.$index === 0;
	            if (!scope.regionObject.object.id) {
	                shouldActivate = true;
	            }
	            if (shouldActivate) {
	                $timeout(function () {
	                    element.find('a').tab('show');
	                }, 0);
	            }
	            element.on('$destroy', function () {
	                var tagName = element.prop('tagName').toLowerCase();
	                var select = element.parent().find(tagName + '[ng-repeat]:not(.active)').first();
	                select.find('a').tab('show');
	            });
	        }
	    };
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
	.directive('hideActionStrip', function () {
	    return {
	        restrict: 'A',
	        require: ['^?axisSingleRegion', '^?axisRegionSet'],
	        link: function link(scope, element, attrs, controllers) {
	            // Action Strip looks up to the regionset so we don't have to add
	            // this directive in every single template.
	            (controllers[0] || controllers[1]).hideActionStrip = true;
	            // Also add it to the region controller, just for good measure.
	            scope.hideActionStrip = true;
	        }
	    };
	}).directive('readMore', function () {
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
	        link: function link(scope, elem, attr, ctrl, transclude) {
	            var moreText = angular.isUndefined(scope.moreText) ? ' <a class="read-more">Read More...</a>' : ' <a class="read-more">' + scope.moreText + '</a>',
	                lessText = angular.isUndefined(scope.lessText) ? ' <a class="read-less">Less ^</a>' : ' <a class="read-less">' + scope.lessText + '</a>',
	                ellipsis = angular.isUndefined(scope.ellipsis) ? '' : scope.ellipsis,
	                limit = angular.isUndefined(scope.limit) ? 150 : scope.limit;

	            attr.$observe('content', function (str) {
	                readmore(str);
	            });

	            transclude(scope.$parent, function (clone, scope) {
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

	                if (countBy === 'words') {
	                    // Count words

	                    foundWords = text.split(/\s+/);

	                    if (foundWords.length > limit) {
	                        text = foundWords.slice(0, limit).join(' ') + ellipsis;
	                        more = foundWords.slice(limit, count).join(' ');
	                        markup = text + moreText + '<span class="more-text">' + more + lessText + '</span>';
	                    }
	                } else {
	                    // Count characters

	                    if (count > limit) {
	                        text = orig.slice(0, limit) + ellipsis;
	                        more = orig.slice(limit, count);
	                        markup = text + moreText + '<span class="more-text">' + more + lessText + '</span>';
	                    }
	                }

	                elem.append(markup);
	                elem.find('.read-more').on('click', function () {
	                    $(this).hide();
	                    elem.find('.more-text').addClass('show').slideDown();
	                });
	                elem.find('.read-less').on('click', function () {
	                    elem.find('.read-more').show();
	                    elem.find('.more-text').hide().removeClass('show');
	                });
	            }
	        }
	    };
	});

/***/ }),

/***/ 150:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.region.regionSet', ['axis.region.region', 'axis.services.RegionService', 'axis.services.HttpQueue']);
	angular.module('axis.region.regionSetSideTabs', ['axis.region.regionSet']);
	angular.module('axis.region.singleRegion', ['axis.region.region', 'axis.services.RegionService', 'axis.services.UrlService', 'axis.services.Actions', 'axis.services.HttpQueue']);
	angular.module('axis.region.region', ['axis.services.Actions']);
	angular.module('axis.region.helpers', []);

	angular.module('axis.region', ['axis.region.regionSet', 'axis.region.regionSetSideTabs', 'axis.region.singleRegion', 'axis.region.region', 'axis.region.helpers']);

/***/ }),

/***/ 151:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.region.region').controller('RegionController', function ($rootScope, $scope, $timeout, $q, $log, Actions, RegionService, ExamineSettings) {
	    var ctrl = this;

	    ctrl.getRegionObject = function () {
	        return $scope.regionObject;
	    };
	    ctrl.children = [];
	    ctrl.axisFields = {};
	    ctrl.activeState = $scope.regionObject.default_instruction || 'default';
	    // ctrl.processing = null;
	    ctrl.processingInstructions = [];
	    ctrl.hasEdited = false;

	    ctrl.error = error; // what type of error?
	    ctrl.reset = reset; // TODO: better name.
	    ctrl.editing = editing;
	    ctrl.success = success; // what type of success?
	    ctrl.isProcessing = isProcessing;
	    ctrl.addProcessingStatus = addProcessingStatus;
	    ctrl.clearProcessingStatus = clearProcessingStatus;
	    ctrl.removeRegion = getRemoveRegion();
	    ctrl.handleAction = handleAction;
	    ctrl.shouldShowCommitAction = shouldShowCommitAction;
	    ctrl.isCommitAction = isCommitAction;

	    $rootScope.$on('reloadRegions', reloadRegionListener);

	    init();

	    function editing() {
	        var editing = ctrl.activeState === 'edit';
	        ctrl.hasEdited = ctrl.hasEdited || editing;
	        return editing;
	    }
	    function handleAction(action) {
	        return Actions.callMethod(action, $scope.regionObject).then(getActionCallback(action));
	    }
	    function reset() {
	        angular.copy($scope.regionObject._masterForm, $scope.regionObject.object);
	    }
	    function success(message) {
	        $scope.regionObject.errors = {};
	        $scope.timedClass('success');
	        $scope.regionSet.regionSuccess(message, ctrl);
	    }
	    function error(message) {
	        if (!angular.isObject(message) || angular.isArray(message)) {
	            message = { 'non_field_errors': angular.isArray(message) ? message : [message] };
	        }
	        if (angular.isDefined(message.__all__)) message = { 'non_field_errors': message.__all__ };

	        angular.copy(message, $scope.regionObject.errors);
	        $scope.timedClass('error');
	        $scope.regionSet.regionError(message, ctrl);
	    }
	    function reloadRegionListener(event, firingType) {
	        if ($scope.regionObject.type_name != firingType && !$scope.regionSet.processing) {
	            Actions.callMethod('reload', $scope.regionObject);
	        }
	    }
	    function isProcessing(methodName) {
	        if (methodName === undefined) {
	            return ctrl.processingInstructions.length > 0;
	        } else if (_.isArray(methodName)) {
	            // Dropdown items
	            var containsInstruction = false;
	            _.map(methodName, function (itemMethodName) {
	                if (itemMethodName !== null && itemMethodName.instruction) {
	                    itemMethodName = itemMethodName.instruction;
	                }
	                if (itemMethodName !== null && _.contains(ctrl.processingInstructions, itemMethodName)) {
	                    containsInstruction = true;
	                }
	            });
	            return containsInstruction;
	        }
	        return _.contains(ctrl.processingInstructions, methodName);
	    }
	    function addProcessingStatus(methodName) {
	        // if (methodName === undefined){
	        //     methodName = true;  // generic flag
	        // }
	        $log.debug('Region busy status added', methodName, 'to', ctrl.processingInstructions);
	        ctrl.processingInstructions.push(methodName);
	        ctrl.processing = methodName;
	    }
	    function clearProcessingStatus(methodName) {
	        if (methodName === undefined) {
	            ctrl.processingInstructions = [];
	            $log.debug('Region cleared ALL');
	        } else {
	            _.pull(ctrl.processingInstructions, methodName);
	            $log.debug('Region cleared', methodName, '(Remaining:', ctrl.processingInstructions, ')');
	        }
	    }
	    function shouldShowCommitAction() {
	        var primaryRegionObject = RegionService.getRegionFromTypeName(ExamineSettings.page);
	        if (primaryRegionObject !== undefined) {
	            if (ctrl.type_name == primaryRegionObject.type_name) {
	                return true;
	            }
	            return primaryRegionObject.object.id !== null;
	        }
	        return true;
	    }
	    function isCommitAction(actionObject) {
	        var instruction = angular.isObject(actionObject) ? actionObject.instruction : actionObject;
	        return instruction === $scope.regionObject.commit_instruction;
	    }

	    // Internal Methods
	    function init() {
	        angular.extend(ctrl, $scope.regionObject.additionalScope);
	        ctrl.type_name = $scope.regionObject.type_name;
	        clearProcessingStatus();
	        initRegionObject();
	        liftInitialFieldValues();
	    }
	    function initRegionObject() {
	        $scope.regionObject.errors = {};
	        $scope.regionObject.controller = ctrl;
	        $scope.regionObject._masterForm = angular.copy($scope.regionObject.object);
	        $scope.regionObject.object_endpoint_pattern = $scope.options.object_endpoint_pattern;
	    }
	    function liftInitialFieldValues() {
	        angular.forEach($scope.regionObject.fields, function (field) {
	            if (field.value) {
	                $scope.regionObject.object[field.field_name] = field.value;
	            }
	        });
	    }
	    function saveChildren() {
	        var childrenSaves = [];

	        angular.forEach(ctrl.children, function (child, index) {
	            if (child.commit_instruction && child.controller.editing() && !child.passive_machinery) {
	                var save = Actions.callMethod(child.commit_instruction, child).then(function () {
	                    Actions.callMethod('exit', child);
	                })['finally'](function () {
	                    // clear the commit instruction in case it failed
	                    child.controller.clearProcessingStatus(child.commit_instruction);
	                    // clear the waiting status that may have been added through saveAll
	                    child.controller.clearProcessingStatus('waiting');
	                });
	                childrenSaves.push(save);
	            }
	        });

	        return $q.all(childrenSaves);
	    }
	    function getActionCallback(action) {
	        // Decides if it needs to save the children first, then return to default state
	        var fn = angular.identity;
	        var saveAction = ctrl.isCommitAction(action);

	        if (action && saveAction && ctrl.children.length) {
	            fn = saveChildren;
	        }

	        return function returnToDefault() {
	            return $q.when(fn()).then(function () {
	                if (saveAction) {
	                    return Actions.callMethod('exit', $scope.regionObject);
	                }
	            });
	            // TODO: handle errors for regions hereish?
	        };
	    }
	    function getRemoveRegion() {
	        return $scope.regionSet.removeRegion || angular.noop;
	    }
	}).directive('axisRegion', function ($compile, $q, HttpQueue, $timeout, RegionService) {
	    /**
	     * Used inside a <axis-single-region/> or <axis-region-set/> for
	     * rendering a detail and form section of a region.
	     *
	     * If not using default template, classes `.detail-content` and `.form-content` are
	     * used to determine where to put respective templates.
	     *
	     * @requires: regionObject
	     * @example:
	     *      <axis-region region-object='{... object ...}'>
	     *          <div class='detail-content'></div>
	     *          <div class='form-content'></div>
	     *      </axis-region>
	     */
	    return {
	        restrict: 'EA',
	        require: '^?axisSingleRegion',
	        scope: true,
	        controller: 'RegionController',
	        controllerAs: 'region',
	        template: '<span ng-include src="regionObject.region_template_url" ng-if="regionObject.region_template_url && !regionSet.region_template_url" ng-include-replace></span>',
	        link: {
	            pre: function preLink(scope, element, attrs, parentController) {
	                if (parentController) {
	                    parentController.setHeadingScope(scope);
	                }
	            },
	            post: function postLink(scope, element, attrs, parentController) {
	                scope.regionObject.$element = element;
	                scope.regionObject.parentRegionSet = scope.regionSet;
	                element.attr('type-name', scope.regionObject.type_name);
	                if (parentController) {
	                    parentController.compileHeading();
	                }

	                scope.timedClass = function (klass, duration) {
	                    element.addClass(klass);
	                    $timeout(function () {
	                        element.removeClass(klass);
	                    }, duration || 3000);
	                };

	                if (scope.regionObject.parentRegionObject && !scope.skipChildRegistration) {
	                    RegionService.registerChildRegion(scope.regionObject.parentRegionObject, scope.regionObject);
	                }
	            }
	        }
	    };
	}).directive('detailContent', function ($compile, HttpQueue) {
	    return {
	        restrict: 'EA',
	        link: function link(scope, element, attrs) {
	            var unwatch;
	            unwatch = scope.$watch(function () {
	                return scope.region.editing();
	            }, function (val) {
	                if (!val) {
	                    HttpQueue.addTemplateRequest(scope.regionObject.detail_template_url).then(function (template) {
	                        var method = attrs.detailContent == 'replace' ? 'replaceWith' : 'html';
	                        element[method]($compile(template)(scope));
	                        scope.detailTemplateLoaded(scope.regionObject, element);
	                        unwatch();
	                    });
	                }
	            });
	        }
	    };
	}).directive('formContent', function ($compile, HttpQueue) {
	    return {
	        restrict: 'EA',
	        link: function link(scope, element, attrs) {
	            var method = attrs.formContent == 'replace' ? 'replaceWith' : 'html';
	            var compiled = null;

	            function _compile() {
	                return HttpQueue.addTemplateRequest(scope.regionObject.form_template_url).then(function (template) {
	                    if (compiled === null) {
	                        compiled = $compile(template);
	                    }
	                });
	            }

	            if (scope.regionObject.form_template_url) {
	                var compileQ = _compile();
	                var unwatch;
	                unwatch = scope.$watch(function () {
	                    return scope.region.editing();
	                }, function (val) {
	                    if (val) {
	                        compileQ.then(function () {
	                            element[method](compiled(scope));
	                            scope.formTemplateLoaded(scope.regionObject, element);
	                            unwatch();
	                        });
	                    }
	                });
	            }
	        }
	    };
	});

/***/ }),

/***/ 152:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.region.regionSet').controller('RegionSetController', function ($rootScope, $scope, $timeout, $compile, $log, HttpQueue, RegionService, Actions) {
	    /**
	     * NOTE: pieceLoaded() and isDoneLoading() use a counter because we want to know when a
	     *       regions compilation process is done, including loading all necessary templates.
	     *       The Region is added to ctrl.regions long before anything is finished loading.
	     */
	    var ctrl = this;

	    var fetched_endpoints = [];

	    ctrl.regions = [];
	    ctrl.processing = false;
	    ctrl.regionsErrors = {};
	    ctrl.initialLoad = false;
	    ctrl.eventPrefix = 'RegionSetLoaded:';
	    ctrl.detailTemplatesCount = 0;
	    ctrl.formTemplatesCount = 0;
	    ctrl.parentRegionObject = $scope.$parent.regionObject; // Try reading outside isolated scope

	    ctrl.addRegion = addRegion;
	    ctrl.hotUpdate = hotUpdate;
	    ctrl.regionError = regionError;
	    ctrl.removeRegion = removeRegion;
	    ctrl.regionSuccess = regionSuccess;
	    ctrl.isDoneLoading = isDoneLoading;
	    ctrl.fetchNewRegion = fetchNewRegion;
	    ctrl.getRegionCount = getRegionCount;
	    ctrl.getRegion = getRegion;
	    ctrl.isFull = isFull;

	    // CHILD API
	    $scope.formTemplateLoaded = formTemplateLoaded;
	    $scope.detailTemplateLoaded = detailTemplateLoaded;

	    init();

	    function addRegion(region) {
	        ctrl.regions.push(RegionService.addRegion(initRegionObject(region)));
	        pieceLoaded();
	        return region;
	    }
	    function removeRegion(region) {
	        var index = ctrl.regions.indexOf(region);
	        ctrl.regions.splice(index, 1);
	        if (ctrl.parentRegionObject) {
	            var parentIndex = ctrl.parentRegionObject.controller.children.indexOf(region);
	            ctrl.parentRegionObject.controller.children.splice(parentIndex, 1);
	        }
	    }
	    function fetchNewRegion(additionalScope) {
	        if (isFull()) {
	            return;
	        }
	        ctrl.processing = true;
	        var depsObject = { region_dependencies: ctrl.region_dependencies, object: {} };
	        return Actions.utils.resolveDependencies(depsObject, false).then(function (context) {
	            return Actions.utils.formatUrl(ctrl.new_region_url, context.object, ctrl.type_name);
	        }).then(function (url) {
	            return HttpQueue.addObjectRequest(url, additionalScope);
	        }).then(ctrl.addRegion)['finally'](function () {
	            ctrl.processing = false;
	        });
	    }
	    function regionSuccess(message, region) {
	        ctrl.regionsErrors = {};
	        $rootScope.$broadcast(ctrl.event + ':success', region.getRegionObject(), ctrl.$element);
	    }
	    function regionError(errors, region) {
	        if (angular.isObject(errors)) {
	            angular.forEach(errors, function (value, key) {
	                if (angular.isUndefined(ctrl.regionsErrors[key])) ctrl.regionsErrors[key] = [];
	                if (angular.isArray(value)) {
	                    angular.forEach(value, function (err) {
	                        if (ctrl.regionsErrors[key].indexOf(err) == -1) ctrl.regionsErrors[key].push(err);
	                    });
	                } else {
	                    if (ctrl.regionsErrors[key].indexOf(value) == -1) ctrl.regionsErrors[key].push(value);
	                }
	            });
	        }
	        $rootScope.$broadcast(ctrl.event + ':error', region.getRegionObject(), ctrl.$element);
	    }
	    function detailTemplateLoaded(region, element) {
	        ctrl.detailTemplatesCount++;
	        $timeout(function () {
	            $rootScope.$broadcast(ctrl.event + ':detailTemplateLoaded', region, element);
	        });
	        pieceLoaded();
	    }
	    function formTemplateLoaded(region, element) {
	        ctrl.formTemplatesCount++;
	        $timeout(function () {
	            $rootScope.$broadcast(ctrl.event + ':formTemplateLoaded', region, element);
	        });
	        pieceLoaded();
	    }
	    function isDoneLoading() {
	        // Check >= because new additions will change the length of the regions, but not the initial
	        // endpoints.
	        var len = ctrl.endpoints.length;
	        var initialLoad = ctrl.regions.length >= len && (ctrl.detailTemplatesCount >= len || ctrl.formTemplatesCount >= len);

	        // once this is true we want to memoize it.
	        if (initialLoad) ctrl.isDoneLoading = function () {
	            return initialLoad;
	        };
	        return initialLoad;
	    }
	    function isBusy() {
	        var processingFlags = _.map(ctrl.regions, function (regionObject) {
	            return regionObject.controller.isProcessing();
	        });
	        return ctrl.processing || _.compact(processingFlags).length > 0;
	    }
	    function getRegionCount() {
	        return ctrl.regions.length;
	    }
	    function hotUpdate() {
	        $scope.$watch('options.endpoints', function (newVal, oldVal) {
	            if (!angular.equals(newVal, oldVal)) {
	                var obj = {
	                    region_dependencies: $scope.options.region_dependencies,
	                    object: {},
	                    parentRegionSet: {
	                        parentRegionObject: ctrl.parentRegionObject
	                    }
	                };
	                Actions.utils.resolveDependencies(obj, false).then(function (context) {
	                    angular.forEach(newVal, function (endpoint) {
	                        var url = Actions.utils.formatUrl(endpoint, context.object);
	                        if (fetched_endpoints.indexOf(url) == -1) {
	                            getRegion(url);
	                        }
	                    });
	                });
	            }
	        });
	    }
	    function isFull() {
	        if (ctrl.max_regions === null) {
	            return false;
	        }
	        return ctrl.regions.length >= ctrl.max_regions;
	    }

	    // Internal Methods
	    function init() {
	        errorCheck();
	        $scope.options.visible_fields = $scope.visibleFields || $scope.options.visible_fields;
	        angular.extend(ctrl, $scope.options);
	        ctrl.event = ctrl.eventPrefix + ctrl.type_name;
	        // trigger the check for everything is loaded
	        // if there is nothing to load.
	        ctrl.endpoints.length == 0 ? pieceLoaded() : getRegions();
	    }
	    function initRegionObject(region) {
	        region.region_dependencies = ctrl.region_dependencies;
	        if (ctrl.parentRegionObject) region.parentRegionObject = ctrl.parentRegionObject;
	        region.parentRegionController = ctrl;
	        return region;
	    }
	    function errorCheck() {
	        // some requirement checks first
	        if (angular.isUndefined($scope.options.endpoints)) {
	            throw new Error('RegionSets require endpoints to be defined');
	        }

	        if (angular.isUndefined($scope.options.new_region_url)) {
	            $log.warn('RegionSet does not have new_region_endpoint defined');
	        }

	        if (angular.isDefined($scope.visibleFields) && angular.isDefined($scope.options.visible_fields)) {
	            $log.warn('RegionSet: visible_fields is defined in both the element and options.');
	        } else if (angular.isUndefined($scope.visibleFields) && angular.isUndefined($scope.options.visible_fields)) {
	            $log.warn('RegionSet: visible_fields is not defined on either the element or options.');
	        }
	    }
	    function pieceLoaded() {
	        // TODO: still not happy with this name.
	        // Gets called when the following are loaded
	        //  [regions, detail templates, form templates]
	        // So we can fire the event as soon as possible.
	        if (isDoneLoading()) {
	            ctrl.processing = false;
	            $timeout(function () {
	                $rootScope.$broadcast('RegionLoaded', ctrl, ctrl.$element);
	                $rootScope.$broadcast(ctrl.event, ctrl.regions, ctrl.$element);
	            });
	        }
	    }
	    function getRegions() {
	        var obj = {
	            region_dependencies: $scope.options.region_dependencies,
	            object: {},
	            parentRegionSet: {
	                parentRegionObject: ctrl.parentRegionObject
	            }
	        };
	        Actions.utils.resolveDependencies(obj, false).then(function (context) {
	            angular.forEach(ctrl.endpoints, function (endpoint) {
	                var url = Actions.utils.formatUrl(endpoint, context.object);
	                getRegion(url);
	            });
	        });
	    }
	    function getRegion(url) {
	        fetched_endpoints.push(url);
	        HttpQueue.addObjectRequest(url).then(ctrl.addRegion);
	    }
	}).directive('axisRegionSet', function ($q, HttpQueue) {
	    /**
	     * Used in Formset type situations.
	     *
	     * In the region template make <axis-region/> by ngRepeating over
	     * `scope.regions` and passing the object.
	     *
	     * @example
	     *  <axis-region region-object='object' ng-repeat='object in regions' />
	     */
	    return {
	        restrict: 'E',
	        scope: {
	            options: '=',
	            visibleFields: '=?'
	        },
	        controller: 'RegionSetController',
	        controllerAs: 'regionSet',
	        template: '<div class="region-set" ng-include src="regionSet.regionset_template_url"></div>',
	        link: function link(scope, element, attrs) {
	            scope.regionSet.$element = element;

	            if (angular.isDefined(attrs.hotUpdate)) {
	                scope.regionSet.hotUpdate();
	            }

	            if (angular.isDefined(attrs.skipChildRegistration)) {
	                scope.skipChildRegistration = scope.$eval(attrs.skipChildRegistration);
	            }
	        }
	    };
	}).directive('regionSetNonFieldErrors', function ($sce) {
	    return {
	        restrict: 'EA',
	        template: '<ul class="text-danger" ng-if="regionSet.regionsErrors.non_field_errors"> <li ng-repeat="message in regionSet.regionsErrors.non_field_errors"><span ng-bind-html="message | trustAsHtml"></span></li> </ul>'
	    };
	});

/***/ }),

/***/ 153:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.region.singleRegion').controller('SingleRegionController', function ($rootScope, $scope, $timeout, $compile, $log, $location, RegionService, UrlService, Actions, HttpQueue) {
	    var ctrl = this;

	    //ctrl.region = {};  // just use $scope.regionObject
	    ctrl.region = $scope.regionObject;
	    ctrl.regionsErrors = {};
	    ctrl.processing = false;
	    ctrl.showLoader = true;
	    ctrl.eventPrefix = 'SingleRegionLoaded:';
	    ctrl.parentRegionObject = $scope.$parent.regionObject; // Try reading outside isolated scope
	    ctrl.isFormTemplateLoaded = false;
	    ctrl.isDetailTemplateLoaded = false;
	    ctrl.heading = {
	        destination: null,
	        element: null,
	        scope: null
	    };

	    ctrl.setRegion = setRegion; // Used in the directive
	    ctrl.regionError = regionError;
	    ctrl.regionSuccess = regionSuccess;
	    ctrl.isDoneLoading = isDoneLoading;
	    ctrl.compileHeading = compileHeading; // region directive postLink
	    ctrl.setHeadingScope = setHeadingScope; // region directive preLink
	    ctrl.setHeadingElement = setHeadingElement; // axisRegionHeading postLink
	    ctrl.primaryRegionWatcher = primaryRegionWatcher;
	    ctrl.setHeadingDestination = setHeadingDestination; // axisTransclude postLink
	    ctrl.getRegionCount = getRegionCount;

	    // CHILD API
	    $scope.isPrimaryRegion = false;
	    $scope.formTemplateLoaded = formTemplateLoaded;
	    $scope.detailTemplateLoaded = detailTemplateLoaded;
	    $scope.flipWatchedAttr = angular.noop; // reset in primaryRegionWatcher, called from region link.

	    init();

	    function setRegion(regionObject) {
	        ctrl.region_template_url = regionObject.region_template_url;
	        RegionService.addRegion(initRegionObject(regionObject));
	        pieceLoaded();
	    }
	    function setHeadingDestination(element) {
	        if (element && element.length && angular.isElement(element)) {
	            ctrl.heading.destination = element;
	        }
	    }
	    function setHeadingElement(element) {
	        if (element && element.length && angular.isElement(element)) {
	            ctrl.heading.element = element;
	        }
	    }
	    function setHeadingScope(scope) {
	        if (scope && !angular.equals({}, scope)) {
	            ctrl.heading.scope = scope;
	        }
	    }
	    function compileHeading() {
	        if (ctrl.heading.destination) {
	            ctrl.heading.destination.html($compile(ctrl.heading.element)(ctrl.heading.scope));
	        }
	    }
	    function primaryRegionWatcher(attr, flipAttr) {
	        /**
	         * The primary-region attr determines if this gets run.
	         *
	         * @param attr (string) - name of attribute to watch on regionObject.object
	         * @param flipAttr (string) - name of attribute to flip on $rootScope when attr changes
	         *
	         * We start out by assuming we're going to get a regionObject.
	         * The first time we're able to do a successful lookup on a region
	         * we set the `startsWithAttr` (may only be set to false) then move on.
	         * When we get an update to the watcher, we check for a true ID value, then ask
	         * if the regionObject started with it. If it did not start with it, change the url.
	         * If it had the ID from the beginning, back off and do nothing.
	         */

	        ctrl.isPrimaryRegion = true;
	        var startsWithAttr = true;
	        function watcher() {
	            // The regionObject may not be available. That's ok
	            try {
	                var thing = ctrl.region.object[attr];
	                if (startsWithAttr) startsWithAttr = !!thing;
	                return thing;
	            } catch (e) {
	                return undefined;
	            }
	        }
	        function changeUrl(newId) {
	            // Do the work to change the URL on a save.
	            var pathname = $location.pathname || location.pathname;
	            var creationPathsRe = /(add|enroll)/;
	            var url = undefined;
	            if (creationPathsRe.test(pathname)) {
	                url = pathname.replace(creationPathsRe, '/' + newId + '/');
	            } else {
	                url = '/' + ctrl.region.type_name + '/' + newId + '/';
	            }

	            UrlService.setUpdatedLink(url);
	            if (ctrl.region.helpers.page_title) {
	                document.title = ctrl.region.helpers.page_title;
	            }
	            // TODO: is there a reason for this to be here anymore?
	            // now that we have all the registering function in {type}/examine.js?
	            //$rootScope.$broadcast('reloadRegions', ctrl.region.type_name);
	        }
	        function flipWatchedAttr() {
	            // Allows nested dotted access by string off of rootScope. Before the assumption was that
	            // `$rootScope.creating` and `$rootScope.examineApp.creating` were the same reference.
	            // They are not, so we have to allow for a dotted string lookup.
	            flipAttr.split('.').reduce(function (old, curr, i, arr) {
	                return i + 1 == arr.length ? old[curr] = !old[curr] : old[curr];
	            }, $rootScope);
	        }

	        var unwatch = $scope.$watch(watcher, function (newId) {
	            if (newId) {
	                if (!startsWithAttr) {
	                    changeUrl(newId);
	                    if (flipAttr) {
	                        $timeout(function () {
	                            flipWatchedAttr();
	                        }, 0);
	                    }
	                }
	                unwatch();
	            }
	        });
	    }
	    function regionSuccess() {
	        $rootScope.$broadcast(ctrl.event + ':success', ctrl.region, ctrl.$element);
	    }
	    function regionError(errors) {
	        if (angular.isObject(errors)) {
	            angular.forEach(errors, function (value, key) {
	                if (angular.isUndefined(ctrl.regionsErrors[key])) ctrl.regionsErrors[key] = [];
	                if (angular.isArray(value)) {
	                    angular.forEach(value, function (err) {
	                        if (ctrl.regionsErrors[key].indexOf(err) == -1) ctrl.regionsErrors[key].push(err);
	                    });
	                } else {
	                    if (ctrl.regionsErrors[key].indexOf(value) == -1) ctrl.regionsErrors[key].push(value);
	                }
	            });
	        }
	        $rootScope.$broadcast(ctrl.event + ':error', ctrl.region, ctrl.$element);
	    }
	    function detailTemplateLoaded() {
	        ctrl.isDetailTemplateLoaded = true;
	        $timeout(function () {
	            $rootScope.$broadcast(ctrl.event + ':detailTemplateLoaded', ctrl.region, ctrl.$element);
	        }, 0);
	        pieceLoaded();
	    }
	    function formTemplateLoaded() {
	        ctrl.isFormTemplateLoaded = true;
	        $timeout(function () {
	            $rootScope.$broadcast(ctrl.event + ':formTemplateLoaded', ctrl.region, ctrl.$element);
	        }, 0);
	        pieceLoaded();
	    }
	    function isDoneLoading() {
	        var loaded = ctrl.region.type_name && (ctrl.isFormTemplateLoaded || ctrl.isDetailTemplateLoaded);
	        if (loaded) ctrl.isDoneLoading = function () {
	            return loaded;
	        };
	        return loaded;
	    }
	    function isBusy() {
	        return ctrl.processing || ctrl.region.controller.isProcessing();
	    }
	    function getRegionCount() {
	        return 1;
	    }

	    // Internal Methods
	    function init() {
	        errorCheck();
	        $scope.options.visible_fields = $scope.visibleFields || $scope.options.visible_fields;
	        angular.extend(ctrl, $scope.options);
	        ctrl.event = ctrl.eventPrefix + ctrl.type_name;
	        getRegionObject();
	    }
	    function initRegionObject(region) {
	        region.region_dependencies = $scope.options.region_dependencies;
	        if (ctrl.parentRegionObject) region.parentRegionObject = ctrl.parentRegionObject;
	        if (region.region_template_url) delete region.region_template_url;

	        // NOTE: this assignment of $scope.regionObject is important
	        // this is the how nested <region> directive gets access to the regionObject.
	        ctrl.region = $scope.regionObject = region;
	        return ctrl.region;
	    }
	    function errorCheck() {
	        if (angular.isDefined($scope.visibleFields) && angular.isDefined($scope.options.visible_fields)) {
	            $log.warn('RegionSet: visible_fields is defined in both the element and options.');
	        } else if (angular.isUndefined($scope.visibleFields) && angular.isUndefined($scope.options.visible_fields)) {
	            $log.warn('RegionSet: visible_fields is not defined on either the element or options.');
	        }
	    }
	    function pieceLoaded() {
	        if (isDoneLoading()) {
	            ctrl.processing = false;
	            ctrl.showLoader = false;
	            $timeout(function () {
	                $rootScope.$broadcast('RegionLoaded', ctrl, ctrl.$element);
	                $rootScope.$broadcast(ctrl.event, ctrl.region, ctrl.$element);
	            }, 0);
	        }
	    }
	    function getRegionObjectUrl(context) {
	        var region_endpoint_pattern = ctrl.region ? ctrl.region.region_endpoint_pattern : $scope.options.region_endpoint_pattern;
	        var url = Actions.utils.formatUrl(region_endpoint_pattern, context.object);
	        // a non existent attr will be replaced with nothing causing two slashes
	        // to bump each other.
	        if (url.indexOf('//') > -1) {
	            // can comfortably take the first index of this list because we're in a single region.
	            url = Actions.utils.formatUrl($scope.options.endpoints[0], context.object);
	        }
	        return url;
	    }
	    function getRegionObject() {
	        var obj = {
	            region_dependencies: $scope.options.region_dependencies,
	            object: {},
	            parentRegionSet: {
	                parentRegionObject: ctrl.parentRegionObject
	            }
	        };
	        Actions.utils.resolveDependencies(obj, false).then(getRegionObjectUrl).then(HttpQueue.addObjectRequest).then(ctrl.setRegion);
	    }
	}).directive('axisSingleRegion', function (HttpQueue, Actions) {
	    /**
	     * Used in regular single form instance situations.
	     * Straps the region fetched onto `scope.regionObject`, pass that to <axis-region/>.
	     *
	     * @example
	     *  <axis-region region-object='regionObject' />
	     */
	    return {
	        restrict: 'E',
	        scope: {
	            options: '=',
	            visibleFields: '=?'
	        },
	        controller: 'SingleRegionController',
	        controllerAs: 'regionSet',
	        transclude: true,
	        template: '<loading-spinner ng-if="regionSet.showLoader"></loading-spinner><div ng-transclude/><div ng-include src="regionSet.region_template_url" axis-region region-object="regionObject" ng-if="regionObject"></div>',
	        link: function link(scope, element, attrs, controller, transclude) {
	            scope.regionSet.$element = element;
	            scope.regionSet.isPrimaryRegion = !!attrs.primaryRegion;
	            if (attrs.primaryRegion && scope.$root.creating) {
	                scope.regionSet.primaryRegionWatcher(attrs.primaryRegion, attrs.primaryRegionFlip);
	            }
	            if (attrs.skipChildRegistration) {
	                scope.skipChildRegistration = scope.$eval(attrs.skipChildRegistration);
	            }
	        }
	    };
	});

/***/ }),

/***/ 154:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 12/31/14.
	 */

	'use strict';

	angular.module('axis.services.Actions').factory('Actions', function ($rootScope, $log, $http, $modal, $q, $interpolate, $timeout, RegionService, Modal, HttpQueue) {
	    /**
	     * Provides the ability to add arbitrary amounts of pre and post method callbacks.
	     *
	     * NOTE: providing a string to 'addPreMethod' or 'addPostMethod'
	     *       will search the Action methods before erroring.
	     * NOTE: Action methods must return a promise. And resolves are expected to be
	     *       the regionObject.
	     *
	     * @Example Adding a geocode that calls save when it's done.
	     *
	     *      function geocode(args...){
	     *          //...
	     *      }
	     *
	     *      Actions.addMethod('geocode', geocode);
	     *      Actions.addPostMethod('geocode', 'save');
	     */

	    var fnMustBeStringOrFn = 'A function or string of a function must be passed to addPreMethod.';

	    var preMethods = {};
	    var postMethods = {};
	    var methods = {
	        edit: methodEdit,
	        save: methodSave,
	        saveAll: methodSaveAll,
	        cancel: methodCancel,
	        exit: methodExit,
	        destroy: methodDestroy,
	        saveAndReload: methodSaveAndReload,
	        'delete': methodDelete,
	        reload: methodReload,
	        validate: methodValidate,
	        editRelated: methodEditRelated
	    };
	    var utils = {
	        formatUrl: formatUrl,
	        deepExtend: deepExtend,
	        updateRegionObject: updateRegionObject,
	        resolveDependencies: _resolveDependencies
	    };

	    addPreMethod('save', 'validate');

	    return {
	        addPreMethodToType: addPreMethodToType,
	        addPostMethodToType: addPostMethodToType,
	        addPreMethod: addPreMethod,
	        addPostMethod: addPostMethod,
	        addMethod: addMethod,
	        getPreMethods: getPreMethods,
	        getPostMethods: getPostMethods,
	        getMethod: getMethod,
	        hasMethod: hasMethod,
	        callMethod: function callMethod(methodName, obj, then) {
	            return _callMethod(methodName, obj, then)['catch'](errorHandler(methodName.instruction || methodName, obj));
	        },
	        methods: methods,
	        utils: utils
	    };

	    // API
	    function addPreMethodToType(methodName, typeName, fn) {
	        fn = getMethodFromString(fn);
	        if (angular.isArray(typeName)) {
	            angular.forEach(typeName, function (name) {
	                addPreMethodToType(methodName, name, fn);
	            });
	        } else {
	            _addPreMethod(methodName, typeName, fn);
	        }
	    }
	    function addPostMethodToType(methodName, typeName, fn) {
	        fn = getMethodFromString(fn);
	        if (angular.isArray(typeName)) {
	            angular.forEach(typeName, function (name) {
	                addPostMethodToType(methodName, name, fn);
	            });
	        } else {
	            _addPostMethod(methodName, typeName, fn);
	        }
	    }
	    function addPreMethod(methodName, fn) {
	        fn = getMethodFromString(fn);
	        _addPreMethod(methodName, 'global', fn);
	    }
	    function addPostMethod(methodName, fn) {
	        fn = getMethodFromString(fn);
	        _addPostMethod(methodName, 'global', fn);
	    }
	    function addMethod(methodName, method, overwrite) {
	        if (angular.isDefined(methods[methodName]) && !overwrite) {
	            $log.error('Method', methodName, 'already exists. ' + 'To overwrite this method pass \'true\' as the last argument.' + 'Otherwise, choose a different method name.');
	        } else {
	            methods[methodName] = method;
	            $log.debug('set', methodName);
	        }
	    }

	    function getPreMethods(methodName, typeName) {
	        /**
	         * Wrapper for pre methods
	         * @param methodName
	         * @param typeName
	         * @returns {callable}
	         */
	        var regionKey = getMethodKey(methodName, typeName),
	            globalKey = getMethodKey(methodName, 'global'),
	            fns = (preMethods[regionKey] || []).concat(preMethods[globalKey] || []);
	        return getPrePostMethodsCallback(fns);
	    }
	    function getPostMethods(methodName, typeName) {
	        /**
	         * Wrapper for post methods
	         * @param methodName
	         * @param typeName
	         * @returns {callable}
	         */
	        var regionKey = getMethodKey(methodName, typeName),
	            globalKey = getMethodKey(methodName, 'global'),
	            fns = (postMethods[regionKey] || []).concat(postMethods[globalKey] || []);
	        return getPrePostMethodsCallback(fns);
	    }
	    function getMethod(methodName, data) {
	        /**
	         * we only allow one method for main actions.
	         * So we can comfortably call the method without putting it in a chain.
	         */
	        return function (regionObject) {
	            return callMethodAndExtendObject(methods[methodName], regionObject, data);
	        };
	    }
	    function hasMethod(methodName) {
	        return !!methods[methodName];
	    }
	    function _callMethod(methodName, regionObject, then) {
	        var action;
	        if (angular.isObject(methodName)) {
	            action = methodName;
	            methodName = methodName.instruction;
	        }

	        if (hasMethod(methodName)) {
	            $log.debug('Calling method', methodName, regionObject.type_name);

	            regionObject.controller.addProcessingStatus(methodName);
	            var typeName = regionObject.type_name;

	            return resolveDependencies(regionObject, methodName == 'save').then(createModal(action)).then(getPreMethods(methodName, typeName)).then(getMethod(methodName, action)).then(getPostMethods(methodName, typeName))['finally'](function () {
	                $timeout(function () {
	                    (then || angular.identity)();
	                    regionObject.controller.clearProcessingStatus(methodName);
	                });
	            });
	        } else {
	            var msg = methodName + ' does not exist as an Action.';
	            $log.error(msg);
	            return $q.reject(msg);
	        }
	    }

	    // DEFAULT METHODS
	    function methodReload(regionObject) {
	        return utils.resolveDependencies(regionObject).then(function (rObject) {
	            var url = formatUrl(regionObject.parentRegionSet.region_endpoint_pattern, rObject.object);
	            return HttpQueue.addObjectRequest(url);
	        }).then(function (freshObject) {
	            return utils.deepExtend(regionObject, freshObject);
	        });
	    }
	    function methodDelete(regionObject) {

	        var delete_url = regionObject.delete_endpoint || regionObject.object_endpoint,
	            modal = {
	            templateUrl: regionObject.delete_confirmation_template_url,
	            dataUrl: regionObject.relatedobjects_endpoint
	        },
	            options = {
	            url: delete_url,
	            method: 'DELETE'
	        };

	        return $q(function _methodDelete(resolve, reject) {
	            Modal({ modal: modal }, regionObject).then(function () {
	                // modal success
	                $http(options).success(function (data) {
	                    // http success
	                    $log.info('Deleted', regionObject.type_name);
	                    regionObject.controller.removeRegion(regionObject);
	                    RegionService.removeRegion(regionObject);
	                    resolve(regionObject);
	                    // reload to list view for primaryRegions
	                    if (regionObject.parentRegionSet.isPrimaryRegion) {
	                        $timeout(function () {
	                            window.location.replace(data.url || data.data.url);
	                        }, 100);
	                    }
	                }).error(function (data, status) {
	                    // http error
	                    regionObject.controller.error(arguments);
	                    reject(status.toString());
	                });
	            }, function () {
	                // modal cancelled
	                reject('modal cancelled');
	            });
	        });
	    }
	    function methodSaveAndReload(regionObject) {
	        // ...
	        return $q(function (resolve, reject) {
	            reject('not implemented yet');
	        });
	    }
	    function methodDestroy(regionObject) {
	        return $q(function _methodDestroy(resolve) {
	            regionObject.controller.removeRegion(regionObject);
	            RegionService.removeRegion(regionObject);
	            resolve(regionObject);
	        });
	    }
	    function methodCancel(regionObject) {
	        regionObject.controller.reset();
	        return _callMethod('exit', regionObject);
	    }
	    function methodExit(regionObject) {
	        regionObject.controller.activeState = 'default';
	        return $q.when(regionObject);
	    }
	    function methodSaveAll(regionObject) {
	        var queue = regionObject.controller.handleAction(regionObject.commit_instruction);
	        var triggeredChildren = [];

	        var filteredRegionObjects = RegionService.helpers.regions.filter(function (otherRegionObject) {
	            return otherRegionObject.commit_instruction !== null;
	        });

	        // Flag regions as pending
	        angular.forEach(filteredRegionObjects, function (otherRegionObject) {
	            if (regionObject != otherRegionObject) {
	                otherRegionObject.controller.addProcessingStatus('waiting');
	            }
	        });

	        // Process regions
	        angular.forEach(filteredRegionObjects, function (otherRegionObject) {
	            if (regionObject != otherRegionObject && triggeredChildren.indexOf(otherRegionObject) == -1) {
	                if (otherRegionObject.passive_machinery === true) {
	                    return;
	                }
	                triggeredChildren.push.apply(triggeredChildren, otherRegionObject.controller.children);

	                queue = queue.then(function (res) {
	                    $log.debug('Issuing', otherRegionObject.commit_instruction, 'to', otherRegionObject.type_name, otherRegionObject);

	                    return otherRegionObject.controller.handleAction(otherRegionObject.commit_instruction).then(function () {
	                        otherRegionObject.controller.clearProcessingStatus('waiting');
	                        return res;
	                    }, function () {
	                        otherRegionObject.controller.clearProcessingStatus('waiting');
	                        return res;
	                    });
	                });
	            }
	        });
	        return queue['finally'](function () {
	            filteredRegionObjects.map(function (otherRegionObject) {
	                otherRegionObject.controller.clearProcessingStatus('waiting');
	            });
	        });
	    }
	    function methodSave(regionObject) {
	        var method = regionObject.object.id ? 'PATCH' : 'POST';
	        var url = method == 'PATCH' ? regionObject.object_endpoint_pattern : regionObject.object_endpoint;
	        url = formatUrl(url, regionObject.object);

	        angular.forEach(regionObject.object, function (value, key) {
	            if (angular.isObject(value) && !angular.isArray(value)) {
	                regionObject.object[key] = value.id;
	            }
	        });

	        return $q(function _methodSave(resolve, reject) {
	            $http({
	                url: url,
	                method: method,
	                data: regionObject.object
	            }).success(function (data) {
	                updateRegionObject(regionObject, data);

	                regionObject.controller.success();
	                resolve(regionObject);
	            }).error(function (data, status) {
	                if (status === 500) {
	                    data = 'System error occurred. \n We apologize for the interruption and have already been notified.';
	                }
	                regionObject.controller.error(data);
	                reject(status.toString());
	            });
	        });
	    }
	    function methodEdit(regionObject) {
	        regionObject.controller.activeState = 'edit';
	        return $q.when(regionObject);
	    }
	    function methodValidate(regionObject) {
	        var typeName = regionObject.type_name;
	        return $q.when(regionObject).then(getPreMethods('validate', typeName)).then(getPostMethods('validate', typeName)).then(function () {
	            return regionObject;
	        });
	    }
	    function methodEditRelated(_regionObject, action) {
	        function getExtraDataMethod(url, initialData) {
	            // create callable closure around the extra data url.
	            return function () {
	                var items = $q.defer();
	                $http.get(url).success(function (data) {
	                    return items.resolve(angular.extend(initialData || {}, data));
	                });
	                return items.promise;
	            };
	        }

	        var extraDataGetter = null;
	        if (action.dataUrl === undefined) {
	            extraDataGetter = function () {
	                return action.extraData;
	            };
	        } else {
	            extraDataGetter = getExtraDataMethod(action.dataUrl, action.extraData);
	        }

	        var resolves = {
	            regionObject: function regionObject() {
	                return _regionObject;
	            },
	            extraData: extraDataGetter,
	            saveUrl: function saveUrl() {
	                return action.saveUrl;
	            }
	        };
	        var modal = $modal.open({
	            templateUrl: action.templateUrl,
	            resolve: resolves,
	            controller: 'EditRelatedModalController',
	            controllerAs: 'vm',
	            size: 'lg'
	        });

	        return modal.result.then(function () {
	            return methodReload(_regionObject);
	        });
	    }

	    // UTILS
	    function getMethodKey(methodName, typeName) {
	        return ['_fn', methodName, typeName].join('_');
	    }
	    function getMethodFromString(fn) {
	        if (typeof fn == 'string' && angular.isDefined(methods[fn])) {
	            fn = methods[fn];
	        }
	        if (typeof fn !== 'function') {
	            throw new Error(fnMustBeStringOrFn);
	        }
	        return fn;
	    }
	    function formatUrl(endpoint, context, typeName) {
	        var startSymbol = $interpolate.startSymbol(),
	            endSymbol = $interpolate.endSymbol(),
	            regex = /__(\w+)__/g,
	            replaceStr = startSymbol + '$1' + endSymbol;

	        if (typeName) {
	            var obj = { endpoint: endpoint, context: context };
	            return getPreMethods('formatUrl', typeName)(obj).then(function (obj) {
	                obj['endpoint'] = $interpolate(obj.endpoint.replace(regex, replaceStr))(obj.context);
	                return obj;
	            }).then(getPostMethods('formatUrl', typeName)).then(function (obj) {
	                return obj.endpoint;
	            });
	        }

	        return $interpolate(endpoint.replace(regex, replaceStr))(context);
	    }
	    function deepExtend(destination, data) {
	        // Try a merge of top-level entries.  updateRegionObject is not a recursive deep merge, but many
	        // of our top-level keys are Object-type.
	        var specialCases = ['controller', 'parentRegionObject', 'parentRegionSet'];
	        for (var k in data) {
	            if (!data.hasOwnProperty(k) || specialCases.indexOf(k) > -1) continue;
	            var original_v = destination[k];
	            var v = data[k];
	            if (angular.isArray(original_v) && !angular.equals(original_v, v)) {
	                original_v.length = 0; // lol, this actually works
	                original_v.push.apply(original_v, v);
	            } else if (angular.isObject(original_v)) {
	                angular.extend(original_v, v);
	            } else {
	                destination[k] = v;
	            }
	        }
	        return destination;
	    }
	    function updateRegionObject(regionObject, data) {
	        deepExtend(regionObject, data);
	        regionObject._masterForm = angular.copy(regionObject.object);
	    }
	    function _resolveDependencies(regionObject, rejectFail) {
	        /**
	         * Look into the object and try to grab things it needs from other Regions.
	         * Non forceful resolve but can choose to reject on fail
	         *
	         * @param regionObject
	         * @param forceful
	         * @returns {promise}
	         */

	        return $q(function __resolveDependencies(resolve, reject) {
	            if (!RegionService.helpers.hasDependencies(regionObject)) {
	                resolve(regionObject);
	            } else {
	                try {
	                    updateRegionObject(regionObject.object, RegionService.helpers.fetchRegionDependencies(regionObject));
	                    resolve(regionObject);
	                } catch (e) {
	                    rejectFail ? reject(e) : resolve(regionObject);
	                }
	            }
	        });
	    }
	    function callMethodAndExtendObject(fn, regionObject, data) {
	        /**
	         * Can't be positive that the function we're running is a promise.
	         * Wrap it and expect the result to be an object that we want to extend
	         * the regionObject by.
	         *
	         * @param fn
	         * @param regionObject
	         * @returns {!Promise.<RESULT>|*}
	         */
	        return $q.when(fn(regionObject, data)).then(function (result) {
	            updateRegionObject(regionObject, result);
	            return regionObject;
	        });
	    }

	    // HELPERS
	    function _addPreMethod(methodName, typeName, fn) {
	        var key = getMethodKey(methodName, typeName);
	        if (!angular.isDefined(preMethods[key])) {
	            preMethods[key] = [];
	        }
	        preMethods[key].push(fn);
	    }
	    function _addPostMethod(methodName, typeName, fn) {
	        var key = getMethodKey(methodName, typeName);
	        if (!angular.isDefined(postMethods[key])) {
	            postMethods[key] = [];
	        }
	        postMethods[key].push(fn);
	    }
	    function _getPrePostMethodsCallback(methods) {
	        /**
	         * creates a callback chain where all the functions aren't called until the previous returns.
	         *
	         * @param {array} methods
	         * @returns {promise}
	         */
	        return function promiseChainer(regionObject) {
	            var queue = $q.when(regionObject);
	            angular.forEach(methods, function (fn, i) {
	                queue = queue.then(function (res) {
	                    return callMethodAndExtendObject(fn, regionObject).then(function () {
	                        return res;
	                    });
	                });
	            });
	            return queue;
	        };
	    }
	    function resolveDependencies(regionObject, forceful) {
	        /**
	         * Look into the object and try to grab things it needs from other Regions.
	         * If it can't find them and we really need them, attempt a save on the region
	         * that we believe contains the data we need.
	         *
	         * @param regionObject
	         * @param forceful
	         * @returns {promise}
	         */
	        var deferred = $q.defer();

	        utils.resolveDependencies(regionObject, forceful).then(function (rObject) {
	            deferred.resolve(rObject);
	        }, function (error) {
	            // error
	            // NOTE: this will only get run if forceful is true.
	            var depsRegion = RegionService.getRegionFromTypeName(error.regionName);
	            _callMethod(depsRegion.commit_instruction, depsRegion).then(utils.resolveDependencies, deferred.reject);
	        });

	        return deferred.promise;
	    }

	    // RETURNS PROMISE CALLBACKS
	    function getPrePostMethodsCallback(methods) {
	        /**
	         * check if there are any methods to be called.
	         * If not, return a function that just returns the regionObject.
	         *
	         * @param {array} methods
	         * @returns {*} (promise chain | identity)
	         */
	        return angular.isDefined(methods) ? _getPrePostMethodsCallback(methods) : angular.identity;
	    }
	    function createModal(action) {
	        /**
	         * If the action calls to be gated by a modal,
	         * this returns a function that will do that when the action chain gets there.
	         *
	         * @param regionObject
	         * @returns {*}
	         */
	        function _createModal(regionObject) {
	            return Modal(action, regionObject);
	        }

	        var useModal = angular.isDefined(action) && angular.isDefined(action.modal) && action.modal !== null;
	        return useModal ? _createModal : angular.identity;
	    }
	    function errorHandler(methodName, regionObject) {
	        //var err = new ActionException(methodName, regionObject);
	        return function (cause) {
	            return $q.reject(cause);
	        };
	    }
	}).controller('EditRelatedModalController', function ($http, $scope, $modalInstance, saveUrl, regionObject, extraData) {
	    var vm = this;
	    $scope.regionObject = vm.regionObject = regionObject;
	    $scope.extraData = vm.extraData = extraData;
	    vm.ok = function () {
	        var method = extraData.id ? 'patch' : 'post';
	        $http[method](saveUrl, regionObject.object).then(function (response) {
	            $modalInstance.close(vm.regionObject);
	        });
	    };
	    vm.cancel = function () {
	        $modalInstance.dismiss('cancel');
	    };
	});

/***/ }),

/***/ 155:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.services.HttpQueue').factory('HttpQueue', function ($q, $http, $templateCache) {
	    var requests = [];
	    var processing = false;

	    return {
	        addObjectRequest: addObjectRequest,
	        addTemplateRequest: addTemplateRequest
	    };

	    function addObjectRequest(endpoint, additionalScope) {
	        // Add to the beginning because we're going to pop the next requests.
	        additionalScope = additionalScope || {};
	        var deferred = $q.defer();
	        requests.unshift([deferred, endpoint, additionalScope]);
	        triggerRequestCycle();
	        return deferred.promise;
	    }
	    function addTemplateRequest(endpoint) {
	        // Call Template paths right away.
	        var deferred = $q.defer();
	        $http.get(endpoint, { cache: $templateCache }).success(deferred.resolve).error(deferred.reject);
	        return deferred.promise;
	    }

	    // helpers
	    function _apiCall(promise, endpoint, additionalScope) {
	        $http.get(endpoint).success(function (data) {
	            data.additionalScope = additionalScope;
	            promise.resolve(data);
	        }).error(function (data, code) {
	            promise.reject(data, code);
	        })['finally'](function () {
	            requests.length ? _apiCall.apply(this, requests.pop()) : processing = false;
	        });
	    }
	    function triggerRequestCycle() {
	        if (!processing && requests.length) {
	            processing = true;
	            _apiCall.apply(this, requests.pop());
	        }
	    }
	});

/***/ }),

/***/ 156:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/20/14.
	 */

	'use strict';

	angular.module('axis.services.Modal').factory('Modal', function ($modal, $q, $http) {
	    function getExtraDataMethod(url) {
	        // create callable closure around the extra data url.
	        return function () {
	            var items = $q.defer();
	            $http.get(url).success(function (data) {
	                return items.resolve(data);
	            });
	            return items.promise;
	        };
	    }

	    return function Modal(action, _regionObject) {
	        var resolves = {
	            regionObject: function regionObject() {
	                return _regionObject;
	            }
	        };
	        if (angular.isDefined(action.modal.dataUrl) && action.modal.dataUrl != null) {
	            resolves['extraData'] = getExtraDataMethod(action.modal.dataUrl);
	        } else {
	            resolves['extraData'] = function () {
	                return null;
	            };
	        }

	        var modal = $modal.open({
	            templateUrl: action.modal.templateUrl,
	            resolve: resolves,
	            controller: 'ModalFactoryController',
	            controllerAs: 'vm',
	            size: action.modal.size
	        });
	        return modal.result;
	    };
	}).controller('ModalFactoryController', function ($scope, $modalInstance, regionObject, extraData) {
	    var vm = this;
	    $scope.regionObject = vm.regionObject = regionObject;
	    vm.extraData = extraData;
	    vm.ok = function () {
	        $modalInstance.close(vm.regionObject);
	    };
	    vm.cancel = function () {
	        $modalInstance.dismiss('cancel');
	    };
	});

/***/ }),

/***/ 157:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.services.RegionService').factory('RegionService', function ($rootScope, $interpolate) {
	    var regions = [];
	    var regionsMap = {};

	    var helpers = {
	        getRegionValue: _getSingleRegionValue,
	        getRegionDependencies: _getRegionDependencies,
	        getRegionDependenciesKeys: _getRegionDependenciesKeys,
	        hasDependencies: _hasDependencies,
	        fetchRegionDependencies: _fetchRegionDependencies,
	        regions: regions,
	        regionsMap: regionsMap
	    };

	    return {
	        addRegion: addRegion,
	        removeRegion: removeRegion,
	        getRegion: getRegion,
	        getRegionFromTypeName: getRegionFromTypeName,
	        getRegionCounter: getRegionCounter,
	        registerChildRegionByTypeName: registerChildRegionByTypeName,
	        registerChildRegion: registerChildRegion,
	        helpers: helpers
	    };

	    function InvalidRegionValueError(regionName, key, message) {
	        this.name = 'InvalidRegionValueError';
	        this.message = message;
	        this.stack = new Error().stack;
	        this.regionName = regionName;
	        this.key = key;
	        this.getMessage = function () {
	            return $interpolate(this.message)(this);
	        };
	    }

	    function _getRegionValue(region, key) {
	        /**
	         * Will attempt to get a value from the region passed.
	         * Throws Errors if the key is undefined.
	         * @param region {object} Region Object
	         * @param key {string} key of value in region object.
	         * @returns {*}
	         * @private
	         */
	        try {
	            var value = region.object[key];
	        } catch (e) {
	            throw new InvalidRegionValueError(region.type_name, key, e);
	        }

	        if (value === null || typeof value === 'undefined') {
	            throw new InvalidRegionValueError(region.type_name, key, '\'[[ key ]]\' is undefined for \'[[ regionName ]]\'');
	        }
	        return value;
	    }
	    function _getSingleRegionValue(regionName, key) {
	        /**
	         * Will attempt to get a value from another region given a type name.
	         * Throws Errors if the region does not exist, or the key is undefined.
	         * @param regionName {string} Region Key
	         * @param key {string} key of value in region dict
	         * @returns {*} Throws Error, or returns value
	         * @private
	         */
	        return _getRegionValue(getRegionFromTypeName(regionName), key);
	    }

	    function _getRegionDependencies(region) {
	        /**
	         * Shortcut for fetching the region dependencies dict.
	         * @param region {object}
	         * @returns {dict}
	         * @private
	         */
	        return region.region_dependencies || {};
	    }
	    function _getRegionDependenciesKeys(region) {
	        /**
	         * Returns an array of the regions holding current regions dependencies.
	         * @param region {object}
	         * @returns {Array}
	         * @private
	         */
	        return Object.keys(_getRegionDependencies(region));
	    }
	    function _hasDependencies(region) {
	        /**
	         * Does a region have requirements for being submitted?
	         * @param region {object}
	         * @returns {boolean}
	         * @private
	         */
	        return !!_getRegionDependenciesKeys(region).length;
	    }

	    function _fetchRegionDependencies(region) {
	        /**
	         * Builds a dict of dependencies for a given region with the values key being the
	         * underscore concatenated result of the region_name and value key.
	         * @param region {object}
	         * @returns {object}
	         * @private
	         */
	        var dependencies = {};

	        angular.forEach(_getRegionDependencies(region), function (keys, region_name) {
	            // keys: array of objects [{field_name: '', serialize_as: ''}]
	            // region_name: region list of associated with
	            angular.forEach(keys, function (obj) {
	                if (angular.isDefined(region.parentRegionSet) && angular.isDefined(region.parentRegionSet.parentRegionObject)) {
	                    dependencies[obj.serialize_as] = _getRegionValue(region.parentRegionSet.parentRegionObject, obj.field_name);
	                } else {
	                    dependencies[obj.serialize_as] = _getSingleRegionValue(region_name, obj.field_name);
	                }
	            });
	        });

	        return dependencies;
	    }

	    function addRegion(region) {
	        regions.push(region);
	        var val = regionsMap[region.type_name];
	        if (val === undefined) {
	            regionsMap[region.type_name] = region;
	        } else if (_.isArray(val)) {
	            regionsMap[region.type_name].push(region);
	        } else {
	            regionsMap[region.type_name] = [val];
	            regionsMap[region.type_name].push(region);
	        }
	        $rootScope.$broadcast('addedRegion', region);
	        $rootScope.$broadcast('addedRegion:' + region.type_name, region);
	        return getRegion(region);
	    }
	    function removeRegion(region) {
	        // Remove from list
	        var index = regions.indexOf(region);
	        regions.splice(index, 1);

	        if (_.isArray(regionsMap[region.type_name])) {
	            var index = regionsMap[region.type_name].indexOf(region);
	            regionsMap[region.type_name].splice(index, 1);
	        }

	        $rootScope.$broadcast('removedRegion', region);
	        $rootScope.$broadcast('removedRegion:' + region.type_name, region);
	    }
	    function getRegion(region) {
	        var index = regions.indexOf(region);
	        return regions[index];
	    }
	    function getRegionFromTypeName(typeName) {
	        return regionsMap[typeName];
	        // var region;
	        // angular.forEach(regions, function(obj){
	        //     if(obj.type_name == typeName) region = obj;
	        // });
	        // return region;
	    }
	    function getRegionCounter(regionNames) {
	        var n = 0;
	        _.forEach(regionNames, function (typeName) {
	            var regionData = regionsMap[typeName];
	            if (angular.isArray(regionData)) {
	                n += regionData.length;
	            } else if (regionData !== undefined) {
	                n += 1;
	            }
	        });
	        return n;
	    }

	    function registerChildRegionByTypeName(typeName, childObject) {
	        return registerChildRegion(getRegionFromTypeName(typeName), childObject);
	    }
	    function registerChildRegion(parentObject, childObject) {
	        return parentObject.controller.children.push(childObject);
	    }
	});

/***/ }),

/***/ 158:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.services.RuntimeStates').provider('RuntimeStates', function ($stateProvider) {
	    this.$get = function () {
	        return {
	            addState: function addState(name, state) {
	                $stateProvider.state(name, state);
	            }
	        };
	    };
	});

/***/ }),

/***/ 159:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.services.TabService').factory('TabService', function ($rootScope, $log, $state, RuntimeStates) {
	    var tabs = {},
	        firstState = 'replace',
	        abstract = {
	        abstract: true,
	        url: '/tabs'
	    };

	    $rootScope.$on('$stateChangeStart', stateChangeStart);
	    return {
	        go: go,
	        addTab: addTab,
	        tabs: tabs,
	        updateDisableListener: updateDisableListener
	    };

	    // GETTERS
	    function getEndpointName(endpoint) {
	        if (!endpoint) throw new Error('Endpoint must be provided.');
	        var temp = endpoint.split('.'),
	            parent = temp[0],
	            name = temp[1];
	        return name;
	    }
	    function getFirstAvailableState() {
	        var states = $state.get();
	        var toState;

	        for (var i = 0; i < states.length; i++) {
	            var s = states[i];
	            if (!s.abstract && s.name.length > 0) {
	                try {
	                    if (!tabs[s.name.split('.').pop()].disabled) {
	                        toState = s.name;
	                        break;
	                    }
	                } catch (e) {}
	            }
	        }
	        if (!toState) toState = 'index';
	        return toState;
	    }

	    // ACTIONS
	    function stateChangeStart(event, toState, toParams, fromState, fromParams) {
	        // Checking for an intersection allows nested urls to keep the tab their in open.
	        var intersection = _.intersection(toState.name.split('.'), fromState.name.split('.'));
	        if (intersection.length) {
	            // only match for things that aren't just tabs.
	            if (intersection.indexOf('tabs') == -1) {
	                return;
	            }
	        }
	        var toTab = tabs[getEndpointName(toState.name)];

	        angular.forEach(tabs, function (obj, key) {
	            obj.active = false;
	        });

	        // protects against switching to home_statuses that aren't
	        // registered as tabs
	        if (angular.isDefined(toTab)) toTab.active = true;
	    }
	    function addTab(endpoint, disabled) {
	        var name = getEndpointName(endpoint);
	        $log.debug('endpoint', endpoint, 'current', $state.current.name, 'disabled', disabled);

	        if (!Object.keys(tabs).length) {
	            RuntimeStates.addState('tabs', abstract);
	        }

	        tabs[name] = {
	            active: $state.current.name == endpoint,
	            disabled: !!disabled
	        };

	        RuntimeStates.addState(endpoint, {
	            url: '/' + name,
	            template: ''
	        });
	    }
	    function updateDisableListener(endpoint, value) {
	        $log.debug('tab', endpoint, 'is', value ? 'disabled' : 'enabled');
	        var name = getEndpointName(endpoint);
	        tabs[name].disabled = value;
	    }
	    function go(endpoint) {
	        try {
	            if (!tabs[getEndpointName(endpoint)].disabled) {
	                $rootScope.$broadcast('TabService.go', endpoint);
	                $state.go(endpoint, {}, { location: firstState });
	                firstState = true;
	            } else {
	                throw endpoint + ' is disabled';
	            }
	        } catch (e) {
	            $state.go(getFirstAvailableState());
	        }
	    }
	});

/***/ }),

/***/ 160:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	'use strict';

	angular.module('axis.services.UrlService').factory('UrlService', function ($location, $state) {
	    var originalLink = $location.pathname || location.pathname;
	    var updatedLink = false;

	    $location.$$$compose = $location.$$compose.bind($location);
	    $location.$$compose = (function () {
	        this.$$$compose();
	        if (updatedLink) {
	            this.$$absUrl = this.$$absUrl.replace(originalLink, updatedLink);
	        }
	    }).bind($location);

	    function setUpdatedLink(link) {
	        updatedLink = link;
	        try {
	            $state.reload();
	        } catch (e) {
	            $state.go('index');
	        }
	    }

	    return {
	        setUpdatedLink: setUpdatedLink
	    };
	});

/***/ }),

/***/ 161:
/***/ (function(module, exports) {

	/**
	 * Created by mjeffrey on 11/5/14.
	 */

	// ACTIONS
	'use strict';

	angular.module('axis.services.Actions', ['axis.services.RegionService', 'axis.services.Modal', 'axis.services.HttpQueue']);

	// OTHER
	angular.module('axis.services.Modal', ['ui.bootstrap']);
	angular.module('axis.services.HttpQueue', []);
	angular.module('axis.services.RuntimeStates', ['ui.router']);
	angular.module('axis.services.TabService', ['axis.services.RuntimeStates', 'ui.router']);
	angular.module('axis.services.RegionService', []);
	angular.module('axis.services.UrlService', ['ui.router']);

	angular.module('axis.services', ['axis.services.Actions', 'axis.services.Modal', 'axis.services.HttpQueue', 'axis.services.RuntimeStates', 'axis.services.TabService', 'axis.services.RegionService', 'axis.services.UrlService']);

/***/ }),

/***/ 179:
/***/ (function(module, exports, __webpack_require__) {

	/*! Moment Duration Format v1.3.0
	 *  https://github.com/jsmreese/moment-duration-format 
	 *  Date: 2014-07-15
	 *
	 *  Duration format plugin function for the Moment.js library
	 *  http://momentjs.com/
	 *
	 *  Copyright 2014 John Madhavan-Reese
	 *  Released under the MIT license
	 */

	(function (root, undefined) {

		// repeatZero(qty)
		// returns "0" repeated qty times
		function repeatZero(qty) {
			var result = "";
			
			// exit early
			// if qty is 0 or a negative number
			// or doesn't coerce to an integer
			qty = parseInt(qty, 10);
			if (!qty || qty < 1) { return result; }
			
			while (qty) {
				result += "0";
				qty -= 1;
			}
			
			return result;
		}
		
		// padZero(str, len [, isRight])
		// pads a string with zeros up to a specified length
		// will not pad a string if its length is aready
		// greater than or equal to the specified length
		// default output pads with zeros on the left
		// set isRight to `true` to pad with zeros on the right
		function padZero(str, len, isRight) {
			if (str == null) { str = ""; }
			str = "" + str;
			
			return (isRight ? str : "") + repeatZero(len - str.length) + (isRight ? "" : str);
		}
		
		// isArray
		function isArray(array) {
			return Object.prototype.toString.call(array) === "[object Array]";
		}
		
		// isObject
		function isObject(obj) {
			return Object.prototype.toString.call(obj) === "[object Object]";
		}
		
		// findLast
		function findLast(array, callback) {
			var index = array.length;

			while (index -= 1) {
				if (callback(array[index])) { return array[index]; }
			}
		}

		// find
		function find(array, callback) {
			var index = 0,
				max = array.length,
				match;
				
			if (typeof callback !== "function") {
				match = callback;
				callback = function (item) {
					return item === match;
				};
			}

			while (index < max) {
				if (callback(array[index])) { return array[index]; }
				index += 1;
			}
		}
		
		// each
		function each(array, callback) {
			var index = 0,
				max = array.length;
				
			if (!array || !max) { return; }

			while (index < max) {
				if (callback(array[index], index) === false) { return; }
				index += 1;
			}
		}
		
		// map
		function map(array, callback) {
			var index = 0,
				max = array.length,
				ret = [];

			if (!array || !max) { return ret; }
					
			while (index < max) {
				ret[index] = callback(array[index], index);
				index += 1;
			}
			
			return ret;
		}
		
		// pluck
		function pluck(array, prop) {
			return map(array, function (item) {
				return item[prop];
			});
		}
		
		// compact
		function compact(array) {
			var ret = [];
			
			each(array, function (item) {
				if (item) { ret.push(item); }
			});
			
			return ret;
		}
		
		// unique
		function unique(array) {
			var ret = [];
			
			each(array, function (_a) {
				if (!find(ret, _a)) { ret.push(_a); }
			});
			
			return ret;
		}
		
		// intersection
		function intersection(a, b) {
			var ret = [];
			
			each(a, function (_a) {
				each(b, function (_b) {
					if (_a === _b) { ret.push(_a); }
				});
			});
			
			return unique(ret);
		}
		
		// rest
		function rest(array, callback) {
			var ret = [];
			
			each(array, function (item, index) {
				if (!callback(item)) {
					ret = array.slice(index);
					return false;
				}
			});
			
			return ret;
		}

		// initial
		function initial(array, callback) {
			var reversed = array.slice().reverse();
			
			return rest(reversed, callback).reverse();
		}
		
		// extend
		function extend(a, b) {
			for (var key in b) {
				if (b.hasOwnProperty(key)) { a[key] = b[key]; }
			}
			
			return a;
		}
				
		// define internal moment reference
		var moment;

		if (true) {
			try { moment = __webpack_require__(1); } 
			catch (e) {}
		} 
		
		if (!moment && root.moment) {
			moment = root.moment;
		}
		
		if (!moment) {
			throw "Moment Duration Format cannot find Moment.js";
		}
		
		// moment.duration.format([template] [, precision] [, settings])
		moment.duration.fn.format = function () {

			var tokenizer, tokens, types, typeMap, momentTypes, foundFirst, trimIndex,
				args = [].slice.call(arguments),
				settings = extend({}, this.format.defaults),
				// keep a shadow copy of this moment for calculating remainders
				remainder = moment.duration(this);

			// add a reference to this duration object to the settings for use
			// in a template function
			settings.duration = this;

			// parse arguments
			each(args, function (arg) {
				if (typeof arg === "string" || typeof arg === "function") {
					settings.template = arg;
					return;
				}

				if (typeof arg === "number") {
					settings.precision = arg;
					return;
				}

				if (isObject(arg)) {
					extend(settings, arg);
				}
			});

			// types
			types = settings.types = (isArray(settings.types) ? settings.types : settings.types.split(" "));

			// template
			if (typeof settings.template === "function") {
				settings.template = settings.template.apply(settings);
			}

			// tokenizer regexp
			tokenizer = new RegExp(map(types, function (type) {
				return settings[type].source;
			}).join("|"), "g");

			// token type map function
			typeMap = function (token) {
				return find(types, function (type) {
					return settings[type].test(token);
				});
			};

			// tokens array
			tokens = map(settings.template.match(tokenizer), function (token, index) {
				var type = typeMap(token),
					length = token.length;

				return {
					index: index,
					length: length,

					// replace escaped tokens with the non-escaped token text
					token: (type === "escape" ? token.replace(settings.escape, "$1") : token),

					// ignore type on non-moment tokens
					type: ((type === "escape" || type === "general") ? null : type)

					// calculate base value for all moment tokens
					//baseValue: ((type === "escape" || type === "general") ? null : this.as(type))
				};
			}, this);

			// unique moment token types in the template (in order of descending magnitude)
			momentTypes = intersection(types, unique(compact(pluck(tokens, "type"))));

			// exit early if there are no momentTypes
			if (!momentTypes.length) {
				return pluck(tokens, "token").join("");
			}

			// calculate values for each token type in the template
			each(momentTypes, function (momentType, index) {
				var value, wholeValue, decimalValue, isLeast, isMost;

				// calculate integer and decimal value portions
				value = remainder.as(momentType);
				wholeValue = (value > 0 ? Math.floor(value) : Math.ceil(value));
				decimalValue = value - wholeValue;

				// is this the least-significant moment token found?
				isLeast = ((index + 1) === momentTypes.length);

				// is this the most-significant moment token found?
				isMost = (!index);

				// update tokens array
				// using this algorithm to not assume anything about
				// the order or frequency of any tokens
				each(tokens, function (token) {
					if (token.type === momentType) {
						extend(token, {
							value: value,
							wholeValue: wholeValue,
							decimalValue: decimalValue,
							isLeast: isLeast,
							isMost: isMost
						});

						if (isMost) {
							// note the length of the most-significant moment token:
							// if it is greater than one and forceLength is not set, default forceLength to `true`
							if (settings.forceLength == null && token.length > 1) {
								settings.forceLength = true;
							}

							// rationale is this:
							// if the template is "h:mm:ss" and the moment value is 5 minutes, the user-friendly output is "5:00", not "05:00"
							// shouldn't pad the `minutes` token even though it has length of two
							// if the template is "hh:mm:ss", the user clearly wanted everything padded so we should output "05:00"
							// if the user wanted the full padded output, they can set `{ trim: false }` to get "00:05:00"
						}
					}
				});

				// update remainder
				remainder.subtract(wholeValue, momentType);
			});
		
			// trim tokens array
			if (settings.trim) {
				tokens = (settings.trim === "left" ? rest : initial)(tokens, function (token) {
					// return `true` if:
					// the token is not the least moment token (don't trim the least moment token)
					// the token is a moment token that does not have a value (don't trim moment tokens that have a whole value)
					return !(token.isLeast || (token.type != null && token.wholeValue));
				});
			}
			
			
			// build output

			// the first moment token can have special handling
			foundFirst = false;

			// run the map in reverse order if trimming from the right
			if (settings.trim === "right") {
				tokens.reverse();
			}

			tokens = map(tokens, function (token) {
				var val,
					decVal;

				if (!token.type) {
					// if it is not a moment token, use the token as its own value
					return token.token;
				}

				// apply negative precision formatting to the least-significant moment token
				if (token.isLeast && (settings.precision < 0)) {
					val = (Math.floor(token.wholeValue * Math.pow(10, settings.precision)) * Math.pow(10, -settings.precision)).toString();
				} else {
					val = token.wholeValue.toString();
				}
				
				// remove negative sign from the beginning
				val = val.replace(/^\-/, "");

				// apply token length formatting
				// special handling for the first moment token that is not the most significant in a trimmed template
				if (token.length > 1 && (foundFirst || token.isMost || settings.forceLength)) {
					val = padZero(val, token.length);
				}

				// add decimal value if precision > 0
				if (token.isLeast && (settings.precision > 0)) {
					decVal = token.decimalValue.toString().replace(/^\-/, "").split(/\.|e\-/);
					switch (decVal.length) {
						case 1:
							val += "." + padZero(decVal[0], settings.precision, true).slice(0, settings.precision);
							break;
							
						case 2:
							val += "." + padZero(decVal[1], settings.precision, true).slice(0, settings.precision);		
							break;
							
						case 3:
							val += "." + padZero(repeatZero((+decVal[2]) - 1) + (decVal[0] || "0") + decVal[1], settings.precision, true).slice(0, settings.precision);		
							break;
						
						default:
							throw "Moment Duration Format: unable to parse token decimal value.";
					}
				}
				
				// add a negative sign if the value is negative and token is most significant
				if (token.isMost && token.value < 0) {
					val = "-" + val;
				}

				foundFirst = true;

				return val;
			});

			// undo the reverse if trimming from the right
			if (settings.trim === "right") {
				tokens.reverse();
			}

			return tokens.join("");
		};

		moment.duration.fn.format.defaults = {
			// token definitions
			escape: /\[(.+?)\]/,
			years: /[Yy]+/,
			months: /M+/,
			weeks: /[Ww]+/,
			days: /[Dd]+/,
			hours: /[Hh]+/,
			minutes: /m+/,
			seconds: /s+/,
			milliseconds: /S+/,
			general: /.+?/,

			// token type names
			// in order of descending magnitude
			// can be a space-separated token name list or an array of token names
			types: "escape years months weeks days hours minutes seconds milliseconds general",

			// format options

			// trim
			// "left" - template tokens are trimmed from the left until the first moment token that has a value >= 1
			// "right" - template tokens are trimmed from the right until the first moment token that has a value >= 1
			// (the final moment token is not trimmed, regardless of value)
			// `false` - template tokens are not trimmed
			trim: "left",

			// precision
			// number of decimal digits to include after (to the right of) the decimal point (positive integer)
			// or the number of digits to truncate to 0 before (to the left of) the decimal point (negative integer)
			precision: 0,

			// force first moment token with a value to render at full length even when template is trimmed and first moment token has length of 1
			forceLength: null,

			// template used to format duration
			// may be a function or a string
			// template functions are executed with the `this` binding of the settings object
			// so that template strings may be dynamically generated based on the duration object
			// (accessible via `this.duration`)
			// or any of the other settings
			template: function () {
				var types = this.types,
					dur = this.duration,
					lastType = findLast(types, function (type) {
						return dur._data[type];
					});

				// default template strings for each duration dimension type
				switch (lastType) {
					case "seconds":
						return "h:mm:ss";
					case "minutes":
						return "d[d] h:mm";
					case "hours":
						return "d[d] h[h]";
					case "days":
						return "M[m] d[d]";
					case "weeks":
						return "y[y] w[w]";
					case "months":
						return "y[y] M[m]";
					case "years":
						return "y[y]";
					default:
						return "y[y] M[m] d[d] h:mm:ss";
				}
			}
		};

	})(this);


/***/ }),

/***/ 192:
/***/ (function(module, exports) {

	/*
	 * Angular JS Multi Select
	 * Creates a dropdown-like button with checkboxes.
	 *
	 * Project started on: Tue, 14 Jan 2014 - 5:18:02 PM
	 * Current version: 2.0.2
	 *
	 * Released under the MIT License
	 * --------------------------------------------------------------------------------
	 * The MIT License (MIT)
	 *
	 * Copyright (c) 2014 Ignatius Steven (https://github.com/isteven)
	 *
	 * Permission is hereby granted, free of charge, to any person obtaining a copy
	 * of this software and associated documentation files (the "Software"), to deal
	 * in the Software without restriction, including without limitation the rights
	 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	 * copies of the Software, and to permit persons to whom the Software is
	 * furnished to do so, subject to the following conditions:
	 *
	 * The above copyright notice and this permission notice shall be included in all
	 * copies or substantial portions of the Software.
	 *
	 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	 * SOFTWARE.
	 * --------------------------------------------------------------------------------
	 */

	angular.module( 'multi-select', ['ng'] ).directive( 'multiSelect' , [ '$sce', '$timeout', function ( $sce, $timeout ) {
	    return {
	        restrict:
	            'AE',

	        replace:
	            true,

	        scope:
	        {
	            // models
	            inputModel      : '=',
	            outputModel     : '=',

	            // settings based on attribute
	            buttonLabel     : '@',
	            defaultLabel    : '@',
	            directiveId     : '@',
	            helperElements  : '@',
	            isDisabled      : '=',
	            itemLabel       : '@',
	            maxLabels       : '@',
	            orientation     : '@',
	            selectionMode   : '@',

	            // settings based on input model property
	            tickProperty    : '@',
	            disableProperty : '@',
	            groupProperty   : '@',
	            maxHeight       : '@',

	            // callbacks
	            onClose         : '&',
	            onItemClick     : '&',
	            onOpen          : '&'
	        },

	        template:
	            '<span class="multiSelect inlineBlock">' +
	                '<button type="button" class="button multiSelectButton" ng-click="toggleCheckboxes( $event ); refreshSelectedItems(); refreshButton();" ng-bind-html="varButtonLabel">' +
	                '</button>' +
	                '<div class="checkboxLayer">' +
	                    '<form>' +
	                        '<div class="helperContainer" ng-if="displayHelper( \'filter\' ) || displayHelper( \'all\' ) || displayHelper( \'none\' ) || displayHelper( \'reset\' )">' +
	                            '<div class="line" ng-if="displayHelper( \'all\' ) || displayHelper( \'none\' ) || displayHelper( \'reset\' )">' +
	                                '<button type="button" ng-click="select( \'all\',   $event );"    class="helperButton" ng-if="!isDisabled && displayHelper( \'all\' )">   &#10003;&nbsp; Select All</button> ' +
	                                '<button type="button" ng-click="select( \'none\',  $event );"   class="helperButton" ng-if="!isDisabled && displayHelper( \'none\' )">  &times;&nbsp; Select None</button>' +
	                                '<button type="button" ng-click="select( \'reset\', $event );"  class="helperButton" ng-if="!isDisabled && displayHelper( \'reset\' )" style="float:right">&#8630;&nbsp; Reset</button>' +
	                            '</div>' +
	                            '<div class="line" style="position:relative" ng-if="displayHelper( \'filter\' )">' +
	                                '<input placeholder="Search..." type="text" ng-click="select( \'filter\', $event )" ng-model="inputLabel.labelFilter" ng-change="updateFilter();$scope.getFormElements();" class="inputFilter" />' +
	                                '<button type="button" class="clearButton" ng-click="inputLabel.labelFilter=\'\';updateFilter();prepareGrouping();prepareIndex();select( \'clear\', $event )">&times;</button> ' +
	                            '</div>' +
	                        '</div>' +
	                        '<div class="checkBoxContainer" style="{{setHeight();}}">' +
	                            '<div ng-repeat="item in filteredModel | filter:removeGroupEndMarker" class="multiSelectItem"' +
	                                'ng-class="{selected: item[ tickProperty ], horizontal: orientationH, vertical: orientationV, multiSelectGroup:item[ groupProperty ], disabled:itemIsDisabled( item )}"' +
	                                'ng-click="syncItems( item, $event, $index );"' +
	                                'ng-mouseleave="removeFocusStyle( tabIndex );">' +
	                                '<div class="acol" ng-if="item[ spacingProperty ] > 0" ng-repeat="i in numberToArray( item[ spacingProperty ] ) track by $index">&nbsp;</div>' +
	                                '<div class="acol">' +
	                                    '<label>' +
	                                        '<input class="checkbox focusable" type="checkbox" ng-disabled="itemIsDisabled( item )" ng-checked="item[ tickProperty ]" ng-click="syncItems( item, $event, $index )" />' +
	                                        '<span ng-class="{disabled:itemIsDisabled( item )}" ng-bind-html="writeLabel( item, \'itemLabel\' )"></span>' +
	                                    '</label>' +
	                                '</div>' +
	                                '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
	                                '<span class="tickMark" ng-if="item[ groupProperty ] !== true && item[ tickProperty ] === true">&#10004;</span>' +
	                            '</div>' +
	                        '</div>' +
	                    '</form>' +
	                '</div>' +
	            '</span>',

	        link: function ( $scope, element, attrs ) {

	            $scope.backUp           = [];
	            $scope.varButtonLabel   = '';
	            $scope.scrolled         = false;
	            $scope.spacingProperty  = '';
	            $scope.indexProperty    = '';
	            $scope.checkBoxLayer    = '';
	            $scope.orientationH     = false;
	            $scope.orientationV     = true;
	            $scope.filteredModel    = [];
	            $scope.inputLabel       = { labelFilter: '' };
	            $scope.selectedItems    = [];
	            $scope.formElements     = [];
	            $scope.tabIndex         = 0;
	            $scope.clickedItem      = null;
	            prevTabIndex            = 0;
	            helperItems             = [];
	            helperItemsLength       = 0;

	            // If user specify a height, call this function
	            $scope.setHeight = function() {
	                if ( typeof $scope.maxHeight !== 'undefined' ) {
	                    return 'max-height: ' + $scope.maxHeight + '; overflow-y:scroll';
	                }
	            }

	            // A little hack so that AngularJS ng-repeat can loop using start and end index like a normal loop
	            // http://stackoverflow.com/questions/16824853/way-to-ng-repeat-defined-number-of-times-instead-of-repeating-over-array
	            $scope.numberToArray = function( num ) {
	                return new Array( num );
	            }

	            $scope.updateFilter = function()
	            {
	                // we check by looping from end of array
	                $scope.filteredModel   = [];
	                var i = 0;

	                if ( typeof $scope.inputModel === 'undefined' ) {
	                    return [];
	                }

	                for( i = $scope.inputModel.length - 1; i >= 0; i-- ) {

	                    // if it's group end
	                    if ( typeof $scope.inputModel[ i ][ $scope.groupProperty ] !== 'undefined' && $scope.inputModel[ i ][ $scope.groupProperty ] === false ) {
	                        $scope.filteredModel.push( $scope.inputModel[ i ] );
	                    }

	                    // if it's data
	                    var gotData = false;
	                    if ( typeof $scope.inputModel[ i ][ $scope.groupProperty ] === 'undefined' ) {

	                        for (var key in $scope.inputModel[ i ] ) {
	                            // if filter string is in one of object property
	                            if ( typeof $scope.inputModel[ i ][ key ] !== 'boolean'  && String( $scope.inputModel[ i ][ key ] ).toUpperCase().indexOf( $scope.inputLabel.labelFilter.toUpperCase() ) >= 0 ) {
	                                gotData = true;
	                                break;
	                            }
	                        }
	                        if ( gotData === true ) {
	                            // push
	                            $scope.filteredModel.push( $scope.inputModel[ i ] );
	                        }
	                    }

	                    // if it's group start
	                    if ( typeof $scope.inputModel[ i ][ $scope.groupProperty ] !== 'undefined' && $scope.inputModel[ i ][ $scope.groupProperty ] === true ) {

	                        if ( typeof $scope.filteredModel[ $scope.filteredModel.length - 1 ][ $scope.groupProperty ] !== 'undefined' && $scope.filteredModel[ $scope.filteredModel.length - 1 ][ $scope.groupProperty ] === false ) {
	                            $scope.filteredModel.pop();
	                        }
	                        else {
	                            $scope.filteredModel.push( $scope.inputModel[ i ] );
	                        }
	                    }
	                }

	                $scope.filteredModel.reverse();
	                $timeout( function() {
	                    $scope.getFormElements();
	                },0);
	            };

	            // List all the input elements.
	            // This function will be called everytime the filter is updated. Not good for performance, but oh well..
	            $scope.getFormElements = function() {
	                $scope.formElements = [];
	                for ( var i = 0; i < element[ 0 ].getElementsByTagName( 'FORM' )[ 0 ].elements.length ; i++ ) {
	                    $scope.formElements.push( element[ 0 ].getElementsByTagName( 'FORM' )[ 0 ].elements[ i ] );
	                }
	            }

	            // check if an item has $scope.groupProperty (be it true or false)
	            $scope.isGroupMarker = function( item , type ) {
	                if ( typeof item[ $scope.groupProperty ] !== 'undefined' && item[ $scope.groupProperty ] === type ) return true;
	                return false;
	            }

	            $scope.removeGroupEndMarker = function( item ) {
	                if ( typeof item[ $scope.groupProperty ] !== 'undefined' && item[ $scope.groupProperty ] === false ) return false;
	                return true;
	            }


	            // Show or hide a helper element
	            $scope.displayHelper = function( elementString ) {

	                if ( attrs.selectionMode && $scope.selectionMode.toUpperCase() === 'SINGLE' ) {

	                    switch( elementString.toUpperCase() ) {
	                        case 'ALL':
	                            return false;
	                            break;
	                        case 'NONE':
	                            return false;
	                            break;
	                        case 'RESET':
	                            if ( typeof attrs.helperElements === 'undefined' ) {
	                                return true;
	                            }
	                            else if ( attrs.helperElements && $scope.helperElements.toUpperCase().indexOf( 'RESET' ) >= 0 ) {
	                                return true;
	                            }
	                            break;
	                        case 'FILTER':
	                            if ( typeof attrs.helperElements === 'undefined' ) {
	                                return true;
	                            }
	                            if ( attrs.helperElements && $scope.helperElements.toUpperCase().indexOf( 'FILTER' ) >= 0 ) {
	                                return true;
	                            }
	                            break;
	                        default:
	                            break;
	                    }

	                    return false;
	                }

	                else {
	                    if ( typeof attrs.helperElements === 'undefined' ) {
	                        return true;
	                    }
	                    if ( attrs.helperElements && $scope.helperElements.toUpperCase().indexOf( elementString.toUpperCase() ) >= 0 ) {
	                        return true;
	                    }
	                    return false;
	                }
	            }

	            // call this function when an item is clicked
	            $scope.syncItems = function( item, e, ng_repeat_index ) {

	                e.preventDefault();
	                e.stopPropagation();

	                // if it's globaly disabled, then don't do anything
	                if ( typeof attrs.disableProperty !== 'undefined' && item[ $scope.disableProperty ] === true ) {
	                    return false;
	                }

	                // don't change disabled items
	                if ( typeof attrs.isDisabled !== 'undefined' && $scope.isDisabled === true ) {
	                    return false;
	                }

	                // we don't care about end of group markers
	                if ( typeof item[ $scope.groupProperty ] !== 'undefined' && item[ $scope.groupProperty ] === false ) {
	                    return false;
	                }

	                index = $scope.filteredModel.indexOf( item );

	                // process items if the start of group marker is clicked ( only for multiple selection! )
	                // if, in a group, there are items which are not selected, then they all will be selected
	                // if, in a group, all items are selected, then they all will be de-selected
	                if ( typeof item[ $scope.groupProperty ] !== 'undefined' && item[ $scope.groupProperty ] === true ) {

	                    if ( attrs.selectionMode && $scope.selectionMode.toUpperCase() === 'SINGLE' ) {
	                        return false;
	                    }

	                    var i,j,k;
	                    var startIndex = 0;
	                    var endIndex = $scope.filteredModel.length - 1;
	                    var tempArr = [];
	                    var nestLevel = 0;

	                    for( i = index ; i < $scope.filteredModel.length ; i++) {

	                        if ( nestLevel === 0 && i > index )
	                        {
	                            break;
	                        }

	                        // if group start
	                        if ( typeof $scope.filteredModel[ i ][ $scope.groupProperty ] !== 'undefined' && $scope.filteredModel[ i ][ $scope.groupProperty ] === true ) {

	                            // To cater multi level grouping
	                            if ( tempArr.length === 0 ) {
	                                startIndex = i + 1;
	                            }
	                            nestLevel = nestLevel + 1;
	                        }

	                        // if group end
	                        else if ( typeof $scope.filteredModel[ i ][ $scope.groupProperty ] !== 'undefined' && $scope.filteredModel[ i ][ $scope.groupProperty ] === false ) {

	                            nestLevel = nestLevel - 1;

	                            // cek if all are ticked or not
	                            if ( tempArr.length > 0 && nestLevel === 0 ) {

	                                var allTicked = true;

	                                endIndex = i;

	                                for ( j = 0; j < tempArr.length ; j++ ) {
	                                    if ( typeof tempArr[ j ][ $scope.tickProperty ] !== 'undefined' &&  tempArr[ j ][ $scope.tickProperty ] === false ) {
	                                        allTicked = false;
	                                        break;
	                                    }
	                                }

	                                if ( allTicked === true ) {
	                                    for ( j = startIndex; j <= endIndex ; j++ ) {
	                                        if ( typeof $scope.filteredModel[ j ][ $scope.groupProperty ] === 'undefined' ) {
	                                            if ( typeof attrs.disableProperty === 'undefined' ) {
	                                                $scope.filteredModel[ j ][ $scope.tickProperty ] = false;
	                                                // we refresh input model as well
	                                                inputModelIndex = $scope.filteredModel[ j ][ $scope.indexProperty ];
	                                                $scope.inputModel[ inputModelIndex ][ $scope.tickProperty ] = false;
	                                            }
	                                            else if ( $scope.filteredModel[ j ][ $scope.disableProperty ] !== true ) {
	                                                $scope.filteredModel[ j ][ $scope.tickProperty ] = false;
	                                                // we refresh input model as well
	                                                inputModelIndex = $scope.filteredModel[ j ][ $scope.indexProperty ];
	                                                $scope.inputModel[ inputModelIndex ][ $scope.tickProperty ] = false;
	                                            }
	                                        }
	                                    }
	                                }

	                                else {
	                                    for ( j = startIndex; j <= endIndex ; j++ ) {
	                                        if ( typeof $scope.filteredModel[ j ][ $scope.groupProperty ] === 'undefined' ) {
	                                            if ( typeof attrs.disableProperty === 'undefined' ) {
	                                                $scope.filteredModel[ j ][ $scope.tickProperty ] = true;
	                                                // we refresh input model as well
	                                                inputModelIndex = $scope.filteredModel[ j ][ $scope.indexProperty ];
	                                                $scope.inputModel[ inputModelIndex ][ $scope.tickProperty ] = true;

	                                            }
	                                            else if ( $scope.filteredModel[ j ][ $scope.disableProperty ] !== true ) {
	                                                $scope.filteredModel[ j ][ $scope.tickProperty ] = true;
	                                                // we refresh input model as well
	                                                inputModelIndex = $scope.filteredModel[ j ][ $scope.indexProperty ];
	                                                $scope.inputModel[ inputModelIndex ][ $scope.tickProperty ] = true;
	                                            }
	                                        }
	                                    }
	                                }
	                            }
	                        }

	                        // if data
	                        else {
	                            tempArr.push( $scope.filteredModel[ i ] );
	                        }
	                    }
	                }

	                // single item click
	                else {

	                    // If it's single selection mode
	                    if ( attrs.selectionMode && $scope.selectionMode.toUpperCase() === 'SINGLE' ) {

	                        // first, set everything to false
	                        for( i=0 ; i < $scope.filteredModel.length ; i++) {
	                            $scope.filteredModel[ i ][ $scope.tickProperty ] = false;
	                        }
	                        for( i=0 ; i < $scope.inputModel.length ; i++) {
	                            $scope.inputModel[ i ][ $scope.tickProperty ] = false;
	                        }

	                        // then set the clicked item to true
	                        $scope.filteredModel[ index ][ $scope.tickProperty ] = true;

	                        $scope.toggleCheckboxes( e );
	                    }

	                    // Multiple
	                    else {
	                        $scope.filteredModel[ index ][ $scope.tickProperty ]   = !$scope.filteredModel[ index ][ $scope.tickProperty ];
	                    }

	                    // we refresh input model as well
	                    inputModelIndex = $scope.filteredModel[ index ][ $scope.indexProperty ];
	                    $scope.inputModel[ inputModelIndex ][ $scope.tickProperty ] = $scope.filteredModel[ index ][ $scope.tickProperty ];
	                }

	                $scope.clickedItem = angular.copy( item );

	                // We update the index here
	                prevTabIndex = $scope.tabIndex;
	                $scope.tabIndex = ng_repeat_index + helperItemsLength;

	                // Set focus on the hidden checkbox
	                e.target.focus();

	                // set & remove CSS style
	                $scope.removeFocusStyle( prevTabIndex );
	                $scope.setFocusStyle( $scope.tabIndex );
	            }

	            // update $scope.selectedItems
	            // this variable is used in $scope.outputModel and to refresh the button label
	            $scope.refreshSelectedItems = function() {
	                $scope.selectedItems    = [];
	                angular.forEach( $scope.inputModel, function( value, key ) {
	                    if ( typeof value !== 'undefined' ) {
	                        if ( typeof value[ $scope.groupProperty ] === 'undefined' ) {
	                            if ( value[ $scope.tickProperty ] === true ) {
	                                $scope.selectedItems.push( value );
	                            }
	                        }
	                    }
	                });
	            }

	            // refresh output model as well
	            $scope.refreshOutputModel = function() {
	                if ( typeof attrs.outputModel !== 'undefined' ) {
	                    $scope.outputModel = angular.copy( $scope.selectedItems );
	                    angular.forEach( $scope.outputModel, function( value, key ) {
	                        // remove the index number and spacing number from output model
	                        delete value[ $scope.indexProperty ];
	                        delete value[ $scope.spacingProperty ];
	                    });
	                }
	            }

	            // refresh button label
	            $scope.refreshButton = function() {

	                $scope.varButtonLabel   = '';
	                ctr                     = 0;

	                // refresh button label...
	                if ( $scope.selectedItems.length === 0 ) {
	                    // https://github.com/isteven/angular-multi-select/pull/19
	                    $scope.varButtonLabel = ( typeof $scope.defaultLabel !== 'undefined' ) ? $scope.defaultLabel : 'None selected';
	                }
	                else {
	                    var tempMaxLabels = $scope.selectedItems.length;
	                    if ( typeof $scope.maxLabels !== 'undefined' && $scope.maxLabels !== '' ) {
	                        tempMaxLabels = $scope.maxLabels;
	                    }

	                    // if max amount of labels displayed..
	                    if ( $scope.selectedItems.length > tempMaxLabels ) {
	                        $scope.more = true;
	                    }
	                    else {
	                        $scope.more = false;
	                    }

	                    angular.forEach( $scope.selectedItems, function( value, key ) {
	                        if ( typeof value !== 'undefined' ) {
	                            if ( ctr < tempMaxLabels ) {
	                                $scope.varButtonLabel += ( $scope.varButtonLabel.length > 0 ? '</div>, <div class="buttonLabel">' : '<div class="buttonLabel">') + $scope.writeLabel( value, 'buttonLabel' );
	                            }
	                            ctr++;
	                        }
	                    });

	                    if ( $scope.more === true ) {
	                        // https://github.com/isteven/angular-multi-select/pull/16
	                        if (tempMaxLabels > 0) {
	                            $scope.varButtonLabel += ', ... ';
	                        }
	                        $scope.varButtonLabel += '(Total: ' + $scope.selectedItems.length + ')';
	                    }
	                }
	                $scope.varButtonLabel = $sce.trustAsHtml( $scope.varButtonLabel + '<span class="caret"></span>' );
	            }

	            // Check if a checkbox is disabled or enabled. It will check the granular control (disableProperty) and global control (isDisabled)
	            // Take note that the granular control has higher priority.
	            $scope.itemIsDisabled = function( item ) {

	                if ( typeof attrs.disableProperty !== 'undefined' && item[ $scope.disableProperty ] === true ) {
	                    return true;
	                }
	                else {
	                    if ( $scope.isDisabled === true ) {
	                        return true;
	                    }
	                    else {
	                        return false;
	                    }
	                }

	            }

	            // A simple function to parse the item label settings
	            $scope.writeLabel = function( item, type ) {
	                var label = '';
	                var temp = $scope[ type ].split( ' ' );
	                angular.forEach( temp, function( value2, key2 ) {
	                    if ( typeof value2 !== 'undefined' ) {
	                        angular.forEach( item, function( value1, key1 ) {
	                            if ( key1 == value2 ) {
	                                label += '&nbsp;' + value1;
	                            }
	                        });
	                    }
	                });
	                if ( type.toUpperCase() === 'BUTTONLABEL' ) {
	                    return label;
	                }
	                return $sce.trustAsHtml( label );
	            }

	            // UI operations to show/hide checkboxes based on click event..
	            $scope.toggleCheckboxes = function( e ) {

	                // We grab the checkboxLayer
	                $scope.checkBoxLayer = element.children()[1];

	                // We grab the button
	                clickedEl = element.children()[0];

	                // Just to make sure.. had a bug where key events were recorded twice
	                angular.element( document ).unbind( 'click', $scope.externalClickListener );
	                angular.element( document ).unbind( 'keydown', $scope.keyboardListener );

	                // clear filter
	                $scope.inputLabel.labelFilter = '';
	                $scope.updateFilter();

	                // close if ESC key is pressed.
	                if ( e.keyCode === 27 ) {
	                    angular.element( $scope.checkBoxLayer ).removeClass( 'show' );
	                    angular.element( clickedEl ).removeClass( 'buttonClicked' );
	                    angular.element( document ).unbind( 'click', $scope.externalClickListener );
	                    angular.element( document ).unbind( 'keydown', $scope.keyboardListener );

	                    // clear the focused element;
	                    $scope.removeFocusStyle( $scope.tabIndex );

	                    // close callback
	                    $scope.onClose( { data: element } );
	                    return true;
	                }

	                // The idea below was taken from another multi-select directive - https://github.com/amitava82/angular-multiselect
	                // His version is awesome if you need a more simple multi-select approach.

	                // close
	                if ( angular.element( $scope.checkBoxLayer ).hasClass( 'show' )) {
	                    angular.element( $scope.checkBoxLayer ).removeClass( 'show' );
	                    angular.element( clickedEl ).removeClass( 'buttonClicked' );
	                    angular.element( document ).unbind( 'click', $scope.externalClickListener );
	                    angular.element( document ).unbind( 'keydown', $scope.keyboardListener );

	                    // clear the focused element;
	                    $scope.removeFocusStyle( $scope.tabIndex );

	                    // close callback
	                    $scope.onClose( { data: element } );
	                }
	                // open
	                else
	                {
	                    helperItems = [];
	                    helperItemsLength = 0;

	                    angular.element( $scope.checkBoxLayer ).addClass( 'show' );
	                    angular.element( clickedEl ).addClass( 'buttonClicked' );
	                    angular.element( document ).bind( 'click', $scope.externalClickListener );
	                    angular.element( document ).bind( 'keydown', $scope.keyboardListener );

	                    // to get the initial tab index, depending on how many helper elements we have.
	                    // priority is to always focus it on the input filter
	                    $scope.getFormElements();
	                    $scope.tabIndex = 0;

	                    var helperContainer = angular.element( element[ 0 ].querySelector( '.helperContainer' ) )[0];

	                    if ( typeof helperContainer !== 'undefined' ) {
	                        for ( i = 0; i < helperContainer.getElementsByTagName( 'BUTTON' ).length ; i++ ) {
	                            helperItems[ i ] = helperContainer.getElementsByTagName( 'BUTTON' )[ i ];
	                        }
	                        helperItemsLength = helperItems.length + helperContainer.getElementsByTagName( 'INPUT' ).length;
	                    }

	                    // focus on the filter element on open.
	                    if ( element[ 0 ].querySelector( '.inputFilter' ) ) {
	                        element[ 0 ].querySelector( '.inputFilter' ).focus();
	                        $scope.tabIndex = $scope.tabIndex + helperItemsLength - 2;
	                    }
	                    // if there's no filter then just focus on the first checkbox item
	                    else {
	                        $scope.formElements[ $scope.tabIndex ].focus();
	                    }

	                    // open callback
	                    $scope.onOpen( { data: element } );
	                }
	            }

	            // handle clicks outside the button / multi select layer
	            $scope.externalClickListener = function( e ) {
	                targetsArr = element.find( e.target.tagName );
	                for (var i = 0; i < targetsArr.length; i++) {
	                    if ( e.target == targetsArr[i] ) {
	                        return;
	                    }
	                }

	                angular.element( $scope.checkBoxLayer.previousSibling ).removeClass( 'buttonClicked' );
	                angular.element( $scope.checkBoxLayer ).removeClass( 'show' );
	                angular.element( document ).unbind( 'click', $scope.externalClickListener );
	                angular.element( document ).unbind( 'keydown', $scope.keyboardListener );

	                // close callback
	                $timeout( function() {
	                    $scope.onClose( { data: element } );
	                }, 0 );
	            }

	            // traverse up to find the button tag
	            // http://stackoverflow.com/questions/7332179/how-to-recursively-search-all-parentnodes
	            $scope.findUpTag = function ( el, tag, className ) {
	                while ( el.parentNode ) {
	                    el = el.parentNode;
	                    if ( typeof el.tagName !== 'undefined' ) {
	                        if ( el.tagName.toUpperCase() === tag.toUpperCase() && el.className.indexOf( className ) > -1 ) {
	                            return el;
	                        }
	                    }
	                }
	                return null;
	            }

	            // select All / select None / reset buttons
	            $scope.select = function( type, e ) {

	                helperIndex = helperItems.indexOf( e.target );
	                $scope.tabIndex = helperIndex;

	                switch( type.toUpperCase() ) {
	                    case 'ALL':
	                        angular.forEach( $scope.filteredModel, function( value, key ) {
	                            if ( typeof value !== 'undefined' && value[ $scope.disableProperty ] !== true ) {
	                                if ( typeof value[ $scope.groupProperty ] === 'undefined' ) {
	                                    value[ $scope.tickProperty ] = true;
	                                }
	                            }
	                        });
	                        break;
	                    case 'NONE':
	                        angular.forEach( $scope.filteredModel, function( value, key ) {
	                            if ( typeof value !== 'undefined' && value[ $scope.disableProperty ] !== true ) {
	                                if ( typeof value[ $scope.groupProperty ] === 'undefined' ) {
	                                    value[ $scope.tickProperty ] = false;
	                                }
	                            }
	                        });
	                        break;
	                    case 'RESET':
	                        angular.forEach( $scope.filteredModel, function( value, key ) {
	                            if ( typeof value[ $scope.groupProperty ] === 'undefined' && typeof value !== 'undefined' && value[ $scope.disableProperty ] !== true ) {
	                                temp = value[ $scope.indexProperty ];
	                                value[ $scope.tickProperty ] = $scope.backUp[ temp ][ $scope.tickProperty ];
	                            }
	                        });
	                        break;
	                    case 'CLEAR':
	                        $scope.tabIndex = $scope.tabIndex + 1;
	                        break;
	                    case 'FILTER':
	                        $scope.tabIndex = helperItems.length - 1;
	                        break;
	                    default:
	                }
	            }

	            // just to create a random variable name
	            genRandomString = function( length ) {
	                var possible    = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
	                var temp        = '';
	                for( var i=0; i < length; i++ ) {
	                     temp += possible.charAt( Math.floor( Math.random() * possible.length ));
	                }
	                return temp;
	            }

	            // count leading spaces
	            $scope.prepareGrouping = function() {
	                var spacing     = 0;
	                angular.forEach( $scope.filteredModel, function( value, key ) {
	                    value[ $scope.spacingProperty ] = spacing;
	                    if ( value[ $scope.groupProperty ] === true ) {
	                        spacing+=2;
	                    }
	                    else if ( value[ $scope.groupProperty ] === false ) {
	                        spacing-=2;
	                    }
	                });
	            }

	            // prepare original index
	            $scope.prepareIndex = function() {
	                ctr = 0;
	                angular.forEach( $scope.filteredModel, function( value, key ) {
	                    value[ $scope.indexProperty ] = ctr;
	                    ctr++;
	                });
	            }

	            // navigate using up and down arrow
	            $scope.keyboardListener = function( e ) {

	                var key = e.keyCode ? e.keyCode : e.which;
	                var isNavigationKey = false;

	                // ESC key (close)
	                if ( key === 27 ) {
	                    $scope.toggleCheckboxes( e );
	                }

	                // next element ( tab, down & right key )
	                else if ( key === 40 || key === 39 || ( !e.shiftKey && key == 9 ) ) {
	                    isNavigationKey = true;
	                    prevTabIndex = $scope.tabIndex;
	                    $scope.tabIndex++;
	                    if ( $scope.tabIndex > $scope.formElements.length - 1 ) {
	                        $scope.tabIndex = 0;
	                        prevTabIndex = $scope.formElements.length - 1;
	                    }
	                    while ( $scope.formElements[ $scope.tabIndex ].disabled === true ) {
	                        $scope.tabIndex++;
	                        if ( $scope.tabIndex > $scope.formElements.length - 1 ) {
	                            $scope.tabIndex = 0;
	                        }
	                    }
	                }

	                // prev element ( shift+tab, up & left key )
	                else if ( key === 38 || key === 37 || ( e.shiftKey && key == 9 ) ) {
	                    isNavigationKey = true;
	                    prevTabIndex = $scope.tabIndex;
	                    $scope.tabIndex--;
	                    if ( $scope.tabIndex < 0 ) {
	                        $scope.tabIndex = $scope.formElements.length - 1;
	                        prevTabIndex = 0;
	                    }
	                    while ( $scope.formElements[ $scope.tabIndex ].disabled === true ) {
	                        $scope.tabIndex--;
	                        if ( $scope.tabIndex < 0 ) {
	                            $scope.tabIndex = $scope.formElements.length - 1;
	                        }
	                    }
	                }

	                if ( isNavigationKey === true ) {

	                    e.preventDefault();
	                    e.stopPropagation();

	                    // set focus on the checkbox
	                    $scope.formElements[ $scope.tabIndex ].focus();

	                    // css styling
	                    var actEl = document.activeElement;

	                    if ( actEl.type.toUpperCase() === 'CHECKBOX' ) {
	                        $scope.setFocusStyle( $scope.tabIndex );
	                        $scope.removeFocusStyle( prevTabIndex );
	                    }
	                    else {
	                        $scope.removeFocusStyle( prevTabIndex );
	                        $scope.removeFocusStyle( helperItemsLength );
	                        $scope.removeFocusStyle( $scope.formElements.length - 1 );
	                    }
	                }

	                isNavigationKey = false;
	            }

	            // set (add) CSS style on selected row
	            $scope.setFocusStyle = function( tabIndex ) {
	                angular.element( $scope.formElements[ tabIndex ] ).parent().parent().parent().addClass( 'multiSelectFocus' );
	            }

	            // remove CSS style on selected row
	            $scope.removeFocusStyle = function( tabIndex ) {
	                angular.element( $scope.formElements[ tabIndex ] ).parent().parent().parent().removeClass( 'multiSelectFocus' );
	            }

	            ///////////////////////////////////////////////////////
	            //
	            // Logic starts here, initiated by watch 1 & watch 2.
	            //
	            ///////////////////////////////////////////////////////

	            var tempStr = genRandomString( 5 );
	            $scope.indexProperty = 'idx_' + tempStr;
	            $scope.spacingProperty = 'spc_' + tempStr;

	            // set orientation css
	            if ( typeof attrs.orientation !== 'undefined' ) {
	                if ( attrs.orientation.toUpperCase() === 'HORIZONTAL' ) {
	                    $scope.orientationH = true;
	                    $scope.orientationV = false;
	                }
	                else {
	                    $scope.orientationH = false;
	                    $scope.orientationV = true;
	                }
	            }

	            // watch1, for changes in input model property
	            // updates multi-select when user select/deselect a single checkbox programatically
	            // https://github.com/isteven/angular-multi-select/issues/8
	            $scope.$watch( 'inputModel' , function( newVal ) {
	                if ( newVal ) {
	                    $scope.refreshSelectedItems();
	                    $scope.refreshOutputModel();
	                    $scope.refreshButton();
	                    if ( $scope.clickedItem !== null ) {
	                        $timeout( function() {
	                            $scope.onItemClick( { data: $scope.clickedItem } );
	                            $scope.clickedItem = null;
	                        }, 0 );
	                    }
	                }
	            }, true);

	            // watch2 for changes in input model as a whole
	            // this on updates the multi-select when a user load a whole new input-model. We also update the $scope.backUp variable
	            $scope.$watch( 'inputModel' , function( newVal ) {
	                if ( newVal ) {
	                    $scope.backUp = angular.copy( $scope.inputModel );
	                    $scope.updateFilter();
	                    $scope.prepareGrouping();
	                    $scope.prepareIndex();
	                    $scope.refreshSelectedItems();
	                    $scope.refreshOutputModel();
	                    $scope.refreshButton();
	                }
	            });

	            // watch for changes in directive state (disabled or enabled)
	            $scope.$watch( 'isDisabled' , function( newVal ) {
	                $scope.isDisabled = newVal;
	            });

	            // this is for touch enabled devices. We don't want to hide checkboxes on scroll.
	            angular.element( document ).bind( 'touchstart', function( e ) {
	                $scope.$apply( function() {
	                    $scope.scrolled = false;
	                });
	            });

	            // also for touch enabled devices
	            angular.element( document ).bind( 'touchmove', function( e ) {
	                $scope.$apply( function() {
	                    $scope.scrolled = true;
	                });
	            });

	            // for IE8, perhaps. Not sure if this is really executed.
	            if ( !Array.prototype.indexOf ) {
	                Array.prototype.indexOf = function(what, i) {
	                    i = i || 0;
	                    var L = this.length;
	                    while (i < L) {
	                        if(this[i] === what) return i;
	                        ++i;
	                    }
	                    return -1;
	                };
	            }
	        }
	    }
	}]);


/***/ }),

/***/ 193:
/***/ (function(module, exports) {

	/**
	 * State-based routing for AngularJS
	 * @version v0.2.11
	 * @link http://angular-ui.github.com/
	 * @license MIT License, http://www.opensource.org/licenses/MIT
	 */

	/* commonjs package manager support (eg componentjs) */
	if (typeof module !== "undefined" && typeof exports !== "undefined" && module.exports === exports){
	  module.exports = 'ui.router';
	}

	(function (window, angular, undefined) {
	/*jshint globalstrict:true*/
	/*global angular:false*/
	'use strict';

	var isDefined = angular.isDefined,
	    isFunction = angular.isFunction,
	    isString = angular.isString,
	    isObject = angular.isObject,
	    isArray = angular.isArray,
	    forEach = angular.forEach,
	    extend = angular.extend,
	    copy = angular.copy;

	function inherit(parent, extra) {
	  return extend(new (extend(function() {}, { prototype: parent }))(), extra);
	}

	function merge(dst) {
	  forEach(arguments, function(obj) {
	    if (obj !== dst) {
	      forEach(obj, function(value, key) {
	        if (!dst.hasOwnProperty(key)) dst[key] = value;
	      });
	    }
	  });
	  return dst;
	}

	/**
	 * Finds the common ancestor path between two states.
	 *
	 * @param {Object} first The first state.
	 * @param {Object} second The second state.
	 * @return {Array} Returns an array of state names in descending order, not including the root.
	 */
	function ancestors(first, second) {
	  var path = [];

	  for (var n in first.path) {
	    if (first.path[n] !== second.path[n]) break;
	    path.push(first.path[n]);
	  }
	  return path;
	}

	/**
	 * IE8-safe wrapper for `Object.keys()`.
	 *
	 * @param {Object} object A JavaScript object.
	 * @return {Array} Returns the keys of the object as an array.
	 */
	function objectKeys(object) {
	  if (Object.keys) {
	    return Object.keys(object);
	  }
	  var result = [];

	  angular.forEach(object, function(val, key) {
	    result.push(key);
	  });
	  return result;
	}

	/**
	 * IE8-safe wrapper for `Array.prototype.indexOf()`.
	 *
	 * @param {Array} array A JavaScript array.
	 * @param {*} value A value to search the array for.
	 * @return {Number} Returns the array index value of `value`, or `-1` if not present.
	 */
	function arraySearch(array, value) {
	  if (Array.prototype.indexOf) {
	    return array.indexOf(value, Number(arguments[2]) || 0);
	  }
	  var len = array.length >>> 0, from = Number(arguments[2]) || 0;
	  from = (from < 0) ? Math.ceil(from) : Math.floor(from);

	  if (from < 0) from += len;

	  for (; from < len; from++) {
	    if (from in array && array[from] === value) return from;
	  }
	  return -1;
	}

	/**
	 * Merges a set of parameters with all parameters inherited between the common parents of the
	 * current state and a given destination state.
	 *
	 * @param {Object} currentParams The value of the current state parameters ($stateParams).
	 * @param {Object} newParams The set of parameters which will be composited with inherited params.
	 * @param {Object} $current Internal definition of object representing the current state.
	 * @param {Object} $to Internal definition of object representing state to transition to.
	 */
	function inheritParams(currentParams, newParams, $current, $to) {
	  var parents = ancestors($current, $to), parentParams, inherited = {}, inheritList = [];

	  for (var i in parents) {
	    if (!parents[i].params) continue;
	    parentParams = objectKeys(parents[i].params);
	    if (!parentParams.length) continue;

	    for (var j in parentParams) {
	      if (arraySearch(inheritList, parentParams[j]) >= 0) continue;
	      inheritList.push(parentParams[j]);
	      inherited[parentParams[j]] = currentParams[parentParams[j]];
	    }
	  }
	  return extend({}, inherited, newParams);
	}

	/**
	 * Performs a non-strict comparison of the subset of two objects, defined by a list of keys.
	 *
	 * @param {Object} a The first object.
	 * @param {Object} b The second object.
	 * @param {Array} keys The list of keys within each object to compare. If the list is empty or not specified,
	 *                     it defaults to the list of keys in `a`.
	 * @return {Boolean} Returns `true` if the keys match, otherwise `false`.
	 */
	function equalForKeys(a, b, keys) {
	  if (!keys) {
	    keys = [];
	    for (var n in a) keys.push(n); // Used instead of Object.keys() for IE8 compatibility
	  }

	  for (var i=0; i<keys.length; i++) {
	    var k = keys[i];
	    if (a[k] != b[k]) return false; // Not '===', values aren't necessarily normalized
	  }
	  return true;
	}

	/**
	 * Returns the subset of an object, based on a list of keys.
	 *
	 * @param {Array} keys
	 * @param {Object} values
	 * @return {Boolean} Returns a subset of `values`.
	 */
	function filterByKeys(keys, values) {
	  var filtered = {};

	  forEach(keys, function (name) {
	    filtered[name] = values[name];
	  });
	  return filtered;
	}
	/**
	 * @ngdoc overview
	 * @name ui.router.util
	 *
	 * @description
	 * # ui.router.util sub-module
	 *
	 * This module is a dependency of other sub-modules. Do not include this module as a dependency
	 * in your angular app (use {@link ui.router} module instead).
	 *
	 */
	angular.module('ui.router.util', ['ng']);

	/**
	 * @ngdoc overview
	 * @name ui.router.router
	 *
	 * @requires ui.router.util
	 *
	 * @description
	 * # ui.router.router sub-module
	 *
	 * This module is a dependency of other sub-modules. Do not include this module as a dependency
	 * in your angular app (use {@link ui.router} module instead).
	 */
	angular.module('ui.router.router', ['ui.router.util']);

	/**
	 * @ngdoc overview
	 * @name ui.router.state
	 *
	 * @requires ui.router.router
	 * @requires ui.router.util
	 *
	 * @description
	 * # ui.router.state sub-module
	 *
	 * This module is a dependency of the main ui.router module. Do not include this module as a dependency
	 * in your angular app (use {@link ui.router} module instead).
	 *
	 */
	angular.module('ui.router.state', ['ui.router.router', 'ui.router.util']);

	/**
	 * @ngdoc overview
	 * @name ui.router
	 *
	 * @requires ui.router.state
	 *
	 * @description
	 * # ui.router
	 *
	 * ## The main module for ui.router
	 * There are several sub-modules included with the ui.router module, however only this module is needed
	 * as a dependency within your angular app. The other modules are for organization purposes.
	 *
	 * The modules are:
	 * * ui.router - the main "umbrella" module
	 * * ui.router.router -
	 *
	 * *You'll need to include **only** this module as the dependency within your angular app.*
	 *
	 * <pre>
	 * <!doctype html>
	 * <html ng-app="myApp">
	 * <head>
	 *   <script src="js/angular.js"></script>
	 *   <!-- Include the ui-router script -->
	 *   <script src="js/angular-ui-router.min.js"></script>
	 *   <script>
	 *     // ...and add 'ui.router' as a dependency
	 *     var myApp = angular.module('myApp', ['ui.router']);
	 *   </script>
	 * </head>
	 * <body>
	 * </body>
	 * </html>
	 * </pre>
	 */
	angular.module('ui.router', ['ui.router.state']);

	angular.module('ui.router.compat', ['ui.router']);

	/**
	 * @ngdoc object
	 * @name ui.router.util.$resolve
	 *
	 * @requires $q
	 * @requires $injector
	 *
	 * @description
	 * Manages resolution of (acyclic) graphs of promises.
	 */
	$Resolve.$inject = ['$q', '$injector'];
	function $Resolve(  $q,    $injector) {

	  var VISIT_IN_PROGRESS = 1,
	      VISIT_DONE = 2,
	      NOTHING = {},
	      NO_DEPENDENCIES = [],
	      NO_LOCALS = NOTHING,
	      NO_PARENT = extend($q.when(NOTHING), { $$promises: NOTHING, $$values: NOTHING });


	  /**
	   * @ngdoc function
	   * @name ui.router.util.$resolve#study
	   * @methodOf ui.router.util.$resolve
	   *
	   * @description
	   * Studies a set of invocables that are likely to be used multiple times.
	   * <pre>
	   * $resolve.study(invocables)(locals, parent, self)
	   * </pre>
	   * is equivalent to
	   * <pre>
	   * $resolve.resolve(invocables, locals, parent, self)
	   * </pre>
	   * but the former is more efficient (in fact `resolve` just calls `study`
	   * internally).
	   *
	   * @param {object} invocables Invocable objects
	   * @return {function} a function to pass in locals, parent and self
	   */
	  this.study = function (invocables) {
	    if (!isObject(invocables)) throw new Error("'invocables' must be an object");

	    // Perform a topological sort of invocables to build an ordered plan
	    var plan = [], cycle = [], visited = {};
	    function visit(value, key) {
	      if (visited[key] === VISIT_DONE) return;

	      cycle.push(key);
	      if (visited[key] === VISIT_IN_PROGRESS) {
	        cycle.splice(0, cycle.indexOf(key));
	        throw new Error("Cyclic dependency: " + cycle.join(" -> "));
	      }
	      visited[key] = VISIT_IN_PROGRESS;

	      if (isString(value)) {
	        plan.push(key, [ function() { return $injector.get(value); }], NO_DEPENDENCIES);
	      } else {
	        var params = $injector.annotate(value);
	        forEach(params, function (param) {
	          if (param !== key && invocables.hasOwnProperty(param)) visit(invocables[param], param);
	        });
	        plan.push(key, value, params);
	      }

	      cycle.pop();
	      visited[key] = VISIT_DONE;
	    }
	    forEach(invocables, visit);
	    invocables = cycle = visited = null; // plan is all that's required

	    function isResolve(value) {
	      return isObject(value) && value.then && value.$$promises;
	    }

	    return function (locals, parent, self) {
	      if (isResolve(locals) && self === undefined) {
	        self = parent; parent = locals; locals = null;
	      }
	      if (!locals) locals = NO_LOCALS;
	      else if (!isObject(locals)) {
	        throw new Error("'locals' must be an object");
	      }
	      if (!parent) parent = NO_PARENT;
	      else if (!isResolve(parent)) {
	        throw new Error("'parent' must be a promise returned by $resolve.resolve()");
	      }

	      // To complete the overall resolution, we have to wait for the parent
	      // promise and for the promise for each invokable in our plan.
	      var resolution = $q.defer(),
	          result = resolution.promise,
	          promises = result.$$promises = {},
	          values = extend({}, locals),
	          wait = 1 + plan.length/3,
	          merged = false;

	      function done() {
	        // Merge parent values we haven't got yet and publish our own $$values
	        if (!--wait) {
	          if (!merged) merge(values, parent.$$values);
	          result.$$values = values;
	          result.$$promises = true; // keep for isResolve()
	          delete result.$$inheritedValues;
	          resolution.resolve(values);
	        }
	      }

	      function fail(reason) {
	        result.$$failure = reason;
	        resolution.reject(reason);
	      }

	      // Short-circuit if parent has already failed
	      if (isDefined(parent.$$failure)) {
	        fail(parent.$$failure);
	        return result;
	      }

	      if (parent.$$inheritedValues) {
	        merge(values, parent.$$inheritedValues);
	      }

	      // Merge parent values if the parent has already resolved, or merge
	      // parent promises and wait if the parent resolve is still in progress.
	      if (parent.$$values) {
	        merged = merge(values, parent.$$values);
	        result.$$inheritedValues = parent.$$values;
	        done();
	      } else {
	        if (parent.$$inheritedValues) {
	          result.$$inheritedValues = parent.$$inheritedValues;
	        }
	        extend(promises, parent.$$promises);
	        parent.then(done, fail);
	      }

	      // Process each invocable in the plan, but ignore any where a local of the same name exists.
	      for (var i=0, ii=plan.length; i<ii; i+=3) {
	        if (locals.hasOwnProperty(plan[i])) done();
	        else invoke(plan[i], plan[i+1], plan[i+2]);
	      }

	      function invoke(key, invocable, params) {
	        // Create a deferred for this invocation. Failures will propagate to the resolution as well.
	        var invocation = $q.defer(), waitParams = 0;
	        function onfailure(reason) {
	          invocation.reject(reason);
	          fail(reason);
	        }
	        // Wait for any parameter that we have a promise for (either from parent or from this
	        // resolve; in that case study() will have made sure it's ordered before us in the plan).
	        forEach(params, function (dep) {
	          if (promises.hasOwnProperty(dep) && !locals.hasOwnProperty(dep)) {
	            waitParams++;
	            promises[dep].then(function (result) {
	              values[dep] = result;
	              if (!(--waitParams)) proceed();
	            }, onfailure);
	          }
	        });
	        if (!waitParams) proceed();
	        function proceed() {
	          if (isDefined(result.$$failure)) return;
	          try {
	            invocation.resolve($injector.invoke(invocable, self, values));
	            invocation.promise.then(function (result) {
	              values[key] = result;
	              done();
	            }, onfailure);
	          } catch (e) {
	            onfailure(e);
	          }
	        }
	        // Publish promise synchronously; invocations further down in the plan may depend on it.
	        promises[key] = invocation.promise;
	      }

	      return result;
	    };
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$resolve#resolve
	   * @methodOf ui.router.util.$resolve
	   *
	   * @description
	   * Resolves a set of invocables. An invocable is a function to be invoked via
	   * `$injector.invoke()`, and can have an arbitrary number of dependencies.
	   * An invocable can either return a value directly,
	   * or a `$q` promise. If a promise is returned it will be resolved and the
	   * resulting value will be used instead. Dependencies of invocables are resolved
	   * (in this order of precedence)
	   *
	   * - from the specified `locals`
	   * - from another invocable that is part of this `$resolve` call
	   * - from an invocable that is inherited from a `parent` call to `$resolve`
	   *   (or recursively
	   * - from any ancestor `$resolve` of that parent).
	   *
	   * The return value of `$resolve` is a promise for an object that contains
	   * (in this order of precedence)
	   *
	   * - any `locals` (if specified)
	   * - the resolved return values of all injectables
	   * - any values inherited from a `parent` call to `$resolve` (if specified)
	   *
	   * The promise will resolve after the `parent` promise (if any) and all promises
	   * returned by injectables have been resolved. If any invocable
	   * (or `$injector.invoke`) throws an exception, or if a promise returned by an
	   * invocable is rejected, the `$resolve` promise is immediately rejected with the
	   * same error. A rejection of a `parent` promise (if specified) will likewise be
	   * propagated immediately. Once the `$resolve` promise has been rejected, no
	   * further invocables will be called.
	   *
	   * Cyclic dependencies between invocables are not permitted and will caues `$resolve`
	   * to throw an error. As a special case, an injectable can depend on a parameter
	   * with the same name as the injectable, which will be fulfilled from the `parent`
	   * injectable of the same name. This allows inherited values to be decorated.
	   * Note that in this case any other injectable in the same `$resolve` with the same
	   * dependency would see the decorated value, not the inherited value.
	   *
	   * Note that missing dependencies -- unlike cyclic dependencies -- will cause an
	   * (asynchronous) rejection of the `$resolve` promise rather than a (synchronous)
	   * exception.
	   *
	   * Invocables are invoked eagerly as soon as all dependencies are available.
	   * This is true even for dependencies inherited from a `parent` call to `$resolve`.
	   *
	   * As a special case, an invocable can be a string, in which case it is taken to
	   * be a service name to be passed to `$injector.get()`. This is supported primarily
	   * for backwards-compatibility with the `resolve` property of `$routeProvider`
	   * routes.
	   *
	   * @param {object} invocables functions to invoke or
	   * `$injector` services to fetch.
	   * @param {object} locals  values to make available to the injectables
	   * @param {object} parent  a promise returned by another call to `$resolve`.
	   * @param {object} self  the `this` for the invoked methods
	   * @return {object} Promise for an object that contains the resolved return value
	   * of all invocables, as well as any inherited and local values.
	   */
	  this.resolve = function (invocables, locals, parent, self) {
	    return this.study(invocables)(locals, parent, self);
	  };
	}

	angular.module('ui.router.util').service('$resolve', $Resolve);


	/**
	 * @ngdoc object
	 * @name ui.router.util.$templateFactory
	 *
	 * @requires $http
	 * @requires $templateCache
	 * @requires $injector
	 *
	 * @description
	 * Service. Manages loading of templates.
	 */
	$TemplateFactory.$inject = ['$http', '$templateCache', '$injector'];
	function $TemplateFactory(  $http,   $templateCache,   $injector) {

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$templateFactory#fromConfig
	   * @methodOf ui.router.util.$templateFactory
	   *
	   * @description
	   * Creates a template from a configuration object.
	   *
	   * @param {object} config Configuration object for which to load a template.
	   * The following properties are search in the specified order, and the first one
	   * that is defined is used to create the template:
	   *
	   * @param {string|object} config.template html string template or function to
	   * load via {@link ui.router.util.$templateFactory#fromString fromString}.
	   * @param {string|object} config.templateUrl url to load or a function returning
	   * the url to load via {@link ui.router.util.$templateFactory#fromUrl fromUrl}.
	   * @param {Function} config.templateProvider function to invoke via
	   * {@link ui.router.util.$templateFactory#fromProvider fromProvider}.
	   * @param {object} params  Parameters to pass to the template function.
	   * @param {object} locals Locals to pass to `invoke` if the template is loaded
	   * via a `templateProvider`. Defaults to `{ params: params }`.
	   *
	   * @return {string|object}  The template html as a string, or a promise for
	   * that string,or `null` if no template is configured.
	   */
	  this.fromConfig = function (config, params, locals) {
	    return (
	      isDefined(config.template) ? this.fromString(config.template, params) :
	      isDefined(config.templateUrl) ? this.fromUrl(config.templateUrl, params) :
	      isDefined(config.templateProvider) ? this.fromProvider(config.templateProvider, params, locals) :
	      null
	    );
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$templateFactory#fromString
	   * @methodOf ui.router.util.$templateFactory
	   *
	   * @description
	   * Creates a template from a string or a function returning a string.
	   *
	   * @param {string|object} template html template as a string or function that
	   * returns an html template as a string.
	   * @param {object} params Parameters to pass to the template function.
	   *
	   * @return {string|object} The template html as a string, or a promise for that
	   * string.
	   */
	  this.fromString = function (template, params) {
	    return isFunction(template) ? template(params) : template;
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$templateFactory#fromUrl
	   * @methodOf ui.router.util.$templateFactory
	   *
	   * @description
	   * Loads a template from the a URL via `$http` and `$templateCache`.
	   *
	   * @param {string|Function} url url of the template to load, or a function
	   * that returns a url.
	   * @param {Object} params Parameters to pass to the url function.
	   * @return {string|Promise.<string>} The template html as a string, or a promise
	   * for that string.
	   */
	  this.fromUrl = function (url, params) {
	    if (isFunction(url)) url = url(params);
	    if (url == null) return null;
	    else return $http
	        .get(url, { cache: $templateCache })
	        .then(function(response) { return response.data; });
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$templateFactory#fromProvider
	   * @methodOf ui.router.util.$templateFactory
	   *
	   * @description
	   * Creates a template by invoking an injectable provider function.
	   *
	   * @param {Function} provider Function to invoke via `$injector.invoke`
	   * @param {Object} params Parameters for the template.
	   * @param {Object} locals Locals to pass to `invoke`. Defaults to
	   * `{ params: params }`.
	   * @return {string|Promise.<string>} The template html as a string, or a promise
	   * for that string.
	   */
	  this.fromProvider = function (provider, params, locals) {
	    return $injector.invoke(provider, null, locals || { params: params });
	  };
	}

	angular.module('ui.router.util').service('$templateFactory', $TemplateFactory);

	/**
	 * @ngdoc object
	 * @name ui.router.util.type:UrlMatcher
	 *
	 * @description
	 * Matches URLs against patterns and extracts named parameters from the path or the search
	 * part of the URL. A URL pattern consists of a path pattern, optionally followed by '?' and a list
	 * of search parameters. Multiple search parameter names are separated by '&'. Search parameters
	 * do not influence whether or not a URL is matched, but their values are passed through into
	 * the matched parameters returned by {@link ui.router.util.type:UrlMatcher#methods_exec exec}.
	 *
	 * Path parameter placeholders can be specified using simple colon/catch-all syntax or curly brace
	 * syntax, which optionally allows a regular expression for the parameter to be specified:
	 *
	 * * `':'` name - colon placeholder
	 * * `'*'` name - catch-all placeholder
	 * * `'{' name '}'` - curly placeholder
	 * * `'{' name ':' regexp '}'` - curly placeholder with regexp. Should the regexp itself contain
	 *   curly braces, they must be in matched pairs or escaped with a backslash.
	 *
	 * Parameter names may contain only word characters (latin letters, digits, and underscore) and
	 * must be unique within the pattern (across both path and search parameters). For colon
	 * placeholders or curly placeholders without an explicit regexp, a path parameter matches any
	 * number of characters other than '/'. For catch-all placeholders the path parameter matches
	 * any number of characters.
	 *
	 * Examples:
	 *
	 * * `'/hello/'` - Matches only if the path is exactly '/hello/'. There is no special treatment for
	 *   trailing slashes, and patterns have to match the entire path, not just a prefix.
	 * * `'/user/:id'` - Matches '/user/bob' or '/user/1234!!!' or even '/user/' but not '/user' or
	 *   '/user/bob/details'. The second path segment will be captured as the parameter 'id'.
	 * * `'/user/{id}'` - Same as the previous example, but using curly brace syntax.
	 * * `'/user/{id:[^/]*}'` - Same as the previous example.
	 * * `'/user/{id:[0-9a-fA-F]{1,8}}'` - Similar to the previous example, but only matches if the id
	 *   parameter consists of 1 to 8 hex digits.
	 * * `'/files/{path:.*}'` - Matches any URL starting with '/files/' and captures the rest of the
	 *   path into the parameter 'path'.
	 * * `'/files/*path'` - ditto.
	 *
	 * @param {string} pattern  The pattern to compile into a matcher.
	 * @param {Object} config  A configuration object hash:
	 *
	 * * `caseInsensitive` - `true` if URL matching should be case insensitive, otherwise `false`, the default value (for backward compatibility) is `false`.
	 * * `strict` - `false` if matching against a URL with a trailing slash should be treated as equivalent to a URL without a trailing slash, the default value is `true`.
	 *
	 * @property {string} prefix  A static prefix of this pattern. The matcher guarantees that any
	 *   URL matching this matcher (i.e. any string for which {@link ui.router.util.type:UrlMatcher#methods_exec exec()} returns
	 *   non-null) will start with this prefix.
	 *
	 * @property {string} source  The pattern that was passed into the constructor
	 *
	 * @property {string} sourcePath  The path portion of the source property
	 *
	 * @property {string} sourceSearch  The search portion of the source property
	 *
	 * @property {string} regex  The constructed regex that will be used to match against the url when
	 *   it is time to determine which url will match.
	 *
	 * @returns {Object}  New `UrlMatcher` object
	 */
	function UrlMatcher(pattern, config) {
	  config = angular.isObject(config) ? config : {};

	  // Find all placeholders and create a compiled pattern, using either classic or curly syntax:
	  //   '*' name
	  //   ':' name
	  //   '{' name '}'
	  //   '{' name ':' regexp '}'
	  // The regular expression is somewhat complicated due to the need to allow curly braces
	  // inside the regular expression. The placeholder regexp breaks down as follows:
	  //    ([:*])(\w+)               classic placeholder ($1 / $2)
	  //    \{(\w+)(?:\:( ... ))?\}   curly brace placeholder ($3) with optional regexp ... ($4)
	  //    (?: ... | ... | ... )+    the regexp consists of any number of atoms, an atom being either
	  //    [^{}\\]+                  - anything other than curly braces or backslash
	  //    \\.                       - a backslash escape
	  //    \{(?:[^{}\\]+|\\.)*\}     - a matched set of curly braces containing other atoms
	  var placeholder = /([:*])(\w+)|\{(\w+)(?:\:((?:[^{}\\]+|\\.|\{(?:[^{}\\]+|\\.)*\})+))?\}/g,
	      compiled = '^', last = 0, m,
	      segments = this.segments = [],
	      params = this.params = {};

	  /**
	   * [Internal] Gets the decoded representation of a value if the value is defined, otherwise, returns the
	   * default value, which may be the result of an injectable function.
	   */
	  function $value(value) {
	    /*jshint validthis: true */
	    return isDefined(value) ? this.type.decode(value) : $UrlMatcherFactory.$$getDefaultValue(this);
	  }

	  function addParameter(id, type, config) {
	    if (!/^\w+(-+\w+)*$/.test(id)) throw new Error("Invalid parameter name '" + id + "' in pattern '" + pattern + "'");
	    if (params[id]) throw new Error("Duplicate parameter name '" + id + "' in pattern '" + pattern + "'");
	    params[id] = extend({ type: type || new Type(), $value: $value }, config);
	  }

	  function quoteRegExp(string, pattern, isOptional) {
	    var result = string.replace(/[\\\[\]\^$*+?.()|{}]/g, "\\$&");
	    if (!pattern) return result;
	    var flag = isOptional ? '?' : '';
	    return result + flag + '(' + pattern + ')' + flag;
	  }

	  function paramConfig(param) {
	    if (!config.params || !config.params[param]) return {};
	    var cfg = config.params[param];
	    return isObject(cfg) ? cfg : { value: cfg };
	  }

	  this.source = pattern;

	  // Split into static segments separated by path parameter placeholders.
	  // The number of segments is always 1 more than the number of parameters.
	  var id, regexp, segment, type, cfg;

	  while ((m = placeholder.exec(pattern))) {
	    id      = m[2] || m[3]; // IE[78] returns '' for unmatched groups instead of null
	    regexp  = m[4] || (m[1] == '*' ? '.*' : '[^/]*');
	    segment = pattern.substring(last, m.index);
	    type    = this.$types[regexp] || new Type({ pattern: new RegExp(regexp) });
	    cfg     = paramConfig(id);

	    if (segment.indexOf('?') >= 0) break; // we're into the search part

	    compiled += quoteRegExp(segment, type.$subPattern(), isDefined(cfg.value));
	    addParameter(id, type, cfg);
	    segments.push(segment);
	    last = placeholder.lastIndex;
	  }
	  segment = pattern.substring(last);

	  // Find any search parameter names and remove them from the last segment
	  var i = segment.indexOf('?');

	  if (i >= 0) {
	    var search = this.sourceSearch = segment.substring(i);
	    segment = segment.substring(0, i);
	    this.sourcePath = pattern.substring(0, last + i);

	    // Allow parameters to be separated by '?' as well as '&' to make concat() easier
	    forEach(search.substring(1).split(/[&?]/), function(key) {
	      addParameter(key, null, paramConfig(key));
	    });
	  } else {
	    this.sourcePath = pattern;
	    this.sourceSearch = '';
	  }

	  compiled += quoteRegExp(segment) + (config.strict === false ? '\/?' : '') + '$';
	  segments.push(segment);

	  this.regexp = new RegExp(compiled, config.caseInsensitive ? 'i' : undefined);
	  this.prefix = segments[0];
	}

	/**
	 * @ngdoc function
	 * @name ui.router.util.type:UrlMatcher#concat
	 * @methodOf ui.router.util.type:UrlMatcher
	 *
	 * @description
	 * Returns a new matcher for a pattern constructed by appending the path part and adding the
	 * search parameters of the specified pattern to this pattern. The current pattern is not
	 * modified. This can be understood as creating a pattern for URLs that are relative to (or
	 * suffixes of) the current pattern.
	 *
	 * @example
	 * The following two matchers are equivalent:
	 * <pre>
	 * new UrlMatcher('/user/{id}?q').concat('/details?date');
	 * new UrlMatcher('/user/{id}/details?q&date');
	 * </pre>
	 *
	 * @param {string} pattern  The pattern to append.
	 * @param {Object} config  An object hash of the configuration for the matcher.
	 * @returns {UrlMatcher}  A matcher for the concatenated pattern.
	 */
	UrlMatcher.prototype.concat = function (pattern, config) {
	  // Because order of search parameters is irrelevant, we can add our own search
	  // parameters to the end of the new pattern. Parse the new pattern by itself
	  // and then join the bits together, but it's much easier to do this on a string level.
	  return new UrlMatcher(this.sourcePath + pattern + this.sourceSearch, config);
	};

	UrlMatcher.prototype.toString = function () {
	  return this.source;
	};

	/**
	 * @ngdoc function
	 * @name ui.router.util.type:UrlMatcher#exec
	 * @methodOf ui.router.util.type:UrlMatcher
	 *
	 * @description
	 * Tests the specified path against this matcher, and returns an object containing the captured
	 * parameter values, or null if the path does not match. The returned object contains the values
	 * of any search parameters that are mentioned in the pattern, but their value may be null if
	 * they are not present in `searchParams`. This means that search parameters are always treated
	 * as optional.
	 *
	 * @example
	 * <pre>
	 * new UrlMatcher('/user/{id}?q&r').exec('/user/bob', {
	 *   x: '1', q: 'hello'
	 * });
	 * // returns { id: 'bob', q: 'hello', r: null }
	 * </pre>
	 *
	 * @param {string} path  The URL path to match, e.g. `$location.path()`.
	 * @param {Object} searchParams  URL search parameters, e.g. `$location.search()`.
	 * @returns {Object}  The captured parameter values.
	 */
	UrlMatcher.prototype.exec = function (path, searchParams) {
	  var m = this.regexp.exec(path);
	  if (!m) return null;
	  searchParams = searchParams || {};

	  var params = this.parameters(), nTotal = params.length,
	    nPath = this.segments.length - 1,
	    values = {}, i, cfg, param;

	  if (nPath !== m.length - 1) throw new Error("Unbalanced capture group in route '" + this.source + "'");

	  for (i = 0; i < nPath; i++) {
	    param = params[i];
	    cfg = this.params[param];
	    values[param] = cfg.$value(m[i + 1]);
	  }
	  for (/**/; i < nTotal; i++) {
	    param = params[i];
	    cfg = this.params[param];
	    values[param] = cfg.$value(searchParams[param]);
	  }

	  return values;
	};

	/**
	 * @ngdoc function
	 * @name ui.router.util.type:UrlMatcher#parameters
	 * @methodOf ui.router.util.type:UrlMatcher
	 *
	 * @description
	 * Returns the names of all path and search parameters of this pattern in an unspecified order.
	 *
	 * @returns {Array.<string>}  An array of parameter names. Must be treated as read-only. If the
	 *    pattern has no parameters, an empty array is returned.
	 */
	UrlMatcher.prototype.parameters = function (param) {
	  if (!isDefined(param)) return objectKeys(this.params);
	  return this.params[param] || null;
	};

	/**
	 * @ngdoc function
	 * @name ui.router.util.type:UrlMatcher#validate
	 * @methodOf ui.router.util.type:UrlMatcher
	 *
	 * @description
	 * Checks an object hash of parameters to validate their correctness according to the parameter
	 * types of this `UrlMatcher`.
	 *
	 * @param {Object} params The object hash of parameters to validate.
	 * @returns {boolean} Returns `true` if `params` validates, otherwise `false`.
	 */
	UrlMatcher.prototype.validates = function (params) {
	  var result = true, isOptional, cfg, self = this;

	  forEach(params, function(val, key) {
	    if (!self.params[key]) return;
	    cfg = self.params[key];
	    isOptional = !val && isDefined(cfg.value);
	    result = result && (isOptional || cfg.type.is(val));
	  });
	  return result;
	};

	/**
	 * @ngdoc function
	 * @name ui.router.util.type:UrlMatcher#format
	 * @methodOf ui.router.util.type:UrlMatcher
	 *
	 * @description
	 * Creates a URL that matches this pattern by substituting the specified values
	 * for the path and search parameters. Null values for path parameters are
	 * treated as empty strings.
	 *
	 * @example
	 * <pre>
	 * new UrlMatcher('/user/{id}?q').format({ id:'bob', q:'yes' });
	 * // returns '/user/bob?q=yes'
	 * </pre>
	 *
	 * @param {Object} values  the values to substitute for the parameters in this pattern.
	 * @returns {string}  the formatted URL (path and optionally search part).
	 */
	UrlMatcher.prototype.format = function (values) {
	  var segments = this.segments, params = this.parameters();

	  if (!values) return segments.join('').replace('//', '/');

	  var nPath = segments.length - 1, nTotal = params.length,
	    result = segments[0], i, search, value, param, cfg, array;

	  if (!this.validates(values)) return null;

	  for (i = 0; i < nPath; i++) {
	    param = params[i];
	    value = values[param];
	    cfg   = this.params[param];

	    if (!isDefined(value) && (segments[i] === '/' || segments[i + 1] === '/')) continue;
	    if (value != null) result += encodeURIComponent(cfg.type.encode(value));
	    result += segments[i + 1];
	  }

	  for (/**/; i < nTotal; i++) {
	    param = params[i];
	    value = values[param];
	    if (value == null) continue;
	    array = isArray(value);

	    if (array) {
	      value = value.map(encodeURIComponent).join('&' + param + '=');
	    }
	    result += (search ? '&' : '?') + param + '=' + (array ? value : encodeURIComponent(value));
	    search = true;
	  }
	  return result;
	};

	UrlMatcher.prototype.$types = {};

	/**
	 * @ngdoc object
	 * @name ui.router.util.type:Type
	 *
	 * @description
	 * Implements an interface to define custom parameter types that can be decoded from and encoded to
	 * string parameters matched in a URL. Used by {@link ui.router.util.type:UrlMatcher `UrlMatcher`}
	 * objects when matching or formatting URLs, or comparing or validating parameter values.
	 *
	 * See {@link ui.router.util.$urlMatcherFactory#methods_type `$urlMatcherFactory#type()`} for more
	 * information on registering custom types.
	 *
	 * @param {Object} config  A configuration object hash that includes any method in `Type`'s public
	 *        interface, and/or `pattern`, which should contain a custom regular expression used to match
	 *        string parameters originating from a URL.
	 *
	 * @property {RegExp} pattern The regular expression pattern used to match values of this type when
	 *           coming from a substring of a URL.
	 *
	 * @returns {Object}  Returns a new `Type` object.
	 */
	function Type(config) {
	  extend(this, config);
	}

	/**
	 * @ngdoc function
	 * @name ui.router.util.type:Type#is
	 * @methodOf ui.router.util.type:Type
	 *
	 * @description
	 * Detects whether a value is of a particular type. Accepts a native (decoded) value
	 * and determines whether it matches the current `Type` object.
	 *
	 * @param {*} val  The value to check.
	 * @param {string} key  Optional. If the type check is happening in the context of a specific
	 *        {@link ui.router.util.type:UrlMatcher `UrlMatcher`} object, this is the name of the
	 *        parameter in which `val` is stored. Can be used for meta-programming of `Type` objects.
	 * @returns {Boolean}  Returns `true` if the value matches the type, otherwise `false`.
	 */
	Type.prototype.is = function(val, key) {
	  return true;
	};

	/**
	 * @ngdoc function
	 * @name ui.router.util.type:Type#encode
	 * @methodOf ui.router.util.type:Type
	 *
	 * @description
	 * Encodes a custom/native type value to a string that can be embedded in a URL. Note that the
	 * return value does *not* need to be URL-safe (i.e. passed through `encodeURIComponent()`), it
	 * only needs to be a representation of `val` that has been coerced to a string.
	 *
	 * @param {*} val  The value to encode.
	 * @param {string} key  The name of the parameter in which `val` is stored. Can be used for
	 *        meta-programming of `Type` objects.
	 * @returns {string}  Returns a string representation of `val` that can be encoded in a URL.
	 */
	Type.prototype.encode = function(val, key) {
	  return val;
	};

	/**
	 * @ngdoc function
	 * @name ui.router.util.type:Type#decode
	 * @methodOf ui.router.util.type:Type
	 *
	 * @description
	 * Converts a string URL parameter value to a custom/native value.
	 *
	 * @param {string} val  The URL parameter value to decode.
	 * @param {string} key  The name of the parameter in which `val` is stored. Can be used for
	 *        meta-programming of `Type` objects.
	 * @returns {*}  Returns a custom representation of the URL parameter value.
	 */
	Type.prototype.decode = function(val, key) {
	  return val;
	};

	/**
	 * @ngdoc function
	 * @name ui.router.util.type:Type#equals
	 * @methodOf ui.router.util.type:Type
	 *
	 * @description
	 * Determines whether two decoded values are equivalent.
	 *
	 * @param {*} a  A value to compare against.
	 * @param {*} b  A value to compare against.
	 * @returns {Boolean}  Returns `true` if the values are equivalent/equal, otherwise `false`.
	 */
	Type.prototype.equals = function(a, b) {
	  return a == b;
	};

	Type.prototype.$subPattern = function() {
	  var sub = this.pattern.toString();
	  return sub.substr(1, sub.length - 2);
	};

	Type.prototype.pattern = /.*/;

	/**
	 * @ngdoc object
	 * @name ui.router.util.$urlMatcherFactory
	 *
	 * @description
	 * Factory for {@link ui.router.util.type:UrlMatcher `UrlMatcher`} instances. The factory
	 * is also available to providers under the name `$urlMatcherFactoryProvider`.
	 */
	function $UrlMatcherFactory() {

	  var isCaseInsensitive = false, isStrictMode = true;

	  var enqueue = true, typeQueue = [], injector, defaultTypes = {
	    int: {
	      decode: function(val) {
	        return parseInt(val, 10);
	      },
	      is: function(val) {
	        if (!isDefined(val)) return false;
	        return this.decode(val.toString()) === val;
	      },
	      pattern: /\d+/
	    },
	    bool: {
	      encode: function(val) {
	        return val ? 1 : 0;
	      },
	      decode: function(val) {
	        return parseInt(val, 10) === 0 ? false : true;
	      },
	      is: function(val) {
	        return val === true || val === false;
	      },
	      pattern: /0|1/
	    },
	    string: {
	      pattern: /[^\/]*/
	    },
	    date: {
	      equals: function (a, b) {
	        return a.toISOString() === b.toISOString();
	      },
	      decode: function (val) {
	        return new Date(val);
	      },
	      encode: function (val) {
	        return [
	          val.getFullYear(),
	          ('0' + (val.getMonth() + 1)).slice(-2),
	          ('0' + val.getDate()).slice(-2)
	        ].join("-");
	      },
	      pattern: /[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2][0-9]|3[0-1])/
	    }
	  };

	  function getDefaultConfig() {
	    return {
	      strict: isStrictMode,
	      caseInsensitive: isCaseInsensitive
	    };
	  }

	  function isInjectable(value) {
	    return (isFunction(value) || (isArray(value) && isFunction(value[value.length - 1])));
	  }

	  /**
	   * [Internal] Get the default value of a parameter, which may be an injectable function.
	   */
	  $UrlMatcherFactory.$$getDefaultValue = function(config) {
	    if (!isInjectable(config.value)) return config.value;
	    if (!injector) throw new Error("Injectable functions cannot be called at configuration time");
	    return injector.invoke(config.value);
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$urlMatcherFactory#caseInsensitive
	   * @methodOf ui.router.util.$urlMatcherFactory
	   *
	   * @description
	   * Defines whether URL matching should be case sensitive (the default behavior), or not.
	   *
	   * @param {boolean} value `false` to match URL in a case sensitive manner; otherwise `true`;
	   */
	  this.caseInsensitive = function(value) {
	    isCaseInsensitive = value;
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$urlMatcherFactory#strictMode
	   * @methodOf ui.router.util.$urlMatcherFactory
	   *
	   * @description
	   * Defines whether URLs should match trailing slashes, or not (the default behavior).
	   *
	   * @param {boolean} value `false` to match trailing slashes in URLs, otherwise `true`.
	   */
	  this.strictMode = function(value) {
	    isStrictMode = value;
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$urlMatcherFactory#compile
	   * @methodOf ui.router.util.$urlMatcherFactory
	   *
	   * @description
	   * Creates a {@link ui.router.util.type:UrlMatcher `UrlMatcher`} for the specified pattern.
	   *
	   * @param {string} pattern  The URL pattern.
	   * @param {Object} config  The config object hash.
	   * @returns {UrlMatcher}  The UrlMatcher.
	   */
	  this.compile = function (pattern, config) {
	    return new UrlMatcher(pattern, extend(getDefaultConfig(), config));
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$urlMatcherFactory#isMatcher
	   * @methodOf ui.router.util.$urlMatcherFactory
	   *
	   * @description
	   * Returns true if the specified object is a `UrlMatcher`, or false otherwise.
	   *
	   * @param {Object} object  The object to perform the type check against.
	   * @returns {Boolean}  Returns `true` if the object matches the `UrlMatcher` interface, by
	   *          implementing all the same methods.
	   */
	  this.isMatcher = function (o) {
	    if (!isObject(o)) return false;
	    var result = true;

	    forEach(UrlMatcher.prototype, function(val, name) {
	      if (isFunction(val)) {
	        result = result && (isDefined(o[name]) && isFunction(o[name]));
	      }
	    });
	    return result;
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.util.$urlMatcherFactory#type
	   * @methodOf ui.router.util.$urlMatcherFactory
	   *
	   * @description
	   * Registers a custom {@link ui.router.util.type:Type `Type`} object that can be used to
	   * generate URLs with typed parameters.
	   *
	   * @param {string} name  The type name.
	   * @param {Object|Function} def  The type definition. See
	   *        {@link ui.router.util.type:Type `Type`} for information on the values accepted.
	   *
	   * @returns {Object}  Returns `$urlMatcherFactoryProvider`.
	   *
	   * @example
	   * This is a simple example of a custom type that encodes and decodes items from an
	   * array, using the array index as the URL-encoded value:
	   *
	   * <pre>
	   * var list = ['John', 'Paul', 'George', 'Ringo'];
	   *
	   * $urlMatcherFactoryProvider.type('listItem', {
	   *   encode: function(item) {
	   *     // Represent the list item in the URL using its corresponding index
	   *     return list.indexOf(item);
	   *   },
	   *   decode: function(item) {
	   *     // Look up the list item by index
	   *     return list[parseInt(item, 10)];
	   *   },
	   *   is: function(item) {
	   *     // Ensure the item is valid by checking to see that it appears
	   *     // in the list
	   *     return list.indexOf(item) > -1;
	   *   }
	   * });
	   *
	   * $stateProvider.state('list', {
	   *   url: "/list/{item:listItem}",
	   *   controller: function($scope, $stateParams) {
	   *     console.log($stateParams.item);
	   *   }
	   * });
	   *
	   * // ...
	   *
	   * // Changes URL to '/list/3', logs "Ringo" to the console
	   * $state.go('list', { item: "Ringo" });
	   * </pre>
	   *
	   * This is a more complex example of a type that relies on dependency injection to
	   * interact with services, and uses the parameter name from the URL to infer how to
	   * handle encoding and decoding parameter values:
	   *
	   * <pre>
	   * // Defines a custom type that gets a value from a service,
	   * // where each service gets different types of values from
	   * // a backend API:
	   * $urlMatcherFactoryProvider.type('dbObject', function(Users, Posts) {
	   *
	   *   // Matches up services to URL parameter names
	   *   var services = {
	   *     user: Users,
	   *     post: Posts
	   *   };
	   *
	   *   return {
	   *     encode: function(object) {
	   *       // Represent the object in the URL using its unique ID
	   *       return object.id;
	   *     },
	   *     decode: function(value, key) {
	   *       // Look up the object by ID, using the parameter
	   *       // name (key) to call the correct service
	   *       return services[key].findById(value);
	   *     },
	   *     is: function(object, key) {
	   *       // Check that object is a valid dbObject
	   *       return angular.isObject(object) && object.id && services[key];
	   *     }
	   *     equals: function(a, b) {
	   *       // Check the equality of decoded objects by comparing
	   *       // their unique IDs
	   *       return a.id === b.id;
	   *     }
	   *   };
	   * });
	   *
	   * // In a config() block, you can then attach URLs with
	   * // type-annotated parameters:
	   * $stateProvider.state('users', {
	   *   url: "/users",
	   *   // ...
	   * }).state('users.item', {
	   *   url: "/{user:dbObject}",
	   *   controller: function($scope, $stateParams) {
	   *     // $stateParams.user will now be an object returned from
	   *     // the Users service
	   *   },
	   *   // ...
	   * });
	   * </pre>
	   */
	  this.type = function (name, def) {
	    if (!isDefined(def)) return UrlMatcher.prototype.$types[name];
	    typeQueue.push({ name: name, def: def });
	    if (!enqueue) flushTypeQueue();
	    return this;
	  };

	  /* No need to document $get, since it returns this */
	  this.$get = ['$injector', function ($injector) {
	    injector = $injector;
	    enqueue = false;
	    UrlMatcher.prototype.$types = {};
	    flushTypeQueue();

	    forEach(defaultTypes, function(type, name) {
	      if (!UrlMatcher.prototype.$types[name]) UrlMatcher.prototype.$types[name] = new Type(type);
	    });
	    return this;
	  }];

	  // To ensure proper order of operations in object configuration, and to allow internal
	  // types to be overridden, `flushTypeQueue()` waits until `$urlMatcherFactory` is injected
	  // before actually wiring up and assigning type definitions
	  function flushTypeQueue() {
	    forEach(typeQueue, function(type) {
	      if (UrlMatcher.prototype.$types[type.name]) {
	        throw new Error("A type named '" + type.name + "' has already been defined.");
	      }
	      var def = new Type(isInjectable(type.def) ? injector.invoke(type.def) : type.def);
	      UrlMatcher.prototype.$types[type.name] = def;
	    });
	  }
	}

	// Register as a provider so it's available to other providers
	angular.module('ui.router.util').provider('$urlMatcherFactory', $UrlMatcherFactory);

	/**
	 * @ngdoc object
	 * @name ui.router.router.$urlRouterProvider
	 *
	 * @requires ui.router.util.$urlMatcherFactoryProvider
	 * @requires $locationProvider
	 *
	 * @description
	 * `$urlRouterProvider` has the responsibility of watching `$location`.
	 * When `$location` changes it runs through a list of rules one by one until a
	 * match is found. `$urlRouterProvider` is used behind the scenes anytime you specify
	 * a url in a state configuration. All urls are compiled into a UrlMatcher object.
	 *
	 * There are several methods on `$urlRouterProvider` that make it useful to use directly
	 * in your module config.
	 */
	$UrlRouterProvider.$inject = ['$locationProvider', '$urlMatcherFactoryProvider'];
	function $UrlRouterProvider(   $locationProvider,   $urlMatcherFactory) {
	  var rules = [], otherwise = null, interceptDeferred = false, listener;

	  // Returns a string that is a prefix of all strings matching the RegExp
	  function regExpPrefix(re) {
	    var prefix = /^\^((?:\\[^a-zA-Z0-9]|[^\\\[\]\^$*+?.()|{}]+)*)/.exec(re.source);
	    return (prefix != null) ? prefix[1].replace(/\\(.)/g, "$1") : '';
	  }

	  // Interpolates matched values into a String.replace()-style pattern
	  function interpolate(pattern, match) {
	    return pattern.replace(/\$(\$|\d{1,2})/, function (m, what) {
	      return match[what === '$' ? 0 : Number(what)];
	    });
	  }

	  /**
	   * @ngdoc function
	   * @name ui.router.router.$urlRouterProvider#rule
	   * @methodOf ui.router.router.$urlRouterProvider
	   *
	   * @description
	   * Defines rules that are used by `$urlRouterProvider` to find matches for
	   * specific URLs.
	   *
	   * @example
	   * <pre>
	   * var app = angular.module('app', ['ui.router.router']);
	   *
	   * app.config(function ($urlRouterProvider) {
	   *   // Here's an example of how you might allow case insensitive urls
	   *   $urlRouterProvider.rule(function ($injector, $location) {
	   *     var path = $location.path(),
	   *         normalized = path.toLowerCase();
	   *
	   *     if (path !== normalized) {
	   *       return normalized;
	   *     }
	   *   });
	   * });
	   * </pre>
	   *
	   * @param {object} rule Handler function that takes `$injector` and `$location`
	   * services as arguments. You can use them to return a valid path as a string.
	   *
	   * @return {object} `$urlRouterProvider` - `$urlRouterProvider` instance
	   */
	  this.rule = function (rule) {
	    if (!isFunction(rule)) throw new Error("'rule' must be a function");
	    rules.push(rule);
	    return this;
	  };

	  /**
	   * @ngdoc object
	   * @name ui.router.router.$urlRouterProvider#otherwise
	   * @methodOf ui.router.router.$urlRouterProvider
	   *
	   * @description
	   * Defines a path that is used when an invalid route is requested.
	   *
	   * @example
	   * <pre>
	   * var app = angular.module('app', ['ui.router.router']);
	   *
	   * app.config(function ($urlRouterProvider) {
	   *   // if the path doesn't match any of the urls you configured
	   *   // otherwise will take care of routing the user to the
	   *   // specified url
	   *   $urlRouterProvider.otherwise('/index');
	   *
	   *   // Example of using function rule as param
	   *   $urlRouterProvider.otherwise(function ($injector, $location) {
	   *     return '/a/valid/url';
	   *   });
	   * });
	   * </pre>
	   *
	   * @param {string|object} rule The url path you want to redirect to or a function
	   * rule that returns the url path. The function version is passed two params:
	   * `$injector` and `$location` services, and must return a url string.
	   *
	   * @return {object} `$urlRouterProvider` - `$urlRouterProvider` instance
	   */
	  this.otherwise = function (rule) {
	    if (isString(rule)) {
	      var redirect = rule;
	      rule = function () { return redirect; };
	    }
	    else if (!isFunction(rule)) throw new Error("'rule' must be a function");
	    otherwise = rule;
	    return this;
	  };


	  function handleIfMatch($injector, handler, match) {
	    if (!match) return false;
	    var result = $injector.invoke(handler, handler, { $match: match });
	    return isDefined(result) ? result : true;
	  }

	  /**
	   * @ngdoc function
	   * @name ui.router.router.$urlRouterProvider#when
	   * @methodOf ui.router.router.$urlRouterProvider
	   *
	   * @description
	   * Registers a handler for a given url matching. if handle is a string, it is
	   * treated as a redirect, and is interpolated according to the syntax of match
	   * (i.e. like `String.replace()` for `RegExp`, or like a `UrlMatcher` pattern otherwise).
	   *
	   * If the handler is a function, it is injectable. It gets invoked if `$location`
	   * matches. You have the option of inject the match object as `$match`.
	   *
	   * The handler can return
	   *
	   * - **falsy** to indicate that the rule didn't match after all, then `$urlRouter`
	   *   will continue trying to find another one that matches.
	   * - **string** which is treated as a redirect and passed to `$location.url()`
	   * - **void** or any **truthy** value tells `$urlRouter` that the url was handled.
	   *
	   * @example
	   * <pre>
	   * var app = angular.module('app', ['ui.router.router']);
	   *
	   * app.config(function ($urlRouterProvider) {
	   *   $urlRouterProvider.when($state.url, function ($match, $stateParams) {
	   *     if ($state.$current.navigable !== state ||
	   *         !equalForKeys($match, $stateParams) {
	   *      $state.transitionTo(state, $match, false);
	   *     }
	   *   });
	   * });
	   * </pre>
	   *
	   * @param {string|object} what The incoming path that you want to redirect.
	   * @param {string|object} handler The path you want to redirect your user to.
	   */
	  this.when = function (what, handler) {
	    var redirect, handlerIsString = isString(handler);
	    if (isString(what)) what = $urlMatcherFactory.compile(what);

	    if (!handlerIsString && !isFunction(handler) && !isArray(handler))
	      throw new Error("invalid 'handler' in when()");

	    var strategies = {
	      matcher: function (what, handler) {
	        if (handlerIsString) {
	          redirect = $urlMatcherFactory.compile(handler);
	          handler = ['$match', function ($match) { return redirect.format($match); }];
	        }
	        return extend(function ($injector, $location) {
	          return handleIfMatch($injector, handler, what.exec($location.path(), $location.search()));
	        }, {
	          prefix: isString(what.prefix) ? what.prefix : ''
	        });
	      },
	      regex: function (what, handler) {
	        if (what.global || what.sticky) throw new Error("when() RegExp must not be global or sticky");

	        if (handlerIsString) {
	          redirect = handler;
	          handler = ['$match', function ($match) { return interpolate(redirect, $match); }];
	        }
	        return extend(function ($injector, $location) {
	          return handleIfMatch($injector, handler, what.exec($location.path()));
	        }, {
	          prefix: regExpPrefix(what)
	        });
	      }
	    };

	    var check = { matcher: $urlMatcherFactory.isMatcher(what), regex: what instanceof RegExp };

	    for (var n in check) {
	      if (check[n]) return this.rule(strategies[n](what, handler));
	    }

	    throw new Error("invalid 'what' in when()");
	  };

	  /**
	   * @ngdoc function
	   * @name ui.router.router.$urlRouterProvider#deferIntercept
	   * @methodOf ui.router.router.$urlRouterProvider
	   *
	   * @description
	   * Disables (or enables) deferring location change interception.
	   *
	   * If you wish to customize the behavior of syncing the URL (for example, if you wish to
	   * defer a transition but maintain the current URL), call this method at configuration time.
	   * Then, at run time, call `$urlRouter.listen()` after you have configured your own
	   * `$locationChangeSuccess` event handler.
	   *
	   * @example
	   * <pre>
	   * var app = angular.module('app', ['ui.router.router']);
	   *
	   * app.config(function ($urlRouterProvider) {
	   *
	   *   // Prevent $urlRouter from automatically intercepting URL changes;
	   *   // this allows you to configure custom behavior in between
	   *   // location changes and route synchronization:
	   *   $urlRouterProvider.deferIntercept();
	   *
	   * }).run(function ($rootScope, $urlRouter, UserService) {
	   *
	   *   $rootScope.$on('$locationChangeSuccess', function(e) {
	   *     // UserService is an example service for managing user state
	   *     if (UserService.isLoggedIn()) return;
	   *
	   *     // Prevent $urlRouter's default handler from firing
	   *     e.preventDefault();
	   *
	   *     UserService.handleLogin().then(function() {
	   *       // Once the user has logged in, sync the current URL
	   *       // to the router:
	   *       $urlRouter.sync();
	   *     });
	   *   });
	   *
	   *   // Configures $urlRouter's listener *after* your custom listener
	   *   $urlRouter.listen();
	   * });
	   * </pre>
	   *
	   * @param {boolean} defer Indicates whether to defer location change interception. Passing
	            no parameter is equivalent to `true`.
	   */
	  this.deferIntercept = function (defer) {
	    if (defer === undefined) defer = true;
	    interceptDeferred = defer;
	  };

	  /**
	   * @ngdoc object
	   * @name ui.router.router.$urlRouter
	   *
	   * @requires $location
	   * @requires $rootScope
	   * @requires $injector
	   * @requires $browser
	   *
	   * @description
	   *
	   */
	  this.$get = $get;
	  $get.$inject = ['$location', '$rootScope', '$injector', '$browser'];
	  function $get(   $location,   $rootScope,   $injector,   $browser) {

	    var baseHref = $browser.baseHref(), location = $location.url();

	    function appendBasePath(url, isHtml5, absolute) {
	      if (baseHref === '/') return url;
	      if (isHtml5) return baseHref.slice(0, -1) + url;
	      if (absolute) return baseHref.slice(1) + url;
	      return url;
	    }

	    // TODO: Optimize groups of rules with non-empty prefix into some sort of decision tree
	    function update(evt) {
	      if (evt && evt.defaultPrevented) return;

	      function check(rule) {
	        var handled = rule($injector, $location);

	        if (!handled) return false;
	        if (isString(handled)) $location.replace().url(handled);
	        return true;
	      }
	      var n = rules.length, i;

	      for (i = 0; i < n; i++) {
	        if (check(rules[i])) return;
	      }
	      // always check otherwise last to allow dynamic updates to the set of rules
	      if (otherwise) check(otherwise);
	    }

	    function listen() {
	      listener = listener || $rootScope.$on('$locationChangeSuccess', update);
	      return listener;
	    }

	    if (!interceptDeferred) listen();

	    return {
	      /**
	       * @ngdoc function
	       * @name ui.router.router.$urlRouter#sync
	       * @methodOf ui.router.router.$urlRouter
	       *
	       * @description
	       * Triggers an update; the same update that happens when the address bar url changes, aka `$locationChangeSuccess`.
	       * This method is useful when you need to use `preventDefault()` on the `$locationChangeSuccess` event,
	       * perform some custom logic (route protection, auth, config, redirection, etc) and then finally proceed
	       * with the transition by calling `$urlRouter.sync()`.
	       *
	       * @example
	       * <pre>
	       * angular.module('app', ['ui.router'])
	       *   .run(function($rootScope, $urlRouter) {
	       *     $rootScope.$on('$locationChangeSuccess', function(evt) {
	       *       // Halt state change from even starting
	       *       evt.preventDefault();
	       *       // Perform custom logic
	       *       var meetsRequirement = ...
	       *       // Continue with the update and state transition if logic allows
	       *       if (meetsRequirement) $urlRouter.sync();
	       *     });
	       * });
	       * </pre>
	       */
	      sync: function() {
	        update();
	      },

	      listen: function() {
	        return listen();
	      },

	      update: function(read) {
	        if (read) {
	          location = $location.url();
	          return;
	        }
	        if ($location.url() === location) return;

	        $location.url(location);
	        $location.replace();
	      },

	      push: function(urlMatcher, params, options) {
	        $location.url(urlMatcher.format(params || {}));
	        if (options && options.replace) $location.replace();
	      },

	      /**
	       * @ngdoc function
	       * @name ui.router.router.$urlRouter#href
	       * @methodOf ui.router.router.$urlRouter
	       *
	       * @description
	       * A URL generation method that returns the compiled URL for a given
	       * {@link ui.router.util.type:UrlMatcher `UrlMatcher`}, populated with the provided parameters.
	       *
	       * @example
	       * <pre>
	       * $bob = $urlRouter.href(new UrlMatcher("/about/:person"), {
	       *   person: "bob"
	       * });
	       * // $bob == "/about/bob";
	       * </pre>
	       *
	       * @param {UrlMatcher} urlMatcher The `UrlMatcher` object which is used as the template of the URL to generate.
	       * @param {object=} params An object of parameter values to fill the matcher's required parameters.
	       * @param {object=} options Options object. The options are:
	       *
	       * - **`absolute`** - {boolean=false},  If true will generate an absolute url, e.g. "http://www.example.com/fullurl".
	       *
	       * @returns {string} Returns the fully compiled URL, or `null` if `params` fail validation against `urlMatcher`
	       */
	      href: function(urlMatcher, params, options) {
	        if (!urlMatcher.validates(params)) return null;

	        var isHtml5 = $locationProvider.html5Mode();
	        var url = urlMatcher.format(params);
	        options = options || {};

	        if (!isHtml5 && url !== null) {
	          url = "#" + $locationProvider.hashPrefix() + url;
	        }
	        url = appendBasePath(url, isHtml5, options.absolute);

	        if (!options.absolute || !url) {
	          return url;
	        }

	        var slash = (!isHtml5 && url ? '/' : ''), port = $location.port();
	        port = (port === 80 || port === 443 ? '' : ':' + port);

	        return [$location.protocol(), '://', $location.host(), port, slash, url].join('');
	      }
	    };
	  }
	}

	angular.module('ui.router.router').provider('$urlRouter', $UrlRouterProvider);

	/**
	 * @ngdoc object
	 * @name ui.router.state.$stateProvider
	 *
	 * @requires ui.router.router.$urlRouterProvider
	 * @requires ui.router.util.$urlMatcherFactoryProvider
	 *
	 * @description
	 * The new `$stateProvider` works similar to Angular's v1 router, but it focuses purely
	 * on state.
	 *
	 * A state corresponds to a "place" in the application in terms of the overall UI and
	 * navigation. A state describes (via the controller / template / view properties) what
	 * the UI looks like and does at that place.
	 *
	 * States often have things in common, and the primary way of factoring out these
	 * commonalities in this model is via the state hierarchy, i.e. parent/child states aka
	 * nested states.
	 *
	 * The `$stateProvider` provides interfaces to declare these states for your app.
	 */
	$StateProvider.$inject = ['$urlRouterProvider', '$urlMatcherFactoryProvider'];
	function $StateProvider(   $urlRouterProvider,   $urlMatcherFactory) {

	  var root, states = {}, $state, queue = {}, abstractKey = 'abstract';

	  // Builds state properties from definition passed to registerState()
	  var stateBuilder = {

	    // Derive parent state from a hierarchical name only if 'parent' is not explicitly defined.
	    // state.children = [];
	    // if (parent) parent.children.push(state);
	    parent: function(state) {
	      if (isDefined(state.parent) && state.parent) return findState(state.parent);
	      // regex matches any valid composite state name
	      // would match "contact.list" but not "contacts"
	      var compositeName = /^(.+)\.[^.]+$/.exec(state.name);
	      return compositeName ? findState(compositeName[1]) : root;
	    },

	    // inherit 'data' from parent and override by own values (if any)
	    data: function(state) {
	      if (state.parent && state.parent.data) {
	        state.data = state.self.data = extend({}, state.parent.data, state.data);
	      }
	      return state.data;
	    },

	    // Build a URLMatcher if necessary, either via a relative or absolute URL
	    url: function(state) {
	      var url = state.url, config = { params: state.params || {} };

	      if (isString(url)) {
	        if (url.charAt(0) == '^') return $urlMatcherFactory.compile(url.substring(1), config);
	        return (state.parent.navigable || root).url.concat(url, config);
	      }

	      if (!url || $urlMatcherFactory.isMatcher(url)) return url;
	      throw new Error("Invalid url '" + url + "' in state '" + state + "'");
	    },

	    // Keep track of the closest ancestor state that has a URL (i.e. is navigable)
	    navigable: function(state) {
	      return state.url ? state : (state.parent ? state.parent.navigable : null);
	    },

	    // Derive parameters for this state and ensure they're a super-set of parent's parameters
	    params: function(state) {
	      if (!state.params) {
	        return state.url ? state.url.params : state.parent.params;
	      }
	      return state.params;
	    },

	    // If there is no explicit multi-view configuration, make one up so we don't have
	    // to handle both cases in the view directive later. Note that having an explicit
	    // 'views' property will mean the default unnamed view properties are ignored. This
	    // is also a good time to resolve view names to absolute names, so everything is a
	    // straight lookup at link time.
	    views: function(state) {
	      var views = {};

	      forEach(isDefined(state.views) ? state.views : { '': state }, function (view, name) {
	        if (name.indexOf('@') < 0) name += '@' + state.parent.name;
	        views[name] = view;
	      });
	      return views;
	    },

	    ownParams: function(state) {
	      state.params = state.params || {};

	      if (!state.parent) {
	          return objectKeys(state.params);
	      }
	      var paramNames = {}; forEach(state.params, function (v, k) { paramNames[k] = true; });

	      forEach(state.parent.params, function (v, k) {
	        if (!paramNames[k]) {
	          throw new Error("Missing required parameter '" + k + "' in state '" + state.name + "'");
	        }
	        paramNames[k] = false;
	      });
	      var ownParams = [];

	      forEach(paramNames, function (own, p) {
	        if (own) ownParams.push(p);
	      });
	      return ownParams;
	    },

	    // Keep a full path from the root down to this state as this is needed for state activation.
	    path: function(state) {
	      return state.parent ? state.parent.path.concat(state) : []; // exclude root from path
	    },

	    // Speed up $state.contains() as it's used a lot
	    includes: function(state) {
	      var includes = state.parent ? extend({}, state.parent.includes) : {};
	      includes[state.name] = true;
	      return includes;
	    },

	    $delegates: {}
	  };

	  function isRelative(stateName) {
	    return stateName.indexOf(".") === 0 || stateName.indexOf("^") === 0;
	  }

	  function findState(stateOrName, base) {
	    if (!stateOrName) return undefined;

	    var isStr = isString(stateOrName),
	        name  = isStr ? stateOrName : stateOrName.name,
	        path  = isRelative(name);

	    if (path) {
	      if (!base) throw new Error("No reference point given for path '"  + name + "'");
	      var rel = name.split("."), i = 0, pathLength = rel.length, current = base;

	      for (; i < pathLength; i++) {
	        if (rel[i] === "" && i === 0) {
	          current = base;
	          continue;
	        }
	        if (rel[i] === "^") {
	          if (!current.parent) throw new Error("Path '" + name + "' not valid for state '" + base.name + "'");
	          current = current.parent;
	          continue;
	        }
	        break;
	      }
	      rel = rel.slice(i).join(".");
	      name = current.name + (current.name && rel ? "." : "") + rel;
	    }
	    var state = states[name];

	    if (state && (isStr || (!isStr && (state === stateOrName || state.self === stateOrName)))) {
	      return state;
	    }
	    return undefined;
	  }

	  function queueState(parentName, state) {
	    if (!queue[parentName]) {
	      queue[parentName] = [];
	    }
	    queue[parentName].push(state);
	  }

	  function registerState(state) {
	    // Wrap a new object around the state so we can store our private details easily.
	    state = inherit(state, {
	      self: state,
	      resolve: state.resolve || {},
	      toString: function() { return this.name; }
	    });

	    var name = state.name;
	    if (!isString(name) || name.indexOf('@') >= 0) throw new Error("State must have a valid name");
	    if (states.hasOwnProperty(name)) throw new Error("State '" + name + "'' is already defined");

	    // Get parent name
	    var parentName = (name.indexOf('.') !== -1) ? name.substring(0, name.lastIndexOf('.'))
	        : (isString(state.parent)) ? state.parent
	        : '';

	    // If parent is not registered yet, add state to queue and register later
	    if (parentName && !states[parentName]) {
	      return queueState(parentName, state.self);
	    }

	    for (var key in stateBuilder) {
	      if (isFunction(stateBuilder[key])) state[key] = stateBuilder[key](state, stateBuilder.$delegates[key]);
	    }
	    states[name] = state;

	    // Register the state in the global state list and with $urlRouter if necessary.
	    if (!state[abstractKey] && state.url) {
	      $urlRouterProvider.when(state.url, ['$match', '$stateParams', function ($match, $stateParams) {
	        if ($state.$current.navigable != state || !equalForKeys($match, $stateParams)) {
	          $state.transitionTo(state, $match, { location: false });
	        }
	      }]);
	    }

	    // Register any queued children
	    if (queue[name]) {
	      for (var i = 0; i < queue[name].length; i++) {
	        registerState(queue[name][i]);
	      }
	    }

	    return state;
	  }

	  // Checks text to see if it looks like a glob.
	  function isGlob (text) {
	    return text.indexOf('*') > -1;
	  }

	  // Returns true if glob matches current $state name.
	  function doesStateMatchGlob (glob) {
	    var globSegments = glob.split('.'),
	        segments = $state.$current.name.split('.');

	    //match greedy starts
	    if (globSegments[0] === '**') {
	       segments = segments.slice(segments.indexOf(globSegments[1]));
	       segments.unshift('**');
	    }
	    //match greedy ends
	    if (globSegments[globSegments.length - 1] === '**') {
	       segments.splice(segments.indexOf(globSegments[globSegments.length - 2]) + 1, Number.MAX_VALUE);
	       segments.push('**');
	    }

	    if (globSegments.length != segments.length) {
	      return false;
	    }

	    //match single stars
	    for (var i = 0, l = globSegments.length; i < l; i++) {
	      if (globSegments[i] === '*') {
	        segments[i] = '*';
	      }
	    }

	    return segments.join('') === globSegments.join('');
	  }


	  // Implicit root state that is always active
	  root = registerState({
	    name: '',
	    url: '^',
	    views: null,
	    'abstract': true
	  });
	  root.navigable = null;


	  /**
	   * @ngdoc function
	   * @name ui.router.state.$stateProvider#decorator
	   * @methodOf ui.router.state.$stateProvider
	   *
	   * @description
	   * Allows you to extend (carefully) or override (at your own peril) the
	   * `stateBuilder` object used internally by `$stateProvider`. This can be used
	   * to add custom functionality to ui-router, for example inferring templateUrl
	   * based on the state name.
	   *
	   * When passing only a name, it returns the current (original or decorated) builder
	   * function that matches `name`.
	   *
	   * The builder functions that can be decorated are listed below. Though not all
	   * necessarily have a good use case for decoration, that is up to you to decide.
	   *
	   * In addition, users can attach custom decorators, which will generate new
	   * properties within the state's internal definition. There is currently no clear
	   * use-case for this beyond accessing internal states (i.e. $state.$current),
	   * however, expect this to become increasingly relevant as we introduce additional
	   * meta-programming features.
	   *
	   * **Warning**: Decorators should not be interdependent because the order of
	   * execution of the builder functions in non-deterministic. Builder functions
	   * should only be dependent on the state definition object and super function.
	   *
	   *
	   * Existing builder functions and current return values:
	   *
	   * - **parent** `{object}` - returns the parent state object.
	   * - **data** `{object}` - returns state data, including any inherited data that is not
	   *   overridden by own values (if any).
	   * - **url** `{object}` - returns a {@link ui.router.util.type:UrlMatcher UrlMatcher}
	   *   or `null`.
	   * - **navigable** `{object}` - returns closest ancestor state that has a URL (aka is
	   *   navigable).
	   * - **params** `{object}` - returns an array of state params that are ensured to
	   *   be a super-set of parent's params.
	   * - **views** `{object}` - returns a views object where each key is an absolute view
	   *   name (i.e. "viewName@stateName") and each value is the config object
	   *   (template, controller) for the view. Even when you don't use the views object
	   *   explicitly on a state config, one is still created for you internally.
	   *   So by decorating this builder function you have access to decorating template
	   *   and controller properties.
	   * - **ownParams** `{object}` - returns an array of params that belong to the state,
	   *   not including any params defined by ancestor states.
	   * - **path** `{string}` - returns the full path from the root down to this state.
	   *   Needed for state activation.
	   * - **includes** `{object}` - returns an object that includes every state that
	   *   would pass a `$state.includes()` test.
	   *
	   * @example
	   * <pre>
	   * // Override the internal 'views' builder with a function that takes the state
	   * // definition, and a reference to the internal function being overridden:
	   * $stateProvider.decorator('views', function (state, parent) {
	   *   var result = {},
	   *       views = parent(state);
	   *
	   *   angular.forEach(views, function (config, name) {
	   *     var autoName = (state.name + '.' + name).replace('.', '/');
	   *     config.templateUrl = config.templateUrl || '/partials/' + autoName + '.html';
	   *     result[name] = config;
	   *   });
	   *   return result;
	   * });
	   *
	   * $stateProvider.state('home', {
	   *   views: {
	   *     'contact.list': { controller: 'ListController' },
	   *     'contact.item': { controller: 'ItemController' }
	   *   }
	   * });
	   *
	   * // ...
	   *
	   * $state.go('home');
	   * // Auto-populates list and item views with /partials/home/contact/list.html,
	   * // and /partials/home/contact/item.html, respectively.
	   * </pre>
	   *
	   * @param {string} name The name of the builder function to decorate.
	   * @param {object} func A function that is responsible for decorating the original
	   * builder function. The function receives two parameters:
	   *
	   *   - `{object}` - state - The state config object.
	   *   - `{object}` - super - The original builder function.
	   *
	   * @return {object} $stateProvider - $stateProvider instance
	   */
	  this.decorator = decorator;
	  function decorator(name, func) {
	    /*jshint validthis: true */
	    if (isString(name) && !isDefined(func)) {
	      return stateBuilder[name];
	    }
	    if (!isFunction(func) || !isString(name)) {
	      return this;
	    }
	    if (stateBuilder[name] && !stateBuilder.$delegates[name]) {
	      stateBuilder.$delegates[name] = stateBuilder[name];
	    }
	    stateBuilder[name] = func;
	    return this;
	  }

	  /**
	   * @ngdoc function
	   * @name ui.router.state.$stateProvider#state
	   * @methodOf ui.router.state.$stateProvider
	   *
	   * @description
	   * Registers a state configuration under a given state name. The stateConfig object
	   * has the following acceptable properties.
	   *
	   * <a id='template'></a>
	   *
	   * - **`template`** - {string|function=} - html template as a string or a function that returns
	   *   an html template as a string which should be used by the uiView directives. This property
	   *   takes precedence over templateUrl.
	   *
	   *   If `template` is a function, it will be called with the following parameters:
	   *
	   *   - {array.&lt;object&gt;} - state parameters extracted from the current $location.path() by
	   *     applying the current state
	   *
	   * <a id='templateUrl'></a>
	   *
	   * - **`templateUrl`** - {string|function=} - path or function that returns a path to an html
	   *   template that should be used by uiView.
	   *
	   *   If `templateUrl` is a function, it will be called with the following parameters:
	   *
	   *   - {array.&lt;object&gt;} - state parameters extracted from the current $location.path() by
	   *     applying the current state
	   *
	   * <a id='templateProvider'></a>
	   *
	   * - **`templateProvider`** - {function=} - Provider function that returns HTML content
	   *   string.
	   *
	   * <a id='controller'></a>
	   *
	   * - **`controller`** - {string|function=} -  Controller fn that should be associated with newly
	   *   related scope or the name of a registered controller if passed as a string.
	   *
	   * <a id='controllerProvider'></a>
	   *
	   * - **`controllerProvider`** - {function=} - Injectable provider function that returns
	   *   the actual controller or string.
	   *
	   * <a id='controllerAs'></a>
	   *
	   * - **`controllerAs`** – {string=} – A controller alias name. If present the controller will be
	   *   published to scope under the controllerAs name.
	   *
	   * <a id='resolve'></a>
	   *
	   * - **`resolve`** - {object.&lt;string, function&gt;=} - An optional map of dependencies which
	   *   should be injected into the controller. If any of these dependencies are promises,
	   *   the router will wait for them all to be resolved or one to be rejected before the
	   *   controller is instantiated. If all the promises are resolved successfully, the values
	   *   of the resolved promises are injected and $stateChangeSuccess event is fired. If any
	   *   of the promises are rejected the $stateChangeError event is fired. The map object is:
	   *
	   *   - key - {string}: name of dependency to be injected into controller
	   *   - factory - {string|function}: If string then it is alias for service. Otherwise if function,
	   *     it is injected and return value it treated as dependency. If result is a promise, it is
	   *     resolved before its value is injected into controller.
	   *
	   * <a id='url'></a>
	   *
	   * - **`url`** - {string=} - A url with optional parameters. When a state is navigated or
	   *   transitioned to, the `$stateParams` service will be populated with any
	   *   parameters that were passed.
	   *
	   * <a id='params'></a>
	   *
	   * - **`params`** - {object=} - An array of parameter names or regular expressions. Only
	   *   use this within a state if you are not using url. Otherwise you can specify your
	   *   parameters within the url. When a state is navigated or transitioned to, the
	   *   $stateParams service will be populated with any parameters that were passed.
	   *
	   * <a id='views'></a>
	   *
	   * - **`views`** - {object=} - Use the views property to set up multiple views or to target views
	   *   manually/explicitly.
	   *
	   * <a id='abstract'></a>
	   *
	   * - **`abstract`** - {boolean=} - An abstract state will never be directly activated,
	   *   but can provide inherited properties to its common children states.
	   *
	   * <a id='onEnter'></a>
	   *
	   * - **`onEnter`** - {object=} - Callback function for when a state is entered. Good way
	   *   to trigger an action or dispatch an event, such as opening a dialog.
	   * If minifying your scripts, make sure to use the `['injection1', 'injection2', function(injection1, injection2){}]` syntax.
	   *
	   * <a id='onExit'></a>
	   *
	   * - **`onExit`** - {object=} - Callback function for when a state is exited. Good way to
	   *   trigger an action or dispatch an event, such as opening a dialog.
	   * If minifying your scripts, make sure to use the `['injection1', 'injection2', function(injection1, injection2){}]` syntax.
	   *
	   * <a id='reloadOnSearch'></a>
	   *
	   * - **`reloadOnSearch = true`** - {boolean=} - If `false`, will not retrigger the same state
	   *   just because a search/query parameter has changed (via $location.search() or $location.hash()).
	   *   Useful for when you'd like to modify $location.search() without triggering a reload.
	   *
	   * <a id='data'></a>
	   *
	   * - **`data`** - {object=} - Arbitrary data object, useful for custom configuration.
	   *
	   * @example
	   * <pre>
	   * // Some state name examples
	   *
	   * // stateName can be a single top-level name (must be unique).
	   * $stateProvider.state("home", {});
	   *
	   * // Or it can be a nested state name. This state is a child of the
	   * // above "home" state.
	   * $stateProvider.state("home.newest", {});
	   *
	   * // Nest states as deeply as needed.
	   * $stateProvider.state("home.newest.abc.xyz.inception", {});
	   *
	   * // state() returns $stateProvider, so you can chain state declarations.
	   * $stateProvider
	   *   .state("home", {})
	   *   .state("about", {})
	   *   .state("contacts", {});
	   * </pre>
	   *
	   * @param {string} name A unique state name, e.g. "home", "about", "contacts".
	   * To create a parent/child state use a dot, e.g. "about.sales", "home.newest".
	   * @param {object} definition State configuration object.
	   */
	  this.state = state;
	  function state(name, definition) {
	    /*jshint validthis: true */
	    if (isObject(name)) definition = name;
	    else definition.name = name;
	    registerState(definition);
	    return this;
	  }

	  /**
	   * @ngdoc object
	   * @name ui.router.state.$state
	   *
	   * @requires $rootScope
	   * @requires $q
	   * @requires ui.router.state.$view
	   * @requires $injector
	   * @requires ui.router.util.$resolve
	   * @requires ui.router.state.$stateParams
	   * @requires ui.router.router.$urlRouter
	   *
	   * @property {object} params A param object, e.g. {sectionId: section.id)}, that
	   * you'd like to test against the current active state.
	   * @property {object} current A reference to the state's config object. However
	   * you passed it in. Useful for accessing custom data.
	   * @property {object} transition Currently pending transition. A promise that'll
	   * resolve or reject.
	   *
	   * @description
	   * `$state` service is responsible for representing states as well as transitioning
	   * between them. It also provides interfaces to ask for current state or even states
	   * you're coming from.
	   */
	  this.$get = $get;
	  $get.$inject = ['$rootScope', '$q', '$view', '$injector', '$resolve', '$stateParams', '$urlRouter'];
	  function $get(   $rootScope,   $q,   $view,   $injector,   $resolve,   $stateParams,   $urlRouter) {

	    var TransitionSuperseded = $q.reject(new Error('transition superseded'));
	    var TransitionPrevented = $q.reject(new Error('transition prevented'));
	    var TransitionAborted = $q.reject(new Error('transition aborted'));
	    var TransitionFailed = $q.reject(new Error('transition failed'));

	    // Handles the case where a state which is the target of a transition is not found, and the user
	    // can optionally retry or defer the transition
	    function handleRedirect(redirect, state, params, options) {
	      /**
	       * @ngdoc event
	       * @name ui.router.state.$state#$stateNotFound
	       * @eventOf ui.router.state.$state
	       * @eventType broadcast on root scope
	       * @description
	       * Fired when a requested state **cannot be found** using the provided state name during transition.
	       * The event is broadcast allowing any handlers a single chance to deal with the error (usually by
	       * lazy-loading the unfound state). A special `unfoundState` object is passed to the listener handler,
	       * you can see its three properties in the example. You can use `event.preventDefault()` to abort the
	       * transition and the promise returned from `go` will be rejected with a `'transition aborted'` value.
	       *
	       * @param {Object} event Event object.
	       * @param {Object} unfoundState Unfound State information. Contains: `to, toParams, options` properties.
	       * @param {State} fromState Current state object.
	       * @param {Object} fromParams Current state params.
	       *
	       * @example
	       *
	       * <pre>
	       * // somewhere, assume lazy.state has not been defined
	       * $state.go("lazy.state", {a:1, b:2}, {inherit:false});
	       *
	       * // somewhere else
	       * $scope.$on('$stateNotFound',
	       * function(event, unfoundState, fromState, fromParams){
	       *     console.log(unfoundState.to); // "lazy.state"
	       *     console.log(unfoundState.toParams); // {a:1, b:2}
	       *     console.log(unfoundState.options); // {inherit:false} + default options
	       * })
	       * </pre>
	       */
	      var evt = $rootScope.$broadcast('$stateNotFound', redirect, state, params);

	      if (evt.defaultPrevented) {
	        $urlRouter.update();
	        return TransitionAborted;
	      }

	      if (!evt.retry) {
	        return null;
	      }

	      // Allow the handler to return a promise to defer state lookup retry
	      if (options.$retry) {
	        $urlRouter.update();
	        return TransitionFailed;
	      }
	      var retryTransition = $state.transition = $q.when(evt.retry);

	      retryTransition.then(function() {
	        if (retryTransition !== $state.transition) return TransitionSuperseded;
	        redirect.options.$retry = true;
	        return $state.transitionTo(redirect.to, redirect.toParams, redirect.options);
	      }, function() {
	        return TransitionAborted;
	      });
	      $urlRouter.update();

	      return retryTransition;
	    }

	    root.locals = { resolve: null, globals: { $stateParams: {} } };

	    $state = {
	      params: {},
	      current: root.self,
	      $current: root,
	      transition: null
	    };

	    /**
	     * @ngdoc function
	     * @name ui.router.state.$state#reload
	     * @methodOf ui.router.state.$state
	     *
	     * @description
	     * A method that force reloads the current state. All resolves are re-resolved, events are not re-fired,
	     * and controllers reinstantiated (bug with controllers reinstantiating right now, fixing soon).
	     *
	     * @example
	     * <pre>
	     * var app angular.module('app', ['ui.router']);
	     *
	     * app.controller('ctrl', function ($scope, $state) {
	     *   $scope.reload = function(){
	     *     $state.reload();
	     *   }
	     * });
	     * </pre>
	     *
	     * `reload()` is just an alias for:
	     * <pre>
	     * $state.transitionTo($state.current, $stateParams, {
	     *   reload: true, inherit: false, notify: false
	     * });
	     * </pre>
	     */
	    $state.reload = function reload() {
	      $state.transitionTo($state.current, $stateParams, { reload: true, inherit: false, notify: false });
	    };

	    /**
	     * @ngdoc function
	     * @name ui.router.state.$state#go
	     * @methodOf ui.router.state.$state
	     *
	     * @description
	     * Convenience method for transitioning to a new state. `$state.go` calls
	     * `$state.transitionTo` internally but automatically sets options to
	     * `{ location: true, inherit: true, relative: $state.$current, notify: true }`.
	     * This allows you to easily use an absolute or relative to path and specify
	     * only the parameters you'd like to update (while letting unspecified parameters
	     * inherit from the currently active ancestor states).
	     *
	     * @example
	     * <pre>
	     * var app = angular.module('app', ['ui.router']);
	     *
	     * app.controller('ctrl', function ($scope, $state) {
	     *   $scope.changeState = function () {
	     *     $state.go('contact.detail');
	     *   };
	     * });
	     * </pre>
	     * <img src='../ngdoc_assets/StateGoExamples.png'/>
	     *
	     * @param {string} to Absolute state name or relative state path. Some examples:
	     *
	     * - `$state.go('contact.detail')` - will go to the `contact.detail` state
	     * - `$state.go('^')` - will go to a parent state
	     * - `$state.go('^.sibling')` - will go to a sibling state
	     * - `$state.go('.child.grandchild')` - will go to grandchild state
	     *
	     * @param {object=} params A map of the parameters that will be sent to the state,
	     * will populate $stateParams. Any parameters that are not specified will be inherited from currently
	     * defined parameters. This allows, for example, going to a sibling state that shares parameters
	     * specified in a parent state. Parameter inheritance only works between common ancestor states, I.e.
	     * transitioning to a sibling will get you the parameters for all parents, transitioning to a child
	     * will get you all current parameters, etc.
	     * @param {object=} options Options object. The options are:
	     *
	     * - **`location`** - {boolean=true|string=} - If `true` will update the url in the location bar, if `false`
	     *    will not. If string, must be `"replace"`, which will update url and also replace last history record.
	     * - **`inherit`** - {boolean=true}, If `true` will inherit url parameters from current url.
	     * - **`relative`** - {object=$state.$current}, When transitioning with relative path (e.g '^'),
	     *    defines which state to be relative from.
	     * - **`notify`** - {boolean=true}, If `true` will broadcast $stateChangeStart and $stateChangeSuccess events.
	     * - **`reload`** (v0.2.5) - {boolean=false}, If `true` will force transition even if the state or params
	     *    have not changed, aka a reload of the same state. It differs from reloadOnSearch because you'd
	     *    use this when you want to force a reload when *everything* is the same, including search params.
	     *
	     * @returns {promise} A promise representing the state of the new transition.
	     *
	     * Possible success values:
	     *
	     * - $state.current
	     *
	     * <br/>Possible rejection values:
	     *
	     * - 'transition superseded' - when a newer transition has been started after this one
	     * - 'transition prevented' - when `event.preventDefault()` has been called in a `$stateChangeStart` listener
	     * - 'transition aborted' - when `event.preventDefault()` has been called in a `$stateNotFound` listener or
	     *   when a `$stateNotFound` `event.retry` promise errors.
	     * - 'transition failed' - when a state has been unsuccessfully found after 2 tries.
	     * - *resolve error* - when an error has occurred with a `resolve`
	     *
	     */
	    $state.go = function go(to, params, options) {
	      return $state.transitionTo(to, params, extend({ inherit: true, relative: $state.$current }, options));
	    };

	    /**
	     * @ngdoc function
	     * @name ui.router.state.$state#transitionTo
	     * @methodOf ui.router.state.$state
	     *
	     * @description
	     * Low-level method for transitioning to a new state. {@link ui.router.state.$state#methods_go $state.go}
	     * uses `transitionTo` internally. `$state.go` is recommended in most situations.
	     *
	     * @example
	     * <pre>
	     * var app = angular.module('app', ['ui.router']);
	     *
	     * app.controller('ctrl', function ($scope, $state) {
	     *   $scope.changeState = function () {
	     *     $state.transitionTo('contact.detail');
	     *   };
	     * });
	     * </pre>
	     *
	     * @param {string} to State name.
	     * @param {object=} toParams A map of the parameters that will be sent to the state,
	     * will populate $stateParams.
	     * @param {object=} options Options object. The options are:
	     *
	     * - **`location`** - {boolean=true|string=} - If `true` will update the url in the location bar, if `false`
	     *    will not. If string, must be `"replace"`, which will update url and also replace last history record.
	     * - **`inherit`** - {boolean=false}, If `true` will inherit url parameters from current url.
	     * - **`relative`** - {object=}, When transitioning with relative path (e.g '^'),
	     *    defines which state to be relative from.
	     * - **`notify`** - {boolean=true}, If `true` will broadcast $stateChangeStart and $stateChangeSuccess events.
	     * - **`reload`** (v0.2.5) - {boolean=false}, If `true` will force transition even if the state or params
	     *    have not changed, aka a reload of the same state. It differs from reloadOnSearch because you'd
	     *    use this when you want to force a reload when *everything* is the same, including search params.
	     *
	     * @returns {promise} A promise representing the state of the new transition. See
	     * {@link ui.router.state.$state#methods_go $state.go}.
	     */
	    $state.transitionTo = function transitionTo(to, toParams, options) {
	      toParams = toParams || {};
	      options = extend({
	        location: true, inherit: false, relative: null, notify: true, reload: false, $retry: false
	      }, options || {});

	      var from = $state.$current, fromParams = $state.params, fromPath = from.path;
	      var evt, toState = findState(to, options.relative);

	      if (!isDefined(toState)) {
	        var redirect = { to: to, toParams: toParams, options: options };
	        var redirectResult = handleRedirect(redirect, from.self, fromParams, options);

	        if (redirectResult) {
	          return redirectResult;
	        }

	        // Always retry once if the $stateNotFound was not prevented
	        // (handles either redirect changed or state lazy-definition)
	        to = redirect.to;
	        toParams = redirect.toParams;
	        options = redirect.options;
	        toState = findState(to, options.relative);

	        if (!isDefined(toState)) {
	          if (!options.relative) throw new Error("No such state '" + to + "'");
	          throw new Error("Could not resolve '" + to + "' from state '" + options.relative + "'");
	        }
	      }
	      if (toState[abstractKey]) throw new Error("Cannot transition to abstract state '" + to + "'");
	      if (options.inherit) toParams = inheritParams($stateParams, toParams || {}, $state.$current, toState);
	      to = toState;

	      var toPath = to.path;

	      // Starting from the root of the path, keep all levels that haven't changed
	      var keep = 0, state = toPath[keep], locals = root.locals, toLocals = [];

	      if (!options.reload) {
	        while (state && state === fromPath[keep] && equalForKeys(toParams, fromParams, state.ownParams)) {
	          locals = toLocals[keep] = state.locals;
	          keep++;
	          state = toPath[keep];
	        }
	      }

	      // If we're going to the same state and all locals are kept, we've got nothing to do.
	      // But clear 'transition', as we still want to cancel any other pending transitions.
	      // TODO: We may not want to bump 'transition' if we're called from a location change
	      // that we've initiated ourselves, because we might accidentally abort a legitimate
	      // transition initiated from code?
	      if (shouldTriggerReload(to, from, locals, options)) {
	        if (to.self.reloadOnSearch !== false) $urlRouter.update();
	        $state.transition = null;
	        return $q.when($state.current);
	      }

	      // Filter parameters before we pass them to event handlers etc.
	      toParams = filterByKeys(objectKeys(to.params), toParams || {});

	      // Broadcast start event and cancel the transition if requested
	      if (options.notify) {
	        /**
	         * @ngdoc event
	         * @name ui.router.state.$state#$stateChangeStart
	         * @eventOf ui.router.state.$state
	         * @eventType broadcast on root scope
	         * @description
	         * Fired when the state transition **begins**. You can use `event.preventDefault()`
	         * to prevent the transition from happening and then the transition promise will be
	         * rejected with a `'transition prevented'` value.
	         *
	         * @param {Object} event Event object.
	         * @param {State} toState The state being transitioned to.
	         * @param {Object} toParams The params supplied to the `toState`.
	         * @param {State} fromState The current state, pre-transition.
	         * @param {Object} fromParams The params supplied to the `fromState`.
	         *
	         * @example
	         *
	         * <pre>
	         * $rootScope.$on('$stateChangeStart',
	         * function(event, toState, toParams, fromState, fromParams){
	         *     event.preventDefault();
	         *     // transitionTo() promise will be rejected with
	         *     // a 'transition prevented' error
	         * })
	         * </pre>
	         */
	        if ($rootScope.$broadcast('$stateChangeStart', to.self, toParams, from.self, fromParams).defaultPrevented) {
	          $urlRouter.update();
	          return TransitionPrevented;
	        }
	      }

	      // Resolve locals for the remaining states, but don't update any global state just
	      // yet -- if anything fails to resolve the current state needs to remain untouched.
	      // We also set up an inheritance chain for the locals here. This allows the view directive
	      // to quickly look up the correct definition for each view in the current state. Even
	      // though we create the locals object itself outside resolveState(), it is initially
	      // empty and gets filled asynchronously. We need to keep track of the promise for the
	      // (fully resolved) current locals, and pass this down the chain.
	      var resolved = $q.when(locals);

	      for (var l = keep; l < toPath.length; l++, state = toPath[l]) {
	        locals = toLocals[l] = inherit(locals);
	        resolved = resolveState(state, toParams, state === to, resolved, locals);
	      }

	      // Once everything is resolved, we are ready to perform the actual transition
	      // and return a promise for the new state. We also keep track of what the
	      // current promise is, so that we can detect overlapping transitions and
	      // keep only the outcome of the last transition.
	      var transition = $state.transition = resolved.then(function () {
	        var l, entering, exiting;

	        if ($state.transition !== transition) return TransitionSuperseded;

	        // Exit 'from' states not kept
	        for (l = fromPath.length - 1; l >= keep; l--) {
	          exiting = fromPath[l];
	          if (exiting.self.onExit) {
	            $injector.invoke(exiting.self.onExit, exiting.self, exiting.locals.globals);
	          }
	          exiting.locals = null;
	        }

	        // Enter 'to' states not kept
	        for (l = keep; l < toPath.length; l++) {
	          entering = toPath[l];
	          entering.locals = toLocals[l];
	          if (entering.self.onEnter) {
	            $injector.invoke(entering.self.onEnter, entering.self, entering.locals.globals);
	          }
	        }

	        // Run it again, to catch any transitions in callbacks
	        if ($state.transition !== transition) return TransitionSuperseded;

	        // Update globals in $state
	        $state.$current = to;
	        $state.current = to.self;
	        $state.params = toParams;
	        copy($state.params, $stateParams);
	        $state.transition = null;

	        if (options.location && to.navigable) {
	          $urlRouter.push(to.navigable.url, to.navigable.locals.globals.$stateParams, {
	            replace: options.location === 'replace'
	          });
	        }

	        if (options.notify) {
	        /**
	         * @ngdoc event
	         * @name ui.router.state.$state#$stateChangeSuccess
	         * @eventOf ui.router.state.$state
	         * @eventType broadcast on root scope
	         * @description
	         * Fired once the state transition is **complete**.
	         *
	         * @param {Object} event Event object.
	         * @param {State} toState The state being transitioned to.
	         * @param {Object} toParams The params supplied to the `toState`.
	         * @param {State} fromState The current state, pre-transition.
	         * @param {Object} fromParams The params supplied to the `fromState`.
	         */
	          $rootScope.$broadcast('$stateChangeSuccess', to.self, toParams, from.self, fromParams);
	        }
	        $urlRouter.update(true);

	        return $state.current;
	      }, function (error) {
	        if ($state.transition !== transition) return TransitionSuperseded;

	        $state.transition = null;
	        /**
	         * @ngdoc event
	         * @name ui.router.state.$state#$stateChangeError
	         * @eventOf ui.router.state.$state
	         * @eventType broadcast on root scope
	         * @description
	         * Fired when an **error occurs** during transition. It's important to note that if you
	         * have any errors in your resolve functions (javascript errors, non-existent services, etc)
	         * they will not throw traditionally. You must listen for this $stateChangeError event to
	         * catch **ALL** errors.
	         *
	         * @param {Object} event Event object.
	         * @param {State} toState The state being transitioned to.
	         * @param {Object} toParams The params supplied to the `toState`.
	         * @param {State} fromState The current state, pre-transition.
	         * @param {Object} fromParams The params supplied to the `fromState`.
	         * @param {Error} error The resolve error object.
	         */
	        evt = $rootScope.$broadcast('$stateChangeError', to.self, toParams, from.self, fromParams, error);

	        if (!evt.defaultPrevented) {
	            $urlRouter.update();
	        }

	        return $q.reject(error);
	      });

	      return transition;
	    };

	    /**
	     * @ngdoc function
	     * @name ui.router.state.$state#is
	     * @methodOf ui.router.state.$state
	     *
	     * @description
	     * Similar to {@link ui.router.state.$state#methods_includes $state.includes},
	     * but only checks for the full state name. If params is supplied then it will be
	     * tested for strict equality against the current active params object, so all params
	     * must match with none missing and no extras.
	     *
	     * @example
	     * <pre>
	     * $state.$current.name = 'contacts.details.item';
	     *
	     * // absolute name
	     * $state.is('contact.details.item'); // returns true
	     * $state.is(contactDetailItemStateObject); // returns true
	     *
	     * // relative name (. and ^), typically from a template
	     * // E.g. from the 'contacts.details' template
	     * <div ng-class="{highlighted: $state.is('.item')}">Item</div>
	     * </pre>
	     *
	     * @param {string|object} stateName The state name (absolute or relative) or state object you'd like to check.
	     * @param {object=} params A param object, e.g. `{sectionId: section.id}`, that you'd like
	     * to test against the current active state.
	     * @returns {boolean} Returns true if it is the state.
	     */
	    $state.is = function is(stateOrName, params) {
	      var state = findState(stateOrName);

	      if (!isDefined(state)) {
	        return undefined;
	      }

	      if ($state.$current !== state) {
	        return false;
	      }

	      return isDefined(params) && params !== null ? angular.equals($stateParams, params) : true;
	    };

	    /**
	     * @ngdoc function
	     * @name ui.router.state.$state#includes
	     * @methodOf ui.router.state.$state
	     *
	     * @description
	     * A method to determine if the current active state is equal to or is the child of the
	     * state stateName. If any params are passed then they will be tested for a match as well.
	     * Not all the parameters need to be passed, just the ones you'd like to test for equality.
	     *
	     * @example
	     * Partial and relative names
	     * <pre>
	     * $state.$current.name = 'contacts.details.item';
	     *
	     * // Using partial names
	     * $state.includes("contacts"); // returns true
	     * $state.includes("contacts.details"); // returns true
	     * $state.includes("contacts.details.item"); // returns true
	     * $state.includes("contacts.list"); // returns false
	     * $state.includes("about"); // returns false
	     *
	     * // Using relative names (. and ^), typically from a template
	     * // E.g. from the 'contacts.details' template
	     * <div ng-class="{highlighted: $state.includes('.item')}">Item</div>
	     * </pre>
	     *
	     * Basic globbing patterns
	     * <pre>
	     * $state.$current.name = 'contacts.details.item.url';
	     *
	     * $state.includes("*.details.*.*"); // returns true
	     * $state.includes("*.details.**"); // returns true
	     * $state.includes("**.item.**"); // returns true
	     * $state.includes("*.details.item.url"); // returns true
	     * $state.includes("*.details.*.url"); // returns true
	     * $state.includes("*.details.*"); // returns false
	     * $state.includes("item.**"); // returns false
	     * </pre>
	     *
	     * @param {string} stateOrName A partial name, relative name, or glob pattern
	     * to be searched for within the current state name.
	     * @param {object} params A param object, e.g. `{sectionId: section.id}`,
	     * that you'd like to test against the current active state.
	     * @returns {boolean} Returns true if it does include the state
	     */
	    $state.includes = function includes(stateOrName, params) {
	      if (isString(stateOrName) && isGlob(stateOrName)) {
	        if (!doesStateMatchGlob(stateOrName)) {
	          return false;
	        }
	        stateOrName = $state.$current.name;
	      }
	      var state = findState(stateOrName);

	      if (!isDefined(state)) {
	        return undefined;
	      }
	      if (!isDefined($state.$current.includes[state.name])) {
	        return false;
	      }
	      return equalForKeys(params, $stateParams);
	    };


	    /**
	     * @ngdoc function
	     * @name ui.router.state.$state#href
	     * @methodOf ui.router.state.$state
	     *
	     * @description
	     * A url generation method that returns the compiled url for the given state populated with the given params.
	     *
	     * @example
	     * <pre>
	     * expect($state.href("about.person", { person: "bob" })).toEqual("/about/bob");
	     * </pre>
	     *
	     * @param {string|object} stateOrName The state name or state object you'd like to generate a url from.
	     * @param {object=} params An object of parameter values to fill the state's required parameters.
	     * @param {object=} options Options object. The options are:
	     *
	     * - **`lossy`** - {boolean=true} -  If true, and if there is no url associated with the state provided in the
	     *    first parameter, then the constructed href url will be built from the first navigable ancestor (aka
	     *    ancestor with a valid url).
	     * - **`inherit`** - {boolean=true}, If `true` will inherit url parameters from current url.
	     * - **`relative`** - {object=$state.$current}, When transitioning with relative path (e.g '^'),
	     *    defines which state to be relative from.
	     * - **`absolute`** - {boolean=false},  If true will generate an absolute url, e.g. "http://www.example.com/fullurl".
	     *
	     * @returns {string} compiled state url
	     */
	    $state.href = function href(stateOrName, params, options) {
	      options = extend({
	        lossy:    true,
	        inherit:  true,
	        absolute: false,
	        relative: $state.$current
	      }, options || {});

	      var state = findState(stateOrName, options.relative);

	      if (!isDefined(state)) return null;
	      if (options.inherit) params = inheritParams($stateParams, params || {}, $state.$current, state);

	      var nav = (state && options.lossy) ? state.navigable : state;

	      if (!nav || !nav.url) {
	        return null;
	      }
	      return $urlRouter.href(nav.url, filterByKeys(objectKeys(state.params), params || {}), {
	        absolute: options.absolute
	      });
	    };

	    /**
	     * @ngdoc function
	     * @name ui.router.state.$state#get
	     * @methodOf ui.router.state.$state
	     *
	     * @description
	     * Returns the state configuration object for any specific state or all states.
	     *
	     * @param {string|Sbject=} stateOrName (absolute or relative) If provided, will only get the config for
	     * the requested state. If not provided, returns an array of ALL state configs.
	     * @returns {Object|Array} State configuration object or array of all objects.
	     */
	    $state.get = function (stateOrName, context) {
	      if (arguments.length === 0) return objectKeys(states).map(function(name) { return states[name].self; });
	      var state = findState(stateOrName, context);
	      return (state && state.self) ? state.self : null;
	    };

	    function resolveState(state, params, paramsAreFiltered, inherited, dst) {
	      // Make a restricted $stateParams with only the parameters that apply to this state if
	      // necessary. In addition to being available to the controller and onEnter/onExit callbacks,
	      // we also need $stateParams to be available for any $injector calls we make during the
	      // dependency resolution process.
	      var $stateParams = (paramsAreFiltered) ? params : filterByKeys(objectKeys(state.params), params);
	      var locals = { $stateParams: $stateParams };

	      // Resolve 'global' dependencies for the state, i.e. those not specific to a view.
	      // We're also including $stateParams in this; that way the parameters are restricted
	      // to the set that should be visible to the state, and are independent of when we update
	      // the global $state and $stateParams values.
	      dst.resolve = $resolve.resolve(state.resolve, locals, dst.resolve, state);
	      var promises = [dst.resolve.then(function (globals) {
	        dst.globals = globals;
	      })];
	      if (inherited) promises.push(inherited);

	      // Resolve template and dependencies for all views.
	      forEach(state.views, function (view, name) {
	        var injectables = (view.resolve && view.resolve !== state.resolve ? view.resolve : {});
	        injectables.$template = [ function () {
	          return $view.load(name, { view: view, locals: locals, params: $stateParams }) || '';
	        }];

	        promises.push($resolve.resolve(injectables, locals, dst.resolve, state).then(function (result) {
	          // References to the controller (only instantiated at link time)
	          if (isFunction(view.controllerProvider) || isArray(view.controllerProvider)) {
	            var injectLocals = angular.extend({}, injectables, locals);
	            result.$$controller = $injector.invoke(view.controllerProvider, null, injectLocals);
	          } else {
	            result.$$controller = view.controller;
	          }
	          // Provide access to the state itself for internal use
	          result.$$state = state;
	          result.$$controllerAs = view.controllerAs;
	          dst[name] = result;
	        }));
	      });

	      // Wait for all the promises and then return the activation object
	      return $q.all(promises).then(function (values) {
	        return dst;
	      });
	    }

	    return $state;
	  }

	  function shouldTriggerReload(to, from, locals, options) {
	    if (to === from && ((locals === from.locals && !options.reload) || (to.self.reloadOnSearch === false))) {
	      return true;
	    }
	  }
	}

	angular.module('ui.router.state')
	  .value('$stateParams', {})
	  .provider('$state', $StateProvider);


	$ViewProvider.$inject = [];
	function $ViewProvider() {

	  this.$get = $get;
	  /**
	   * @ngdoc object
	   * @name ui.router.state.$view
	   *
	   * @requires ui.router.util.$templateFactory
	   * @requires $rootScope
	   *
	   * @description
	   *
	   */
	  $get.$inject = ['$rootScope', '$templateFactory'];
	  function $get(   $rootScope,   $templateFactory) {
	    return {
	      // $view.load('full.viewName', { template: ..., controller: ..., resolve: ..., async: false, params: ... })
	      /**
	       * @ngdoc function
	       * @name ui.router.state.$view#load
	       * @methodOf ui.router.state.$view
	       *
	       * @description
	       *
	       * @param {string} name name
	       * @param {object} options option object.
	       */
	      load: function load(name, options) {
	        var result, defaults = {
	          template: null, controller: null, view: null, locals: null, notify: true, async: true, params: {}
	        };
	        options = extend(defaults, options);

	        if (options.view) {
	          result = $templateFactory.fromConfig(options.view, options.params, options.locals);
	        }
	        if (result && options.notify) {
	        /**
	         * @ngdoc event
	         * @name ui.router.state.$state#$viewContentLoading
	         * @eventOf ui.router.state.$view
	         * @eventType broadcast on root scope
	         * @description
	         *
	         * Fired once the view **begins loading**, *before* the DOM is rendered.
	         *
	         * @param {Object} event Event object.
	         * @param {Object} viewConfig The view config properties (template, controller, etc).
	         *
	         * @example
	         *
	         * <pre>
	         * $scope.$on('$viewContentLoading',
	         * function(event, viewConfig){
	         *     // Access to all the view config properties.
	         *     // and one special property 'targetView'
	         *     // viewConfig.targetView
	         * });
	         * </pre>
	         */
	          $rootScope.$broadcast('$viewContentLoading', options);
	        }
	        return result;
	      }
	    };
	  }
	}

	angular.module('ui.router.state').provider('$view', $ViewProvider);

	/**
	 * @ngdoc object
	 * @name ui.router.state.$uiViewScrollProvider
	 *
	 * @description
	 * Provider that returns the {@link ui.router.state.$uiViewScroll} service function.
	 */
	function $ViewScrollProvider() {

	  var useAnchorScroll = false;

	  /**
	   * @ngdoc function
	   * @name ui.router.state.$uiViewScrollProvider#useAnchorScroll
	   * @methodOf ui.router.state.$uiViewScrollProvider
	   *
	   * @description
	   * Reverts back to using the core [`$anchorScroll`](http://docs.angularjs.org/api/ng.$anchorScroll) service for
	   * scrolling based on the url anchor.
	   */
	  this.useAnchorScroll = function () {
	    useAnchorScroll = true;
	  };

	  /**
	   * @ngdoc object
	   * @name ui.router.state.$uiViewScroll
	   *
	   * @requires $anchorScroll
	   * @requires $timeout
	   *
	   * @description
	   * When called with a jqLite element, it scrolls the element into view (after a
	   * `$timeout` so the DOM has time to refresh).
	   *
	   * If you prefer to rely on `$anchorScroll` to scroll the view to the anchor,
	   * this can be enabled by calling {@link ui.router.state.$uiViewScrollProvider#methods_useAnchorScroll `$uiViewScrollProvider.useAnchorScroll()`}.
	   */
	  this.$get = ['$anchorScroll', '$timeout', function ($anchorScroll, $timeout) {
	    if (useAnchorScroll) {
	      return $anchorScroll;
	    }

	    return function ($element) {
	      $timeout(function () {
	        $element[0].scrollIntoView();
	      }, 0, false);
	    };
	  }];
	}

	angular.module('ui.router.state').provider('$uiViewScroll', $ViewScrollProvider);

	/**
	 * @ngdoc directive
	 * @name ui.router.state.directive:ui-view
	 *
	 * @requires ui.router.state.$state
	 * @requires $compile
	 * @requires $controller
	 * @requires $injector
	 * @requires ui.router.state.$uiViewScroll
	 * @requires $document
	 *
	 * @restrict ECA
	 *
	 * @description
	 * The ui-view directive tells $state where to place your templates.
	 *
	 * @param {string=} ui-view A view name. The name should be unique amongst the other views in the
	 * same state. You can have views of the same name that live in different states.
	 *
	 * @param {string=} autoscroll It allows you to set the scroll behavior of the browser window
	 * when a view is populated. By default, $anchorScroll is overridden by ui-router's custom scroll
	 * service, {@link ui.router.state.$uiViewScroll}. This custom service let's you
	 * scroll ui-view elements into view when they are populated during a state activation.
	 *
	 * *Note: To revert back to old [`$anchorScroll`](http://docs.angularjs.org/api/ng.$anchorScroll)
	 * functionality, call `$uiViewScrollProvider.useAnchorScroll()`.*
	 *
	 * @param {string=} onload Expression to evaluate whenever the view updates.
	 *
	 * @example
	 * A view can be unnamed or named.
	 * <pre>
	 * <!-- Unnamed -->
	 * <div ui-view></div>
	 *
	 * <!-- Named -->
	 * <div ui-view="viewName"></div>
	 * </pre>
	 *
	 * You can only have one unnamed view within any template (or root html). If you are only using a
	 * single view and it is unnamed then you can populate it like so:
	 * <pre>
	 * <div ui-view></div>
	 * $stateProvider.state("home", {
	 *   template: "<h1>HELLO!</h1>"
	 * })
	 * </pre>
	 *
	 * The above is a convenient shortcut equivalent to specifying your view explicitly with the {@link ui.router.state.$stateProvider#views `views`}
	 * config property, by name, in this case an empty name:
	 * <pre>
	 * $stateProvider.state("home", {
	 *   views: {
	 *     "": {
	 *       template: "<h1>HELLO!</h1>"
	 *     }
	 *   }
	 * })
	 * </pre>
	 *
	 * But typically you'll only use the views property if you name your view or have more than one view
	 * in the same template. There's not really a compelling reason to name a view if its the only one,
	 * but you could if you wanted, like so:
	 * <pre>
	 * <div ui-view="main"></div>
	 * </pre>
	 * <pre>
	 * $stateProvider.state("home", {
	 *   views: {
	 *     "main": {
	 *       template: "<h1>HELLO!</h1>"
	 *     }
	 *   }
	 * })
	 * </pre>
	 *
	 * Really though, you'll use views to set up multiple views:
	 * <pre>
	 * <div ui-view></div>
	 * <div ui-view="chart"></div>
	 * <div ui-view="data"></div>
	 * </pre>
	 *
	 * <pre>
	 * $stateProvider.state("home", {
	 *   views: {
	 *     "": {
	 *       template: "<h1>HELLO!</h1>"
	 *     },
	 *     "chart": {
	 *       template: "<chart_thing/>"
	 *     },
	 *     "data": {
	 *       template: "<data_thing/>"
	 *     }
	 *   }
	 * })
	 * </pre>
	 *
	 * Examples for `autoscroll`:
	 *
	 * <pre>
	 * <!-- If autoscroll present with no expression,
	 *      then scroll ui-view into view -->
	 * <ui-view autoscroll/>
	 *
	 * <!-- If autoscroll present with valid expression,
	 *      then scroll ui-view into view if expression evaluates to true -->
	 * <ui-view autoscroll='true'/>
	 * <ui-view autoscroll='false'/>
	 * <ui-view autoscroll='scopeVariable'/>
	 * </pre>
	 */
	$ViewDirective.$inject = ['$state', '$injector', '$uiViewScroll'];
	function $ViewDirective(   $state,   $injector,   $uiViewScroll) {

	  function getService() {
	    return ($injector.has) ? function(service) {
	      return $injector.has(service) ? $injector.get(service) : null;
	    } : function(service) {
	      try {
	        return $injector.get(service);
	      } catch (e) {
	        return null;
	      }
	    };
	  }

	  var service = getService(),
	      $animator = service('$animator'),
	      $animate = service('$animate');

	  // Returns a set of DOM manipulation functions based on which Angular version
	  // it should use
	  function getRenderer(attrs, scope) {
	    var statics = function() {
	      return {
	        enter: function (element, target, cb) { target.after(element); cb(); },
	        leave: function (element, cb) { element.remove(); cb(); }
	      };
	    };

	    if ($animate) {
	      return {
	        enter: function(element, target, cb) { $animate.enter(element, null, target, cb); },
	        leave: function(element, cb) { $animate.leave(element, cb); }
	      };
	    }

	    if ($animator) {
	      var animate = $animator && $animator(scope, attrs);

	      return {
	        enter: function(element, target, cb) {animate.enter(element, null, target); cb(); },
	        leave: function(element, cb) { animate.leave(element); cb(); }
	      };
	    }

	    return statics();
	  }

	  var directive = {
	    restrict: 'ECA',
	    terminal: true,
	    priority: 400,
	    transclude: 'element',
	    compile: function (tElement, tAttrs, $transclude) {
	      return function (scope, $element, attrs) {
	        var previousEl, currentEl, currentScope, latestLocals,
	            onloadExp     = attrs.onload || '',
	            autoScrollExp = attrs.autoscroll,
	            renderer      = getRenderer(attrs, scope);

	        scope.$on('$stateChangeSuccess', function() {
	          updateView(false);
	        });
	        scope.$on('$viewContentLoading', function() {
	          updateView(false);
	        });

	        updateView(true);

	        function cleanupLastView() {
	          if (previousEl) {
	            previousEl.remove();
	            previousEl = null;
	          }

	          if (currentScope) {
	            currentScope.$destroy();
	            currentScope = null;
	          }

	          if (currentEl) {
	            renderer.leave(currentEl, function() {
	              previousEl = null;
	            });

	            previousEl = currentEl;
	            currentEl = null;
	          }
	        }

	        function updateView(firstTime) {
	          var newScope,
	              name            = getUiViewName(attrs, $element.inheritedData('$uiView')),
	              previousLocals  = name && $state.$current && $state.$current.locals[name];

	          if (!firstTime && previousLocals === latestLocals) return; // nothing to do
	          newScope = scope.$new();
	          latestLocals = $state.$current.locals[name];

	          var clone = $transclude(newScope, function(clone) {
	            renderer.enter(clone, $element, function onUiViewEnter() {
	              if (angular.isDefined(autoScrollExp) && !autoScrollExp || scope.$eval(autoScrollExp)) {
	                $uiViewScroll(clone);
	              }
	            });
	            cleanupLastView();
	          });

	          currentEl = clone;
	          currentScope = newScope;
	          /**
	           * @ngdoc event
	           * @name ui.router.state.directive:ui-view#$viewContentLoaded
	           * @eventOf ui.router.state.directive:ui-view
	           * @eventType emits on ui-view directive scope
	           * @description           *
	           * Fired once the view is **loaded**, *after* the DOM is rendered.
	           *
	           * @param {Object} event Event object.
	           */
	          currentScope.$emit('$viewContentLoaded');
	          currentScope.$eval(onloadExp);
	        }
	      };
	    }
	  };

	  return directive;
	}

	$ViewDirectiveFill.$inject = ['$compile', '$controller', '$state'];
	function $ViewDirectiveFill ($compile, $controller, $state) {
	  return {
	    restrict: 'ECA',
	    priority: -400,
	    compile: function (tElement) {
	      var initial = tElement.html();
	      return function (scope, $element, attrs) {
	        var current = $state.$current,
	            name = getUiViewName(attrs, $element.inheritedData('$uiView')),
	            locals  = current && current.locals[name];

	        if (! locals) {
	          return;
	        }

	        $element.data('$uiView', { name: name, state: locals.$$state });
	        $element.html(locals.$template ? locals.$template : initial);

	        var link = $compile($element.contents());

	        if (locals.$$controller) {
	          locals.$scope = scope;
	          var controller = $controller(locals.$$controller, locals);
	          if (locals.$$controllerAs) {
	            scope[locals.$$controllerAs] = controller;
	          }
	          $element.data('$ngControllerController', controller);
	          $element.children().data('$ngControllerController', controller);
	        }

	        link(scope);
	      };
	    }
	  };
	}

	/**
	 * Shared ui-view code for both directives:
	 * Given attributes and inherited $uiView data, return the view's name
	 */
	function getUiViewName(attrs, inherited) {
	  var name = attrs.uiView || attrs.name || '';
	  return name.indexOf('@') >= 0 ?  name :  (name + '@' + (inherited ? inherited.state.name : ''));
	}

	angular.module('ui.router.state').directive('uiView', $ViewDirective);
	angular.module('ui.router.state').directive('uiView', $ViewDirectiveFill);

	function parseStateRef(ref, current) {
	  var preparsed = ref.match(/^\s*({[^}]*})\s*$/), parsed;
	  if (preparsed) ref = current + '(' + preparsed[1] + ')';
	  parsed = ref.replace(/\n/g, " ").match(/^([^(]+?)\s*(\((.*)\))?$/);
	  if (!parsed || parsed.length !== 4) throw new Error("Invalid state ref '" + ref + "'");
	  return { state: parsed[1], paramExpr: parsed[3] || null };
	}

	function stateContext(el) {
	  var stateData = el.parent().inheritedData('$uiView');

	  if (stateData && stateData.state && stateData.state.name) {
	    return stateData.state;
	  }
	}

	/**
	 * @ngdoc directive
	 * @name ui.router.state.directive:ui-sref
	 *
	 * @requires ui.router.state.$state
	 * @requires $timeout
	 *
	 * @restrict A
	 *
	 * @description
	 * A directive that binds a link (`<a>` tag) to a state. If the state has an associated
	 * URL, the directive will automatically generate & update the `href` attribute via
	 * the {@link ui.router.state.$state#methods_href $state.href()} method. Clicking
	 * the link will trigger a state transition with optional parameters.
	 *
	 * Also middle-clicking, right-clicking, and ctrl-clicking on the link will be
	 * handled natively by the browser.
	 *
	 * You can also use relative state paths within ui-sref, just like the relative
	 * paths passed to `$state.go()`. You just need to be aware that the path is relative
	 * to the state that the link lives in, in other words the state that loaded the
	 * template containing the link.
	 *
	 * You can specify options to pass to {@link ui.router.state.$state#go $state.go()}
	 * using the `ui-sref-opts` attribute. Options are restricted to `location`, `inherit`,
	 * and `reload`.
	 *
	 * @example
	 * Here's an example of how you'd use ui-sref and how it would compile. If you have the
	 * following template:
	 * <pre>
	 * <a ui-sref="home">Home</a> | <a ui-sref="about">About</a> | <a ui-sref="{page: 2}">Next page</a>
	 *
	 * <ul>
	 *     <li ng-repeat="contact in contacts">
	 *         <a ui-sref="contacts.detail({ id: contact.id })">{{ contact.name }}</a>
	 *     </li>
	 * </ul>
	 * </pre>
	 *
	 * Then the compiled html would be (assuming Html5Mode is off and current state is contacts):
	 * <pre>
	 * <a href="#/home" ui-sref="home">Home</a> | <a href="#/about" ui-sref="about">About</a> | <a href="#/contacts?page=2" ui-sref="{page: 2}">Next page</a>
	 *
	 * <ul>
	 *     <li ng-repeat="contact in contacts">
	 *         <a href="#/contacts/1" ui-sref="contacts.detail({ id: contact.id })">Joe</a>
	 *     </li>
	 *     <li ng-repeat="contact in contacts">
	 *         <a href="#/contacts/2" ui-sref="contacts.detail({ id: contact.id })">Alice</a>
	 *     </li>
	 *     <li ng-repeat="contact in contacts">
	 *         <a href="#/contacts/3" ui-sref="contacts.detail({ id: contact.id })">Bob</a>
	 *     </li>
	 * </ul>
	 *
	 * <a ui-sref="home" ui-sref-opts="{reload: true}">Home</a>
	 * </pre>
	 *
	 * @param {string} ui-sref 'stateName' can be any valid absolute or relative state
	 * @param {Object} ui-sref-opts options to pass to {@link ui.router.state.$state#go $state.go()}
	 */
	$StateRefDirective.$inject = ['$state', '$timeout'];
	function $StateRefDirective($state, $timeout) {
	  var allowedOptions = ['location', 'inherit', 'reload'];

	  return {
	    restrict: 'A',
	    require: ['?^uiSrefActive', '?^uiSrefActiveEq'],
	    link: function(scope, element, attrs, uiSrefActive) {
	      var ref = parseStateRef(attrs.uiSref, $state.current.name);
	      var params = null, url = null, base = stateContext(element) || $state.$current;
	      var isForm = element[0].nodeName === "FORM";
	      var attr = isForm ? "action" : "href", nav = true;

	      var options = { relative: base, inherit: true };
	      var optionsOverride = scope.$eval(attrs.uiSrefOpts) || {};

	      angular.forEach(allowedOptions, function(option) {
	        if (option in optionsOverride) {
	          options[option] = optionsOverride[option];
	        }
	      });

	      var update = function(newVal) {
	        if (newVal) params = newVal;
	        if (!nav) return;

	        var newHref = $state.href(ref.state, params, options);

	        var activeDirective = uiSrefActive[1] || uiSrefActive[0];
	        if (activeDirective) {
	          activeDirective.$$setStateInfo(ref.state, params);
	        }
	        if (newHref === null) {
	          nav = false;
	          return false;
	        }
	        element[0][attr] = newHref;
	      };

	      if (ref.paramExpr) {
	        scope.$watch(ref.paramExpr, function(newVal, oldVal) {
	          if (newVal !== params) update(newVal);
	        }, true);
	        params = scope.$eval(ref.paramExpr);
	      }
	      update();

	      if (isForm) return;

	      element.bind("click", function(e) {
	        var button = e.which || e.button;
	        if ( !(button > 1 || e.ctrlKey || e.metaKey || e.shiftKey || element.attr('target')) ) {
	          // HACK: This is to allow ng-clicks to be processed before the transition is initiated:
	          var transition = $timeout(function() {
	            $state.go(ref.state, params, options);
	          });
	          e.preventDefault();

	          e.preventDefault = function() {
	            $timeout.cancel(transition);
	          };
	        }
	      });
	    }
	  };
	}

	/**
	 * @ngdoc directive
	 * @name ui.router.state.directive:ui-sref-active
	 *
	 * @requires ui.router.state.$state
	 * @requires ui.router.state.$stateParams
	 * @requires $interpolate
	 *
	 * @restrict A
	 *
	 * @description
	 * A directive working alongside ui-sref to add classes to an element when the
	 * related ui-sref directive's state is active, and removing them when it is inactive.
	 * The primary use-case is to simplify the special appearance of navigation menus
	 * relying on `ui-sref`, by having the "active" state's menu button appear different,
	 * distinguishing it from the inactive menu items.
	 *
	 * ui-sref-active can live on the same element as ui-sref or on a parent element. The first
	 * ui-sref-active found at the same level or above the ui-sref will be used.
	 *
	 * Will activate when the ui-sref's target state or any child state is active. If you
	 * need to activate only when the ui-sref target state is active and *not* any of
	 * it's children, then you will use
	 * {@link ui.router.state.directive:ui-sref-active-eq ui-sref-active-eq}
	 *
	 * @example
	 * Given the following template:
	 * <pre>
	 * <ul>
	 *   <li ui-sref-active="active" class="item">
	 *     <a href ui-sref="app.user({user: 'bilbobaggins'})">@bilbobaggins</a>
	 *   </li>
	 * </ul>
	 * </pre>
	 *
	 *
	 * When the app state is "app.user" (or any children states), and contains the state parameter "user" with value "bilbobaggins",
	 * the resulting HTML will appear as (note the 'active' class):
	 * <pre>
	 * <ul>
	 *   <li ui-sref-active="active" class="item active">
	 *     <a ui-sref="app.user({user: 'bilbobaggins'})" href="/users/bilbobaggins">@bilbobaggins</a>
	 *   </li>
	 * </ul>
	 * </pre>
	 *
	 * The class name is interpolated **once** during the directives link time (any further changes to the
	 * interpolated value are ignored).
	 *
	 * Multiple classes may be specified in a space-separated format:
	 * <pre>
	 * <ul>
	 *   <li ui-sref-active='class1 class2 class3'>
	 *     <a ui-sref="app.user">link</a>
	 *   </li>
	 * </ul>
	 * </pre>
	 */

	/**
	 * @ngdoc directive
	 * @name ui.router.state.directive:ui-sref-active-eq
	 *
	 * @requires ui.router.state.$state
	 * @requires ui.router.state.$stateParams
	 * @requires $interpolate
	 *
	 * @restrict A
	 *
	 * @description
	 * The same as {@link ui.router.state.directive:ui-sref-active ui-sref-active} but will will only activate
	 * when the exact target state used in the `ui-sref` is active; no child states.
	 *
	 */
	$StateRefActiveDirective.$inject = ['$state', '$stateParams', '$interpolate'];
	function $StateRefActiveDirective($state, $stateParams, $interpolate) {
	  return  {
	    restrict: "A",
	    controller: ['$scope', '$element', '$attrs', function ($scope, $element, $attrs) {
	      var state, params, activeClass;

	      // There probably isn't much point in $observing this
	      // uiSrefActive and uiSrefActiveEq share the same directive object with some
	      // slight difference in logic routing
	      activeClass = $interpolate($attrs.uiSrefActiveEq || $attrs.uiSrefActive || '', false)($scope);

	      // Allow uiSref to communicate with uiSrefActive[Equals]
	      this.$$setStateInfo = function (newState, newParams) {
	        state = $state.get(newState, stateContext($element));
	        params = newParams;
	        update();
	      };

	      $scope.$on('$stateChangeSuccess', update);

	      // Update route state
	      function update() {
	        if (isMatch()) {
	          $element.addClass(activeClass);
	        } else {
	          $element.removeClass(activeClass);
	        }
	      }

	      function isMatch() {
	        if (typeof $attrs.uiSrefActiveEq !== 'undefined') {
	          return $state.$current.self === state && matchesParams();
	        } else {
	          return $state.includes(state.name) && matchesParams();
	        }
	      }

	      function matchesParams() {
	        return !params || equalForKeys(params, $stateParams);
	      }
	    }]
	  };
	}

	angular.module('ui.router.state')
	  .directive('uiSref', $StateRefDirective)
	  .directive('uiSrefActive', $StateRefActiveDirective)
	  .directive('uiSrefActiveEq', $StateRefActiveDirective);

	/**
	 * @ngdoc filter
	 * @name ui.router.state.filter:isState
	 *
	 * @requires ui.router.state.$state
	 *
	 * @description
	 * Translates to {@link ui.router.state.$state#methods_is $state.is("stateName")}.
	 */
	$IsStateFilter.$inject = ['$state'];
	function $IsStateFilter($state) {
	  return function(state) {
	    return $state.is(state);
	  };
	}

	/**
	 * @ngdoc filter
	 * @name ui.router.state.filter:includedByState
	 *
	 * @requires ui.router.state.$state
	 *
	 * @description
	 * Translates to {@link ui.router.state.$state#methods_includes $state.includes('fullOrPartialStateName')}.
	 */
	$IncludedByStateFilter.$inject = ['$state'];
	function $IncludedByStateFilter($state) {
	  return function(state) {
	    return $state.includes(state);
	  };
	}

	angular.module('ui.router.state')
	  .filter('isState', $IsStateFilter)
	  .filter('includedByState', $IncludedByStateFilter);
	})(window, window.angular);


/***/ }),

/***/ 194:
/***/ (function(module, exports) {

	/*!
	 * ui-select
	 * http://github.com/angular-ui/ui-select
	 * Version: 0.19.7 - 2017-04-15T14:28:36.649Z
	 * License: MIT
	 */
	!function(){"use strict";function e(e){return angular.isUndefined(e)||null===e}var t={TAB:9,ENTER:13,ESC:27,SPACE:32,LEFT:37,UP:38,RIGHT:39,DOWN:40,SHIFT:16,CTRL:17,ALT:18,PAGE_UP:33,PAGE_DOWN:34,HOME:36,END:35,BACKSPACE:8,DELETE:46,COMMAND:91,MAP:{91:"COMMAND",8:"BACKSPACE",9:"TAB",13:"ENTER",16:"SHIFT",17:"CTRL",18:"ALT",19:"PAUSEBREAK",20:"CAPSLOCK",27:"ESC",32:"SPACE",33:"PAGE_UP",34:"PAGE_DOWN",35:"END",36:"HOME",37:"LEFT",38:"UP",39:"RIGHT",40:"DOWN",43:"+",44:"PRINTSCREEN",45:"INSERT",46:"DELETE",48:"0",49:"1",50:"2",51:"3",52:"4",53:"5",54:"6",55:"7",56:"8",57:"9",59:";",61:"=",65:"A",66:"B",67:"C",68:"D",69:"E",70:"F",71:"G",72:"H",73:"I",74:"J",75:"K",76:"L",77:"M",78:"N",79:"O",80:"P",81:"Q",82:"R",83:"S",84:"T",85:"U",86:"V",87:"W",88:"X",89:"Y",90:"Z",96:"0",97:"1",98:"2",99:"3",100:"4",101:"5",102:"6",103:"7",104:"8",105:"9",106:"*",107:"+",109:"-",110:".",111:"/",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NUMLOCK",145:"SCROLLLOCK",186:";",187:"=",188:",",189:"-",190:".",191:"/",192:"`",219:"[",220:"\\",221:"]",222:"'"},isControl:function(e){var s=e.which;switch(s){case t.COMMAND:case t.SHIFT:case t.CTRL:case t.ALT:return!0}return!!(e.metaKey||e.ctrlKey||e.altKey)},isFunctionKey:function(e){return e=e.which?e.which:e,e>=112&&e<=123},isVerticalMovement:function(e){return~[t.UP,t.DOWN].indexOf(e)},isHorizontalMovement:function(e){return~[t.LEFT,t.RIGHT,t.BACKSPACE,t.DELETE].indexOf(e)},toSeparator:function(e){var s={ENTER:"\n",TAB:"\t",SPACE:" "}[e];return s?s:t[e]?void 0:e}};void 0===angular.element.prototype.querySelectorAll&&(angular.element.prototype.querySelectorAll=function(e){return angular.element(this[0].querySelectorAll(e))}),void 0===angular.element.prototype.closest&&(angular.element.prototype.closest=function(e){for(var t=this[0],s=t.matches||t.webkitMatchesSelector||t.mozMatchesSelector||t.msMatchesSelector;t;){if(s.bind(t)(e))return t;t=t.parentElement}return!1});var s=0,i=angular.module("ui.select",[]).constant("uiSelectConfig",{theme:"bootstrap",searchEnabled:!0,sortable:!1,placeholder:"",refreshDelay:1e3,closeOnSelect:!0,skipFocusser:!1,dropdownPosition:"auto",removeSelected:!0,resetSearchInput:!0,generateId:function(){return s++},appendToBody:!1,spinnerEnabled:!1,spinnerClass:"glyphicon glyphicon-refresh ui-select-spin",backspaceReset:!0}).service("uiSelectMinErr",function(){var e=angular.$$minErr("ui.select");return function(){var t=e.apply(this,arguments),s=t.message.replace(new RegExp("\nhttp://errors.angularjs.org/.*"),"");return new Error(s)}}).directive("uisTranscludeAppend",function(){return{link:function(e,t,s,i,c){c(e,function(e){t.append(e)})}}}).filter("highlight",function(){function e(e){return(""+e).replace(/([.?*+^$[\]\\(){}|-])/g,"\\$1")}return function(t,s){return s&&t?(""+t).replace(new RegExp(e(s),"gi"),'<span class="ui-select-highlight">$&</span>'):t}}).factory("uisOffset",["$document","$window",function(e,t){return function(s){var i=s[0].getBoundingClientRect();return{width:i.width||s.prop("offsetWidth"),height:i.height||s.prop("offsetHeight"),top:i.top+(t.pageYOffset||e[0].documentElement.scrollTop),left:i.left+(t.pageXOffset||e[0].documentElement.scrollLeft)}}}]);i.factory("$$uisDebounce",["$timeout",function(e){return function(t,s){var i;return function(){var c=this,n=Array.prototype.slice.call(arguments);i&&e.cancel(i),i=e(function(){t.apply(c,n)},s)}}}]),i.directive("uiSelectChoices",["uiSelectConfig","uisRepeatParser","uiSelectMinErr","$compile","$window",function(e,t,s,i,c){return{restrict:"EA",require:"^uiSelect",replace:!0,transclude:!0,templateUrl:function(t){t.addClass("ui-select-choices");var s=t.parent().attr("theme")||e.theme;return s+"/choices.tpl.html"},compile:function(i,n){if(!n.repeat)throw s("repeat","Expected 'repeat' expression.");var l=n.groupBy,a=n.groupFilter;if(l){var r=i.querySelectorAll(".ui-select-choices-group");if(1!==r.length)throw s("rows","Expected 1 .ui-select-choices-group but got '{0}'.",r.length);r.attr("ng-repeat",t.getGroupNgRepeatExpression())}var o=t.parse(n.repeat),u=i.querySelectorAll(".ui-select-choices-row");if(1!==u.length)throw s("rows","Expected 1 .ui-select-choices-row but got '{0}'.",u.length);u.attr("ng-repeat",o.repeatExpression(l)).attr("ng-if","$select.open");var d=i.querySelectorAll(".ui-select-choices-row-inner");if(1!==d.length)throw s("rows","Expected 1 .ui-select-choices-row-inner but got '{0}'.",d.length);d.attr("uis-transclude-append","");var p=c.document.addEventListener?u:d;return p.attr("ng-click","$select.select("+o.itemName+",$select.skipFocusser,$event)"),function(t,s,c,n){n.parseRepeatAttr(c.repeat,l,a),n.disableChoiceExpression=c.uiDisableChoice,n.onHighlightCallback=c.onHighlight,n.minimumInputLength=parseInt(c.minimumInputLength)||0,n.dropdownPosition=c.position?c.position.toLowerCase():e.dropdownPosition,t.$watch("$select.search",function(e){e&&!n.open&&n.multiple&&n.activate(!1,!0),n.activeIndex=n.tagging.isActivated?-1:0,!c.minimumInputLength||n.search.length>=c.minimumInputLength?n.refresh(c.refresh):n.items=[]}),c.$observe("refreshDelay",function(){var s=t.$eval(c.refreshDelay);n.refreshDelay=void 0!==s?s:e.refreshDelay}),t.$watch("$select.open",function(e){e?(i.attr("role","listbox"),n.refresh(c.refresh)):s.removeAttr("role")})}}}}]),i.controller("uiSelectCtrl",["$scope","$element","$timeout","$filter","$$uisDebounce","uisRepeatParser","uiSelectMinErr","uiSelectConfig","$parse","$injector","$window",function(s,i,c,n,l,a,r,o,u,d,p){function h(e,t,s){if(e.findIndex)return e.findIndex(t,s);for(var i,c=Object(e),n=c.length>>>0,l=0;l<n;l++)if(i=c[l],t.call(s,i,l,c))return l;return-1}function g(){y.resetSearchInput&&(y.search=x,y.selected&&y.items.length&&!y.multiple&&(y.activeIndex=h(y.items,function(e){return angular.equals(this,e)},y.selected)))}function f(e,t){var s,i,c=[];for(s=0;s<t.length;s++)for(i=0;i<e.length;i++)e[i].name==[t[s]]&&c.push(e[i]);return c}function v(e,t){var s=I.indexOf(e);t&&s===-1&&I.push(e),!t&&s>-1&&I.splice(s,1)}function m(e){return I.indexOf(e)>-1}function $(e){function t(e,t){var s=i.indexOf(e);t&&s===-1&&i.push(e),!t&&s>-1&&i.splice(s,1)}function s(e){return i.indexOf(e)>-1}if(e){var i=[];y.isLocked=function(e,i){var c=!1,n=y.selected[i];return n&&(e?(c=!!e.$eval(y.lockChoiceExpression),t(n,c)):c=s(n)),c}}}function b(e){var s=!0;switch(e){case t.DOWN:if(!y.open&&y.multiple)y.activate(!1,!0);else if(y.activeIndex<y.items.length-1)for(var i=++y.activeIndex;m(y.items[i])&&i<y.items.length;)y.activeIndex=++i;break;case t.UP:var c=0===y.search.length&&y.tagging.isActivated?-1:0;if(!y.open&&y.multiple)y.activate(!1,!0);else if(y.activeIndex>c)for(var n=--y.activeIndex;m(y.items[n])&&n>c;)y.activeIndex=--n;break;case t.TAB:y.multiple&&!y.open||y.select(y.items[y.activeIndex],!0);break;case t.ENTER:y.open&&(y.tagging.isActivated||y.activeIndex>=0)?y.select(y.items[y.activeIndex],y.skipFocusser):y.activate(!1,!0);break;case t.ESC:y.close();break;default:s=!1}return s}function w(){var e=i.querySelectorAll(".ui-select-choices-content"),t=e.querySelectorAll(".ui-select-choices-row");if(t.length<1)throw r("choices","Expected multiple .ui-select-choices-row but got '{0}'.",t.length);if(!(y.activeIndex<0)){var s=t[y.activeIndex],c=s.offsetTop+s.clientHeight-e[0].scrollTop,n=e[0].offsetHeight;c>n?e[0].scrollTop+=c-n:c<s.clientHeight&&(y.isGrouped&&0===y.activeIndex?e[0].scrollTop=0:e[0].scrollTop-=s.clientHeight-c)}}var y=this,x="";if(y.placeholder=o.placeholder,y.searchEnabled=o.searchEnabled,y.sortable=o.sortable,y.refreshDelay=o.refreshDelay,y.paste=o.paste,y.resetSearchInput=o.resetSearchInput,y.refreshing=!1,y.spinnerEnabled=o.spinnerEnabled,y.spinnerClass=o.spinnerClass,y.removeSelected=o.removeSelected,y.closeOnSelect=!0,y.skipFocusser=!1,y.search=x,y.activeIndex=0,y.items=[],y.open=!1,y.focus=!1,y.disabled=!1,y.selected=void 0,y.dropdownPosition="auto",y.focusser=void 0,y.multiple=void 0,y.disableChoiceExpression=void 0,y.tagging={isActivated:!1,fct:void 0},y.taggingTokens={isActivated:!1,tokens:void 0},y.lockChoiceExpression=void 0,y.clickTriggeredSelect=!1,y.$filter=n,y.$element=i,y.$animate=function(){try{return d.get("$animate")}catch(e){return null}}(),y.searchInput=i.querySelectorAll("input.ui-select-search"),1!==y.searchInput.length)throw r("searchInput","Expected 1 input.ui-select-search but got '{0}'.",y.searchInput.length);y.isEmpty=function(){return e(y.selected)||""===y.selected||y.multiple&&0===y.selected.length},y.activate=function(e,t){if(y.disabled||y.open)y.open&&!y.searchEnabled&&y.close();else{t||g(),s.$broadcast("uis:activate"),y.open=!0,y.activeIndex=y.activeIndex>=y.items.length?0:y.activeIndex,y.activeIndex===-1&&y.taggingLabel!==!1&&(y.activeIndex=0);var n=i.querySelectorAll(".ui-select-choices-content"),l=i.querySelectorAll(".ui-select-search");if(y.$animate&&y.$animate.on&&y.$animate.enabled(n[0])){var a=function(t,s){"start"===s&&0===y.items.length?(y.$animate.off("removeClass",l[0],a),c(function(){y.focusSearchInput(e)})):"close"===s&&(y.$animate.off("enter",n[0],a),c(function(){y.focusSearchInput(e)}))};y.items.length>0?y.$animate.on("enter",n[0],a):y.$animate.on("removeClass",l[0],a)}else c(function(){y.focusSearchInput(e),!y.tagging.isActivated&&y.items.length>1&&w()})}},y.focusSearchInput=function(e){y.search=e||y.search,y.searchInput[0].focus()},y.findGroupByName=function(e){return y.groups&&y.groups.filter(function(t){return t.name===e})[0]},y.parseRepeatAttr=function(e,t,i){function c(e){var c=s.$eval(t);if(y.groups=[],angular.forEach(e,function(e){var t=angular.isFunction(c)?c(e):e[c],s=y.findGroupByName(t);s?s.items.push(e):y.groups.push({name:t,items:[e]})}),i){var n=s.$eval(i);angular.isFunction(n)?y.groups=n(y.groups):angular.isArray(n)&&(y.groups=f(y.groups,n))}y.items=[],y.groups.forEach(function(e){y.items=y.items.concat(e.items)})}function n(e){y.items=e||[]}y.setItemsFn=t?c:n,y.parserResult=a.parse(e),y.isGrouped=!!t,y.itemProperty=y.parserResult.itemName;var l=y.parserResult.source,o=function(){var e=l(s);s.$uisSource=Object.keys(e).map(function(t){var s={};return s[y.parserResult.keyName]=t,s.value=e[t],s})};y.parserResult.keyName&&(o(),y.parserResult.source=u("$uisSource"+y.parserResult.filters),s.$watch(l,function(e,t){e!==t&&o()},!0)),y.refreshItems=function(e){e=e||y.parserResult.source(s);var t=y.selected;if(y.isEmpty()||angular.isArray(t)&&!t.length||!y.multiple||!y.removeSelected)y.setItemsFn(e);else if(void 0!==e&&null!==e){var i=e.filter(function(e){return angular.isArray(t)?t.every(function(t){return!angular.equals(e,t)}):!angular.equals(e,t)});y.setItemsFn(i)}"auto"!==y.dropdownPosition&&"up"!==y.dropdownPosition||s.calculateDropdownPos(),s.$broadcast("uis:refresh")},s.$watchCollection(y.parserResult.source,function(e){if(void 0===e||null===e)y.items=[];else{if(!angular.isArray(e))throw r("items","Expected an array but got '{0}'.",e);y.refreshItems(e),angular.isDefined(y.ngModel.$modelValue)&&(y.ngModel.$modelValue=null)}})};var E;y.refresh=function(e){void 0!==e&&(E&&c.cancel(E),E=c(function(){if(s.$select.search.length>=s.$select.minimumInputLength){var t=s.$eval(e);t&&angular.isFunction(t.then)&&!y.refreshing&&(y.refreshing=!0,t["finally"](function(){y.refreshing=!1}))}},y.refreshDelay))},y.isActive=function(e){if(!y.open)return!1;var t=y.items.indexOf(e[y.itemProperty]),s=t==y.activeIndex;return!(!s||t<0)&&(s&&!angular.isUndefined(y.onHighlightCallback)&&e.$eval(y.onHighlightCallback),s)};var S=function(e){return y.selected&&angular.isArray(y.selected)&&y.selected.filter(function(t){return angular.equals(t,e)}).length>0},I=[];y.isDisabled=function(e){if(y.open){var t=e[y.itemProperty],s=y.items.indexOf(t),i=!1;if(s>=0&&(angular.isDefined(y.disableChoiceExpression)||y.multiple)){if(t.isTag)return!1;y.multiple&&(i=S(t)),!i&&angular.isDefined(y.disableChoiceExpression)&&(i=!!e.$eval(y.disableChoiceExpression)),v(t,i)}return i}},y.select=function(t,i,c){if(e(t)||!m(t)){if(!y.items&&!y.search&&!y.tagging.isActivated)return;if(!t||!m(t)){if(y.clickTriggeredSelect=!1,c&&("click"===c.type||"touchend"===c.type)&&t&&(y.clickTriggeredSelect=!0),y.tagging.isActivated&&y.clickTriggeredSelect===!1){if(y.taggingLabel===!1)if(y.activeIndex<0){if(void 0===t&&(t=void 0!==y.tagging.fct?y.tagging.fct(y.search):y.search),!t||angular.equals(y.items[0],t))return}else t=y.items[y.activeIndex];else if(0===y.activeIndex){if(void 0===t)return;if(void 0!==y.tagging.fct&&"string"==typeof t){if(t=y.tagging.fct(t),!t)return}else"string"==typeof t&&(t=t.replace(y.taggingLabel,"").trim())}if(S(t))return void y.close(i)}g(),s.$broadcast("uis:select",t),y.closeOnSelect&&y.close(i)}}},y.close=function(e){y.open&&(y.ngModel&&y.ngModel.$setTouched&&y.ngModel.$setTouched(),y.open=!1,g(),s.$broadcast("uis:close",e))},y.setFocus=function(){y.focus||y.focusInput[0].focus()},y.clear=function(e){y.select(null),e.stopPropagation(),c(function(){y.focusser[0].focus()},0,!1)},y.toggle=function(e){y.open?(y.close(),e.preventDefault(),e.stopPropagation()):y.activate()},y.isLocked=function(){return!1},s.$watch(function(){return angular.isDefined(y.lockChoiceExpression)&&""!==y.lockChoiceExpression},$);var C=null,k=!1;y.sizeSearchInput=function(){var e=y.searchInput[0],t=y.$element[0],i=function(){return t.clientWidth*!!e.offsetParent},n=function(t){if(0===t)return!1;var s=t-e.offsetLeft;return s<50&&(s=t),y.searchInput.css("width",s+"px"),!0};y.searchInput.css("width","10px"),c(function(){null!==C||n(i())||(C=s.$watch(function(){k||(k=!0,s.$$postDigest(function(){k=!1,n(i())&&(C(),C=null)}))},angular.noop))})},y.searchInput.on("keydown",function(e){var i=e.which;~[t.ENTER,t.ESC].indexOf(i)&&(e.preventDefault(),e.stopPropagation()),s.$apply(function(){var s=!1;if((y.items.length>0||y.tagging.isActivated)&&(b(i)||y.searchEnabled||(e.preventDefault(),e.stopPropagation()),y.taggingTokens.isActivated)){for(var n=0;n<y.taggingTokens.tokens.length;n++)y.taggingTokens.tokens[n]===t.MAP[e.keyCode]&&y.search.length>0&&(s=!0);s&&c(function(){y.searchInput.triggerHandler("tagged");var s=y.search.replace(t.MAP[e.keyCode],"").trim();y.tagging.fct&&(s=y.tagging.fct(s)),s&&y.select(s,!0)})}}),t.isVerticalMovement(i)&&y.items.length>0&&w(),i!==t.ENTER&&i!==t.ESC||(e.preventDefault(),e.stopPropagation())}),y.searchInput.on("paste",function(e){var s;if(s=window.clipboardData&&window.clipboardData.getData?window.clipboardData.getData("Text"):(e.originalEvent||e).clipboardData.getData("text/plain"),s=y.search+s,s&&s.length>0)if(y.taggingTokens.isActivated){for(var i=[],c=0;c<y.taggingTokens.tokens.length;c++){var n=t.toSeparator(y.taggingTokens.tokens[c])||y.taggingTokens.tokens[c];if(s.indexOf(n)>-1){i=s.split(n);break}}0===i.length&&(i=[s]);var l=y.search;angular.forEach(i,function(e){var t=y.tagging.fct?y.tagging.fct(e):e;t&&y.select(t,!0)}),y.search=l||x,e.preventDefault(),e.stopPropagation()}else y.paste&&(y.paste(s),y.search=x,e.preventDefault(),e.stopPropagation())}),y.searchInput.on("tagged",function(){c(function(){g()})});var A=l(function(){y.sizeSearchInput()},50);angular.element(p).bind("resize",A),s.$on("$destroy",function(){y.searchInput.off("keyup keydown tagged blur paste"),angular.element(p).off("resize",A)}),s.$watch("$select.activeIndex",function(e){e&&i.find("input").attr("aria-activedescendant","ui-select-choices-row-"+y.generatedId+"-"+e)}),s.$watch("$select.open",function(e){e||i.find("input").removeAttr("aria-activedescendant")})}]),i.directive("uiSelect",["$document","uiSelectConfig","uiSelectMinErr","uisOffset","$compile","$parse","$timeout",function(e,t,s,i,c,n,l){return{restrict:"EA",templateUrl:function(e,s){var i=s.theme||t.theme;return i+(angular.isDefined(s.multiple)?"/select-multiple.tpl.html":"/select.tpl.html")},replace:!0,transclude:!0,require:["uiSelect","^ngModel"],scope:!0,controller:"uiSelectCtrl",controllerAs:"$select",compile:function(c,a){var r=/{(.*)}\s*{(.*)}/.exec(a.ngClass);if(r){var o="{"+r[1]+", "+r[2]+"}";a.ngClass=o,c.attr("ng-class",o)}return angular.isDefined(a.multiple)?c.append("<ui-select-multiple/>").removeAttr("multiple"):c.append("<ui-select-single/>"),a.inputId&&(c.querySelectorAll("input.ui-select-search")[0].id=a.inputId),function(c,a,r,o,u){function d(e){if(g.open){var t=!1;if(t=window.jQuery?window.jQuery.contains(a[0],e.target):a[0].contains(e.target),!t&&!g.clickTriggeredSelect){var s;if(g.skipFocusser)s=!0;else{var i=["input","button","textarea","select"],n=angular.element(e.target).controller("uiSelect");s=n&&n!==g,s||(s=~i.indexOf(e.target.tagName.toLowerCase()))}g.close(s),c.$digest()}g.clickTriggeredSelect=!1}}function p(){var t=i(a);m=angular.element('<div class="ui-select-placeholder"></div>'),m[0].style.width=t.width+"px",m[0].style.height=t.height+"px",a.after(m),$=a[0].style.width,e.find("body").append(a),a[0].style.position="absolute",a[0].style.left=t.left+"px",a[0].style.top=t.top+"px",a[0].style.width=t.width+"px"}function h(){null!==m&&(m.replaceWith(a),m=null,a[0].style.position="",a[0].style.left="",a[0].style.top="",a[0].style.width=$,g.setFocus())}var g=o[0],f=o[1];g.generatedId=t.generateId(),g.baseTitle=r.title||"Select box",g.focusserTitle=g.baseTitle+" focus",g.focusserId="focusser-"+g.generatedId,g.closeOnSelect=function(){return angular.isDefined(r.closeOnSelect)?n(r.closeOnSelect)():t.closeOnSelect}(),c.$watch("skipFocusser",function(){var e=c.$eval(r.skipFocusser);g.skipFocusser=void 0!==e?e:t.skipFocusser}),g.onSelectCallback=n(r.onSelect),g.onRemoveCallback=n(r.onRemove),g.ngModel=f,g.choiceGrouped=function(e){return g.isGrouped&&e&&e.name},r.tabindex&&r.$observe("tabindex",function(e){g.focusInput.attr("tabindex",e),a.removeAttr("tabindex")}),c.$watch(function(){return c.$eval(r.searchEnabled)},function(e){g.searchEnabled=void 0!==e?e:t.searchEnabled}),c.$watch("sortable",function(){var e=c.$eval(r.sortable);g.sortable=void 0!==e?e:t.sortable}),r.$observe("backspaceReset",function(){var e=c.$eval(r.backspaceReset);g.backspaceReset=void 0===e||e}),r.$observe("limit",function(){g.limit=angular.isDefined(r.limit)?parseInt(r.limit,10):void 0}),c.$watch("removeSelected",function(){var e=c.$eval(r.removeSelected);g.removeSelected=void 0!==e?e:t.removeSelected}),r.$observe("disabled",function(){g.disabled=void 0!==r.disabled&&r.disabled}),r.$observe("resetSearchInput",function(){var e=c.$eval(r.resetSearchInput);g.resetSearchInput=void 0===e||e}),r.$observe("paste",function(){g.paste=c.$eval(r.paste)}),r.$observe("tagging",function(){if(void 0!==r.tagging){var e=c.$eval(r.tagging);g.tagging={isActivated:!0,fct:e!==!0?e:void 0}}else g.tagging={isActivated:!1,fct:void 0}}),r.$observe("taggingLabel",function(){void 0!==r.tagging&&("false"===r.taggingLabel?g.taggingLabel=!1:g.taggingLabel=void 0!==r.taggingLabel?r.taggingLabel:"(new)")}),r.$observe("taggingTokens",function(){if(void 0!==r.tagging){var e=void 0!==r.taggingTokens?r.taggingTokens.split("|"):[",","ENTER"];g.taggingTokens={isActivated:!0,tokens:e}}}),r.$observe("spinnerEnabled",function(){var e=c.$eval(r.spinnerEnabled);g.spinnerEnabled=void 0!==e?e:t.spinnerEnabled}),r.$observe("spinnerClass",function(){var e=r.spinnerClass;g.spinnerClass=void 0!==e?r.spinnerClass:t.spinnerClass}),angular.isDefined(r.autofocus)&&l(function(){g.setFocus()}),angular.isDefined(r.focusOn)&&c.$on(r.focusOn,function(){l(function(){g.setFocus()})}),e.on("click",d),c.$on("$destroy",function(){e.off("click",d)}),u(c,function(e){var t=angular.element("<div>").append(e),i=t.querySelectorAll(".ui-select-match");if(i.removeAttr("ui-select-match"),i.removeAttr("data-ui-select-match"),1!==i.length)throw s("transcluded","Expected 1 .ui-select-match but got '{0}'.",i.length);a.querySelectorAll(".ui-select-match").replaceWith(i);var c=t.querySelectorAll(".ui-select-choices");if(c.removeAttr("ui-select-choices"),c.removeAttr("data-ui-select-choices"),1!==c.length)throw s("transcluded","Expected 1 .ui-select-choices but got '{0}'.",c.length);a.querySelectorAll(".ui-select-choices").replaceWith(c);var n=t.querySelectorAll(".ui-select-no-choice");n.removeAttr("ui-select-no-choice"),n.removeAttr("data-ui-select-no-choice"),1==n.length&&a.querySelectorAll(".ui-select-no-choice").replaceWith(n)});var v=c.$eval(r.appendToBody);(void 0!==v?v:t.appendToBody)&&(c.$watch("$select.open",function(e){e?p():h()}),c.$on("$destroy",function(){h()}));var m=null,$="",b=null,w="direction-up";c.$watch("$select.open",function(){"auto"!==g.dropdownPosition&&"up"!==g.dropdownPosition||c.calculateDropdownPos()});var y=function(e,t){e=e||i(a),t=t||i(b),b[0].style.position="absolute",b[0].style.top=t.height*-1+"px",a.addClass(w)},x=function(e,t){a.removeClass(w),e=e||i(a),t=t||i(b),b[0].style.position="",b[0].style.top=""},E=function(){l(function(){if("up"===g.dropdownPosition)y();else{a.removeClass(w);var t=i(a),s=i(b),c=e[0].documentElement.scrollTop||e[0].body.scrollTop;t.top+t.height+s.height>c+e[0].documentElement.clientHeight?y(t,s):x(t,s)}b[0].style.opacity=1})},S=!1;c.calculateDropdownPos=function(){if(g.open){if(b=angular.element(a).querySelectorAll(".ui-select-dropdown"),0===b.length)return;if(""!==g.search||S||(b[0].style.opacity=0,S=!0),!i(b).height&&g.$animate&&g.$animate.on&&g.$animate.enabled(b)){var e=!0;g.$animate.on("enter",b,function(t,s){"close"===s&&e&&(E(),e=!1)})}else E()}else{if(null===b||0===b.length)return;b[0].style.opacity=0,b[0].style.position="",b[0].style.top="",a.removeClass(w)}}}}}}]),i.directive("uiSelectMatch",["uiSelectConfig",function(e){function t(e,t){return e[0].hasAttribute(t)?e.attr(t):e[0].hasAttribute("data-"+t)?e.attr("data-"+t):e[0].hasAttribute("x-"+t)?e.attr("x-"+t):void 0}return{restrict:"EA",require:"^uiSelect",replace:!0,transclude:!0,templateUrl:function(s){s.addClass("ui-select-match");var i=s.parent(),c=t(i,"theme")||e.theme,n=angular.isDefined(t(i,"multiple"));return c+(n?"/match-multiple.tpl.html":"/match.tpl.html")},link:function(t,s,i,c){function n(e){c.allowClear=!!angular.isDefined(e)&&(""===e||"true"===e.toLowerCase())}c.lockChoiceExpression=i.uiLockChoice,i.$observe("placeholder",function(t){c.placeholder=void 0!==t?t:e.placeholder}),i.$observe("allowClear",n),n(i.allowClear),c.multiple&&c.sizeSearchInput()}}}]),i.directive("uiSelectMultiple",["uiSelectMinErr","$timeout",function(s,i){return{restrict:"EA",require:["^uiSelect","^ngModel"],controller:["$scope","$timeout",function(e,t){var s,i=this,c=e.$select;angular.isUndefined(c.selected)&&(c.selected=[]),e.$evalAsync(function(){s=e.ngModel}),i.activeMatchIndex=-1,i.updateModel=function(){s.$setViewValue(Date.now()),i.refreshComponent()},i.refreshComponent=function(){c.refreshItems&&c.refreshItems(),c.sizeSearchInput&&c.sizeSearchInput()},i.removeChoice=function(s){if(c.isLocked(null,s))return!1;var n=c.selected[s],l={};return l[c.parserResult.itemName]=n,c.selected.splice(s,1),i.activeMatchIndex=-1,c.sizeSearchInput(),t(function(){c.onRemoveCallback(e,{$item:n,$model:c.parserResult.modelMapper(e,l)})}),i.updateModel(),!0},i.getPlaceholder=function(){if(!c.selected||!c.selected.length)return c.placeholder}}],controllerAs:"$selectMultiple",link:function(c,n,l,a){function r(e){return angular.isNumber(e.selectionStart)?e.selectionStart:e.value.length}function o(e){function s(){switch(e){case t.LEFT:return~g.activeMatchIndex?u:l;case t.RIGHT:return~g.activeMatchIndex&&a!==l?o:(p.activate(),!1);case t.BACKSPACE:return~g.activeMatchIndex?g.removeChoice(a)?u:a:l;case t.DELETE:return!!~g.activeMatchIndex&&(g.removeChoice(g.activeMatchIndex),a)}}var i=r(p.searchInput[0]),c=p.selected.length,n=0,l=c-1,a=g.activeMatchIndex,o=g.activeMatchIndex+1,u=g.activeMatchIndex-1,d=a;return!(i>0||p.search.length&&e==t.RIGHT)&&(p.close(),d=s(),p.selected.length&&d!==!1?g.activeMatchIndex=Math.min(l,Math.max(n,d)):g.activeMatchIndex=-1,!0)}function u(e){if(void 0===e||void 0===p.search)return!1;var t=e.filter(function(e){return void 0!==p.search.toUpperCase()&&void 0!==e&&e.toUpperCase()===p.search.toUpperCase()}).length>0;return t}function d(e,t){var s=-1;if(angular.isArray(e))for(var i=angular.copy(e),c=0;c<i.length;c++)if(void 0===p.tagging.fct)i[c]+" "+p.taggingLabel===t&&(s=c);else{var n=i[c];angular.isObject(n)&&(n.isTag=!0),angular.equals(n,t)&&(s=c)}return s}var p=a[0],h=c.ngModel=a[1],g=c.$selectMultiple;p.multiple=!0,p.focusInput=p.searchInput,h.$isEmpty=function(e){return!e||0===e.length},h.$parsers.unshift(function(){for(var e,t={},s=[],i=p.selected.length-1;i>=0;i--)t={},t[p.parserResult.itemName]=p.selected[i],e=p.parserResult.modelMapper(c,t),s.unshift(e);return s}),h.$formatters.unshift(function(e){var t,s=p.parserResult&&p.parserResult.source(c,{$select:{search:""}}),i={};if(!s)return e;var n=[],l=function(e,s){if(e&&e.length){for(var l=e.length-1;l>=0;l--){if(i[p.parserResult.itemName]=e[l],t=p.parserResult.modelMapper(c,i),p.parserResult.trackByExp){var a=/(\w*)\./.exec(p.parserResult.trackByExp),r=/\.([^\s]+)/.exec(p.parserResult.trackByExp);if(a&&a.length>0&&a[1]==p.parserResult.itemName&&r&&r.length>0&&t[r[1]]==s[r[1]])return n.unshift(e[l]),!0}if(angular.equals(t,s))return n.unshift(e[l]),!0}return!1}};if(!e)return n;for(var a=e.length-1;a>=0;a--)l(p.selected,e[a])||l(s,e[a])||n.unshift(e[a]);return n}),c.$watchCollection(function(){return h.$modelValue},function(e,t){t!=e&&(angular.isDefined(h.$modelValue)&&(h.$modelValue=null),g.refreshComponent())}),h.$render=function(){if(!angular.isArray(h.$viewValue)){if(!e(h.$viewValue))throw s("multiarr","Expected model value to be array but got '{0}'",h.$viewValue);h.$viewValue=[]}p.selected=h.$viewValue,g.refreshComponent(),c.$evalAsync()},c.$on("uis:select",function(e,t){if(!(p.selected.length>=p.limit)){p.selected.push(t);var s={};s[p.parserResult.itemName]=t,i(function(){p.onSelectCallback(c,{$item:t,$model:p.parserResult.modelMapper(c,s)})}),g.updateModel()}}),c.$on("uis:activate",function(){g.activeMatchIndex=-1}),c.$watch("$select.disabled",function(e,t){t&&!e&&p.sizeSearchInput()}),p.searchInput.on("keydown",function(e){var s=e.which;c.$apply(function(){var i=!1;t.isHorizontalMovement(s)&&(i=o(s)),i&&s!=t.TAB&&(e.preventDefault(),e.stopPropagation())})}),p.searchInput.on("keyup",function(e){if(t.isVerticalMovement(e.which)||c.$evalAsync(function(){p.activeIndex=p.taggingLabel===!1?-1:0}),p.tagging.isActivated&&p.search.length>0){if(e.which===t.TAB||t.isControl(e)||t.isFunctionKey(e)||e.which===t.ESC||t.isVerticalMovement(e.which))return;if(p.activeIndex=p.taggingLabel===!1?-1:0,p.taggingLabel===!1)return;var s,i,n,l,a=angular.copy(p.items),r=angular.copy(p.items),o=!1,h=-1;if(void 0!==p.tagging.fct){if(n=p.$filter("filter")(a,{isTag:!0}),n.length>0&&(l=n[0]),a.length>0&&l&&(o=!0,a=a.slice(1,a.length),r=r.slice(1,r.length)),s=p.tagging.fct(p.search),r.some(function(e){return angular.equals(e,s)})||p.selected.some(function(e){return angular.equals(e,s)}))return void c.$evalAsync(function(){p.activeIndex=0,p.items=a});s&&(s.isTag=!0)}else{if(n=p.$filter("filter")(a,function(e){return e.match(p.taggingLabel)}),n.length>0&&(l=n[0]),i=a[0],void 0!==i&&a.length>0&&l&&(o=!0,a=a.slice(1,a.length),r=r.slice(1,r.length)),s=p.search+" "+p.taggingLabel,d(p.selected,p.search)>-1)return;if(u(r.concat(p.selected)))return void(o&&(a=r,c.$evalAsync(function(){p.activeIndex=0,p.items=a})));if(u(r))return void(o&&(p.items=r.slice(1,r.length)))}o&&(h=d(p.selected,s)),h>-1?a=a.slice(h+1,a.length-1):(a=[],s&&a.push(s),a=a.concat(r)),c.$evalAsync(function(){if(p.activeIndex=0,p.items=a,p.isGrouped){var e=s?a.slice(1):a;p.setItemsFn(e),s&&(p.items.unshift(s),p.groups.unshift({name:"",items:[s],tagging:!0}))}})}}),p.searchInput.on("blur",function(){i(function(){g.activeMatchIndex=-1})})}}}]),i.directive("uiSelectNoChoice",["uiSelectConfig",function(e){return{restrict:"EA",require:"^uiSelect",replace:!0,transclude:!0,templateUrl:function(t){t.addClass("ui-select-no-choice");var s=t.parent().attr("theme")||e.theme;return s+"/no-choice.tpl.html"}}}]),i.directive("uiSelectSingle",["$timeout","$compile",function(s,i){return{restrict:"EA",require:["^uiSelect","^ngModel"],link:function(c,n,l,a){var r=a[0],o=a[1];o.$parsers.unshift(function(t){if(e(t))return t;var s,i={};return i[r.parserResult.itemName]=t,s=r.parserResult.modelMapper(c,i)}),o.$formatters.unshift(function(t){if(e(t))return t;var s,i=r.parserResult&&r.parserResult.source(c,{$select:{search:""}}),n={};if(i){var l=function(e){return n[r.parserResult.itemName]=e,s=r.parserResult.modelMapper(c,n),s===t};if(r.selected&&l(r.selected))return r.selected;for(var a=i.length-1;a>=0;a--)if(l(i[a]))return i[a]}return t}),c.$watch("$select.selected",function(e){o.$viewValue!==e&&o.$setViewValue(e)}),o.$render=function(){r.selected=o.$viewValue},c.$on("uis:select",function(t,i){r.selected=i;var n={};n[r.parserResult.itemName]=i,s(function(){r.onSelectCallback(c,{$item:i,$model:e(i)?i:r.parserResult.modelMapper(c,n)})})}),c.$on("uis:close",function(e,t){s(function(){r.focusser.prop("disabled",!1),t||r.focusser[0].focus()},0,!1)}),c.$on("uis:activate",function(){u.prop("disabled",!0)});var u=angular.element("<input ng-disabled='$select.disabled' class='ui-select-focusser ui-select-offscreen' type='text' id='{{ $select.focusserId }}' aria-label='{{ $select.focusserTitle }}' aria-haspopup='true' role='button' />");i(u)(c),r.focusser=u,r.focusInput=u,n.parent().append(u),u.bind("focus",function(){c.$evalAsync(function(){r.focus=!0})}),u.bind("blur",function(){c.$evalAsync(function(){r.focus=!1})}),u.bind("keydown",function(e){return e.which===t.BACKSPACE&&r.backspaceReset!==!1?(e.preventDefault(),e.stopPropagation(),r.select(void 0),void c.$apply()):void(e.which===t.TAB||t.isControl(e)||t.isFunctionKey(e)||e.which===t.ESC||(e.which!=t.DOWN&&e.which!=t.UP&&e.which!=t.ENTER&&e.which!=t.SPACE||(e.preventDefault(),e.stopPropagation(),r.activate()),c.$digest()))}),u.bind("keyup input",function(e){e.which===t.TAB||t.isControl(e)||t.isFunctionKey(e)||e.which===t.ESC||e.which==t.ENTER||e.which===t.BACKSPACE||(r.activate(u.val()),u.val(""),c.$digest())})}}}]),i.directive("uiSelectSort",["$timeout","uiSelectConfig","uiSelectMinErr",function(e,t,s){return{require:["^^uiSelect","^ngModel"],link:function(t,i,c,n){if(null===t[c.uiSelectSort])throw s("sort","Expected a list to sort");var l=n[0],a=n[1],r=angular.extend({axis:"horizontal"},t.$eval(c.uiSelectSortOptions)),o=r.axis,u="dragging",d="dropping",p="dropping-before",h="dropping-after";t.$watch(function(){return l.sortable},function(e){e?i.attr("draggable",!0):i.removeAttr("draggable")}),i.on("dragstart",function(e){i.addClass(u),(e.dataTransfer||e.originalEvent.dataTransfer).setData("text",t.$index.toString())}),i.on("dragend",function(){v(u)});var g,f=function(e,t){this.splice(t,0,this.splice(e,1)[0])},v=function(e){angular.forEach(l.$element.querySelectorAll("."+e),function(t){angular.element(t).removeClass(e)})},m=function(e){e.preventDefault();var t="vertical"===o?e.offsetY||e.layerY||(e.originalEvent?e.originalEvent.offsetY:0):e.offsetX||e.layerX||(e.originalEvent?e.originalEvent.offsetX:0);t<this["vertical"===o?"offsetHeight":"offsetWidth"]/2?(v(h),i.addClass(p)):(v(p),i.addClass(h))},$=function(t){t.preventDefault();var s=parseInt((t.dataTransfer||t.originalEvent.dataTransfer).getData("text"),10);e.cancel(g),g=e(function(){b(s)},20)},b=function(e){var s=t.$eval(c.uiSelectSort),n=s[e],l=null;l=i.hasClass(p)?e<t.$index?t.$index-1:t.$index:e<t.$index?t.$index:t.$index+1,f.apply(s,[e,l]),a.$setViewValue(Date.now()),t.$apply(function(){t.$emit("uiSelectSort:change",{array:s,item:n,from:e,to:l})}),v(d),v(p),v(h),i.off("drop",$)};i.on("dragenter",function(){i.hasClass(u)||(i.addClass(d),i.on("dragover",m),i.on("drop",$))}),i.on("dragleave",function(e){e.target==i&&(v(d),v(p),v(h),i.off("dragover",m),i.off("drop",$))})}}}]),i.directive("uisOpenClose",["$parse","$timeout",function(e,t){return{restrict:"A",require:"uiSelect",link:function(s,i,c,n){n.onOpenCloseCallback=e(c.uisOpenClose),s.$watch("$select.open",function(e,i){e!==i&&t(function(){n.onOpenCloseCallback(s,{isOpen:e});
	})})}}}]),i.service("uisRepeatParser",["uiSelectMinErr","$parse",function(e,t){var s=this;s.parse=function(s){var i;if(i=s.match(/^\s*(?:([\s\S]+?)\s+as\s+)?(?:([\$\w][\$\w]*)|(?:\(\s*([\$\w][\$\w]*)\s*,\s*([\$\w][\$\w]*)\s*\)))\s+in\s+(\s*[\s\S]+?)?(?:\s+track\s+by\s+([\s\S]+?))?\s*$/),!i)throw e("iexp","Expected expression in form of '_item_ in _collection_[ track by _id_]' but got '{0}'.",s);var c=i[5],n="";if(i[3]){c=i[5].replace(/(^\()|(\)$)/g,"");var l=i[5].match(/^\s*(?:[\s\S]+?)(?:[^\|]|\|\|)+([\s\S]*)\s*$/);l&&l[1].trim()&&(n=l[1],c=c.replace(n,""))}return{itemName:i[4]||i[2],keyName:i[3],source:t(c),filters:n,trackByExp:i[6],modelMapper:t(i[1]||i[4]||i[2]),repeatExpression:function(e){var t=this.itemName+" in "+(e?"$group.items":"$select.items");return this.trackByExp&&(t+=" track by "+this.trackByExp),t}}},s.getGroupNgRepeatExpression=function(){return"$group in $select.groups track by $group.name"}}])}(),angular.module("ui.select").run(["$templateCache",function(e){e.put("bootstrap/choices.tpl.html",'<ul class="ui-select-choices ui-select-choices-content ui-select-dropdown dropdown-menu" ng-show="$select.open && $select.items.length > 0"><li class="ui-select-choices-group" id="ui-select-choices-{{ $select.generatedId }}"><div class="divider" ng-show="$select.isGrouped && $index > 0"></div><div ng-show="$select.isGrouped" class="ui-select-choices-group-label dropdown-header" ng-bind="$group.name"></div><div ng-attr-id="ui-select-choices-row-{{ $select.generatedId }}-{{$index}}" class="ui-select-choices-row" ng-class="{active: $select.isActive(this), disabled: $select.isDisabled(this)}" role="option"><span class="ui-select-choices-row-inner"></span></div></li></ul>'),e.put("bootstrap/match-multiple.tpl.html",'<span class="ui-select-match"><span ng-repeat="$item in $select.selected track by $index"><span class="ui-select-match-item btn btn-default btn-xs" tabindex="-1" type="button" ng-disabled="$select.disabled" ng-click="$selectMultiple.activeMatchIndex = $index;" ng-class="{\'btn-primary\':$selectMultiple.activeMatchIndex === $index, \'select-locked\':$select.isLocked(this, $index)}" ui-select-sort="$select.selected"><span class="close ui-select-match-close" ng-hide="$select.disabled" ng-click="$selectMultiple.removeChoice($index)">&nbsp;&times;</span> <span uis-transclude-append=""></span></span></span></span>'),e.put("bootstrap/match.tpl.html",'<div class="ui-select-match" ng-hide="$select.open && $select.searchEnabled" ng-disabled="$select.disabled" ng-class="{\'btn-default-focus\':$select.focus}"><span tabindex="-1" class="btn btn-default form-control ui-select-toggle" aria-label="{{ $select.baseTitle }} activate" ng-disabled="$select.disabled" ng-click="$select.activate()" style="outline: 0;"><span ng-show="$select.isEmpty()" class="ui-select-placeholder text-muted">{{$select.placeholder}}</span> <span ng-hide="$select.isEmpty()" class="ui-select-match-text pull-left" ng-class="{\'ui-select-allow-clear\': $select.allowClear && !$select.isEmpty()}" ng-transclude=""></span> <i class="caret pull-right" ng-click="$select.toggle($event)"></i> <a ng-show="$select.allowClear && !$select.isEmpty() && ($select.disabled !== true)" aria-label="{{ $select.baseTitle }} clear" style="margin-right: 10px" ng-click="$select.clear($event)" class="btn btn-xs btn-link pull-right"><i class="glyphicon glyphicon-remove" aria-hidden="true"></i></a></span></div>'),e.put("bootstrap/no-choice.tpl.html",'<ul class="ui-select-no-choice dropdown-menu" ng-show="$select.items.length == 0"><li ng-transclude=""></li></ul>'),e.put("bootstrap/select-multiple.tpl.html",'<div class="ui-select-container ui-select-multiple ui-select-bootstrap dropdown form-control" ng-class="{open: $select.open}"><div><div class="ui-select-match"></div><input type="search" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" class="ui-select-search input-xs" placeholder="{{$selectMultiple.getPlaceholder()}}" ng-disabled="$select.disabled" ng-click="$select.activate()" ng-model="$select.search" role="combobox" aria-expanded="{{$select.open}}" aria-label="{{$select.baseTitle}}" ng-class="{\'spinner\': $select.refreshing}" ondrop="return false;"></div><div class="ui-select-choices"></div><div class="ui-select-no-choice"></div></div>'),e.put("bootstrap/select.tpl.html",'<div class="ui-select-container ui-select-bootstrap dropdown" ng-class="{open: $select.open}"><div class="ui-select-match"></div><span ng-show="$select.open && $select.refreshing && $select.spinnerEnabled" class="ui-select-refreshing {{$select.spinnerClass}}"></span> <input type="search" autocomplete="off" tabindex="-1" aria-expanded="true" aria-label="{{ $select.baseTitle }}" aria-owns="ui-select-choices-{{ $select.generatedId }}" class="form-control ui-select-search" ng-class="{ \'ui-select-search-hidden\' : !$select.searchEnabled }" placeholder="{{$select.placeholder}}" ng-model="$select.search" ng-show="$select.open"><div class="ui-select-choices"></div><div class="ui-select-no-choice"></div></div>'),e.put("select2/choices.tpl.html",'<ul tabindex="-1" class="ui-select-choices ui-select-choices-content select2-results"><li class="ui-select-choices-group" ng-class="{\'select2-result-with-children\': $select.choiceGrouped($group) }"><div ng-show="$select.choiceGrouped($group)" class="ui-select-choices-group-label select2-result-label" ng-bind="$group.name"></div><ul id="ui-select-choices-{{ $select.generatedId }}" ng-class="{\'select2-result-sub\': $select.choiceGrouped($group), \'select2-result-single\': !$select.choiceGrouped($group) }"><li role="option" ng-attr-id="ui-select-choices-row-{{ $select.generatedId }}-{{$index}}" class="ui-select-choices-row" ng-class="{\'select2-highlighted\': $select.isActive(this), \'select2-disabled\': $select.isDisabled(this)}"><div class="select2-result-label ui-select-choices-row-inner"></div></li></ul></li></ul>'),e.put("select2/match-multiple.tpl.html",'<span class="ui-select-match"><li class="ui-select-match-item select2-search-choice" ng-repeat="$item in $select.selected track by $index" ng-class="{\'select2-search-choice-focus\':$selectMultiple.activeMatchIndex === $index, \'select2-locked\':$select.isLocked(this, $index)}" ui-select-sort="$select.selected"><span uis-transclude-append=""></span> <a href="javascript:;" class="ui-select-match-close select2-search-choice-close" ng-click="$selectMultiple.removeChoice($index)" tabindex="-1"></a></li></span>'),e.put("select2/match.tpl.html",'<a class="select2-choice ui-select-match" ng-class="{\'select2-default\': $select.isEmpty()}" ng-click="$select.toggle($event)" aria-label="{{ $select.baseTitle }} select"><span ng-show="$select.isEmpty()" class="select2-chosen">{{$select.placeholder}}</span> <span ng-hide="$select.isEmpty()" class="select2-chosen" ng-transclude=""></span> <abbr ng-if="$select.allowClear && !$select.isEmpty()" class="select2-search-choice-close" ng-click="$select.clear($event)"></abbr> <span class="select2-arrow ui-select-toggle"><b></b></span></a>'),e.put("select2/no-choice.tpl.html",'<div class="ui-select-no-choice dropdown" ng-show="$select.items.length == 0"><div class="dropdown-content"><div data-selectable="" ng-transclude=""></div></div></div>'),e.put("select2/select-multiple.tpl.html",'<div class="ui-select-container ui-select-multiple select2 select2-container select2-container-multi" ng-class="{\'select2-container-active select2-dropdown-open open\': $select.open, \'select2-container-disabled\': $select.disabled}"><ul class="select2-choices"><span class="ui-select-match"></span><li class="select2-search-field"><input type="search" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" role="combobox" aria-expanded="true" aria-owns="ui-select-choices-{{ $select.generatedId }}" aria-label="{{ $select.baseTitle }}" aria-activedescendant="ui-select-choices-row-{{ $select.generatedId }}-{{ $select.activeIndex }}" class="select2-input ui-select-search" placeholder="{{$selectMultiple.getPlaceholder()}}" ng-disabled="$select.disabled" ng-hide="$select.disabled" ng-model="$select.search" ng-click="$select.activate()" style="width: 34px;" ondrop="return false;"></li></ul><div class="ui-select-dropdown select2-drop select2-with-searchbox select2-drop-active" ng-class="{\'select2-display-none\': !$select.open || $select.items.length === 0}"><div class="ui-select-choices"></div></div></div>'),e.put("select2/select.tpl.html",'<div class="ui-select-container select2 select2-container" ng-class="{\'select2-container-active select2-dropdown-open open\': $select.open, \'select2-container-disabled\': $select.disabled, \'select2-container-active\': $select.focus, \'select2-allowclear\': $select.allowClear && !$select.isEmpty()}"><div class="ui-select-match"></div><div class="ui-select-dropdown select2-drop select2-with-searchbox select2-drop-active" ng-class="{\'select2-display-none\': !$select.open}"><div class="search-container" ng-class="{\'ui-select-search-hidden\':!$select.searchEnabled, \'select2-search\':$select.searchEnabled}"><input type="search" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" ng-class="{\'select2-active\': $select.refreshing}" role="combobox" aria-expanded="true" aria-owns="ui-select-choices-{{ $select.generatedId }}" aria-label="{{ $select.baseTitle }}" class="ui-select-search select2-input" ng-model="$select.search"></div><div class="ui-select-choices"></div><div class="ui-select-no-choice"></div></div></div>'),e.put("selectize/choices.tpl.html",'<div ng-show="$select.open" class="ui-select-choices ui-select-dropdown selectize-dropdown" ng-class="{\'single\': !$select.multiple, \'multi\': $select.multiple}"><div class="ui-select-choices-content selectize-dropdown-content"><div class="ui-select-choices-group optgroup"><div ng-show="$select.isGrouped" class="ui-select-choices-group-label optgroup-header" ng-bind="$group.name"></div><div role="option" class="ui-select-choices-row" ng-class="{active: $select.isActive(this), disabled: $select.isDisabled(this)}"><div class="option ui-select-choices-row-inner" data-selectable=""></div></div></div></div></div>'),e.put("selectize/match-multiple.tpl.html",'<div class="ui-select-match" data-value="" ng-repeat="$item in $select.selected track by $index" ng-click="$selectMultiple.activeMatchIndex = $index;" ng-class="{\'active\':$selectMultiple.activeMatchIndex === $index}" ui-select-sort="$select.selected"><span class="ui-select-match-item" ng-class="{\'select-locked\':$select.isLocked(this, $index)}"><span uis-transclude-append=""></span> <span class="remove ui-select-match-close" ng-hide="$select.disabled" ng-click="$selectMultiple.removeChoice($index)">&times;</span></span></div>'),e.put("selectize/match.tpl.html",'<div ng-hide="$select.searchEnabled && ($select.open || $select.isEmpty())" class="ui-select-match"><span ng-show="!$select.searchEnabled && ($select.isEmpty() || $select.open)" class="ui-select-placeholder text-muted">{{$select.placeholder}}</span> <span ng-hide="$select.isEmpty() || $select.open" ng-transclude=""></span></div>'),e.put("selectize/no-choice.tpl.html",'<div class="ui-select-no-choice selectize-dropdown" ng-show="$select.items.length == 0"><div class="selectize-dropdown-content"><div data-selectable="" ng-transclude=""></div></div></div>'),e.put("selectize/select-multiple.tpl.html",'<div class="ui-select-container selectize-control multi plugin-remove_button" ng-class="{\'open\': $select.open}"><div class="selectize-input" ng-class="{\'focus\': $select.open, \'disabled\': $select.disabled, \'selectize-focus\' : $select.focus}" ng-click="$select.open && !$select.searchEnabled ? $select.toggle($event) : $select.activate()"><div class="ui-select-match"></div><input type="search" autocomplete="off" tabindex="-1" class="ui-select-search" ng-class="{\'ui-select-search-hidden\':!$select.searchEnabled}" placeholder="{{$selectMultiple.getPlaceholder()}}" ng-model="$select.search" ng-disabled="$select.disabled" aria-expanded="{{$select.open}}" aria-label="{{ $select.baseTitle }}" ondrop="return false;"></div><div class="ui-select-choices"></div><div class="ui-select-no-choice"></div></div>'),e.put("selectize/select.tpl.html",'<div class="ui-select-container selectize-control single" ng-class="{\'open\': $select.open}"><div class="selectize-input" ng-class="{\'focus\': $select.open, \'disabled\': $select.disabled, \'selectize-focus\' : $select.focus}" ng-click="$select.open && !$select.searchEnabled ? $select.toggle($event) : $select.activate()"><div class="ui-select-match"></div><input type="search" autocomplete="off" tabindex="-1" class="ui-select-search ui-select-toggle" ng-class="{\'ui-select-search-hidden\':!$select.searchEnabled}" ng-click="$select.toggle($event)" placeholder="{{$select.placeholder}}" ng-model="$select.search" ng-hide="!$select.isEmpty() && !$select.open" ng-disabled="$select.disabled" aria-label="{{ $select.baseTitle }}"></div><div class="ui-select-choices"></div><div class="ui-select-no-choice"></div></div>')}]);
	//# sourceMappingURL=select.min.js.map


/***/ })

});
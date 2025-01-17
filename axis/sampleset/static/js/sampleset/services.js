    /**
    * Created by mjeffrey on 8/11/14.
    */
var s = angular.module('axis.services', []);

s.factory('QuestionProperties', function(){
    var properties = {
        currentQuestion: null,
        viewingQuestions: []
    };

    var getObject = function(){
        /**
         * Get a reference of needed variables to help with keeping data in sync.
         * @returns {{currentQuestion: number, viewingQuestions: Array}}
         */
        return properties;
    };
    var setCurrentQuestion = function(id){
        /**
         * Set the value of currentQuestion.
         * @param {int} id - question id.
         */
        properties['currentQuestion'] = id;
    };

    var addViewingQuestions = function(id){
        /**
         * Add a questions to being currently viewed.
         * @param {int} id - question id.
         */
        if(typeof id === 'string') id = parseInt(id);
        if(properties['viewingQuestions'].indexOf(id) == -1){
            properties['viewingQuestions'].push(id);
        }
    };
    var removeViewingQuestions = function(id){
        /**
         * Remove a question that is currently being viewed.
         * @param {int} id - question id.
         */
        if(typeof id === 'string') id = parseInt(id);
        properties['viewingQuestions'].splice(properties['viewingQuestions'].indexOf(id), 1);
    };

    var cleanAnswers = function(home){
        /**
         * returns an object of homes answers to be used for calculating display.
         * @param {object} home - home object
         * @returns {object}
         */
        var answers = {};
        for(var question_id in home.source_answers){

            var answer = home.source_answers[question_id],
                type = 'source';

            if(!answer){
                answer = home.failing_answers[question_id];
                type = 'failing';
            }

            if(!answer){
                answer = home.contributed_answers[question_id];
                type = 'contributed';
            }
            answers[question_id] = {
                question_id: question_id,
                answer_id: answer,
                type: type
            };
        }
        return answers;
    };

    return {
        getObject: getObject,
        setCurrentQuestion: setCurrentQuestion,
        addViewingQuestions: addViewingQuestions,
        removeViewingQuestions: removeViewingQuestions,
        cleanAnswers: cleanAnswers
    };
});

s.factory('HomeProperties', function(){
    var properties = {
        homeCache: {},
        removedHomeCache: {}
    };

    var cacheHome = function(obj){
        properties.homeCache[obj.home_status_id] = obj;
    };
    var getCachedHome = function(id){
        return properties.homeCache[id] || properties.removedHomeCache[id];
    };
    var homeRemoved = function(id){
        properties.removedHomeCache[id] = properties.homeCache[id];
        delete properties.homeCache[id];
        window.dispatchEvent(window.custom_event);
        return true;
    };
    var getCachedHomesIds = function(){
        // just passing parseInt to map causes it to return NaN for anything larger than 1.
        return Object.keys(properties.homeCache).map(function(num){
            return parseInt(num, 10);
        });
    };

    return {
        cacheHome: cacheHome,
        homeRemoved: homeRemoved,
        getCachedHome: getCachedHome,
        getCachedHomesIds: getCachedHomesIds
    }
});

s.factory('SampleSetProperties', function($rootScope, $q, $log, SampleSetAPI, HomeAPI, HomeProperties, CustomEvents){
    var properties = {
        isDragging: false,
        viewingSampleSets: [],
        availableTestAnswers: {}
    };

    // helpers
    var _getSampleSetIds = function(){
            /**
         * Get a list of ids for all the Sample Sets on the page.
         * @returns {Array}
         * @private
         */
        var temp = [];
        for(var i = 0; i < properties.viewingSampleSets.length; i++){
            var obj = properties.viewingSampleSets[i];
            if(obj.id) temp.push(String(obj.id));
        }
        return temp;
    };
    var _getSampleSetUUIDs = function(){
            /**
         * Get a list of uuids / names for all the Sample Sets on the page.
         * @returns {Array}
         * @private
         */
        var temp = [];
        for(var i = 0; i < properties.viewingSampleSets.length; i++){
            var obj = properties.viewingSampleSets[i];
            // TODO: this is being changed to uuid
            temp.push(obj.name);
        }
        return temp;
    };
    var _getSampleSetIndex = function(sampleSet){
        /**
         * Get the index for a Sample Set to make changes or check if it exists.
         * @param sampleSet
         * @returns {int} - index of sample set, or -1 if it doesn't exist.
         * @private
         */
        sampleSet = String(sampleSet);
        // This returns null when nothing is found to avoid a zero index being false.
        var i = _getSampleSetIds().indexOf(sampleSet);
        if(i != -1) return i;

        i = _getSampleSetUUIDs().indexOf(sampleSet);
        return i;

    };
    var _getAnsweredQuestionKeys = function(questions){
        /**
         * Get a list of all the questions with answers.
         * @param {object} questions - dictionary of {questionIds: answerIds}
         * @returns {Array}
         * @private
         */
        var temp = [];
        angular.forEach(questions, function(value, key){
            if(value && !(key in temp)){
                temp.push(key);
            }
        });
        return temp;
    };
    var _removeTestHome = function(ssIndex, homeId, sampleSet){
        /**
         * Remove a Test home from a Sample Set.
         * Also handles removing the answers that Test home was contributing.
         * @param {int} ssIndex - Sample Set Index.
         * @param {int} homeId - home status id.
         * @param {string} sampleSet - name of Sample Set home is being removed from.
         * @returns {boolean} - status of removal.
         * @private
         */
        var testHomes = properties.viewingSampleSets[ssIndex].test_homes;
        for(var i = 0; i < testHomes.length; i++){
            var obj = testHomes[i];
            if(obj.home_status_id == homeId){
                testHomes.splice(i, 1);
                return true;
            }
        }
    };
    var _removeSampleHome = function(ssIndex, homeId){
        /**
         * Remove a Sampled home from a Sample Set.
         * @param {int} ssIndex - Sample Set Index.
         * @param {int} homeId - home status id.
         * @returns {boolean} - status of removal.
         * @private
         */
        var sampledHomes = properties.viewingSampleSets[ssIndex].sampled_homes;
        for(var i = 0; i < sampledHomes.length; i++){
            var obj = sampledHomes[i];
            if(obj.home_status_id == homeId){
                sampledHomes.splice(i, 1);
                return true;
            }
        }
    };
    var _getTestHomeFromSampleSetById = function(homeId, sampleSet){
        var ssIndex = _getSampleSetIndex(sampleSet);
        if(ssIndex != -1){
            var testHomes = properties.viewingSampleSets[ssIndex].test_homes;
            for(var i = 0; i < testHomes.length; i++){
                var obj = testHomes[i];
                if(obj.home_status_id == homeId){
                   return obj;
                }
            }
        }
        return null;
    };
    var _getSampledHomeFromSampleSetById = function(homeId, sampleSet){
        var ssIndex = _getSampleSetIndex(sampleSet);
        if(ssIndex != -1){
            var sampledHomes = properties.viewingSampleSets[ssIndex].sampled_homes;
            for(var i = 0; i < sampledHomes.length; i++){
                var obj1 = sampledHomes[i];
                if(obj1.home_status_id == homeId){
                   return obj1;
                }
            }
        }
        return null;
    };
    var _getHomeFromSampleSetById = function(homeId, sampleSet){
        /**
         * Retrieve the home object from a Sampleset.
         * @param {int} homeId - home status id
         * @param {string} sampleSet - sample set uuid.
         * @private
         */
        return (_getTestHomeFromSampleSetById(homeId, sampleSet) ||
                _getSampledHomeFromSampleSetById(homeId, sampleSet) ||
                null);
    };
    var _checkTestHomeExists = function(homeId, sampleSet){
        /**
         * Check if a test home exists in a sample set.
         * @param {int} homeId - home status id
         * @param {string} sampleSet - sample set uuid.
         * @returns {boolean}
         * @private
         */
        return !!_getTestHomeFromSampleSetById(homeId, sampleSet);
    };
    var _checkSampledHomeExists = function(homeId, sampleSet){
        /**
         * Check if a sampled home exists in a sample set.
         * @param {int} homeId - home status id
         * @param {string} sampleSet - sample set uuid.
         * @returns {boolean}
         * @private
         */
        return !!_getSampledHomeFromSampleSetById(homeId, sampleSet);
    };

    // inner workings of sample sets
    var getObject = function(){
        /**
         * Returns a reference of needed variables to help with keeping data in sync.
         * @returns {{isDragging: boolean, viewingSampleSets: Array, availableTestAnswers: {}}}
         */
        return properties;
    };
    var moveHome = function(home, exSampleSet, newSampleSet){
        /**
         * One stop shop for moving a adding a home to SampleSet and removing it from another.
         * @param {int} home - home status id.
         * @param {string} exType - type of home that is getting removed.
         * @param {string} exSampleSet - sample set home being removed from.
         * @param {string} newType - type of home that is being added.
         * @param {string} newSampleSet - sample set home is being added to.
         * @returns {boolean} - both add and remove were successful.
         */
        var added = addHome(home, newSampleSet),
            removed;
        if(added){
            return added.then(function(wasAdded){
                if(wasAdded){
                    removed = removeHome(home, exSampleSet);
                    return wasAdded == removed;
                }
                return false;
            })
        }
    };
    var addHome = function(home, sampleSet){
        /**
         * Add a home to a Sample Set.
         * Adds the source answers to a sample sets whenever a test home passes through this.
         * Triggers the 'used_homes_updated' event for datatable.
         * @param {int} home - home status id.
         * @param {string} type - New type of home. ('test' or 'sample')
         * @param {int} sampleSet - Sample Set id.
         * @returns {promise} - status of home move.
         */
        var sampleSetIndex = _getSampleSetIndex(sampleSet),
            homeAdded = $q.defer(),
            event = sampleSet + CustomEvents.suffixes.HOME_MOVE;

        if(sampleSetIndex != -1){
            var homeObj = HomeAPI.get(home);
            homeObj.then(function(data){
                if(data.is_test_home){
                    if(!_checkTestHomeExists(data.home_status_id, sampleSet)){
                        properties.viewingSampleSets[sampleSetIndex].test_homes.push(data);
                        addSourceAnswers(data, sampleSet);
                        homeAdded.resolve(true);
                    }
                } else {
                    if(!_checkSampledHomeExists(data.home_status_id, sampleSet)){
                        properties.viewingSampleSets[sampleSetIndex].sampled_homes.push(data);
                        homeAdded.resolve(true);
                    }
                }
            }).finally(function(){
                $rootScope.$broadcast(event);
            });
        } else {
            homeAdded.resolve(false);
        }
        window.dispatchEvent(window.custom_event);
        return homeAdded.promise;
    };
    var removeHome = function(home, sampleSet, removeHomeFromCache){
        /**
         * Remove a home from a Sample Set.
         * Removes the source answers from a sample set whenever a test home passes through here.
         * Triggers the 'used_homes_updated' event for datatable.
         * @param {int} home - home status id.
         * @param {int} sampleSet - Sample Set id.
         * @param {boolean} removeHomeFromCache - remove home from the used homes cache?
         * @returns {boolean} - status of home removal.
         */
        var sampleSetIndex = _getSampleSetIndex(sampleSet),
            removed = false,
            event = sampleSet + CustomEvents.suffixes.HOME_MOVE,
            homeObj = _getHomeFromSampleSetById(home, sampleSet);
            removeHomeFromCache = typeof removeHomeFromCache !== 'undefined' ? removeHomeFromCache : false;

        if(sampleSetIndex != -1 && homeObj){
            if(homeObj.is_test_home){
                // make sure the answers get removed before the home is removed.
                removeSourceAnswers(homeObj, sampleSet);
                _removeTestHome(sampleSetIndex, home, sampleSet);
            } else {
                _removeSampleHome(sampleSetIndex, home);
            }
            removed = true;
            if(removeHomeFromCache) HomeProperties.homeRemoved(homeObj.home_status_id);
        }
        $rootScope.$broadcast(event);
        window.dispatchEvent(window.custom_event);
        return removed;
    };
    var addSourceAnswers = function(home, sampleSet){
        /**
         * Add a test homes answered questions that are able to be contributed to a Sample Set.
         * If Sample Set has no contributing answers yet, create a dict for tracking future answers.
         * @param {object} home - Home Object
         * @param {int} sampleSet - Sample Set Name.
         */
        var questions = _getAnsweredQuestionKeys(home.source_answers),
            event = sampleSet + CustomEvents.suffixes.UPDATE_ANSWERS;
        if(!(sampleSet in properties.availableTestAnswers)){
            properties.availableTestAnswers[sampleSet] = {
                homes: [],
                questions: {}
            };
        }
        if(properties.availableTestAnswers[sampleSet].homes.indexOf(String(home.home_status_id)) != -1){
            $log.debug('home', home.home_status_id, 'already being accounted for');
            return;
        }
        var ss = properties.availableTestAnswers[sampleSet].questions;
        for(var i = 0; i < questions.length; i++){
            var obj = questions[i];
            if(!(obj in ss)){
                ss[obj] = 0
            }
            ss[obj] += 1;
        }
        properties.availableTestAnswers[sampleSet].homes.push(String(home.home_status_id));
        $rootScope.$broadcast(event);
    };
    var removeSourceAnswers = function(home, sampleSet){
        /**
         * Remove a test homes answered questions that are able to be contributed to a Sample Set from
         * the tracking dict.
         * @param {object} home - Home object
         * @param {int} sampleSet - Sample Set Name
         */
        var questions = _getAnsweredQuestionKeys(home.source_answers),
            ss = properties.availableTestAnswers[sampleSet].questions,
            event = sampleSet + CustomEvents.suffixes.UPDATE_ANSWERS;
        if(ss){
            for(var i = 0; i < questions.length; i++){
                ss[questions[i]] -= 1;
            }
        }
        var homes = properties.availableTestAnswers[sampleSet].homes;
        homes.splice(homes.indexOf(String(home.id), 1));
        $rootScope.$broadcast(event);
    };

    // whole sample set
    var addSampleSet = function(id){
        /**
         * Get an existing Sample Set form the server and add it to the page.
         * @param {int} id - Sample Set id.
         */
        var ssIndex = _getSampleSetIndex(id);
        var ss = SampleSetAPI.getSummary(id);

        if(ssIndex == -1){
            properties.viewingSampleSets.push(ss);
        }

        ss.then(function(data){
            if(ssIndex == -1){
                properties.viewingSampleSets[properties.viewingSampleSets.indexOf(ss)] = data;
            } else {
                angular.extend(properties.viewingSampleSets[ssIndex], data);
            }

            for(var i = 0; i < data.test_homes.length; i++){
                addSourceAnswers(data.test_homes[i], data.name);
            }

        });
    };
    var removeSampleSet = function(id){
        var index = _getSampleSetIndex(id);
        if(index != -1){
            var ss = properties.viewingSampleSets[index];
            properties.viewingSampleSets.splice(index, 1);
            for(var i=0; i<ss.test_homes.length; i++){
                var home = ss.test_homes[i];
                HomeProperties.homeRemoved(home.home_status_id);
            }
            for(i=0; i<ss.sampled_homes.length; i++){
                home = ss.sampled_homes[i];
                HomeProperties.homeRemoved(home.home_status_id);
            }
        }
    };
    var addBlankSampleSet = function(){
        /**
         * Get the skeleton for a blank Sample Set. Fetch a UUID from the server for naming and saving.
         * @returns {object} - Sample Set Object
         */
        var ss = SampleSetAPI.create();
        properties.viewingSampleSets.push(ss);
        ss.then(function(data){
            properties.viewingSampleSets[properties.viewingSampleSets.indexOf(ss)] = data
        });
        return ss;
    };
    var addBlankSampleSetWithHome = function(home_id, fromSampleSet){
        var ss_name;
        var ss = addBlankSampleSet();
        ss.then(function(ss_data){
            ss_name = ss_data.name;
            return HomeAPI.get(home_id);
        }).then(function(home_data){
            moveHome(home_data.home_status_id, fromSampleSet, ss_name);
        })
    };

    // others
    var changeDrag = function(value){
        properties.isDragging = value;
    };
    var getSampleSetHomeIds = function(){
        var dict = {};
        for(var i = 0; i < properties.viewingSampleSets.length; i++){
            var obj = properties.viewingSampleSets[i];
            for(var j = 0; j < obj.test_homes.length; j++){
                var obj1 = obj.test_homes[j];
                dict[obj1.home_status_id] = obj.name
            }
            for(var j = 0; j < obj.sampled_homes.length; j++){
                var obj2 = obj.sampled_homes[j];
                dict[obj2.home_status_id] = obj.name
            }
        }
        return dict;
    };

    return {
        getObject: getObject,
        changeDrag: changeDrag,
        getSampleSetHomeIds: getSampleSetHomeIds,

        moveHome: moveHome,
        addHome: addHome,
        removeHome: removeHome,
        addSourceAnswers: addSourceAnswers,
        removeSourceAnswers: removeSourceAnswers,

        addSampleSet: addSampleSet,
        removeSampleSet: removeSampleSet,
        addBlankSampleSet: addBlankSampleSet,
        addBlankSampleSetWithHome: addBlankSampleSetWithHome
    }
});

s.factory('APIMixin', function($http, $q){
    var baseUrl = '/api/v2/';
    var _defaultOptions = {
        method: 'GET',
        url: baseUrl,
        cache: true
    };

    var _apiCall = function(options){
        /**
         * Configurable method for making an API request.
         * @param {object} options -> [method, url, cache, data, params]
         * @returns {promise}
         * @private
         */
        var deferred = $q.defer();
        options = angular.extend({}, _defaultOptions, options);

        $http(options).success(function(data){
            deferred.resolve(data);
        }).error(function(data, code){
            deferred.reject(data, code);
        });

        return deferred.promise;
    };
    return {
        call: _apiCall
    }
});

s.factory('SampleSetAPI', function($http, $q, APIMixin, HomeProperties){
    var baseUrl = '/api/v2/sampleset/';
    var _sampleSetBaseObj = {
        'name': '',
        'alt_name': '',
        'test_homes': [],
        'sampled_homes': []
    };

    // helpers
    var _getHomeStatusArguments = function(sampleSet){
        /**
         * Get data to send to server for analyzing and saving Sample Sets.
         * Data structure produced:
         *    { test: [], sampled: [] }
         *
         * @param {object} sampleSet - Sample Set object from Controller.
         * @returns {Array} - Data structure of homes.
         * @private
         */
        var homeStatusIds = {test: [], sampled: []};
        for (var i = 0; i < sampleSet.test_homes.length; i++) {
            var testHome = sampleSet.test_homes[i];
            homeStatusIds.test.push(testHome.home_status_id);
        }
        for (var ii = 0; ii < sampleSet.sampled_homes.length; ii++) {
            var sampleHome = sampleSet.sampled_homes[ii];
            homeStatusIds.sampled.push(sampleHome.home_status_id);
        }
        return homeStatusIds;
    };
    var _getUuid = function(){
        /**
         * Fetch a server generated UUID for applying to new blank Sample Sets
         * @returns {promise}
         * @private
         */
        var url = baseUrl + 'uuid/';
        return APIMixin.call({url: url, cache: false});
    };

    // calls
    var create = function(options){
        /**
         * Create a blank Sample Set.
         *
         * @param {object} options - anything that can be already defined about the Sample Set.
         * @returns {promise} - Sample Set Call.
         */
        var ss = $q.defer();
        var obj = angular.extend({}, angular.copy(_sampleSetBaseObj), options);
        _getUuid().then(function(data){
            obj.name = data['uuid'];
            ss.resolve(obj);
        });
        return ss.promise;
    };
    var get = function(id){
        /**
         * Get an existing Sample Set.
         * @param {int} id - Sample Set id.
         * @returns {promise}
         */
        var url = baseUrl + id + '/';
        return APIMixin.call({url: url, cache: false});
    };
    var getSummary = function(id){
        var call = this.get(id + '/summary');
        call.then(function(data){
            for(var i = 0; i < data.test_homes.length; i++){
                var obj = data.test_homes[i];
                HomeProperties.cacheHome(obj);
            }
            for(var i = 0; i < data.sampled_homes.length; i++){
                var obj1 = data.sampled_homes[i];
                HomeProperties.cacheHome(obj1);
            }
        });
        return  call;
    };
    var analyze = function(sampleSet){
        /**
         * Used to check the current state of a Sample Set
         * @param {object} sampleSet - Sample Set from Controller
         * @returns {promise}
         */
        var options = {
            params: _getHomeStatusArguments(sampleSet),
            method: 'GET',
            url: baseUrl + 'analyze/',
            cache: false
        };
        return APIMixin.call(options);
    };
    var commit = function(sampleSet){
        /**
         * Used to save the current state of a Sample Set to the database.
         * @param {object} sampleSet - Sample Set from Controller
         * @returns {promise}
         */
        var creating = !sampleSet.id;

        var data = creating ? {uuid: sampleSet.name} : {sampleset: sampleSet.id};
        if(sampleSet.alt_name) data['alt_name'] = sampleSet.alt_name;

        angular.extend(data, _getHomeStatusArguments(sampleSet));

        var options = {
            data: data,
            method: creating ? 'POST' : 'PUT',
            url: baseUrl + 'commit/',
            cache: false
        };
        return APIMixin.call(options);
    };
    var advance = function(id){
        var url = baseUrl + id + '/advance/';
        return APIMixin.call({
            url: url,
            method: 'POST',
            cache: false
        });
    };

    return {
        analyze: analyze,
        commit: commit,
        advance: advance,
        create: create,
        get: get,
        getSummary: getSummary
    };
});

s.factory('HomeAPI', function($q, APIMixin, HomeProperties){
    var baseUrl = '/api/v2/homestatus/';
    var urlExtension = '/question_summary/';

    var get = function(homeStatusId){
        /**
         * Get a Home summary. Includes all questions information.
         * Checks a cache first. Returns that as a promise if its found.
         * To overwrite the cache. Request a new SampleSet summary, that will bypass this.
         * NOTE: When testing this. Because it has the possibility of returning a non api call promise
         *      that won't be dealt with by a '$httpBackend.flush()'. 'scope.$apply()' may need to be
         *      called.
         *
         * @param {int} homeStatusId - home status id.
         * @returns {promise}
         */
        if(HomeProperties.getCachedHome(homeStatusId)){
            var deferred = $q.defer();
            deferred.resolve(HomeProperties.getCachedHome(homeStatusId));
            return deferred.promise
        }

        var url = baseUrl + homeStatusId + urlExtension;

        var call = APIMixin.call({url: url});
        call.then(function(obj){
            HomeProperties.cacheHome(obj);
        });
        return  call;
    };

    return {
        get: get
    }
});

s.factory('CollapseHelper', function($timeout){
    function CollapseHelper(prefix){
        this.open = false;
        this.currentClass = '';
        this.previousClass = '';
        this.classPrefix = prefix;

        this.alertClasses = {
            0: '',
            1: this.classPrefix+'-success',
            2: this.classPrefix+'-info',
            3: this.classPrefix+'-warning',
            4: this.classPrefix+'-danger'
        };

        this.openCollapse = function(){
            this.open = true;
        };

        this.show = function(){
            this.openCollapse();
        };

        this.closeCollapse = function(){
            this.open = false;
        };

        this.hide = function(){
            this.closeCollapse();
        };

        this.setClass = function(klass){
            this.previousClass = this.currentClass;
            this.currentClass = klass;
        };

        this.resetClass = function(){
            this.currentClass = this.previousClass;
        };

        this.setClassForDuration = function(klass, duration){
            this.setClass(klass);
            $timeout(this.resetClass.bind(this), duration || 2000)
        };

        this.setClassFromLevel = function(level){
            this.setClass(this.alertClasses[level]);
        };

        this.setClassFromLevelForDuration = function(level, duration){
            this.setClassForDuration(this.alertClasses[level], duration);
        };

        this.error = function(){
            this.setClassFromLevel(4);
        };

        this.success = function(){
            this.setClassFromLevelForDuration(1, 2000);
        };
    }

    return {
        get: function(prefix){
            return new CollapseHelper(prefix);
        }
    }
});

s.factory('LocationService', function($location){
    var properties = {
        sampleSetIds: []
    };

    // helpers
    var _addId = function(id){
        if(properties.sampleSetIds.indexOf(String(id)) == -1){
            properties.sampleSetIds.push(String(id));
        }
    };
    var _removeId = function(id){
        var index = properties.sampleSetIds.indexOf(String(id));
        if(index != -1){
            properties.sampleSetIds.splice(index, 1);
        }
    };
    var _getIdsFromAngularLocation = function(){
        var params = $location.search();
        for(var key in params){
            if(key == 'id'){
                var _ids = params[key];

                if(angular.isArray(_ids)){
                    for(var i = 0; i < _ids.length; i++){
                        var obj = _ids[i];
                        _addId(obj);
                    }
                } else {
                    _addId(params[key]);
                }
            }
        }
    };
    var _getIdsFromPageLocation = function(){
        var params = location.search.substr(1).split('&');
        for(var item in params){
            var temp = params[item].split('=');
            var key = temp[0];
            var value = temp[1];
            if(key == 'id'){
                _addId(value);
            }
        }
    };

    // actions
    var getIdsFromUrl = function(){
        _getIdsFromPageLocation();
        _getIdsFromAngularLocation();
    };
    var addId = function(id){
        _addId(id);
        $location.search('id', properties.sampleSetIds);
    };
    var removeId = function(id){
        _removeId(id);
        $location.search('id', properties.sampleSetIds.length ? properties.sampleSetIds : null);
    };
    var getSampleSetIds = function(){
        return properties.sampleSetIds;
    };

    return {
        getIdsFromUrl: getIdsFromUrl,
        addId: addId,
        removeId: removeId,
        getSampleSetIds: getSampleSetIds
    }
});

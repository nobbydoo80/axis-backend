/**
 * Created by mjeffrey on 11/5/14.
 */

angular.module('axis.services.RegionService')
.factory('RegionService', function($rootScope, $interpolate){
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
    }

    function InvalidRegionValueError(regionName, key, message){
        this.name = 'InvalidRegionValueError';
        this.message = message;
        this.stack = (new Error()).stack;
        this.regionName = regionName;
        this.key = key;
        this.getMessage = function(){
            return $interpolate(this.message)(this);
        };
    }

    function _getRegionValue(region, key){
        /**
         * Will attempt to get a value from the region passed.
         * Throws Errors if the key is undefined.
         * @param region {object} Region Object
         * @param key {string} key of value in region object.
         * @returns {*}
         * @private
         */
        try{
            var value = region.object[key];
        } catch(e){
            throw new InvalidRegionValueError(region.type_name, key, e);
        }

        if(value === null || typeof value === 'undefined'){
            throw new InvalidRegionValueError(region.type_name, key, "'[[ key ]]' is undefined for '[[ regionName ]]'");
        }
        return value;
    }
    function _getSingleRegionValue(regionName, key){
        /**
         * Will attempt to get a value from another region given a type name.
         * Throws Errors if the region does not exist, or the key is undefined.
         * @param regionName {string} Region Key
         * @param key {string} key of value in region dict
         * @returns {*} Throws Error, or returns value
         * @private
         */
        return _getRegionValue(getRegionFromTypeName(regionName), key)
    }

    function _getRegionDependencies(region){
        /**
         * Shortcut for fetching the region dependencies dict.
         * @param region {object}
         * @returns {dict}
         * @private
         */
        return region.region_dependencies || {};
    }
    function _getRegionDependenciesKeys(region){
        /**
         * Returns an array of the regions holding current regions dependencies.
         * @param region {object}
         * @returns {Array}
         * @private
         */
        return Object.keys(_getRegionDependencies(region));
    }
    function _hasDependencies(region){
        /**
         * Does a region have requirements for being submitted?
         * @param region {object}
         * @returns {boolean}
         * @private
         */
        return !!_getRegionDependenciesKeys(region).length;
    }

    function _fetchRegionDependencies(region){
        /**
         * Builds a dict of dependencies for a given region with the values key being the
         * underscore concatenated result of the region_name and value key.
         * @param region {object}
         * @returns {object}
         * @private
         */
        var dependencies = {};

        angular.forEach(_getRegionDependencies(region), function(keys, region_name){
            // keys: array of objects [{field_name: '', serialize_as: ''}]
            // region_name: region list of associated with
            angular.forEach(keys, function(obj){
                if(angular.isDefined(region.parentRegionSet) && angular.isDefined(region.parentRegionSet.parentRegionObject)){
                    dependencies[obj.serialize_as] = _getRegionValue(region.parentRegionSet.parentRegionObject, obj.field_name);
                } else {
                    dependencies[obj.serialize_as] = _getSingleRegionValue(region_name, obj.field_name);
                }
            });


        });

        return dependencies;
    }

    function addRegion(region){
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
    function removeRegion(region){
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
    function getRegion(region){
        var index = regions.indexOf(region);
        return regions[index];
    }
    function getRegionFromTypeName(typeName){
        return regionsMap[typeName];
        // var region;
        // angular.forEach(regions, function(obj){
        //     if(obj.type_name == typeName) region = obj;
        // });
        // return region;
    }
    function getRegionCounter(regionNames){
        var n = 0;
        _.forEach(regionNames, function(typeName){
            var regionData = regionsMap[typeName];
            if (angular.isArray(regionData)) {
                n += regionData.length;
            } else if (regionData !== undefined) {
                n += 1;
            }
        });
        return n;
    }

    function registerChildRegionByTypeName(typeName, childObject){
        return registerChildRegion(getRegionFromTypeName(typeName), childObject);
    }
    function registerChildRegion(parentObject, childObject){
        return parentObject.controller.children.push(childObject);
    }
});

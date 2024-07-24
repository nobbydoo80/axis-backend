angular.module('examineApp')

.run(function($http, Actions, RegionService){
  /* These functions deserve to be exposed more easily from our default examine client api.
   * For now, they exist here as a decent reference for how to do the footwork around actions.
   **/

  /* Issue http request to `url` via `method`, and reloads objects defined by `reloadTypes`. */
  function doRequest(regionObject, method, url, reloadTypes) {
    return $http[method](url).then(function(){
      Actions.callMethod('reload', regionObject);
      reload(reloadTypes);
    });
  }

  /* Reload all regions with a type_name in the sent `typeNames` array. */
  function reload(typeNames) {
    function getRegionsArray(typeName){
      var regionObjects = RegionService.getRegionFromTypeName(typeName);
      if (regionObjects === undefined) {
        return [];
      }
      if (!angular.isArray(regionObjects)) {
        return [regionObjects];
      }
      return regionObjects;
    }
    (typeNames || []).map(function(typeName){
      getRegionsArray(typeName).forEach(function(remoteRegionObject){
        Actions.callMethod('reload', remoteRegionObject);
      });
    })
  }

  /* Replace __FOO__ tokens in `s` with lowercased matches in the namespace object. */
  function sub(s, ns) {
    return s.replace(/__([A-Z][A-Z0-9_]*)__/g, function(match, name){
      var value = ns[name.toLowerCase()];
      if (value === undefined) {
        return match;  // Keep original match text to signal that nothing happened
      }
      return value;
    });
  }

  /* Register `name` from the region's api url helper dictionary, reloading target types
     afterward. */
  function addApiMethod(name, reloadTypes) {
    Actions.addMethod(name, function apiMethod(regionObject){
      var actionUrl = sub(regionObject.helpers.api_urls[name], regionObject.object);
      return doRequest(regionObject, 'post', actionUrl, reloadTypes);
    });
  }

  /* Register `name` with the 'transition' api url helper and the name in the query params. */
  function addTransitionMethod(name, reloadTypes) {
    Actions.addMethod(name, function transition(regionObject){
      var transitionUrl = sub(regionObject.helpers.api_urls.transition, regionObject.object);
      transitionUrl += '?name=' + name;
      return doRequest(regionObject, 'post', transitionUrl, reloadTypes);
    });
  }

  function addForceSetStateMethod(name, reloadTypes) {
    Actions.addMethod(name, function transition(regionObject){
      var transitionUrl = sub(regionObject.helpers.api_urls.force_state, regionObject.object);
      transitionUrl += '?name=' + name;
      return doRequest(regionObject, 'post', transitionUrl, reloadTypes);
    });
  }

  Actions.addPostMethodToType('save', ['hirl_verifier_agreement_documents'], function(regionObject){
    reload(['hirl_verifier_agreement', 'hirl_verifier_enrollment']);
    return regionObject;
  });

  /* Owner actions */
  addTransitionMethod('approve');
  addTransitionMethod('submit_insurance');
  addTransitionMethod('verify');
  addTransitionMethod('countersign');
  addTransitionMethod('expire');

  addForceSetStateMethod('approved');
  addForceSetStateMethod('verified');
  addForceSetStateMethod('countersigned');
  addForceSetStateMethod('expired');

  addApiMethod('ensure_blank_document', ['hirl_verifier_agreement', 'hirl_verifier_enrollment']);
  addApiMethod('update_docusign_status', ['hirl_verifier_agreement', 'hirl_verifier_enrollment']);
  addApiMethod('resend_email', []);

}).controller('VerifierAgreementEnrollmentFormController', function($scope, $http, $timeout, $window, $location){
    $scope.differentShippingAddress = function () {
        return Boolean(
            $scope.regionObject.object.shipping_geocode_street_line1 ||
            $scope.regionObject.object.shipping_geocode_street_line2 ||
            $scope.regionObject.object.shipping_geocode_city ||
            $scope.regionObject.object.shipping_geocode_zipcode
        );
    }();

    $scope.mailingCity = $scope.regionObject.object['mailing_geocode_city_display'];
    // $scope.regionObject.object['mailing_geocode_city'] = {text: $scope.regionObject.object['mailing_geocode_city_display'], value: $scope.regionObject.object['mailing_geocode_city']};
    // $scope.regionObject.object['shipping_geocode_city'] = {text: $scope.regionObject.object['shipping_geocode_city_display'], value: $scope.regionObject.object['shipping_geocode_city']};

    $scope.differentAdministrativeContact = function () {
        return Boolean(
            $scope.regionObject.object.administrative_contact_first_name ||
            $scope.regionObject.object.administrative_contact_last_name ||
            $scope.regionObject.object.administrative_contact_phone_number ||
            $scope.regionObject.object.administrative_contact_email
        );
    }();

    $scope.multipleVerifiers = function () {
        return Boolean(
            $scope.regionObject.object.company_officer_first_name ||
            $scope.regionObject.object.company_officer_last_name ||
            $scope.regionObject.object.company_officer_phone_number ||
            $scope.regionObject.object.company_officer_email
        );
    }();

    $scope.useDifferentShippingAddress = function () {
        $scope.differentShippingAddress = !$scope.differentShippingAddress;

        $scope.regionObject.object.shipping_geocode_street_line1 = '';
        $scope.regionObject.object.shipping_geocode_street_line2 = '';
        $scope.regionObject.object.shipping_geocode_city = '';
        $scope.regionObject.object.shipping_geocode_zipcode = '';
    }

    $scope.useDifferentAdministrativeContact = function () {
        $scope.differentAdministrativeContact = !$scope.differentAdministrativeContact;

        $scope.regionObject.object.administrative_contact_first_name = '';
        $scope.regionObject.object.administrative_contact_last_name = '';
        $scope.regionObject.object.administrative_contact_phone_number = '';
        $scope.regionObject.object.administrative_contact_email = '';
    }

    $scope.mailingCityChanged = function ($item) {
        $scope.mailingCity = $item.text;
    }

    $scope.clearMultipleVerifiersData = function () {
        $scope.regionObject.object.company_officer_first_name = '';
        $scope.regionObject.object.company_officer_last_name = '';
        $scope.regionObject.object.company_officer_phone_number = '';
        $scope.regionObject.object.company_officer_email = '';
        $scope.regionObject.object.company_officer_title = '';
    }

    /**
     * Convert our null object fields to empty string to display correct errors from serializer
     */
    $scope.covertRegionObjectNullToString = function () {
        let fields = [
            'mailing_geocode_street_line1',
            'mailing_geocode_street_line2',
            'mailing_geocode_zipcode',
            'shipping_geocode_street_line1',
            'shipping_geocode_street_line2',
            'shipping_geocode_zipcode'
        ];
        for (let i=0; i<fields.length; i++) {
            if ($scope.regionObject.object.hasOwnProperty(fields[i]) &&
                $scope.regionObject.object[fields[i]] === null) {
                $scope.regionObject.object[fields[i]] = '';
            }
        }
    }

    $scope.covertRegionObjectNullToString();
});

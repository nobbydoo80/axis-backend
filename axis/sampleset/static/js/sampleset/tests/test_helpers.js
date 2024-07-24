/**
 * This file holds things that need to happen in almost all jasmine tests.
 * Created by mjeffrey on 8/27/14.
 */
// PhantomJS doesn't support bind yet.
Function.prototype.bind = Function.prototype.bind || function(thisp){
    var fn = this;
    return function(){
        return fn.apply(thisp, arguments);
    }
};

beforeEach(function(){
    // need to provide this before trying to load the app module
    var ExamineSettingsMock = {static_url: '/static/'};
    module(function($provide){
        $provide.constant('ExamineSettings', ExamineSettingsMock);
    });

    window.custom_event = document.createEvent('Event');
    custom_event.initEvent('used_homes_updated', true, true);

    // load the service's module
    module('app');
    module('templates');
});

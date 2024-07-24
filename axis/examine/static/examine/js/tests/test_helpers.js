/**
 * This file holds things that need to happen in almost all jasmine tests.
 * Created by mjeffrey on 10/20/14.
 */
// PhantomJS doesn't support bind yet.
Function.prototype.bind = Function.prototype.bind || function (thisp) {
  var fn = this;
  return function () {
    return fn.apply(thisp, arguments);
  }
};
var ExamineSettingsObj = {static_url: '/static/'};
var __ExamineSettings = ExamineSettingsObj;

function updateExamineSettings(key, obj) {
  ExamineSettingsObj[key] = obj;
}

beforeEach(function () {
  // need to provide this before trying to load the app module
  module(function ($provide) {
    $provide.constant('ExamineSettings', ExamineSettingsObj);
  });

  // load the service's module
  //module('examineApp', 'fixtureData', 'templates');
});

angular.module('fixtureData', [])
  .value('RegionObjects', [])
  .value('RegionEndpointsFixture', {
    one: {
      "relationships": {
        "new_region_url": null,
        "endpoints": ["/api/v2/subdivision/relationships/133/region/"],
        "verbose_name": "Subdivision",
        "regionset_template_url": "/examine/angular_regionset_default.html",
        "visible_fields": ["rater", "provider", "eep", "hvac", "utility", "qa", "general"]
      },
      "base_floorplan": {
        "new_region_url": "/api/v2/base_floorplan/new_region/",
        "endpoints": ["/api/v2/base_floorplan/3408/region/", "/api/v2/base_floorplan/3411/region/", "/api/v2/base_floorplan/318/region/", "/api/v2/base_floorplan/3407/region/", "/api/v2/base_floorplan/3406/region/"],
        "verbose_name": "floorplan name",
        "regionset_template_url": "/examine/angular_regionset_table.html",
        "visible_fields": ["plan_name", "plan_number", "plan_square_footage"]
      },
      "subdivision": {
        "new_region_url": null,
        "endpoints": ["/api/v2/subdivision/133/region/"],
        "verbose_name": "Subdivision",
        "regionset_template_url": null,
        "visible_fields": ["name", "builder_org", "community", "city", "cross_roads", "builder_name", "use_sampling", "use_metro_sampling"]
      },
      "subdivision_documents": {
        "new_region_url": "/api/v2/subdivision/documents/new_region/",
        "endpoints": ["/api/v2/subdivision/documents/46/region/"],
        "verbose_name": "subdivision document",
        "regionset_template_url": "/examine/angular_regionset_table.html",
        "visible_fields": ["document", "description", "is_public"]
      },
      "history": {
        "new_region_url": null,
        "endpoints": ["/api/v2/subdivision/history/133/region/"],
        "verbose_name": "Subdivision",
        "regionset_template_url": "/examine/angular_regionset_datatable.html",
        "visible_fields": ["Date", "User", "Object", "Type", "Fields", "Previous Values", "Current Values"]
      }
    }
  })
  .value('RegionSetFixture', {
    new_subdivision_document: {
      "region_dependencies": {"subdivision": [{"serialize_as": "subdivision", "field_name": "id"}]},
      "delete_endpoint": null,
      "field_order": ["document", "description", "is_public", "subdivision", "document_raw_name", "document_raw"],
      "object": {
        "id": null,
        "company": null,
        "subdivision": null,
        "admin_only": false,
        "name": null,
        "description": null,
        "document": "",
        "is_active": true,
        "is_public": true
      },
      "detail_template_url": "/examine/subdivision/subdivision_document_detail.html",
      "default_instruction": "edit",
      "fields": {
        "subdivision": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "HiddenInput",
            "input_type": "hidden",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": true,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "subdivision",
          "value_label": "",
          "value": null,
          "label": "Subdivision",
          "help_text": "",
          "field_name": "subdivision",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "description": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "TextInput",
            "input_type": "text",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "choices": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "description",
          "value_label": "",
          "value": null,
          "label": "Description",
          "help_text": "",
          "field_name": "description",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": 255,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "document_raw_name": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "HiddenInput",
            "input_type": "hidden",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": true,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "document_raw_name",
          "value_label": "",
          "value": null,
          "label": "Document raw name",
          "help_text": "",
          "field_name": "document_raw_name",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "document_raw": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "HiddenInput",
            "input_type": "hidden",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": true,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "document_raw",
          "value_label": "",
          "value": null,
          "label": "Document raw",
          "help_text": "",
          "field_name": "document_raw",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "is_public": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "CheckboxInput",
            "input_type": "checkbox",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "choices": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "is_public",
          "value_label": "",
          "value": true,
          "label": "Is public",
          "help_text": "",
          "field_name": "is_public",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "document": {
          "widget": {
            "clear_checkbox_label": "<django.utils.functional.__proxy__ object at 0x1037eb510>",
            "needs_multipart_form": true,
            "format": null,
            "_widget": "ClearableFileInput",
            "input_type": "file",
            "initial_text": "<django.utils.functional.__proxy__ object at 0x1037eb410>",
            "template_with_initial": "%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s",
            "field_id": null,
            "choices": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": "%(clear)s <label for=\"%(clear_checkbox_id)s\">%(clear_checkbox_label)s</label>",
            "is_hidden": false,
            "input_text": "<django.utils.functional.__proxy__ object at 0x1037eb490>",
            "options": null
          },
          "prefixed_name": "document",
          "value_label": "",
          "value": null,
          "label": "Document",
          "help_text": "",
          "field_name": "document",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": false,
            "required": true,
            "max_results": null,
            "max_length": 512,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        }
      },
      "type_name": "subdivision_documents",
      "object_endpoint": "/api/v2/subdivision/documents/",
      "actions": {
        "default": {
          "style": null,
          "name": "default",
          "actions": [{
            "attrs": {},
            "is_mode": false,
            "style": "default",
            "name": "",
            "items": null,
            "instruction": "delete",
            "type": "button",
            "size": "xs",
            "icon": "trash-o"
          }, {
            "attrs": {},
            "is_mode": true,
            "style": "primary",
            "name": "Edit",
            "items": null,
            "instruction": "edit",
            "type": "button",
            "size": "xs",
            "icon": null
          }]
        },
        "edit": {
          "style": null,
          "name": "edit",
          "actions": [{
            "attrs": {},
            "is_mode": false,
            "style": "default",
            "name": "",
            "items": null,
            "instruction": "destroy",
            "type": "button",
            "size": "xs",
            "icon": "times"
          }, {
            "attrs": {},
            "is_mode": false,
            "style": "primary",
            "name": "",
            "items": null,
            "instruction": "save",
            "type": "button",
            "size": "xs",
            "icon": "check"
          }]
        },
        "static": {"style": null, "name": "static", "actions": []}
      },
      "commit_instruction": "save",
      "region_template_url": "/examine/angular_region_tablerow.html",
      "object_name": "New subdivision document",
      "visible_fields": ["document", "description", "is_public"],
      "verbose_names": {
        "subdivision": "subdivision",
        "description": "description",
        "document_raw_name": "Document raw name",
        "admin_only": "admin only",
        "is_active": "is active",
        "id": "ID",
        "document_raw": "Document raw",
        "is_public": "is public",
        "document": "document",
        "company": "company",
        "name": "name"
      },
      "absolute_url": null,
      "form_template_url": "/examine/subdivision/subdivision_document_form.html",
      "helpers": {"verbose_name": "subdivision document"},
      "relatedobjects_endpoint": "/api/v2/subdivisiondocument/related/None/",
      "id": "subdivision_documents__1413909032"
    }
  })
  .value('SingleRegionFixture', {
    one: {
      "region_dependencies": {},
      "delete_endpoint": "/api/v2/subdivision/133/",
      "field_order": ["name", "builder_org", "community", "city", "cross_roads", "builder_name", "geocode_response", "use_sampling", "use_metro_sampling"],
      "object": {
        "id": 133,
        "address_override": false,
        "builder_org": 32,
        "builder_name": "Sweet Subdivision",
        "confirmed_address": false,
        "created_date": "2012-07-25T14:18:00Z",
        "cross_roads": "Broadway and McClintock",
        "is_active": true,
        "latitude": null,
        "longitude": null,
        "modified_date": "2014-10-09T18:50:20Z",
        "name": "Subdivision One three Three",
        "slug": "brooksidelakeside-at-prescott-lakes",
        "state": "AR",
        "use_metro_sampling": false,
        "use_sampling": true,
        "city": 11829,
        "city_name": "Prescott AR",
        "county": 161,
        "county_name": "Nevada",
        "metro": null,
        "metro_name": null,
        "builder_org_name": "Dorn Homes"
      },
      "detail_template_url": "/examine/subdivision/subdivision_detail.html",
      "default_instruction": null,
      "fields": {
        "city": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "AutoHeavySelect2Widget",
            "input_type": "hidden",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": "d23df40411cb3b01578f82609555d3cf1ca3d638",
            "choices": [],
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": {
              "allowClear": true,
              "initSelection": "django_select2.onInit",
              "multiple": false,
              "escapeMarkup": "function(m){ return m; }",
              "minimumInputLength": 1,
              "minimumResultsForSearch": 6,
              "closeOnSelect": "true",
              "ajax": {
                "dataType": "json",
                "quietMillis": 100,
                "data": "django_select2.get_url_params",
                "results": "django_select2.process_results"
              },
              "placeholder": "Type to search"
            }
          },
          "prefixed_name": "city",
          "value_label": "Prescott, AR (Nevada)",
          "value": 11829,
          "label": "City/State/County",
          "help_text": "Type the first few letters of the name of the city of the location and select the correct city/state/county combination from the list presented. If the correct city is not available, click \"Add New\" to add a city to the database.",
          "field_name": "city",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": 1000,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "cross_roads": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "TextInput",
            "input_type": "text",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "choices": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "cross_roads",
          "value_label": null,
          "value": "Broadway and McClintock",
          "label": "Crossroads",
          "help_text": "Enter the crossroads or street intersection of this subdivision or leave blank if unknown.",
          "field_name": "cross_roads",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": 128,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "name": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "TextInput",
            "input_type": "text",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "choices": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "name",
          "value_label": null,
          "value": "Subdivision One three Three",
          "label": "Subdivision Name",
          "help_text": "A subdivision is a parcel of land in which one builder intends to build several homes.  To add a subdivision association or create a new subdivision, type the first few letters of the name of the subdivision that you wish to associate with.  If the subdivision you wish to associate with already exists within the database, select it from the \"Select from existing\" list and click on \"Submit\" at the bottom of this page to create the association.  If the subdivision does not exist within the database, type the name of the subdivision, select it in the \"Create new\" list, and populate the fields below.",
          "field_name": "name",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": true,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "use_metro_sampling": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "CheckboxInput",
            "input_type": "checkbox",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "choices": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "use_metro_sampling",
          "value_label": null,
          "value": false,
          "label": "Use metro sampling",
          "help_text": "",
          "field_name": "use_metro_sampling",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "community": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "Select2Widget",
            "input_type": "select",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "choices": [["", "--------"], [27, "Anthem"], [24, "Anthem Merrill Ranch"], [18, "Arroyo Mountain Estates"], [17, "Blackstone at Vistancia"], [7, "Blue Horizons"], [15, "Buckeye"], [64, "Camino A Lago"], [20, "Canyon Trails"], [152, "Coldwater Ranch"], [8, "Cortessa"], [67, "Crossriver"], [21, "DC Ranch"], [136, "Desert Oasis"], [23, "Desert Ridge"], [5, "Estrella"], [12, "Estrella Mountain Ranch"], [69, "Festival Foothills"], [3, "Glenmont Estates"], [61, "Greer Ranch"], [38, "Grey Fox Ridge"], [33, "Happy Valley"], [142, "Hunter Field Estates"], [10, "Litchfield Park"], [31, "Lone Mountain"], [34, "Marley Park"], [39, "Melton Ranch"], [16, "Mirabel Village"], [13, "Montecito in Estrella"], [148, "MPC Test"], [35, "Norterra"], [25, "Northgate"], [6, "Palm Valley"], [2, "PebbleCreek"], [50, "Portales"], [141, "Rancho Cabrillo"], [29, "Red Rock Village"], [30, "Rock Springs"], [172, "Sarah Ann Ranch"], [19, "Savannah"], [68, "Sedella"], [159, "Sonoran Commons"], [14, "Sonoran Mountain Ranch"], [9, "Stetson Valley"], [22, "Sun City Festival"], [149, "Sundance"], [32, "Sunset Ranch"], [4, "Surprise Farms"], [63, "Talking Rock"], [169, "The Meadows"], [174, "The Village at Litchfield Park II"], [138, "Tierra Del Rio"], [41, "Tramonto"], [40, "Travata"], [1, "Verrado"], [28, "Vista De Montana"], [11, "Vistancia"], [26, "White Tank Foothills"]],
            "allow_multiple_selected": false,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": {
              "minimumResultsForSearch": 6,
              "allowClear": true,
              "closeOnSelect": false,
              "placeholder": ""
            }
          },
          "prefixed_name": "community",
          "value_label": "",
          "value": null,
          "label": "Community Name",
          "help_text": "Select the community from the list presented.  If the correct community is not available, click \"Add New\" to add a new community or community association.",
          "field_name": "community",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "builder_name": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "TextInput",
            "input_type": "text",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "choices": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "builder_name",
          "value_label": null,
          "value": "Sweet Subdivision",
          "label": "Alternate Name or Code",
          "help_text": "Enter an alternate name or identifier for the subdivision if applicable.",
          "field_name": "builder_name",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": 255,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "geocode_response": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "HiddenInput",
            "input_type": "hidden",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": true,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "geocode_response",
          "value_label": "",
          "value": null,
          "label": "Geocode response",
          "help_text": "The response this place was constructed from.",
          "field_name": "geocode_response",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "builder_org": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "Select2Widget",
            "input_type": "select",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "choices": [[2006, "Abbott-Rhoton Investments DBA Capstone Homes"], [20, "Ashton Woods Homes"], [21, "Beazer Homes"], [1332, "Bellago Development LLC DBA Bellago Homes"], [26, "C&B Construction"], [22, "Cachet Homes"], [97, "Calvis Wyant"], [24, "Centex Homes"], [27, "Columbia Communities"], [29, "Copper State Custom"], [82, "Courtland Communities"], [1006, "D.E.F. Construction, Inc. DBA Frank Residential"], [31, "David Weekley Homes"], [32, "Dorn Homes"], [34, "DR Horton"], [37, "Elliott Construction"], [40, "Ericksen Homes"], [993, "Gehan Homes Construction Company, LLC"], [43, "Habitat for Humanity - Flagstaff"], [44, "Habitat for Humanity - Prescott"], [42, "Habitat for Humanity Central Arizona"], [81, "Habitat for Humanity Desert Foothills"], [45, "Homes By Towne"], [98, "Hope Construction LLC"], [102, "Housing America Corporation"], [47, "Hunter Custom Homes"], [48, "Jacobson Companies"], [49, "JCH Construction, LLC"], [101, "JJGB Construction, LLC"], [994, "John Nanke Signature Group LLC dba Mom's Custom Homes"], [3, "K. Hovnanian Homes"], [1465, "KB Home Phoenix, Inc."], [51, "Keystone at Ironwood LLC"], [84, "Keystone at Rancho Madera, LLC"], [1390, "Keystone Homes"], [2028, "Lawler Construction, Inc."], [52, "Lennar"], [53, "Liberty Companies, LLC"], [54, "Loven Contracting"], [1184, "LSH Construction LLC DBA Lifestyle Homes LLC"], [991, "Mandalay Homes Prescott"], [55, "Maracay Homes"], [998, "Mark Hancock Development dba Camelot Homes"], [56, "Mattamy Homes"], [57, "MC Homes"], [58, "Meritage Active Adult"], [1, "Meritage Homes of Arizona, Inc."], [60, "Monarch Privada"], [63, "Perricone Development Group"], [1500, "Porchlight Homes"], [41, "Prescott Green Builders"], [64, "Pulte Homes"], [65, "RES Contracting, Inc."], [2, "Richmond American"], [67, "Robson Communities"], [68, "Rosewood Homes Construction, LLC"], [1338, "Ryland Homes of Arizona Inc."], [6, "Shea Homes"], [69, "Shea Homes for Active Adults"], [71, "Standard Pacific Homes"], [70, "Sun Pine Homes"], [72, "Suncor Homes"], [5, "Taylor Morrison"], [1011, "TDLC Development Inc."], [85, "Toll Brothers"], [76, "Trend Homes"], [77, "TW Lewis by David Weekley Homes"], [2014, "Verde Valley Habitat for Humanity"], [103, "VIP Construction, Inc."], [1573, "VisionCraft Homes"], [78, "William Lyon Homes"], [80, "William Ryan Homes"], [79, "Woodside Homes of Arizona"]],
            "allow_multiple_selected": false,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": {
              "minimumResultsForSearch": 6,
              "allowClear": true,
              "closeOnSelect": false,
              "placeholder": ""
            }
          },
          "prefixed_name": "builder_org",
          "value_label": "Dorn Homes",
          "value": 32,
          "label": "Builder",
          "help_text": "Type the first few letters of the name of the Builder that is building all homes in this subdivision, and select the correct company from the list presented.  If the correct company is not available, click \"Add New\" to add a new Builder or Builder association.",
          "field_name": "builder_org",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": true,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        },
        "use_sampling": {
          "widget": {
            "clear_checkbox_label": null,
            "needs_multipart_form": false,
            "format": null,
            "_widget": "CheckboxInput",
            "input_type": "checkbox",
            "initial_text": null,
            "template_with_initial": null,
            "field_id": null,
            "choices": null,
            "allow_multiple_selected": null,
            "is_localized": false,
            "template_with_clear": null,
            "is_hidden": false,
            "input_text": null,
            "options": null
          },
          "prefixed_name": "use_sampling",
          "value_label": null,
          "value": true,
          "label": "Use sampling",
          "help_text": "",
          "field_name": "use_sampling",
          "options": {
            "min_length": null,
            "min_value": null,
            "max_value": null,
            "allow_empty_file": null,
            "required": false,
            "max_results": null,
            "max_length": null,
            "max_digits": null,
            "max_whole_digits": null,
            "empty_value": null,
            "max_decimal_places": null
          }
        }
      },
      "type_name": "subdivision",
      "object_endpoint": "/api/v2/subdivision/133/",
      "actions": {
        "default": {
          "style": null,
          "name": "default",
          "actions": [{
            "attrs": {},
            "is_mode": true,
            "style": "primary",
            "name": "Edit",
            "items": null,
            "instruction": "edit",
            "type": "button",
            "size": "md",
            "icon": null
          }]
        },
        "edit": {
          "style": "well well-sm wide",
          "name": "edit",
          "actions": [{
            "attrs": {},
            "is_mode": false,
            "style": "primary",
            "name": "Save",
            "items": null,
            "instruction": "geocode",
            "type": "button",
            "size": "md",
            "icon": null
          }, {
            "attrs": {},
            "is_mode": false,
            "style": "default",
            "name": "Cancel",
            "items": null,
            "instruction": "exit",
            "type": "button",
            "size": "md",
            "icon": null
          }]
        },
        "static": {"style": null, "name": "static", "actions": []}
      },
      "commit_instruction": "geocode",
      "region_template_url": "/examine/angular_region_bottomactions.html",
      "object_name": "Subdivision One three Three (Sweet Subdivision)",
      "visible_fields": ["name", "builder_org", "community", "city", "cross_roads", "builder_name", "use_sampling", "use_metro_sampling"],
      "verbose_names": {
        "use_metro_sampling": "use metro sampling",
        "community": "Community Name",
        "county": "county",
        "builder_name": "Alternate Name or Code",
        "geocode_response": "geocode response",
        "id": "ID",
        "city": "City/State/County",
        "cross_roads": "Crossroads",
        "confirmed_address": "confirmed address",
        "address_override": "address override",
        "state": "state",
        "latitude": "latitude",
        "builder_org": "Builder",
        "climate_zone": "climate zone",
        "use_sampling": "use sampling",
        "modified_date": "modified date",
        "is_active": "is active",
        "slug": "slug",
        "name": "Subdivision Name",
        "metro": "metro",
        "longitude": "longitude",
        "place": "place",
        "created_date": "created date"
      },
      "absolute_url": "/subdivision/133/",
      "form_template_url": "/examine/subdivision/subdivision_form.html",
      "helpers": {"verbose_name": "Subdivision"},
      "relatedobjects_endpoint": "/api/v2/subdivision/related/133/",
      "id": "subdivision_133"
    }
  })
  .value('FieldFixture', {
    AutoHeavySelect2Widget: {
      "widget": {
        "clear_checkbox_label": null,
        "needs_multipart_form": false,
        "format": null,
        "_widget": "AutoHeavySelect2Widget",
        "input_type": "hidden",
        "initial_text": null,
        "template_with_initial": null,
        "field_id": "d23df40411cb3b01578f82609555d3cf1ca3d638",
        "choices": [],
        "allow_multiple_selected": null,
        "is_localized": false,
        "template_with_clear": null,
        "is_hidden": false,
        "input_text": null,
        "options": {
          "allowClear": true,
          "initSelection": "django_select2.onInit",
          "multiple": false,
          "escapeMarkup": "function(m){ return m; }",
          "minimumInputLength": 1,
          "minimumResultsForSearch": 6,
          "closeOnSelect": "true",
          "ajax": {
            "dataType": "json",
            "quietMillis": 100,
            "data": "django_select2.get_url_params",
            "results": "django_select2.process_results"
          },
          "placeholder": "Type to search"
        }
      },
      "prefixed_name": "city",
      "value_label": "Prescott, AR (Nevada)",
      "value": 11829,
      "label": "City/State/County",
      "help_text": "Type the first few letters of the name of the city of the location and select the correct city/state/county combination from the list presented. If the correct city is not available, click \"Add New\" to add a city to the database.",
      "field_name": "city",
      "options": {
        "min_length": null,
        "min_value": null,
        "max_value": null,
        "allow_empty_file": null,
        "required": false,
        "max_results": 1000,
        "max_length": null,
        "max_digits": null,
        "max_whole_digits": null,
        "empty_value": null,
        "max_decimal_places": null
      }
    },
    TextInput: {
      "widget": {
        "clear_checkbox_label": null,
        "needs_multipart_form": false,
        "format": null,
        "_widget": "TextInput",
        "input_type": "text",
        "initial_text": null,
        "template_with_initial": null,
        "field_id": null,
        "choices": null,
        "allow_multiple_selected": null,
        "is_localized": false,
        "template_with_clear": null,
        "is_hidden": false,
        "input_text": null,
        "options": null
      },
      "prefixed_name": "name",
      "value_label": null,
      "value": "Subdivision One three Three",
      "label": "Subdivision Name",
      "help_text": "A subdivision is a parcel of land in which one builder intends to build several homes.  To add a subdivision association or create a new subdivision, type the first few letters of the name of the subdivision that you wish to associate with.  If the subdivision you wish to associate with already exists within the database, select it from the \"Select from existing\" list and click on \"Submit\" at the bottom of this page to create the association.  If the subdivision does not exist within the database, type the name of the subdivision, select it in the \"Create new\" list, and populate the fields below.",
      "field_name": "name",
      "options": {
        "min_length": null,
        "min_value": null,
        "max_value": null,
        "allow_empty_file": null,
        "required": true,
        "max_results": null,
        "max_length": null,
        "max_digits": null,
        "max_whole_digits": null,
        "empty_value": null,
        "max_decimal_places": null
      }
    },
    CheckBoxInput: {
      "widget": {
        "clear_checkbox_label": null,
        "needs_multipart_form": false,
        "format": null,
        "_widget": "CheckboxInput",
        "input_type": "checkbox",
        "initial_text": null,
        "template_with_initial": null,
        "field_id": null,
        "choices": null,
        "allow_multiple_selected": null,
        "is_localized": false,
        "template_with_clear": null,
        "is_hidden": false,
        "input_text": null,
        "options": null
      },
      "prefixed_name": "use_sampling",
      "value_label": null,
      "value": true,
      "label": "Use sampling",
      "help_text": "",
      "field_name": "use_sampling",
      "options": {
        "min_length": null,
        "min_value": null,
        "max_value": null,
        "allow_empty_file": null,
        "required": false,
        "max_results": null,
        "max_length": null,
        "max_digits": null,
        "max_whole_digits": null,
        "empty_value": null,
        "max_decimal_places": null
      }
    },
    Select2Widget: {
      "widget": {
        "clear_checkbox_label": null,
        "needs_multipart_form": false,
        "format": null,
        "_widget": "Select2Widget",
        "input_type": "select",
        "initial_text": null,
        "template_with_initial": null,
        "field_id": null,
        "choices": [["", "--------"], [27, "Anthem"], [24, "Anthem Merrill Ranch"], [18, "Arroyo Mountain Estates"], [17, "Blackstone at Vistancia"], [7, "Blue Horizons"], [15, "Buckeye"], [64, "Camino A Lago"], [20, "Canyon Trails"], [152, "Coldwater Ranch"], [8, "Cortessa"], [67, "Crossriver"], [21, "DC Ranch"], [136, "Desert Oasis"], [23, "Desert Ridge"], [5, "Estrella"], [12, "Estrella Mountain Ranch"], [69, "Festival Foothills"], [3, "Glenmont Estates"], [61, "Greer Ranch"], [38, "Grey Fox Ridge"], [33, "Happy Valley"], [142, "Hunter Field Estates"], [10, "Litchfield Park"], [31, "Lone Mountain"], [34, "Marley Park"], [39, "Melton Ranch"], [16, "Mirabel Village"], [13, "Montecito in Estrella"], [148, "MPC Test"], [35, "Norterra"], [25, "Northgate"], [6, "Palm Valley"], [2, "PebbleCreek"], [50, "Portales"], [141, "Rancho Cabrillo"], [29, "Red Rock Village"], [30, "Rock Springs"], [172, "Sarah Ann Ranch"], [19, "Savannah"], [68, "Sedella"], [159, "Sonoran Commons"], [14, "Sonoran Mountain Ranch"], [9, "Stetson Valley"], [22, "Sun City Festival"], [149, "Sundance"], [32, "Sunset Ranch"], [4, "Surprise Farms"], [63, "Talking Rock"], [169, "The Meadows"], [174, "The Village at Litchfield Park II"], [138, "Tierra Del Rio"], [41, "Tramonto"], [40, "Travata"], [1, "Verrado"], [28, "Vista De Montana"], [11, "Vistancia"], [26, "White Tank Foothills"]],
        "allow_multiple_selected": false,
        "is_localized": false,
        "template_with_clear": null,
        "is_hidden": false,
        "input_text": null,
        "options": {
          "minimumResultsForSearch": 6,
          "allowClear": true,
          "closeOnSelect": false,
          "placeholder": ""
        }
      },
      "prefixed_name": "community",
      "value_label": "",
      "value": null,
      "label": "Community Name",
      "help_text": "Select the community from the list presented.  If the correct community is not available, click \"Add New\" to add a new community or community association.",
      "field_name": "community",
      "options": {
        "min_length": null,
        "min_value": null,
        "max_value": null,
        "allow_empty_file": null,
        "required": false,
        "max_results": null,
        "max_length": null,
        "max_digits": null,
        "max_whole_digits": null,
        "empty_value": null,
        "max_decimal_places": null
      }
    },
    HiddenInput: {
      "widget": {
        "clear_checkbox_label": null,
        "needs_multipart_form": false,
        "format": null,
        "_widget": "HiddenInput",
        "input_type": "hidden",
        "initial_text": null,
        "template_with_initial": null,
        "field_id": null,
        "allow_multiple_selected": null,
        "is_localized": false,
        "template_with_clear": null,
        "is_hidden": true,
        "input_text": null,
        "options": null
      },
      "prefixed_name": "geocode_response",
      "value_label": "",
      "value": null,
      "label": "Geocode response",
      "help_text": "The response this place was constructed from.",
      "field_name": "geocode_response",
      "options": {
        "min_length": null,
        "min_value": null,
        "max_value": null,
        "allow_empty_file": null,
        "required": false,
        "max_results": null,
        "max_length": null,
        "max_digits": null,
        "max_whole_digits": null,
        "empty_value": null,
        "max_decimal_places": null
      }
    },
  })
  .value('HomeOptions', {
    "type_name_slug": "home",
    "endpoints": ["/api/v2/home/9428/region/?machinery=HomeExamineMachinery"],
    "visible_fields": ["lot_number", "street_line1", "street_line2", "is_multi_family", "city", "zipcode", "subdivision", "address_override"],
    "region_dependencies": {},
    "new_region_url": null,
    "object_endpoint_pattern": "/api/v2/home/{id}/?machinery=HomeExamineMachinery",
    "type_name": "home",
    "verbose_name": "Home",
    "regionset_template_url": null,
    "region_endpoint_pattern": "/api/v2/home/{id}/region/?machinery=HomeExamineMachinery",
    "object": {}
  });

angular.module('httpReal', ['ng'])
  .config(function ($provide) {
    $provide.decorator('$httpBackend', function () {
      return angular.injector(['ng']).get('$httpBackend');
    });
  })
  .run(function ($http) {
    var username = 'mjeffrey',
      password = 'Migpok*35';
    var authorization = 'Basic ' + btoa(username + ':' + password);
    //console.log(authorization)
    $http.defaults.headers.common.Authorization = authorization;
  })
  .service('httpReal', function ($rootScope) {
    this.submit = function () {
      $rootScope.$digest();
    }
  });

angular.module('bracketInterpolator', ['ng'])
  .config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  });

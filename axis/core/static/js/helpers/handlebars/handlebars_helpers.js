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

Handlebars.registerHelper('debug', function(optionalValue){
    console.log("Current Context");
    console.log("====================");
    console.log(this);
});

Handlebars.registerHelper('compare', function(lvalue, rvalue, options){
    if(arguments.length < 3){
        throw new Error("Handlebars Helper 'compare' needs 2 parameters")
    }

    var operator = options.hash.operator || '==';

    var operators = {
        '==':   function(l, r){ return l == r; },
        '===':  function(l, r){ return l === r; },
        '!=':   function(l, r){ return l != r; },
        '<':    function(l, r){ return l < r; },
        '>':    function(l, r){ return l > r; },
        '<=':   function(l, r){ return l <= r; },
        '>=':   function(l, r){ return l >= r; },
        'typeof': function(l, r){ return typeof l == r; }
    };

    if(!operators[operator]){
        throw new Error("Handlebars helper 'compare' doesn't know the operator "+ operator)
    }

    var result = operators[operator](lvalue, rvalue);
    if(result){
        return options.fn(this);
    } else {
        return options.inverse(this);
    }
});

Handlebars.registerHelper('checklist_textarea', function(context, options){
    var scaffolding = $("<div class='form-group'><div class='controls'></div></div>");
    var el = $("<textarea/>");

    scaffolding.prepend("<label class='control-label'>Comment</label>");

    var dynamic = {
        'id': 'id_'+context.id+'-comment',
        'name': context.id+'-comment'
    };

    el.attr(attr_dict['textarea']);
    el.attr(dynamic);
    if('hash' in options) el.attr(options.hash);
    el = scaffolding.find('.controls').append(el).parent();
    return new Handlebars.SafeString($("<div></div>").append(el).html());
});

Handlebars.registerHelper('checklist_input', function(context, options){
    var scaffolding = $("<div class='form-group'><div class='controls'></div></div>");
    var el = $("<input/>");

    var dynamic = {
        'id': 'id_'+context.id+'-answer',
        'name': context.id+'-answer'
    };

    var attributes = jQuery.extend(true, {}, attr_dict[context.type]);

    if(context.answer && context.answer.answer){
        dynamic['value'] = context.answer.answer;
        if(context.answer.answer.length > 20){
            attributes['title'] = context.answer.answer
        } else {
            delete attributes['data-toggle'];
        }
    }

    el.attr(attributes);
    el.attr(dynamic);
    if('hash' in options) el.attr(options.hash);
    el = scaffolding.find('.controls').append(el).parent();
    return new Handlebars.SafeString($("<div></div>").append(el).html());
});

Handlebars.registerHelper('yesno', function(value, options){
    return value ? '1' : '0';
});

Handlebars.registerHelper('media_url', function(value, options){
    return [media_url, value].join('');
});

Handlebars.registerHelper('join', function(list, options){
    var list = Array.isArray(list) ? list : [list];
    var separator = options.hash.separator || ' / ';
    return list.join(separator);
});

Handlebars.registerHelper('panel-class', function(context){
    if(context.has_errors) return 'panel-danger';

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

    var values = $.map(context, function(val, i){
        return importance[i];
    });

    var level = Math.max.apply(Math, values);
    return levels[level] || 'panel-default';
});

Handlebars.registerHelper('active-tab', function(context, checker){
    var importance = {
        'CRITICAL': 4,
        'ERROR': 3,
        'WARNING': 2,
        'INFO': 1
    };

    var values = $.map(context, function(val, i){
        return importance[i];
    });

    return Math.max.apply(Math, values) == importance[checker] ? 'active' : '';
});

Handlebars.registerHelper('list', function(context){
    var ret = "<ul>";
    for(var i= 0, j=context.length; i<j; i++){
        ret = ret + "<li>" + context[i] + "</li>";
    }
    return ret + "</ul>";
});

Handlebars.registerHelper('strip', function(str){
    return str.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
});

Handlebars.registerHelper('set_key', function(key, value){
    this[key] = value;
});

#Core *(core)*
----------------------------

## Description

TBD

## Authors

* Steven Klass
* Rajesh Pappula
* Gaurav Kapoor
* Mohammad Rafi
* Etienne Robillard
* Eric Walker
* Amit Kumar Pathak
* Tim Valenta
* Kevin Riggen

## Front-end (entire project)

### Template Organization
    * While updating the template system to Bootstrap, I have not modified any of the current template files
    * To override templates, I put them in sites/bootstrap_pivotalenergy_net/templates/{template-folder}


### DOM Organization
    * Bootstrap_base.html is the new base template file
    * Within the base template, there is a {full_content} and a {content}
    * {content} is inside of {full_content}, and should be used when {sidebar} is desired
    * {content} is currently a .span9 item within a .row item
    * {full_content} is currently a .row item
    * So, if you are using {full_content}, your first parent element should be a .span12, and it should contain groups of .row-fluid elements
    * If you are using {content}, you should use groups of .row-fluid elements as your parent elements
    * We use .row-fluid instead of .row, because a .span12 in a .row-fluid item will only be as big as its parent. This means that we can change only the parent widths in the future and have a different layout. Otherwise, all .span* elements would need to be changed throughout the entire page if we were to make a layout change.
    * The base template provides a {body_classes} and {body_id} block so that you can set the body's classes and id's on your templates


### Meta Tags
    * The base template provides a {page_title} block for you to set the page's title


### Stylesheets and Scripts
    * All css styles and scripting should be done in external files.
    * The base template provides {style_sheet} and {javascript_head} blocks for inserting your includes
    * The base template provides a {jquery} block if you want to replace the version of jquery being used. This should not be done for fixes, but for experimentations or isolated upgrades with the intent to upgrade universally.


## Copyright

Copyright 2011-2023 Pivotal Energy Solutions.  All rights reserved.

export const USER_DETAIL = '/api/v2/user/[[ id ]]/';

export const urls = {
    'auth': {
        'login': '/accounts/ajax-login/'
    },
    'impersonate': {
        'list': '/api/v2/user/impersonate_list/',
        'detail': USER_DETAIL,
        'impersonate_start': '/api/v2/user/[[ id ]]/impersonate_start/',
        'impersonate_stop': '/api/v2/user/impersonate_stop/'
    },
    'user': {
        'detail': USER_DETAIL
    }
};

export const auth = {
    'urls': urls.auth
};

export const impersonate = {
    'urls': urls.impersonate,
    'keys': {
        'counts': 'axis_impersonate_user_counts',
        'latest_impersonate': 'axis_latest_impersonate_users_list'
    }
};

export const zendesk = {
    'urls': {
        'list': '/api/v2/zendesk/tickets/',
        'create': '/api/v2/zendesk/new_ticket/',
        'ticket_fields': '/api/v2/zendesk/ticket_fields/'
    },
    'keys': {
        'ticket_fields': 'zendesk_ticket_fields',
        'open_pages': 'zendesk_open_pages'
    },
    'widget': {
        'min_height': '39px',
        'max_height': '500px'
    }
};

export const USER_DETAIL = "/api/v2/user/[[ id ]]/";

export const impersonate = {
  'urls': {
    list: "/api/v2/user/impersonate_list/",
    detail: USER_DETAIL,
    impersonate_start: "/api/v2/user/[[ id ]]/impersonate_start/",
    impersonate_stop: "/api/v2/user/impersonate_stop/"
  },
  'keys': {
      'counts': 'axis_impersonate_user_counts',
      'latest_impersonate': 'axis_latest_impersonate_users_list'
  }
};

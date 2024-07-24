export const READONLY = window.readonly;

export var QuestionFilters = {
    searchString: '',
    types: {
        'open': {
            label: 'Open',
            active: true
        },
        'multiple-choice': {
            label: 'Multiple Choice',
            active: true
        },
        'date': {
            label: 'Date',
            active: true
        },
        'datetime': {
            label: 'Date Time',
            active: true
        },
        'integer': {
            label: 'Whole Number',
            active: true
        },
        'float': {
            label: 'Decimal Number',
            active: true
        },
        'csv': {
            label: 'Comma Separated Value',
            active: true
        },
        'kvfloatcsv': {
            label: 'Key Value Comma Separated Value',
            active: true
        }
    },
    states: {
        'required': {
            label: 'Required',
            active: true
        },
        'optional': {
            label: 'Optional',
            active: false
        },
        'answered': {
            label: 'Answered',
            active: false
        },
        'unanswered': {
            label: 'Unanswered',
            active: true
        }
    },
    sections: {},
    programs: {}
};
export const QuestionTypeLabels = _.mapValues(QuestionFilters.types, 'label');
export const QuestionStateLabels = _.mapValues(QuestionFilters.states, 'label');

export const INTERACTIONS = {
    autoSubmitMultipleChoice: {
        active: true,
        label: 'Submit Multiple Choice Answer when selected'
    },
    submitOpenOnEnter: {
        active: true,
        label: 'Submit Open field answers on Enter'
    },
    autoAdvanceOnAnswer: {
        active: true,
        label: 'Advance to next question on Answer'
    },
    // deferCorrection: {
    //     active: false,
    //     label: 'Defer any errors'
    // },
    skipAnsweredQuestions: {
        active: true,
        label: 'Skip Questions that already have answers'
    }
};
export const INTERACTION_VALUES = _.mapValues(INTERACTIONS, 'active');
export const INTERACTION_LABELS = _.mapValues(INTERACTIONS, 'label');
export const INTERACTION_ORDER = [
    'autoSubmitMultipleChoice',
    'submitOpenOnEnter',
    'autoAdvanceOnAnswer',
    // 'deferCorrection',
    'skipAnsweredQuestions'
];

export const DISPLAY = {
    qaListColoringEnabled: {
        active: true,
        label: 'Color questions in the list to show QA status',
        canShow: function(state){
            return _.filter(state.entities.eepPrograms, {user_role: 'qa'});
        }
    },
    showRelatedAnswers: {
        active: true,
        label: 'Show related Answers inline when viewing a question',
        canShow: function(state){
            return _.filter(state.entities.eepPrograms, {user_role: 'qa'});
        }
    },
    splitQuestionsByProgram: {
        active: false,
        label: 'Split questions by the Program they belong to',
        canShow: function(state){
            return Object.keys(state.entities.eepPrograms).length > 1;
        }
    },
    showRelatedAnswerInQuestionList: {
        active: false,
        label: 'Show Related Answer in Question List (default: QA Answer)',
        canShow: function(state){
            return _.filter(state.entities.eepPrograms, {user_role: 'qa'}).length;
        }
    }
};

export const DISPLAY_VALUES = _.mapValues(DISPLAY, 'active');
export const DISPLAY_LABELS = _.mapValues(DISPLAY, 'label');
export const DISPLAY_CAN_SHOW = _.mapValues(DISPLAY, 'canShow');
export const DISPLAY_ORDER = [
    'qaListColoringEnabled',
    'showRelatedAnswers',
    'splitQuestionsByProgram',
    'showRelatedAnswerInQuestionList'
];

export const DEFAULT_PLACEHOLDER = 'Enter Answer'
export const PLACEHOLDERS = {
    'open': DEFAULT_PLACEHOLDER,
    'date': 'Enter a date',
    'integer': 'Enter a Whole Number',
    'float': 'Enter a decimal',
    'csv': DEFAULT_PLACEHOLDER,
    'kvfloatcsv': DEFAULT_PLACEHOLDER,
    'text': DEFAULT_PLACEHOLDER,
    'hidden': ''
};

export const DETAUL_TOOLTIP = DEFAULT_PLACEHOLDER;
export const TOOLTIPS = {
    'open': DETAUL_TOOLTIP,
    'date': 'Enter a date',
    'integer': 'Enter a Whole Number',
    'float': 'Enter a decimal',
    'csv': DETAUL_TOOLTIP,
    'kvfloatcsv': DETAUL_TOOLTIP,
    'text': DETAUL_TOOLTIP,
    'hidden': ''
};

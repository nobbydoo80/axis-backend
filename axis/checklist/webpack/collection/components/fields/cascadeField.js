import { collector } from '../../collector';

import { createSelector } from 'reselect';
import { multipleChoiceSelectedChoice } from './../../redux/selectors/multipleChoiceSelectedChoice';

const emptyValue = null;
const skipValue = 'N/A';
const customValuePrefix = '(Custom) '
const customValuePrefixRE = new RegExp('^' + customValuePrefix.replace(/[()]/g, '\\$&'));

class CascadeFieldController {
    constructor($ngRedux, $scope, $element, $timeout, $interpolate){
        this.$element = $element;
        this.$timeout = $timeout;
        this.$interpolate = $interpolate;
        this.clear = () => this.selections.fill(emptyValue);
        this.getSelectedChoice = i => this.selectedChoiceGetter($ngRedux.getState());
        this.setSelectedChoice = () => this.selectedChoice = this.getSelectedChoice($ngRedux.getState());
        this.setSelectedChoice();

        this.spec = collector.collectors[this.question.collection_request].full_specification.instruments_info.instruments[this.question.id];
        this.labels = this.spec.response_info.method.labels;
        this.labelCodes = this.spec.response_info.method.label_codes;
        this.choicesLookups = this.spec.response_info.method.source_structured;
        this.choices = [];
        this.selections = [];
        this.selections.length = this.labels.length;
        this.clear();
        this.updateChoices();

        $scope.$on('$destroy', $ngRedux.subscribe(() => this.setSelectedChoice()));
        $scope.$on('$destroy', $scope.$watch(() => this.question, () => this.setSelectedChoice(), true));
    }
    isChoiceSelected(choice){
        return this.selectedChoice && this.selectedChoice.id === choice.id;
    }
    getDisplayClass(choice){
        // FIXME: do we want this to be red if its technically not a failure, but will display as one?
        if(choice.display_as_failure || choice.is_considered_failure){
            return 'btn-danger';
        } else {
            return 'btn-success';
        }
    }
    getPlaceholderText(index){
        if (!this.isAvailable(index)) {
            return '';
        } else if (index == this.choices.length - 1) {
            return '(Search)';
        }
        return '(Search or manually enter)';
    }
    getChoices(index){
        var lookups = this.choicesLookups;
        for (var i = 0; i < index; i++) {
            if (selection === emptyValue) {
                break;
            }
            var selection = this.selections[i];
            lookups = lookups[selection] || {};
        }
        if (_.isArray(lookups)) {
            var leafFormat = this.spec.response_info.method.leaf_display_format;
            lookups = _.slice(lookups).map(choice => this.format(leafFormat, choice));
        } else {
            lookups = _.keys(lookups);
        }
        return lookups;
    }
    format(spec, data) {
        // Convert spec to angular tokens
        spec = spec.replace(/\{/g, '[[ ').replace(/\}/g, ' ]]');
        return this.$interpolate(spec)(data);
    }
    isAvailable(index) {
        if (this.isDisabled) {
            return false;
        }

        // Last box is locked if there are no choices (custom answers not allowed)
        var isLeafChoice = this.choices.length == index;
        var isSingleChoice = this.choices[index].length === 1;
        if (isLeafChoice && isSingleChoice) {
            return false;
        }

        var isFirst = index === 0;
        var isPopulated = this.selections[index] !== emptyValue;
        var isFollowsPopulated = this.selections[index - 1] !== emptyValue;
        var isFollowsSkipped = this.selections[index - 1] === skipValue;
        if (isFirst || isPopulated || isFollowsPopulated || isFollowsSkipped) {
            return true;
        }
        return false;
    }
    hasCustomChoice() {
        return _.filter(_.map(this.selections, v => customValuePrefixRE.test(v))).length > 0;
    }
    selectedChoiceGetter(state){
        if (this.answer) {
            return this.answer.data.input;
        } else {
            if (state.entities.temporaryAnswer[this.question.id]) {
                let answer = state.entities.temporaryAnswer[this.question.id].answer;
                return answer;
            }
        }
        return {};
    }
    refreshHandler(index, search) {
        this.updateChoices(index, search);
    }
    changeHandler(index, search) {
        this.truncateRemaining(index);
        this.updateChoices();
        let data = {
            choice: this.getChoiceInfo()
        }
        let leafPosition = this.labelCodes[this.labelCodes.length - 1];
        if (!data.choice[leafPosition] && !this.hasCustomChoice()) {
            data = emptyValue;
        }
        if (data !== emptyValue) {
            this.answer.data.input = data.choice;
            this.hooks.update(false, data.choice);
        }
    }
    getChoiceInfo() {
        let info = {};

        function _cleanValue(selection){
            if (selection !== emptyValue) {
                selection = selection.replace(customValuePrefixRE, '');
            }
            return selection;
        }

        this.selections.map((selection, i) => info[this.labelCodes[i]] = _cleanValue(selection));
        return info;
    }
    updateChoices(index, search) {
        // If we have an answer id lets seed this
        if (this.answer.id) {
            let characteristics = {};
            // We need to map characteristics into its own dataset for matching later on.
            _.forOwn(this.answer.data.input, (v, k) => {
                let i = this.labelCodes.indexOf(k);
                let isLeaf = (i === -1);
                if ( isLeaf ) {
                    if ( v  != null ) {
                        characteristics[k] = v;
                    }
                } else {
                    this.selections[i] = v;
                }
            });
            // If this isn't a custom answer then try and feed it in.
            if ( Object.keys(characteristics).length  ) {
                this.selections[this.selections.length - 1] = this.format(
                  this.spec.response_info.method.leaf_display_format, characteristics);
            }
        }

        function _filterChoices(choices, search, isLeaf, lowercaseChoices) {
            choices = _.filter(choices, choice => choice.match(new RegExp('.*'+search+'.*', 'i')));

            // Inject custom search choice if no full matches
            if (!isLeaf) {
                var isCustom = (lowercaseChoices.indexOf(search.toLowerCase()) === -1)
                if (isCustom) {
                    choices.push(customValuePrefix + search);
                }
            }

            return choices;
        }

        function _injectCurrentSelection(choices, selection, lowercaseChoices) {
            var isCustom = (lowercaseChoices.indexOf(selection.toLowerCase()) === -1)
            if (isCustom) {
                choices.push(selection);
            }
        }

        // Here is where we start.
        // Typically, there are 3 fields [selections] (brand, model, charateristics)
        for (var i in this.selections) {
            // Grab the available choices
            this.choices[i] = this.getChoices(i);
            var lowercaseChoices = _.map(this.choices[i], s=>s.toLowerCase());

            // Do search filter on applicable box
            if (search && index == i) {
                var isLeaf = (index == this.selections.length - 1);
                this.choices[i] = _filterChoices(this.choices[i], search, isLeaf, lowercaseChoices);
            }

            // Inject current selection if it's not already a choice
            if (this.selections[i] !== emptyValue) {
                _injectCurrentSelection(this.choices[i], this.selections[i], lowercaseChoices);
            }

            // If the filter is skippable, then the skip option is all that should be seen.
            // In every other case, we add the empty option to the front of the choices.
            if (this.choices[i].length === 1) {
                this.selections[i] = this.choices[i][0];
            }
        }
    }
    truncateRemaining(index) {
        this.selections.fill(emptyValue, index + 1);
    }
}

class cascadeOptionController {
    constructor(){
        // used in template
        this.getClasses = createSelector(...this.inputSelectors(), this.classesGetter);
    }
    inputSelectors(){
        return [
            () => this.selectedClass,
            () => this.isSelected,
            () => this.isDisabled
        ];
    }
    classesGetter(selectedClass, isSelected, isDisabled){
        return {
            [selectedClass]: isSelected,
            'disabled': isDisabled
        };
    }
}

export function cascadeField(){
    return {
        scope: {
            hooks: '=',
            tableLookup: '=',
            question: '=',
            answer: '=',
            isDisabled: '=',
            answerCallback: '&'
        },
        template: `
        <div class="form-group"
             ng-repeat="label in ctrl.labels">
            <label>[[ label ]] <copy-value-button text-to-copy="ctrl.selections[$index]"></copy-value-button></label>

            <div ng-switch="$last && ctrl.hasCustomChoice()">
                <p ng-switch-when="true">
                    <em>No characteristics available for manually submitted equipment.</em>
                </p>

                <div ng-switch-default>
                    <ui-select ng-model="ctrl.selections[$index]"
                               theme="bootstrap"
                               ng-change="ctrl.changeHandler($index)"
                               ng-disabled="!ctrl.isAvailable($index)"
                               reset-search-input="true"
                        >
                        <ui-select-match ng-attr-placeholder="[[ ctrl.getPlaceholderText($index) ]]">
                            [[ $select.selected ]]
                        </ui-select-match>
                        <ui-select-choices repeat="choice in ctrl.choices[$index] track by $index"
                                           refresh="ctrl.refreshHandler($index, $select.search)"
                                           refresh-delay="0">
                            <div ng-bind="choice"></div>
                        </ui-select-choices>
                    </ui-select>
                </div>
            </div>
        </div>
        `,
        controller: CascadeFieldController,
        controllerAs: 'ctrl',
        bindToController: true
    };
}

export function cascadeOption(){
    return {
        scope: {
            label: '=',
            isSelected: '='
        },
        template: `
        <option ng-value='input.label'>[[ input.label ]]</option>
        `,
        replace: true,  // deprecated in next version of angular
        controller: cascadeOptionController,
        controllerAs: 'input',
        bindToController: true
    };
}

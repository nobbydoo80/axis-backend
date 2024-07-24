const isHomePage = window.__ExamineSettings.page === 'home';
const checklistParent = isHomePage ? 'tabs.checklist' : null;

const checklistPageEmptyDetail = `
    <span ng-controller="ExamineViewController as examineApp">
        <axis-single-region options="pageRegions.home"></axis-single-region>
    </span>
`;

const homePageEmptyDetail = `
    <h4 class="text-center">Please select a question.</h4>
`;

export const checklistList = {
    url: '/',
    parent: checklistParent,
    views: {
        detail: {
            template: isHomePage ? homePageEmptyDetail : checklistPageEmptyDetail
        }
    }
};

export const checklistDetail = {
    url: 'question/:id',
    views: {
        'detail@': {
            template: ` <question-detail></question-detail> `
        }
    }
};

export const settings = {
    url: 'settings',
    views: {
        'detail@': {
            template: `
                <div class="row">
                    <div class="col-xs-12">
                        <user-settings></user-settings>
                    </div>
                </div>
            `
        }
    }
};

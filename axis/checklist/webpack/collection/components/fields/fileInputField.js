export function fileInput(){
    return {
        scope: {
            callback: '&'
        },
        link: function(scope, elem, attrs){
            let input = elem.find('input[type="file"]');
            let jasny = elem.find('.fileinput');

            input.bind('change', function(event){
                let clearFn = _.after(event.target.files.length, () => jasny.fileinput('clear'));
                return _.map(event.target.files, function(file){
                    let name =file.name;
                    let extension = name.split('.').pop();

                    scope.callback({name, file, extension});
                    clearFn();

                });
            });
        },
        template: `<div class="row">
    <div class="col-xs-12">
        <div class="form-group">
            <div class="controls">
                <div class="fileinput fileinput-new input-group" data-provides="fileinput">
                    <div class="form-control" data-trigger="fileinput">
                        <i class="icon-file fileinput-exists"></i>
                        <span class="fileinput-filename"></span>
                    </div>
                        <span class="input-group-addon btn btn-default btn-file">
                            <span class="fileinput-new">Select file</span>
                            <span class="fileinput-exists">Change</span>
                            <input name="fileupload" type="file" multiple/>
                        </span>
                </div>
            </div>
        </div>
    </div>
</div>
        `,
    }
}

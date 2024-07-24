/**
 * Created by michaeljeffrey on 8/7/15.
 */

(function(root, factory){
    if(typeof module === 'object' && module.exports){
        module.exports = factory();
    } else {
        root.AsyncProgressBar = factory();
    }
})(this, function AsyncProgressBarModule(){
    var _progressBar = $("<div class='progress-bar' role='progressbar' aria-valuemin='0' aria-valuemax='100' style='width:0%;'></div>"),
        progressSuccess = _progressBar.clone().addClass('progress-bar-success'),
        progressInfo = _progressBar.clone().addClass('progress-bar-info'),
        progressError = _progressBar.clone().addClass('progress-bar-danger'),
        progressBarHolder = $("<div><div class='progress progress-striped active'></div></div>"),
        textElement = $("<span class='text'></span>"),
        closeButton = $("<button type='button' class='close' aria-hidden='true' style='margin-top: -1px;'>&times;</button>"),
        defaultOptions = {
            'show_text': true,
            'removeable': true
        };

    function AsyncProgressBar(total, target, options){
        // init values
        this.target = $(target);
        this.total = total;
        this.options = options || defaultOptions;

        this.counts = {
            success: 0,
            info: 0,
            error: 0
        };

        // Setup progress bar
        this.container = buildProgressBar(this.options);
        this.container.hide();
        this.target.append(this.container);
        this.container.slideDown();
        this.bars = {
            success: this.container.find('.progress-bar-success'),
            info: this.container.find('.progress-bar-info'),
            error: this.container.find('.progress-bar-danger')
        };

        // init text
        if(this.options.show_text){
            this.updateText();
        }
        // init listener
        if(this.options.removeable){
            this.container.on('click', '.close', this.destroy.bind(this));
        }
    }
    Object.defineProperties(AsyncProgressBar.prototype, {
        'progress': {
            get: function(){
                return this.counts.success + this.counts.info + this.counts.error;
            }
        },
        'isDone': {
            get: function(){
                return this.progress === this.total;
            }
        }
    });

    // Callbacks
    AsyncProgressBar.prototype.success = getIncrementListener('success');
    AsyncProgressBar.prototype.info = getIncrementListener('info');
    AsyncProgressBar.prototype.error = getIncrementListener('error');

    // Others
    AsyncProgressBar.prototype.complete = complete;
    AsyncProgressBar.prototype.destroy = destroy;
    AsyncProgressBar.prototype.add_proxy = add_proxy;
    AsyncProgressBar.prototype.getTextString = getTextString;
    AsyncProgressBar.prototype.updateProgressBar = updateProgressBar;
    AsyncProgressBar.prototype.updateText = updateText;

    // ****************************** //
    // METHODS                        //
    // ****************************** //
    function complete(){
        this.container.find('.progress').removeClass('progress-striped active');
    }
    function destroy(){
        var that = this;
        this.container.slideUp(function(){
            that.container.remove();
        });
    }
    function add_proxy(key, fn){
        proxy_method(this, key, fn);
    }
    function getTextString(){
        return [this.progress, this.total].join(' / ') + ' complete.';
    }
    function updateProgressBar(key){
        var width = (this.counts[key] / this.total)*100;
        this.bars[key].width(width+'%');
    }
    function updateText(){
        this.container.find('.text').html(this.getTextString());
    }

    // ****************************** //
    // HELPERS                        //
    // ****************************** //
    function getIncrementListener(key){
        return function _increment_listener(){
            this.counts[key]++;
            this.updateProgressBar(key);
            this.updateText();
            if(this.isDone) this.complete();
        }
    }
    function proxy_method(bar, callback_key, proxy){
        var fn = bar[callback_key];

        bar[callback_key] = function(){
            fn.call(bar);
            proxy.call(bar, callback_key);
        }
    }
    function buildProgressBar(options){
        var p_bar = progressBarHolder.clone();

        if(options.show_text){
            p_bar.prepend(textElement.clone());
        }
        if(options.removeable){
            p_bar.prepend(closeButton.clone());
        }

        // Prepend text and close button here. <---
        p_bar.find('.progress').append(progressSuccess.clone(), progressInfo.clone(), progressError.clone());
        return p_bar
    }

    return AsyncProgressBar;
});

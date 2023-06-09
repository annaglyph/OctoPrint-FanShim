/*
 * View model for OctoPrint-FanShim
 *
 * Author: Rus Wetherell
 * License: AGPLv3
 */
$(function() {
    function FanshimViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[1];

        self.fanshim_indicator = $("#fanshim_indicator");
    	self.isFanShimOn = ko.observable(undefined);

        self.onBeforeBinding = function() {
            self.settings = self.settingsViewModel.settings;
        };

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "fanshim") {
                return;
            }

            if (data.isFanShimOn !== undefined) {
                self.isFanShimOn(data.isFanShimOn);
            }
        };

        self.onStartup = function () {
            self.isFanShimOn.subscribe(function() {
                if (self.isFanShimOn()) {
                    self.fanshim_indicator.removeClass("off").addClass("on");
                } else {
                    self.fanshim_indicator.removeClass("on").addClass("off");
                }
            });
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: FanshimViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["loginStateViewModel", "settingsViewModel"],
        // Elements to bind to, e.g. #settings_plugin_fanshim, #tab_plugin_fanshim, ...
        elements: ["#navbar_plugin_fanshim","#settings_plugin_fanshim"]
    });
});
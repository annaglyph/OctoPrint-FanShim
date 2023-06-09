# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask

from octoprint.events import Events
from octoprint.util import RepeatedTimer

class FanshimPlugin(
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.RestartNeedingPlugin
    ):

    def __init__(self):
        self.debugMode = True
    
    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            "on_threshold": 65,
            "off_threshold": 55,
            "delay": 2,
            "preempt": False,
            "brightness": 255,
            "noled": False,
            "nobutton": False
        }
    
   
    ##~~ TemplatePlugin mixin

    def get_template_configs(self):
        return [
			dict(type="navbar", custom_bindings=True),
			dict(type="settings", custom_bindings=True)
		]

    
    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/fanshim.js"],
            "css": ["css/fanshim.css"],
            #"less": ["less/fanshim.less"]
        }
    

    def on_after_startup(self):
        self.fanshim_state = False
        self._logger.info("--------------------------------------------")
        self._logger.info("FanShim started, listening for GET request")
        self._logger.info("ON temp: {}, OFF temp: {}, Delay: {}, Preempt: {}, Brightness: {}, No LED: {}, No button".format(
            self._settings.get(["on_threshold"]),
            self._settings.get(["off_threshold"]),
            self._settings.get(["delay"]),
            self._settings.get(["preempt"]),
            self._settings.get(["brightness"]),
            self._settings.get(["noled"]),
            self._settings.get(["nobutton"])))
        self._logger.info("--------------------------------------------")

		# Setting the default state of fanshim
        self._logger.info("Let's start RepeatedTimer!")
        interval = 5.0 if self.debugMode else 30.0
        self.start_soc_timer(interval)


    def start_fanshim_timer(self, interval):
        self._checkFanShimTimer = RepeatedTimer(
            interval, self.update_fanshim_status, run_first=True
        )
        self._checkFanShimTimer.start()


    def update_fanshim_status(self):
        self._logger.info("FanShim status: {}".format(self.fanshim_state))
        self._plugin_manager.send_plugin_message(self._identifier, dict(isFanShimOn=self.fanshim_state))
                

    def fanshim_toggle(self):
        self.fanshim_state = not self.fanshim_state

        self._logger.info("Got toggle request. fanshim_state: {}, on_threshold: {}".format(
			self.fanshim_state,
            self._settings.get(["on_threshold"])
		))

        self._plugin_manager.send_plugin_message(self._identifier, dict(isFanShimtOn=self.fanshim_state))
                
    
    def on_api_get(self, request):
        action = request.args.get('action', default="toggle", type=str)

        if action == "toggle":
            self.fanshim_toggle()

            return flask.jsonify(state=self.fanshim_state)

        elif action == "getState":
            return flask.jsonify(state=self.fanshim_state)

        elif action == "turnOn":
            if not self.fanshim_state:
                self.fanshim_toggle()

            return flask.jsonify(state=self.fanshim_state)

        elif action == "turnOff":
            if self.fanshim_state:
                self.fanshim_toggle()

            return flask.jsonify(state=self.fanshim_state)

        else:
            return flask.jsonify(error="action not recognized")

    def on_event(self, event, payload):
        if event == Events.CLIENT_OPENED:
            self._plugin_manager.send_plugin_message(self._identifier, dict(isFanShimOn=self.fanshim_state))
            return
        

    def on_settings_save(self, data):
        diff = super(FanshimPlugin, self).on_settings_save(data)
        self._logger.info("FanshimPlugin settings data: " + str(data))

        if "preempt" in data:
            self.preempt = data["preempt"]
            if self.preempt:
                interval = 5.0 if self.debugMode else 30.0
                self.start_fanshim_timer(interval)
            else:
                if self._checkFanShimTimer is not None:
                    try:
                        self._checkFanShimTimer.cancel()
                    except Exception:
                        pass

        self._plugin_manager.send_plugin_message(self._identifier, dict())

        return diff

   
   ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "fanshim": {
                "displayName": "Fanshim Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "anaglyph",
                "repo": "OctoPrint-FanShim",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/anaglyph/OctoPrint-FanShim/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Fanshim Plugin"
__plugin_author__ = "Rus Wetherell"
__plugin_url__ = "https://github.com/anaglyph/OctoPrint-FanShim"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = FanshimPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }


class SystemAPIMixin(object):
    """
    Mixin class providing the API endpoints corresponding to fin.System

    Don't use this class directly, it should only be mixed into the public OpenFinClient
    """

    # These methods are all implemented in the same order as the js version

    def get_version(self, callback=None):
        """
        Get the OpenFin version
        """

        self._check_status()
        self._ws('get-version', callback=callback)

    def clear_cache(self, callback=None):
        """
        Clear cache
        """

        self._check_status()
        self._ws('clear-cache', callback=callback)

    def delete_cache_on_exit(self, callback=None):
        """
        Delete cache on exit
        """
        self._check_status()
        self._ws('delete-cache-request', callback=callback)

    def get_all_windows(self, callback=None):
        """
        Get a list of all application windows, including their sizes
        and positions
        """
        self._check_status()
        self._ws('get-all-windows', callback=callback)

    def get_all_applications(self, callback=None):
        """
        Get a list of all openfin applications
        """
        self._check_status()
        self._ws('get-all-applications', callback=callback)

    def get_command_line_arguments(self, callback=None):
        """
        Get the command line arguments used to launch openfin
        """
        self._check_status()
        self._ws('get-command-line-arguments', callback=callback)

    def get_device_id(self, callback=None):
        """
        Get device id
        """
        self._check_status()
        self._ws('get-device-id', callback=callback)

    def get_environment_variable(self, callback=None):
        """
        Get environment variable
        """
        self._check_status()
        self._ws('get-environment-variable', callback=callback)

    # TODO: the js-adapter version also takes endFile and sizeLimit as optional args,
    # but those arguments don't seem to do anything
    def get_log(self, name, callback=None):
        """
        Get the contents of the given log (such as debug.log)

        See get_log_list
        """
        self._check_status()
        self._ws('get_log', args=(name,), callback=callback)

    def get_log_list(self, callback=None):
        """
        Get all log names which can be passed into get_log
        """
        self._check_status()
        self._ws('list-logs', callback=callback)

    def get_monitor_info(self, callback=None):
        """
        Get information describing all of the connected monitors,
        including their sizes and virtual positioning
        """
        self._check_status()
        self._ws('get-monitor-info', callback=callback)

    def get_mouse_position(self, callback=None):
        """
        Get the current position of the mouse cursor
        """
        self._check_status()
        self._ws('get-mouse-position', callback=callback)

    def get_process_list(self, callback=None):
        """
        Get a list of operating system processes and relevant data,
        including their CPU usage, PID, memory usage, etc.
        """
        self._check_status()
        self._ws('process-snapshot', callback=callback)

    def get_proxy_settings(self, callback=None):
        """
        Get the network proxy settings
        """
        self._check_status()
        self._ws('get-proxy-settings', callback=callback)

    def get_rvm_info(self, callback=None):
        """
        Get information about the openfin RVM, including its path, version, etc.
        """
        self._check_status()
        self._ws('get-rvm-info', callback=callback)

    def launch_external_process(self, path, arguments='', callback=None):
        """
        Launch an external process
        """
        self._check_status()
        self._ws(
            'launch_external_process',
            args=(
                path,
                arguments),
            callback=callback)

    def monitor_external_process(self, pid, callback=None):
        """
        Given a PID, return a UUID that will allow openfin to interact with a process
        """
        self._check_status()
        self._ws('monitor_external_process', args=(pid,), callback=callback)

    def log(self, level, message, callback=None):
        """
        Record a log message
        """
        self._check_status()
        self._ws('log', args=(level, message), callback=callback)

    def open_url_with_browser(self, url, callback=None):
        """
        Open a url in the default system browser
        """
        self._check_status()
        self._ws('open_url_with_browser', args=(url,), callback=callback)

    def release_external_process(self, uuid, callback=None):
        """
        Stop monitoring an external process
        """
        self._check_status()
        self._ws('release_external_process', args=(uuid,), callback=callback)

    # Show developer tools doesn't seem to work from the JS adapter
    # def show_developer_tools(self, destination):
    #    """
    #    Show developer tools
    #    """
    #    self._check_status()
    #    key = SubKey.from_string(destination)
    #    self._ws('show_developer_tools', args=(key,))

    def terminate_external_process(self, uuid, callback=None):
        """
        Terminate an external process
        """
        self._check_status()
        self._ws('terminate_external_process', args=(uuid,), callback=callback)

    def update_proxy_settings(self, address, port, proxy_type, callback=None):
        """
        Update the network proxy settings used by openfin
        """
        self._check_status()
        self._ws(
            'update_proxy',
            args=(
                address,
                port,
                proxy_type),
            callback=callback)

    def download_asset(self, src, alias, version,
                       target=None, asset_args=None, callback=None):
        """
        Download asset
        """
        self._check_status()
        self._ws('download_asset',
                 args=(src, alias, version, target, asset_args),
                 callback=callback)

    def get_all_external_applications(self, callback=None):
        """
        Get a list of UUIDs corresponding to external applications
        """
        self._check_status()
        self._ws('get-all-external-applications', callback=callback)

    def resolve_uuid(self, uuid, callback=None):
        """
        Get information about a given UUID
        """
        self._check_status()
        self._ws('resolve_uuid', args=(uuid,), callback=callback)

    # TODO: I'm not sure what this is intended for
    # It's also the only call in the js-adpter that uses wire.ferryAction
    # instead of wire.sendAction (the python version only implements
    # sendAction)
    def execute_on_remote(self):
        self._check_status()
        raise NotImplementedError()

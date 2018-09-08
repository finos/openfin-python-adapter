from tornado import gen


class SystemPrivateMixin(object):
    """
    Mixin class providing the private methods corresponding to fin.System

    Don't use this class directly, it should only be mixed into the private OpenFinTornadoWebSocket
    """

    @gen.coroutine
    def get_log(self, name):

        payload = yield self._action('view-log', {
            'name': name,
        })
        result = payload.get('data') if payload else None
        raise gen.Return(result)

    @gen.coroutine
    def launch_external_process(self, path, arguments):

        payload = yield self._action('launch-external-process', {
            'path': path,
            'arguments': arguments,
        })
        result = payload.get('data').get('uuid') if payload else None
        raise gen.Return(result)

    @gen.coroutine
    def terminate_external_process(self, uuid):

        payload = yield self._action('terminate-external-process', {
            'uuid': uuid,
        })
        result = payload.get('data') if payload else None
        raise gen.Return(result)

    @gen.coroutine
    def monitor_external_process(self, pid):

        payload = yield self._action('monitor-external-process', {
            'pid': pid,
        })
        result = payload.get('data').get('uuid') if payload else None
        raise gen.Return(result)

    @gen.coroutine
    def log(self, level, message):
        _ = yield self._action('write-to-log', {
            'level': level,
            'message': message,
        })

    @gen.coroutine
    def open_url_with_browser(self, url):
        _ = yield self._action('open-url-with-browser', {
            'url': url,
        })

    @gen.coroutine
    def release_external_process(self, uuid):
        _ = yield self._action('release-external-process', {
            'uuid': uuid,
        })

    @gen.coroutine
    def update_proxy(self, address, port, proxy_type):
        _ = yield self._action('update-proxy', {
            'proxyAddress': address,
            'proxyPort': port,
            'type': proxy_type,
        })

    @gen.coroutine
    def download_asset(self, src, alias, version, target, asset_args):
        request = {
            'src': src,
            'alias': alias,
            'version': version,
        }
        if target is not None:
            request['target'] = target
        if asset_args is not None:
            request['args'] = asset_args
        _ = yield self._action('download-asset', request)

    @gen.coroutine
    def resolve_uuid(self, uuid):

        payload = yield self._action('resolve-uuid', {
            'entityKey': uuid,
        })
        result = payload.get('data') if payload else None
        raise gen.Return(result)

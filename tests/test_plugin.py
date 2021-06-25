from tests.factories import MockedConnectedAgent


def test_add_plugin():
    class PluginMixin:
        async def _hook_plugin_before_connection(self, *args, **kwargs):
            await super()._hook_plugin_before_connection(*args, **kwargs)
            self.before_hook = True

        async def _hook_plugin_after_connection(self, *args, **kwargs):
            await super()._hook_plugin_after_connection(*args, **kwargs)
            self.after_hook = True

    class AgentWithPlugin(PluginMixin, MockedConnectedAgent):
        pass

    agent = AgentWithPlugin("test@localhost", "secret")

    future = agent.start()
    future.result()

    assert agent.before_hook
    assert agent.after_hook


def test_plugin_override():
    class PluginMixin:
        async def _hook_plugin_after_connection(self, *args, **kwargs):
            await super()._hook_plugin_after_connection(*args, **kwargs)
            self.client = None

    class AgentWithPlugin(PluginMixin, MockedConnectedAgent):
        pass

    agent = AgentWithPlugin("test@localhost", "secret")

    future = agent.start()
    future.result()

    assert agent.client is None


def test_plugin_multiple_override():
    """
    The order of the mixins is important
    """
    class PluginMixin1:
        async def _hook_plugin_after_connection(self, *args, **kwargs):
            await super()._hook_plugin_after_connection(*args, **kwargs)
            self.client = 1

    class PluginMixin2:
        async def _hook_plugin_after_connection(self, *args, **kwargs):
            await super()._hook_plugin_after_connection(*args, **kwargs)
            self.client = 2

    class PluginMixin3:
        async def _hook_plugin_after_connection(self, *args, **kwargs):
            await super()._hook_plugin_after_connection(*args, **kwargs)
            self.client = 3

    class AgentWithPlugin(PluginMixin1, PluginMixin2, PluginMixin3, MockedConnectedAgent):
        pass

    agent = AgentWithPlugin("test@localhost", "secret")

    future = agent.start()
    future.result()

    assert agent.client == 1

from abc import ABCMeta, abstractmethod
import attr
from django.conf import settings

from edx_ace.channel import ChannelType
from edx_ace.utils.plugins import get_plugins
from edx_ace.utils.once import once


@attr.s
class PolicyResult(object):
    deny = attr.ib(
        default=attr.Factory(set),
    )

    @deny.validator
    def check_set_of_channel_types(self, attribute, set_value):
        for value in set_value:
            if value not in ChannelType:
                raise ValueError(u"PolicyResult for {} has an invalid value {}.".format(attribute, value))


class Policy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def check(self, message):
        """
        Returns PolicyResult.
        """
        pass


POLICY_PLUGIN_NAMESPACE = 'openedx.ace.policy'


def channels_for(message):
    allowed_channels = set(ChannelType)

    for policy in policies():
        allowed_channels -= policy.check(message).deny

    return allowed_channels


@once
def policies():
    return [
        extension.obj
        for extension in get_plugins(
            namespace=POLICY_PLUGIN_NAMESPACE,
            names=getattr(settings, 'ACE_ENABLED_POLICIES', []),
        )
    ]

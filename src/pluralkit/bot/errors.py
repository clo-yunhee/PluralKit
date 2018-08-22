from pluralkit.utils import humanize_delta


class CommandError(Exception):
    def __init__(self, message):
        super().__init__("❌ {}".format(message))


class SystemParamNotFound(CommandError):
    def __init__(self, param):
        super().__init__("Could not find the system '{}'. You can refer to systems by ID or by account mention.".format(param))


class MemberParamNotFound(CommandError):
    def __init__(self, param):
        super().__init__("Could not find the member '{}'. You can refer to members by ID, or if they're in your own system, by name.".format(param))


class NoRegisteredSystem(CommandError):
    def __init__(self):
        super().__init__("You do not have a system registered with the bot. To register a system, use `pk;system register`. If you already have a system on a different account, use `pk;link` from that account.")


class AlreadyRegisteredSystem(CommandError):
    def __init__(self):
        super().__init__("You already have a system registered. To delete your existing system, use `pk;system delete`.")


class ConfirmTimedOut(CommandError):
    def __init__(self):
        super().__init__("Confirmation timed out.")


class NotEnoughArgumentsProvided(CommandError):
    def __init__(self):
        super().__init__("Not enough arguments provided.")


class LinkeeAlreadyInSystem(CommandError):
    def __init__(self, system_id):
        super().__init__("That account is already in a system (with ID: {})".format(system_id))


class ConfirmCancelled(CommandError):
    def __init__(self):
        super().__init__("Confirmation cancelled.")


class CannotUnlinkOnlyAccount(CommandError):
    def __init__(self):
        super().__init__("This is the only account in your system, so you can't unlink it.")


class NoMembersSpecified(CommandError):
    def __init__(self):
        super().__init__("You need to specify one or more system members to register a switch to.")


class MembersAlreadyFronting(CommandError):
    def __init__(self, member_names):
        if len(member_names) == 1:
            super().__init__("{} is already fronting.".format(member_names[0]))
        else:
            super().__init__("Members {} are already fronting.".format(", ".join(member_names)))


class DuplicateSwitchMembers(CommandError):
    def __init__(self):
        super().__init__("Duplicate members in switch list.")


class InvalidTime(CommandError):
    def __init__(self, param):
        super().__init__("'{}' can't be parsed as a valid time.".format(param))


class CannotMoveSwitchToFuture(CommandError):
    def __init__(self):
        super().__init__("Can't move switch to a time in the future.")


class NoSwitches(CommandError):
    def __init__(self):
        super().__init__("There are no registered switches for this system.")


class CannotMoveSwitchBeforeLast(CommandError):
    def __init__(self, last_switch_time):
        super().__init__("Can't move switch to before last switch time ({} ago).".format(humanize_delta(last_switch_time)))


class AccountNotFound(CommandError):
    def __init__(self, param):
        super().__init__("Could not find account '{}'.".format(param))


class InvalidExampleProxy(CommandError):
    def __init__(self):
        super().__init__("Example proxy message must contain 'text' exactly once.")

class InvalidAvatarURL(CommandError):
    def __init__(self):
        super().__init__("Invalid avatar URL.")

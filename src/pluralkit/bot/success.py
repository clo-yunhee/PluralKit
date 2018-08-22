class CommandSuccess:
    def __init__(self, message, image=None):
        self.message = "✅ {}".format(message)
        self.image = image


class SystemRegistered(CommandSuccess):
    def __init__(self):
        super().__init__("System registered. To start adding members, try the member wizard with `pk;member setup`, or look around the help pages with `pk;help`.")


class SystemLinked(CommandSuccess):
    def __init__(self):
        super().__init__("Account linked to system.")


class SystemDeleted(CommandSuccess):
    def __init__(self):
        super().__init__("System deleted.")


class SwitchRegistered(CommandSuccess):
    def __init__(self, member_names):
        super().__init__("Switch registered. Current fronter{} now {}.".format(
            "s are" if len(member_names) > 1 else " is",
            ", ".join(member_names)
        ))


class SwitchMoved(CommandSuccess):
    def __init__(self):
        super().__init__("Switch moved.")


class MemberCreated(CommandSuccess):
    def __init__(self, name, hid):
        super().__init__("Member '{}' (ID: {}) registered!".format(name, id))


class MemberDeleted(CommandSuccess):
    def __init__(self):
        super().__init__("Member deleted.")


class ProxySettingsUpdated(CommandSuccess):
    def __init__(self, was_set):
        super().__init__("Proxy settings {}.".format("updated" if was_set else "cleared"))


class DescriptionSet(CommandSuccess):
    def __init__(self, was_set):
        super().__init__("Description {}.".format("updated" if was_set else "cleared"))


class TagSet(CommandSuccess):
    def __init__(self, was_set):
        super().__init__("Tag {}.".format("updated" if was_set else "cleared"))


class NameSet(CommandSuccess):
    def __init__(self, was_set):
        super().__init__("Name {}.".format("updated" if was_set else "cleared"))


class AvatarSet(CommandSuccess):
    def __init__(self, avatar_url):
        super().__init__("Avatar set.", image=avatar_url)

from datetime import datetime

from pluralkit import utils
from pluralkit.bot import errors, success
from pluralkit.bot.commands.member import member_new, member_description, member_avatar, member_delete, member_info, member_name
from pluralkit.bot.commands.proxy import member_proxy
from pluralkit.bot.commands.switch import switch_member, switch_move
from pluralkit.bot.commands.system import system_link, system_unlink, system_register, system_delete, system_info, system_description, system_tag, system_avatar, system_name
from pluralkit.bot.test.test_utils import async_test, mock_user, ctx, DBTestCase


class TestSystemCommands(DBTestCase):
    @async_test
    async def test_create(self):
        # Test basic creation
        self.assertIsInstance(await system_register(await ctx(self.conn, sender=mock_user(1))), success.SystemRegistered)

        # Test failure if there's already a system
        with self.assertRaises(errors.AlreadyRegisteredSystem):
            await system_register(await ctx(self.conn, sender=mock_user(1)))

        # Test system existing and name being none
        system = await self.conn.get_system_by_account(1)
        self.assertIsNotNone(system)
        self.assertIsNone(system.name)

        # Test new system with name
        await system_register(await ctx(self.conn, sender=mock_user(2), args="Test System"))
        system = await self.conn.get_system_by_account(2)
        self.assertEqual(system.name, "Test System")

    @async_test
    async def test_info(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await system_info(await ctx(self.conn, mock_user(1)))

        with self.assertRaises(errors.SystemParamNotFound):
            await system_info(await ctx(self.conn, mock_user(1), args="abcde"))

        # Create system and member
        await system_register(await ctx(self.conn, mock_user(1)))

        with self.assertRaises(errors.SystemParamNotFound):
            await system_info(await ctx(self.conn, mock_user(1), args="abcde"))

        hid = (await self.conn.get_system_by_account(1)).hid

        await system_info(await ctx(self.conn, mock_user(1)))
        await system_info(await ctx(self.conn, mock_user(1), args=hid))

        # Add info and make sure it doesn't error
        await system_link(await ctx(self.conn, mock_user(1), "<@2>", confirm=True, users={
            2: {"name": "Bar"}
        }))
        await system_info(await ctx(self.conn, mock_user(1)))

    @async_test
    async def test_link_unlink(self):
        users = {
            1: {"name": "Foo"},
            2: {"name": "Bar"}
        }

        # Set up a system for us
        await system_register(await ctx(self.conn, sender=mock_user(1), users=users))

        # Test declining request
        with self.assertRaises(errors.ConfirmCancelled):
            await system_link(await ctx(self.conn, mock_user(1), "<@2>", confirm=False, users=users))

        # Test successful request
        await system_link(await ctx(self.conn, mock_user(1), "<@2>", confirm=True, users=users))

        # Make sure both account IDs return the same system
        self.assertEqual(await self.conn.get_system_by_account(1), await self.conn.get_system_by_account(2))

        # Test unlinking
        await system_unlink(await ctx(self.conn, sender=mock_user(1), users=users))

        # Can't unlink twice
        with self.assertRaises(errors.NoRegisteredSystem):
            await system_unlink(await ctx(self.conn, sender=mock_user(1), users=users))

        self.assertIsNone(await self.conn.get_system_by_account(1))
        self.assertIsNotNone(await self.conn.get_system_by_account(2))

        # Can't unlink last
        with self.assertRaises(errors.CannotUnlinkOnlyAccount):
            await system_unlink(await ctx(self.conn, sender=mock_user(2), users=users))

    @async_test
    async def test_delete(self):
        # Test delete with no system
        with self.assertRaises(errors.NoRegisteredSystem):
            await system_delete(await ctx(self.conn, mock_user(1)))

        # Register a system to use
        await system_register(await ctx(self.conn, mock_user(1)))

        # Test cancelling the confirm
        with self.assertRaises(errors.ConfirmCancelled):
            await system_delete(await ctx(self.conn, mock_user(1), confirm=False))

        # Test with confirm
        await system_delete(await ctx(self.conn, mock_user(1), confirm=True))

        # Make sure it's gone
        self.assertIsNone(await self.conn.get_system_by_account(1))

    @async_test
    async def test_name(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await system_name(await ctx(self.conn, mock_user(1)))
        await system_register(await ctx(self.conn, mock_user(1)))

        await system_name(await ctx(self.conn, mock_user(1), args="My System"))
        self.assertEqual((await self.conn.get_system(1)).name, "My System")

        await system_name(await ctx(self.conn, mock_user(1)))
        self.assertEqual((await self.conn.get_system(1)).name, None)

    @async_test
    async def test_description(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await system_description(await ctx(self.conn, mock_user(1)))
        await system_register(await ctx(self.conn, mock_user(1)))

        await system_description(await ctx(self.conn, mock_user(1), args="Test description 123."))
        self.assertEqual((await self.conn.get_system(1)).description, "Test description 123.")

        await system_description(await ctx(self.conn, mock_user(1)))
        self.assertEqual((await self.conn.get_system(1)).description, None)

    @async_test
    async def test_tag(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await system_tag(await ctx(self.conn, mock_user(1)))
        await system_register(await ctx(self.conn, mock_user(1)))

        await system_tag(await ctx(self.conn, mock_user(1), args="[Whatever]"))
        self.assertEqual((await self.conn.get_system(1)).tag, "[Whatever]")

        await system_tag(await ctx(self.conn, mock_user(1)))
        self.assertEqual((await self.conn.get_system(1)).tag, None)

    @async_test
    async def test_avatar_url(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await system_description(await ctx(self.conn, mock_user(1)))
        await system_register(await ctx(self.conn, mock_user(1)))

        # TODO: figure out how to test user avatar lookup
        with self.assertRaises(errors.InvalidAvatarURL):
            await system_avatar(await ctx(self.conn, mock_user(1), args="qwerty fake link"))

        await system_avatar(await ctx(self.conn, mock_user(1), args="http://via.placeholder.com/1024x1024"))
        self.assertEqual((await self.conn.get_system(1)).avatar_url, "http://via.placeholder.com/1024x1024")


class TestSwitchCommands(DBTestCase):
    @async_test
    async def test_switch(self):
        async def fronters():
            fs, _ = await utils.get_fronters(self.conn, 1)
            return [f.name for f in fs]

        # Test with no system
        with self.assertRaises(errors.NoRegisteredSystem):
            await switch_member(await ctx(self.conn, mock_user(1)))

        # Create system and member
        await system_register(await ctx(self.conn, mock_user(1)))
        await member_new(await ctx(self.conn, mock_user(1), args="Foo"))

        # No switch should be registered
        self.assertEqual(await fronters(), [])

        # Register a switch (with no args)
        with self.assertRaises(errors.NoMembersSpecified):
            await switch_member(await ctx(self.conn, mock_user(1)))

        # Register a switch (to member who doesn't exist)
        with self.assertRaises(errors.MemberParamNotFound):
            await switch_member(await ctx(self.conn, mock_user(1), args="Doesn'tExist"))

        # Register a switch to Foo
        await switch_member(await ctx(self.conn, mock_user(1), args="Foo"))
        self.assertEqual(await fronters(), ["Foo"])

        # Register a switch to Foo again, should error because already fronting
        with self.assertRaises(errors.MembersAlreadyFronting):
            await switch_member(await ctx(self.conn, mock_user(1), args="Foo"))

        # Check duplicates
        with self.assertRaises(errors.DuplicateSwitchMembers):
            await switch_member(await ctx(self.conn, mock_user(1), args="Foo Foo"))

        # Make a new member to test cofronting
        await member_new(await ctx(self.conn, mock_user(1), args="Bar"))

        # Switch to just Bar
        await switch_member(await ctx(self.conn, mock_user(1), args="Bar"))
        self.assertEqual(await fronters(), ["Bar"])

        # Switch to Foo AND Bar
        await switch_member(await ctx(self.conn, mock_user(1), args="Foo Bar"))
        self.assertEqual(await fronters(), ["Foo", "Bar"])

        # Test already fronting error
        with self.assertRaises(errors.MembersAlreadyFronting):
            await switch_member(await ctx(self.conn, mock_user(1), args="Foo Bar"))

        # Test swapping fronter
        await switch_member(await ctx(self.conn, mock_user(1), args="Bar Foo"))
        self.assertEqual(await fronters(), ["Bar", "Foo"])

        # Test front history logged properly
        switches = await utils.get_front_history(self.conn, 1, 9999)
        switch_names = [[m.name for m in members] for _, members in switches]

        self.assertEqual(switch_names, list(reversed([
            ["Foo"],
            ["Bar"],
            ["Foo", "Bar"],
            ["Bar", "Foo"]
        ])))

    @async_test
    async def test_move(self):
        # Test with no system
        with self.assertRaises(errors.NoRegisteredSystem):
            await switch_member(await ctx(self.conn, mock_user(1)))

        # Create system and members
        await system_register(await ctx(self.conn, mock_user(1)))
        await member_new(await ctx(self.conn, mock_user(1), args="Foo"))
        await member_new(await ctx(self.conn, mock_user(1), args="Bar"))

        # Test no switches
        with self.assertRaises(errors.NoSwitches):
            await switch_move(await ctx(self.conn, mock_user(1), args="1 day ago", confirm=True))

        # Make switch
        await switch_member(await ctx(self.conn, mock_user(1), args="Foo"))

        # Test confirm
        with self.assertRaises(errors.ConfirmCancelled):
            await switch_move(await ctx(self.conn, mock_user(1), args="1 day ago", confirm=False))

        # Move it to 1 day ago
        await switch_move(await ctx(self.conn, mock_user(1), args="1 day ago", confirm=True))

        # Check whether it's actually moved
        members, timestamp = await utils.get_fronters(self.conn, 1)
        self.assertEqual(members[0].name, "Foo")
        self.assertEqual((datetime.now() - timestamp).days, 1)

        # Test future error
        with self.assertRaises(errors.CannotMoveSwitchToFuture):
            await switch_move(await ctx(self.conn, mock_user(1), args="tomorrow", confirm=True))

        # Make another switch just now
        await switch_member(await ctx(self.conn, mock_user(1), args="Bar"))

        # Try to move it before last
        with self.assertRaises(errors.CannotMoveSwitchBeforeLast):
            await switch_move(await ctx(self.conn, mock_user(1), args="2 days ago"))

        # Try to move it a *little bit*
        await switch_move(await ctx(self.conn, mock_user(1), args="6 hours ago", confirm=True))

        # Check it
        members, timestamp = await utils.get_fronters(self.conn, 1)
        self.assertEqual(members[0].name, "Bar")
        self.assertTrue((datetime.now() - timestamp).seconds >= 60 * 60 * 6)

        # Test invalid
        with self.assertRaises(errors.InvalidTime):
            await switch_move(await ctx(self.conn, mock_user(1), args="qwerty"))

        # Test no args
        with self.assertRaises(errors.NotEnoughArgumentsProvided):
            await switch_move(await ctx(self.conn, mock_user(1)))


class TestProxyCommands(DBTestCase):
    @async_test
    async def test_proxy(self):
        # Test with no system
        with self.assertRaises(errors.NoRegisteredSystem):
            await member_proxy(await ctx(self.conn, mock_user(1)))

        # Create system and member
        await system_register(await ctx(self.conn, mock_user(1)))
        await member_new(await ctx(self.conn, mock_user(1), args="Foo"))

        # Test with no system
        with self.assertRaises(errors.MemberParamNotFound):
            await member_proxy(await ctx(self.conn, mock_user(1), args="Bar [text]"))

        # Set proxy tags
        with self.assertRaises(errors.InvalidExampleProxy):
            await member_proxy(await ctx(self.conn, mock_user(1), args="Foo []"))

        with self.assertRaises(errors.InvalidExampleProxy):
            await member_proxy(await ctx(self.conn, mock_user(1), args="Foo [text text]"))

        with self.assertRaises(errors.InvalidExampleProxy):
            await member_proxy(await ctx(self.conn, mock_user(1), args="Foo [test]"))

        # Test []s
        await member_proxy(await ctx(self.conn, mock_user(1), args="Foo [text]"))
        self.assertEqual((await self.conn.get_member_by_name(1, "Foo")).prefix, "[")
        self.assertEqual((await self.conn.get_member_by_name(1, "Foo")).suffix, "]")

        # Test + prefix
        await member_proxy(await ctx(self.conn, mock_user(1), args="Foo + text"))
        self.assertEqual((await self.conn.get_member_by_name(1, "Foo")).prefix, "+")
        self.assertEqual((await self.conn.get_member_by_name(1, "Foo")).suffix, None)

        # Test clear
        await member_proxy(await ctx(self.conn, mock_user(1), args="Foo"))
        self.assertEqual((await self.conn.get_member_by_name(1, "Foo")).prefix, None)
        self.assertEqual((await self.conn.get_member_by_name(1, "Foo")).suffix, None)

    @async_test
    async def test_message(self):
        # TODO: figure out how to test this
        pass


class TestMemberCommands(DBTestCase):
    @async_test
    async def test_info(self):
        with self.assertRaises(errors.NotEnoughArgumentsProvided):
            await member_info(await ctx(self.conn, mock_user(1)))

        with self.assertRaises(errors.MemberParamNotFound):
            await member_info(await ctx(self.conn, mock_user(1), args="abcde"))

        await system_register(await ctx(self.conn, mock_user(1)))
        await member_new(await ctx(self.conn, mock_user(1), args="Foo"))
        hid = (await self.conn.get_member_by_name(1, "Foo")).hid

        await member_info(await ctx(self.conn, mock_user(1), args="Foo"))

        with self.assertRaises(errors.MemberParamNotFound):
            await member_info(await ctx(self.conn, mock_user(2), args="Foo"))
        await member_info(await ctx(self.conn, mock_user(2), args=hid))

        # Add info to make it not crash

    @async_test
    async def test_create(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await member_new(await ctx(self.conn, mock_user(1)))
        await system_register(await ctx(self.conn, mock_user(1)))

        with self.assertRaises(errors.NotEnoughArgumentsProvided):
            await member_new(await ctx(self.conn, mock_user(1)))

        # Test creating members
        await member_new(await ctx(self.conn, mock_user(1), args="Foo"))

        # Test duplicate members
        with self.assertRaises(errors.ConfirmCancelled):
            await member_new(await ctx(self.conn, mock_user(1), args="Foo", confirm=False))
        await member_new(await ctx(self.conn, mock_user(1), args="Foo", confirm=True))

        # Test members
        await member_new(await ctx(self.conn, mock_user(1), args="Bar"))

        member_names = [m.name for m in await self.conn.get_all_members(1)]
        self.assertEqual(member_names, ["Foo", "Foo", "Bar"])

    @async_test
    async def test_delete(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await member_description(await ctx(self.conn, mock_user(1)))
        await system_register(await ctx(self.conn, mock_user(1)))
        await member_new(await ctx(self.conn, mock_user(1), args="Foo"))

        with self.assertRaises(errors.NotEnoughArgumentsProvided):
            await member_delete(await ctx(self.conn, mock_user(1)))

        with self.assertRaises(errors.MemberParamNotFound):
            await member_delete(await ctx(self.conn, mock_user(1), args="Bar"))

        with self.assertRaises(errors.ConfirmCancelled):
            await member_delete(await ctx(self.conn, mock_user(1), args="Foo", confirm=False))
        await member_delete(await ctx(self.conn, mock_user(1), args="Foo", confirm=True))

        self.assertEqual(await self.conn.get_all_members(1), [])

    @async_test
    async def test_description(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await member_description(await ctx(self.conn, mock_user(1)))
        await system_register(await ctx(self.conn, mock_user(1)))
        await member_new(await ctx(self.conn, mock_user(1), args="Foo"))

        with self.assertRaises(errors.MemberParamNotFound):
            await member_description(await ctx(self.conn, mock_user(1), args="Bar"))

        await member_description(await ctx(self.conn, mock_user(1), args="Foo Test description 123."))
        self.assertEqual((await self.conn.get_member(1)).description, "Test description 123.")

        await member_description(await ctx(self.conn, mock_user(1), args="Foo"))
        self.assertEqual((await self.conn.get_member(1)).description, None)


    @async_test
    async def test_name(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await member_name(await ctx(self.conn, mock_user(1)))
        await system_register(await ctx(self.conn, mock_user(1)))
        await member_new(await ctx(self.conn, mock_user(1), args="Foo"))

        with self.assertRaises(errors.MemberParamNotFound):
            await member_name(await ctx(self.conn, mock_user(1), args="Bar"))

        await member_name(await ctx(self.conn, mock_user(1), args="Foo Bar"))
        self.assertEqual((await self.conn.get_member(1)).name, "Bar")

        with self.assertRaises(errors.NotEnoughArgumentsProvided):
            await member_name(await ctx(self.conn, mock_user(1), args="Bar"))

    @async_test
    async def test_avatar_url(self):
        with self.assertRaises(errors.NoRegisteredSystem):
            await member_avatar(await ctx(self.conn, mock_user(1)))
        await system_register(await ctx(self.conn, mock_user(1)))
        await member_new(await ctx(self.conn, mock_user(1), args="Foo"))

        with self.assertRaises(errors.MemberParamNotFound):
            await member_avatar(await ctx(self.conn, mock_user(1), args="Bar"))

        # TODO: figure out how to test user avatar lookup
        with self.assertRaises(errors.InvalidAvatarURL):
            await member_avatar(await ctx(self.conn, mock_user(1), args="Foo qwerty fake link"))

        await member_avatar(await ctx(self.conn, mock_user(1), args="Foo http://via.placeholder.com/1024x1024"))
        self.assertEqual((await self.conn.get_member(1)).avatar_url, "http://via.placeholder.com/1024x1024")

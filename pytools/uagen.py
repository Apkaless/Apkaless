from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem, HardwareType, SoftwareType, SoftwareEngine


def GetRandomUA():
    software_names = [SoftwareName.CHROME.value, SoftwareName.DISCORD_BOT.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.ANDROID.value, OperatingSystem.IOS.value, OperatingSystem.MACOS.value]   
    hardware_type = [HardwareType.COMPUTER.value, HardwareType.MOBILE.value]
    software_type = [SoftwareType.APPLICATION.value, SoftwareType.WEB_BROWSER.value]
    software_Engine = [SoftwareEngine.KHTML.value, SoftwareEngine.GECKO.value, SoftwareEngine.WEBKIT.name, SoftwareEngine.BLINK.name]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, hardware_types=hardware_type, software_types=software_type, software_engines=software_Engine, limit=100)
    user_agents = user_agent_rotator.get_user_agents()
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent



# Author ==> Apkaless, Iraqi (MM6xAk), Instagram ==> Apkaless |

import urllib.request





class HttpProxyChecker():
    """"
    (Http Type Proxy)
    Return True If The Given Proxy Is Working, 
    Return False If The Given Proxy Is Dead
    """
    def __init__(self, proxy: str, timeout: float) -> None:
        self.proxy = proxy
        self.timeout = timeout
    

    def __buildHandler__(self):

        proxyHandler = urllib.request.ProxyHandler(proxies={'https': f'http://{self.proxy}'})

        return proxyHandler
    
    def __build_opener__(self, handler):

        return urllib.request.build_opener(handler)
    
    def __install_opener__(self, opener):

        return urllib.request.install_opener(opener)
    
    def start_checker(self):
        handler = self.__buildHandler__()
        opener = self.__build_opener__(handler)
        self.__install_opener__(opener)

        try:

            resp = urllib.request.urlopen('https://github.com', timeout=self.timeout)
            return True
        
        except Exception as e:
            return False
        
    def remove_duplicated(self, anyList: list) -> list:

        cleaned_list = [dict.fromkeys(anyList)]

        return cleaned_list


class Socks4ProxyChecker():
    """"
    (Socks4 Type Proxy)
    Return True If The Given Proxy Is Working, 
    Return False If The Given Proxy Is Dead
    """
    def __init__(self, proxy: str, timeout: float) -> None:
        self.proxy = proxy
        self.timeout = timeout
    

    def __buildHandler__(self):

        proxyHandler = urllib.request.ProxyHandler(proxies={'https': f'socks4://{self.proxy}'})

        return proxyHandler
    
    def __build_opener__(self, handler):

        return urllib.request.build_opener(handler)
    
    def __install_opener__(self, opener):

        return urllib.request.install_opener(opener)
    
    def start_checker(self):
        handler = self.__buildHandler__()
        opener = self.__build_opener__(handler)
        self.__install_opener__(opener)

        try:

            resp = urllib.request.urlopen('https://github.com', timeout=self.timeout)
            return True
        
        except Exception as e:
            return False
        
    def remove_duplicated(self, anyList: list) -> list:

        cleaned_list = [dict.fromkeys(anyList)]

        return cleaned_list

class Socks5ProxyChecker():
    """"
    (Socks5 Type Proxy)
    Return True If The Given Proxy Is Working, 
    Return False If The Given Proxy Is Dead
    """
    def __init__(self, proxy: str, timeout: float) -> None:
        self.proxy = proxy
        self.timeout = timeout
    

    def __buildHandler__(self):

        proxyHandler = urllib.request.ProxyHandler(proxies={'https': f'socks5://{self.proxy}'})

        return proxyHandler
    
    def __build_opener__(self, handler):

        return urllib.request.build_opener(handler)
    
    def __install_opener__(self, opener):

        return urllib.request.install_opener(opener)
    
    def start_checker(self):
        handler = self.__buildHandler__()
        opener = self.__build_opener__(handler)
        self.__install_opener__(opener)

        try:

            resp = urllib.request.urlopen('https://github.com', timeout=self.timeout)
            return True
        
        except Exception as e:
            return False
        
    def remove_duplicated(self, anyList: list) -> list:

        cleaned_list = [dict.fromkeys(anyList)]

        return cleaned_list

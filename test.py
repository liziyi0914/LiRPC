from core import *

server=RPCServer()

@server.Function('add')
def plus(x,y,**kwargs):
    print(('%s+%s=%s'%(x,y,x+y)))
    return x+y

@server.Class('Magic',['who'])
class MagicClass:
    def __init__(self,**kwargs):
        print('Hello Magic!')
    def who(self,**kwargs):
        print('I LOVE HP!')
        return 233

#    server.regFunction('add',plus)
#    server.regClass('Magic',MagicClass,['who'])

server.Variable('ip','192.168.0.1')
desc=server.genRemoteDesc()

client=RPCClient(server)
client.load(desc)
remote=client.remote
print(remote.add(**{'x':1,'y':2}))
m=remote.Magic()
m.who()
print(remote.ip)
remote.ip='127.0.0.1'
print(remote.ip)
remote.mac = 'Null'
print(remote.mac)

class Test:
    def do(self):
        m.who()

t=Test()
t.do()

import json
import random


class RPCServer():
    def __init__(self):
        self.regf = {}
        self.regf_cfg = {}
        self.regc = {}
        self.regc_cfg = {}
        self.cInst = {}
        self.regv = {}
        self.regv_cfg = {}

    def _checkType(self,name):
        builtin = [
                str(int),
                str(float),
                str(str),
                str(bool),
                str(tuple),
                str(list),
                str(dict),
                str(None)
                ]
        print(builtin)
        return str(type(name)) in builtin

    def getRegList(self):
        return {
            'Variables': {k: v
                          for k, v in self.regv_cfg.items()},
            'Functions': {k: v
                          for k, v in self.regf_cfg.items()},
            'Classes': {k: v
                        for k, v in self.regc_cfg.items()}
        }

    def regVariable(self, name, typestr, value=None):
        self.regv[name] = value
        self.regv_cfg[name] = {'Name': name, 'Type': typestr}

    def getVariable(self, name):
        return self.regv[name]

    def setVariable(self, name, value):
        self.regv[name] = value

    def regFunction(self, name, function, args={}, ret='None'):
        self.regf[name] = function
        self.regf_cfg[name] = {'Name': name, 'Args': args, 'Ret': ret}

    def callFunction(self, name, kwargs):
        return self.regf[name](**kwargs)

    def regClass(self, name, cls, functions=[]):
        self.regc[name] = cls
        self.regc_cfg[name] = {
            'Name': name,
            'Functions': [{
                'Name': f['Name'],
                'Args': f['Args'],
                'Ret': f['Ret']
            } for f in functions]
        }

    def createClassInstance(self, name, kwargs={}):
        r = random.Random()
        instName = hex(r.randint(0, 256 * 256 * 256 * 256)) + '@' + name
        while (instName in self.cInst):
            instName = hex(r.randint(0, 256 * 256 * 256 * 256)) + '@' + name
        self.cInst[instName] = self.regc[name](**kwargs)
        return instName

    def callClassFunction(self, instName, name, kwargs={}):
        return getattr(self.cInst[instName], name)(**kwargs)

    def executeJSON(self, jsonstr):
        jsonobj = json.loads(jsonstr)
        f = jsonobj['Function']
        args = jsonobj['Args']
        ret = {"Function": f, "Return": ''}
        if '@' in f:
            ret['Return'] = self.callClassFunction(f[:f.find('.')],
                                                   f[f.find('.') + 1:], args)
        elif '#' in f:
            ret['Return'] = self.createClassInstance(f[f.find('#') + 1:], args)
        else:
            ret['Return'] = self.callFunction(f, args)
        return ret

class RPCClient:
    def __init__(self,server):
        self.server = server

    def sendPacket(self,packet):
        return self.server.executeJSON(packet)

    def genRequestPacket(self,name,kwargs):
        packet = {
                'Function': name,
                'Args': kwargs
                }
        print(packet)
        return json.dumps(packet)
    
    def genFunction(self,name):
        def f(**kwargs):
            pack = self.genRequestPacket(name,kwargs)
            return self.sendPacket(pack)
        return f

    def genClass(self,name,functions=[]):
        cli = self
        cname = name
        cfunctions = functions
        class c:
            def __init__(self,**kwargs):
                pack = cli.genRequestPacket('#%s'%(cname,),kwargs)
                self.id = cli.sendPacket(pack)['Return']
                for func in cfunctions:
                    def f(self,**kwargs):
                        pack = cli.genRequestPacket('%s.%s'%(self.id,func['Name']),kwargs)
                        print(pack)
                        return cli.sendPacket(pack)
                    setattr(c,func['Name'],f)
        return c


def plus(x,y):
    print(('%s+%s=%s'%(x,y,x+y)))
    return x+y
class MagicClass:
    def __init__(self,**kwargs):
        print('Hello Magic!')
    def who(self,**kwargs):
        print('I LOVE HP!')
        return 233


server=RPCServer()
server.regFunction('add',plus)
server.regClass('Magic',MagicClass,[{'Name':'who','Args':[],'Ret':'Int'}])
client=RPCClient(server)
add=client.genFunction('add')
Magic=client.genClass('Magic',functions=[{'Name':'who'}])
print(add(**{'x':1,'y':2}))
m=Magic()
m.who()

import json
import random

class RPCServer():
    def __init__(self):
        self.regf = {}
        self.regf_cfg = []
        self.regc = {}
        self.regc_cfg = {}
        self.cInst = {}
        self.regv = {}
        self.regv_cfg = []

    def genRemoteDesc(self):
        return {
            'Variables': self.regv_cfg,
            'Functions': self.regf_cfg,
            'Classes': {k: v
                        for k, v in self.regc_cfg.items()}
        }

    def regVariable(self, name, value=None):
        self.regv[name] = value
        self.regv_cfg.append(name)
        self.regFunction('_get_%s'%(name,),self.getVariable)
        self.regFunction('_set_%s'%(name,),self.setVariable)

    def getVariable(self, name, **kwargs):
        return self.regv[name]

    def setVariable(self, name, value, **kwargs):
        self.regv[name] = value

    def regFunction(self, name, function):
        self.regf[name] = function
        self.regf_cfg.append(name)

    def callFunction(self, name, kwargs):
        return self.regf[name](**kwargs)

    def regClass(self, name, cls, functions=[]):
        self.regc[name] = cls
        self.regc_cfg[name] = {
            'Name': name,
            'Functions': functions
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

    def executeJSON(self, jsonstr,inst = None, callback = lambda inst,ret:str(inst)):
        jsonobj = json.loads(jsonstr)
        f = jsonobj['Function']
        args = jsonobj['Args']
        ret = {"Function": f, "Return": ''}
        if '@' in f:
            r = self.callClassFunction(f[:f.find('.')],
                                                   f[f.find('.') + 1:], args)
        elif '#' in f:
            r = self.createClassInstance(f[f.find('#') + 1:], args)
        else:
            r = self.callFunction(f, args)
        print('Instance:',callback(inst,r))
        ret['Return'] = r
        return ret
    
    def Function(self,name):
        def proxy(f):
            self.regFunction(name,f)
            return f
        return proxy

    def Class(self,name,functions=[]):
        def proxy(c):
            self.regClass(name,c,functions)
            return c
        return proxy

    def Variable(self,name,value):
        self.regVariable(name,value)
        return value

class RPCClient:
    def __init__(self,server):
        self.server = server

    def load(self,remoteDesc):
        client = self
        class Remote:
            def __init__(self):
                object.__setattr__(self,'remoteVariable',[])

            def __getattr__(self,name):
                if name in self.remoteVariable:
                    pack = client.genRequestPacket('_get_%s'%(name,),{'name':name})
                    return client.sendPacket(pack)
                else:
                    return None

            def __setattr__(self,name,value):
                if name in self.remoteVariable:
                    pack = client.genRequestPacket('_set_%s'%(name,),{'name':name,'value':value})
                    client.sendPacket(pack)
                else:
                    object.__setattr__(self,name,value)

        self.remote = Remote()
        print('==Desc==')
        for it in remoteDesc['Functions']:
            setattr(self.remote,it,self.genFunction(it))
        for k,v in remoteDesc['Classes'].items():
            setattr(self.remote,k,self.genClass(k,v['Functions']))
        for it in remoteDesc['Variables']:
            self.remote.remoteVariable.append(it)
        print(dir(self.remote))
        print('========')

    def sendPacket(self,packet):
        return self.server.executeJSON(packet,self)

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
                        pack = cli.genRequestPacket('%s.%s'%(self.id,func),kwargs)
                        print(pack)
                        return cli.sendPacket(pack)
                    setattr(c,func,f)
        return c

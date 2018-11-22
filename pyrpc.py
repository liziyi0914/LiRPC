

class RPC():
    def __init__(self):
        self.regf = {}
        self.regf_cfg = {}
        self.regc = {}
        self.regc_cfg = {}
        self.cInst = {}
        self.regv = {}
        self.regv_cfg = {}

    def getRegList(self):
        return {
                'Variables': {k:v for k,v in self.regv_cfg.items()},
                'Functions': {k:v for k,v in self.regf_cfg.items()},
                'Classes': {k:v for k,v in self.regc_cfg.items()}
                }

    def regVariable(self,name,typestr,value=None):
        self.regv[name] = value
        self.regv_cfg[name] = {
                'Name': name,
                'Type': typestr
                }

    def getVariable(self,name):
        return self.regv[name]

    def setVariable(self,name,value):
        self.regv[name] = value

    def regFunction(self,name,function,args={},ret='None'):
        self.regf[name] = function
        self.regf_cfg[name] = {
                'Name': name,
                'Args': args,
                'Ret': ret
                }

    def callFunction(self,name,kwargs):
        return self.regf[name](**kwargs)

    def regClass(self,name,cls,functions=[]):
        self.regc[name] = cls
        self.regc_cfg[name] = {
                'Name': name,
                'Functions': [{
                    'Name': f['name'],
                    'Args': f['args'],
                    'Ret': f['ret']
                    } for f in functions]
                }

    def createClassInstance(self,name,kwargs={}):
        instName = '@'+name
        self.cInst[instName] = self.regc[name](**kwargs)
        return instName

    def callClassFunction(self,instName,name,kwargs={}):
        return getattr(self.cInst[instName],name)(**kwargs)


def add(a,b):
    print(a+b)

class Math():
    def __init__(self):
        print('Math is initing...')

    def multiply(self,a,b):
        print(a*b)

t = 1024

add(1,2)
rpc = RPC()
rpc.regVariable('t','Int',t)
print(rpc.getVariable('t'))
rpc.setVariable('t',512)
print(rpc.getVariable('t'))
rpc.regFunction('add',add,{'a':'Int','b':'Int'},'Int')
rpc.callFunction('add',{'a':2,'b':3})
rpc.regClass('Math',Math,[{'name':'multiply','args':[],'ret':''}])
m = rpc.createClassInstance('Math')
print(m)
print(rpc.callClassFunction(m,'multiply',{'a':3,'b':4}))
print(rpc.getRegList())

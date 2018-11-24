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
            'Name':
            name,
            'Functions': [{
                'Name': f['name'],
                'Args': f['args'],
                'Ret': f['ret']
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

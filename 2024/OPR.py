
from scipy.sparse import csr_array
from scipy.sparse.linalg import spsolve, norm
import numpy as np
from scipy.sparse.linalg import lsqr
from scipy.linalg import lstsq


class OPR: 
    @staticmethod
    def get_rows(m):
        yield m.alliances.red.team_keys, m.score_breakdown['red']['totalPoints']
        yield m.alliances.blue.team_keys, m.score_breakdown['blue']['totalPoints']

    def __init__(self, matches, teams: set):
        team_lookup = dict((k,i) for (i,k) in enumerate(teams))
        
        A_data = []
        row = []
        col = []
        b = []
        ctr = 0
        for m in map(OPR.get_rows, matches):
            for r in m:
                for t in r[0]:
                    row.append(len(b))
                    col.append(team_lookup[t])
                    A_data.append(1)
                b.append(r[1])
        b = np.array(b)            
        A = csr_array((A_data, (row, col)), shape=(len(b), len(team_lookup)))
        print(A.shape, b.shape )
        #x = spsolve(A, b)
        #x

        # Thanks ChatGPT!
        x, residuals, rank, s = lstsq(A.todense(), b)

        RSS = residuals.sum()
        Rinv = np.linalg.inv(np.triu(s))

        sigmas = np.sqrt(RSS / (len(b) - len(x)) * np.diag(Rinv))

        #return_values = lsqr(A, b, calc_var=True)
        #result = return_values
        #print(result)
        #x = return_values[0]
        #var = return_values[-1]
        #print(var)

        #for t,opr,sigma in sorted(opr, key=lambda x: x[1], reverse=True):
        #    print(t,opr,sigma)

        #print((A@x).shape,b.shape)
        #print(A@x-b)
        err = np.mean(A@x-b)
        print(f'Error: {err}')
        #self.opr = [(t,x[i],sigmas[i]) for i,t in enumerate(teams)]
        self.opr_lookup = dict([(t,{'opr':x[i],'sigma':sigmas[i]}) for i,t in enumerate(teams)])
        self.opr_lookup[''] = {'opr':0,'sigma':0}

    def predict(self, red,blue):
        mu = []
        sigma = []
        for r in red:
            mu.append(self.opr_lookup[r]['opr'])
            sigma.append(self.opr_lookup[r]['sigma'])
        for b in blue:
            mu.append(-self.opr_lookup[b]['opr'])
            sigma.append(self.opr_lookup[b]['sigma'])
        mu = sum(mu)
        sigma = np.linalg.norm(sigma)
        return(mu,sigma)